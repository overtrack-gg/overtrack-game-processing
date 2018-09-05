import bisect
import os
import queue
import shutil
import tempfile
import time
import requests
import streamlink
import logging
from typing import NamedTuple, List
from threading import Thread

from overtrack.util import humansize

logger = logging.getLogger(__name__)
requests_session = requests.Session()


class TwitchLiveTSDownloader(Thread):

    class TSChunk(NamedTuple):
        url: str
        timestamp: float
        duration: float

        playlist_source: str
        stream_source: str

        def __eq__(self, other):
            if not isinstance(other, self.__class__):
                return False
            return self.url == other.url

    class DownloadedTSChunk:

        def __init__(self, chunk: 'TwitchLiveTSDownloader.TSChunk', max_kb: int=None) -> None:
            """
            :param chunk: chunk to download
            :param max_kb: maximum kb to download, or None to download the full file
            """
            self.chunk = chunk

            logger.debug('Downloading chunk at %1.1fs', self.chunk.timestamp)
            self.ts = tempfile.NamedTemporaryFile(
                prefix=f'twitch_{ self.chunk.stream_source.rsplit("/")[-1] }_',
                suffix=f'_{ self.chunk.timestamp * 1000 :.0f}.ts',
                delete=False
            )

            r = requests_session.get(self.chunk.url, stream=True)
            r.raise_for_status()

            # FIXME: connection can die here - retry with exponential backoff up to a limit

            if max_kb is None:
                shutil.copyfileobj(r.raw, self.ts)
            else:
                for i, chunk in enumerate(r.iter_content(1024)):
                    self.ts._write(chunk)
                    if i >= max_kb:
                        r.close()
                        break
            logger.debug('Saved %s to %s', humansize(self.ts.tell()), self.file)
            self.ts.close()

        @property
        def file(self):
            return self.ts.name

        def delete(self):
            os.remove(self.file)

    def __init__(self, source: str, min_recheck_time: float=None, max_kb: int=None, seek: float=0, queuesize: int=None) -> None:
        """
        :param source: The source to fetch .ts chunks from. Can be a stream or a VOD
        :param min_recheck_time: Minimum of time to wait when before checking for the next chunk. Only valid for live streams.
        :param max_kb: Maximum kb to download for each chunk or None to download the full chunk. This is useful if we only want the first frame(s) of a chunk.
        :param seek: Position (in seconds) to seek to in a vod.
        :param queuesize: Size of the queue to download chunks to or None to choose a default depending on live status.
        """
        self.stream_name = source
        self.max_kb = max_kb
        self.seek = seek

        self.stream_url = source
        if not source.startswith('http'):
            if 'twitch.tv' in source:
                self.stream_url = 'https://' + source
            else:
                self.stream_url = 'https://twitch.tv/' + source

        # download list of m3u8 streams
        self.streams = streamlink.streams(self.stream_url)

        # if the source had 'video' in it then it comes from /video/<id> or /videos/<id> and is a VOD
        self.live = 'video' not in self.stream_url

        if seek and self.live:
            raise ValueError('Cannot seek in live stream')

        if min_recheck_time is not None and not self.live:
            raise ValueError('Cannot specify recheck time on non-live stream')
        if min_recheck_time is None and self.live:
            min_recheck_time = 1.
        self.min_recheck_time = min_recheck_time

        # automatically choose queue size
        # if live then we should be downloading chunks as they arrive and want lower latency, so size=1
        # if playlist then we want to maximise download rate and can queue up more so size=10
        if not queuesize:
            if self.live:
                queuesize = 1
            else:
                queuesize = 10
        self.queuesize = queuesize
        self.queue: queue.Queue[self.DownloadedTSChunk] = queue.Queue(queuesize)

        logger.info('Reading from stream %s', self.streams['best'])

        self.stop_ = False
        super().__init__(name='TwitchLiveTSDownloader', daemon=True)

    def run(self) -> None:
        try:
            if self.live:
                self.loop_for_last()
            else:
                self.download_all()
        except Exception as e:
            logger.exception('Got exception in %s', self.name, exc_info=e)
            self.queue.put(e)
        self.queue.put(None)

    def loop_for_last(self) -> None:
        last_check = 0
        previous_chunk = None
        while not self.stop_:
            # wait at least min_recheck_time between checking the playlist for a new chunk
            if time.time() - last_check < self.min_recheck_time:
                time.sleep(1)
                continue
            last_check = time.time()

            # download the new playlist and get the last chunk
            chunks = self.download_playlist()
            if not len(chunks):
                continue
            chunk = chunks[-1]

            # check this chunk is new, not just the one we processed last time
            if chunk == previous_chunk:
                logger.debug('Same chunk')
                continue

            # detect and warn in skipped chunks
            try:
                skipped_chunks = (chunks.index(chunk) - chunks.index(previous_chunk)) - 1
            except ValueError:
                pass
            else:
                if skipped_chunks:
                    logger.warning('Skipped %d chunks', skipped_chunks)

            self.enqueue_chunks([chunk])
            previous_chunk = chunk

    def download_all(self):
        playlist = self.download_playlist()
        if self.seek:
            # find chunk that contains timestamp 'seek' and only use the playlist from that point
            index = max(0, bisect.bisect([c.timestamp for c in playlist], self.seek) - 1)
            logger.info('Seeking to %1.1fs in playlist => position %d/%d in playlist', self.seek, index, len(playlist))
            playlist = playlist[index:]
        else:
            logger.info('Downloaded playlist with %d chunks', len(playlist))
        self.enqueue_chunks(playlist)
        self.queue.put(None)

    def download_playlist(self) -> List[TSChunk]:
        # download playlist contents
        m3u8_url = self.streams['best'].url
        base_url = m3u8_url.rsplit('/', 1)[0]
        r = requests_session.get(m3u8_url)
        r.raise_for_status()

        if r.encoding is None:
            r.encoding = 'utf-8'

        end_time = 0.
        chunks = []

        lines = r.iter_lines(decode_unicode=True)
        while True:
            # parse commands 1-by-1
            line = next(lines, None)
            if not line:
                break

            # decode command
            # commands start with '#', so strip this off
            if ':' in line:
                command, args_str = line[1:].split(':', 1)
            else:
                command = line[1:]
                args_str = None

            if command == 'EXT-X-TWITCH-ELAPSED-SECS':
                # use twitch's extension to detect the timestamp that a live-playlist starts
                end_time = float(args_str)
            elif command == 'EXTINF':
                # EXTINF is followed by a URL
                url = next(lines)

                # live playlists do not include the HOST, just the path
                if not url.startswith('http'):
                    url = base_url + '/' + url

                length = float(args_str.split(',', 1)[0])
                chunks.append(self.TSChunk(
                    url,
                    timestamp=end_time,
                    duration=length,

                    playlist_source=m3u8_url,
                    stream_source=self.stream_name
                ))
                end_time += length

        return chunks

    def enqueue_chunks(self, chunks):
        for chunk in chunks:
            if self.stop_:
                return
            self.queue.put(
                self.DownloadedTSChunk(
                    chunk,
                    max_kb=self.max_kb
                )
            )

    def stop(self):
        self.stop_ = True


