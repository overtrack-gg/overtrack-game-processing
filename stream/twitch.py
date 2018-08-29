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

from util import humansize

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
            self.chunk = chunk

            r = requests_session.get(self.chunk.url, stream=True)
            r.raise_for_status()

            logger.debug('Downloading chunk at %1.1fs', self.chunk.timestamp)
            self.ts = tempfile.NamedTemporaryFile(
                prefix=f'twitch_{ self.chunk.stream_source.rsplit("/")[-1] }_',
                suffix=f'_{ self.chunk.timestamp * 1000 :.0f}.ts',
                delete=False
            )
            if max_kb is None:
                shutil.copyfileobj(r.raw, self.ts)
            else:
                for i, chunk in enumerate(r.iter_content(1024)):
                    self.ts.write(chunk)
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

    def __init__(self, stream_name, min_recheck_time=1, max_kb=None):
        self.stream_name = stream_name
        self.min_recheck_time = min_recheck_time
        self.max_kb = max_kb

        self.stream_url = stream_name
        if not stream_name.startswith('http'):
            if 'twitch.tv' in stream_name:
                self.stream_url = 'https://' + stream_name
            else:
                self.stream_url = 'https://twitch.tv/' + stream_name

        self.streams = streamlink.streams(self.stream_url)
        self.live = 'video' not in self.stream_url
        self.queue: queue.Queue[self.DownloadedTSChunk] = queue.Queue(1)

        logger.info('Reading from stream %s', self.streams['best'])

        self.stop_ = False
        super().__init__(name='TwitchLiveTSDownloader')

    def run(self):
        try:
            if self.live:
                self.loop_for_last()
            else:
                self.download_all()
        except Exception as e:
            logger.exception('Got exception in %s', self.name, exc_info=e)
            self.queue.put(e)
        self.queue.put(None)

    def loop_for_last(self):
        last_check = 0
        previous_chunk = None
        while not self.stop_:
            if time.time() - last_check < self.min_recheck_time:
                time.sleep(0.01)
                continue
            last_check = time.time()

            chunks = self.download_playlist()
            if not len(chunks):
                continue
            chunk = chunks[-1]

            # wait until we have a new chunk
            if chunk == previous_chunk:
                logger.debug('Same chunk')
                continue

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
        playlist = self.download_playlist()[61:]
        self.enqueue_chunks(playlist)

    def download_playlist(self) -> List[TSChunk]:
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
            line = next(lines, None)
            if not line:
                break

            if ':' in line:
                command, args_str = line[1:].split(':', 1)
            else:
                command = line[1:]
                args_str = None
            if command == 'EXT-X-TWITCH-ELAPSED-SECS':
                end_time = float(args_str)
            elif command == 'EXTINF':
                url = next(lines)
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


