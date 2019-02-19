import json
import random
import subprocess

from overtrack.source.stream import Twitch

SAMPLES = 5


def main():
    stream = input('stream?\n').strip()
    # stream = 'https://www.twitch.tv/videos/303359180'

    t = Twitch(stream)
    playlist = t.ts_downloader.download_playlist()

    sum_bitrate = 0
    for _ in range(SAMPLES):
        chunk = random.choice(playlist)
        args = 'ffprobe -v quiet -print_format json -show_entries stream -show_format'.split()
        r = subprocess.check_output(args + [chunk.file]).decode('utf-8')
        chunk.delete()

        data = json.loads(r)
        nonvideo_bitrates = [int(s.get('bit_rate', 0)) for s in data['streams'] if s['codec_type'] != 'video']
        total_bitrate = int(data['format']['bit_rate'])
        vid_kbrate = (total_bitrate - sum(nonvideo_bitrates)) / 1000
        print(vid_kbrate, 'kb/s')
        sum_bitrate += vid_kbrate

    print()
    print('avg over', SAMPLES, 'samples:', sum_bitrate / SAMPLES, 'kb/s')


if __name__ == '__main__':
    main()
