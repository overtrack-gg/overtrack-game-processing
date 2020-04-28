import glob
import json
import os

import cv2
from tqdm import tqdm

from overtrack.frame import Frame, Timings
from overtrack.util import frameload
from overtrack.valorant.game.default_pipeline import create_pipeline
from overtrack.valorant.game.top_hud.top_hud_processor import TopHudProcessor


def main():

    version = 9

    # pipeline = TopHudProcessor()
    # TOREMOVE = ['top_hud']
    # min_time_between_frames = 0

    pipeline = create_pipeline(aggressive=True)
    TOREMOVE = ['home_screen', 'top_hud', 'timer', 'buy_phase', 'agent_select', 'postgame', 'scoreboard']
    min_time_between_frames = 0

    frames = []
    started = False
    last = 0

    bar = tqdm(sorted(glob.glob("D:/overtrack/valorant/game5/*.frame.json")))

    # bar = tqdm(sorted(glob.glob("D:/overtrack/valorant_stream/*.frame.json")))

    for p in bar:
        if '_frame' in p:
            np = p.replace('_frame', '.frame')
            os.rename(p, np)
            os.rename(p.replace('_frame.json', '_image.png'), p.replace('_frame.json', '.image.png'))
            os.rename(p.replace('_frame.json', '_debug_image.png'), p.replace('_frame.json', '.debug.png'))
            p = np

        bar.set_description(os.path.basename(p))

        print(p)
        with open(p) as f:
            orig_data = json.load(f)

        ftime = orig_data['timestamp']
        if ftime - last < min_time_between_frames:
            continue
        last = ftime

        if orig_data.get('pipeline_version', -1) >= version:
            frame = frameload.frames_load(orig_data, Frame)
        else:
            for toremove in TOREMOVE:
                if toremove in orig_data:
                    del orig_data[toremove]
            if 'valorant' in orig_data:
                del orig_data['valorant']

            frame = frameload.frames_load(orig_data, Frame)

            del frame['timings']
            frame.timings = Timings()
            if 'pipeline_version' in frame:
                del frame['pipeline_version']
            frame.pipeline_version = version

            del frame['image']
            del frame['debug_image']
            frame.image = cv2.imread(p.replace('.frame.json', '.image.png'))
            frame.debug_image = frame.image.copy()

            pipeline.process(frame)
            cv2.imshow('image', frame.debug_image)
            cv2.imwrite(p.replace('.frame.json', '.debug.png'), frame.debug_image)
            frame.strip()

            with open(p, 'w') as f:
                try:
                    json.dump(frameload.frames_dump(frame), f, indent=2)
                except Exception as e:
                    json.dump(orig_data, f, indent=2)
                    raise e
            cv2.waitKey(1)

        if frame.valorant.agent_select:
            if len(frames) and frame.timestamp - frames[0].timestamp > 120:
                print('stopping after', frames[-1].timestamp - frames[0].timestamp)
                break
            print('starting', frame.timestamp, frame.valorant.agent_select)
            started = True

        if started:
            frames.append(frame)

    with open('./frames.json', 'w') as f:
        json.dump(frameload.frames_dump(frames), f, indent=2)

    # with open('./frames.json') as f:
    #     frames = frameload.frames_load(json.load(f), List[Frame])

    # frames = [
    #     f
    #     for f in frames
    #     if f.timestamp < 1.5873e9
    # ]
    # start = frames[0].timestamp
    #
    # countdown_pattern = re.compile(r'^([01]:\d\d)|(0.\d\d)$')
    #
    # frames = [f for f in frames if 'timer' in f and f.timer.countdown and countdown_pattern.match(f.timer.countdown)]
    #
    # plt.figure()
    #
    # plt.scatter(
    #     [
    #         f.timestamp - start
    #         for f in frames
    #         if 'timer' in f and f.timer.countdown and countdown_pattern.match(f.timer.countdown)
    #     ],
    #     [
    #         ts2s(f.timer.countdown)
    #         for f in frames
    #         if 'timer' in f and f.timer.countdown and countdown_pattern.match(f.timer.countdown)
    #     ]
    # )
    # plt.scatter(
    #     [
    #         f.timestamp - start
    #         for f in frames
    #         if 'timer' in f and f.timer.spike_planted
    #     ],
    #     [
    #         5
    #         for f in frames
    #         if 'timer' in f and f.timer.spike_planted
    #     ],
    #     color='orange'
    # )
    #
    # full_duration = int(frames[-1].timestamp - start + 0.5) + 120
    # hough = np.zeros((full_duration, ))
    # for f in frames:
    #     if 'timer' in f and f.timer.countdown and countdown_pattern.match(f.timer.countdown):
    #         countdown = ts2s(f.timer.countdown)
    #         if countdown > 120:
    #             continue
    #         x_isct = int((f.timestamp - start) + countdown + 0.5)
    #         hough[x_isct] += 1
    #
    # # plt.figure()
    # plt.plot(np.linspace(0, full_duration, len(hough)), hough, color='r')
    # plt.show()


if __name__ == '__main__':
    main()