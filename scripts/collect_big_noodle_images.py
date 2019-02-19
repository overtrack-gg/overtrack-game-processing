import os

import cv2
import shortuuid
import tensorflow as tf

from overtrack.game import Frame
from overtrack.game.loading_map.loading_map_processor import LoadingMapProcessor
from overtrack.game.processor import ShortCircuitProcessor
from overtrack.game.tab.tab_processor import TabProcessor


def save_images(typ, names, ims):
    d = os.path.join('C:\\scratch\\big_noodle', typ)
    for name, im in zip(names, ims):
        sd = os.path.join(d, name)
        os.makedirs(sd, exist_ok=True)
        cv2.imwrite(f'{sd}\\{shortuuid.uuid()}.png', im)


def main():
    pipeline = ShortCircuitProcessor(
        TabProcessor(save_name_images=True),
        LoadingMapProcessor(save_name_images=True),
        order_defined=False
    )
    last_teams: LoadingMapProcessor.Teams = None
    current_teams: LoadingMapProcessor.Teams = None

    DEBUG = False
    if DEBUG:
        image = cv2.imread('p.png')
        frame = Frame.create(
            image,
            0,
            debug=True
        )
        pipeline.process(frame)
        cv2.imshow('frame', frame.debug_image)
        cv2.waitKey(0)
        return

    # cap = VideoFrameExtractor(
    #     "C:/scratch/NRG Fahzix _ Educational support-v306835334.mp4",
    #     fps=1,
    #     seek=ts2ms('0:8:0') / 1000,
    #     debug=True
    # )
    # tsdownloader = TwitchLiveTSDownloader('aimbotcalvin')
    # cap = TSFrameExtractor(tsdownloader.queue, 10, extract_fps=4, debug_frames=True)
    # tsdownloader.start()
    # cap.start()

    tsdownloader = TwitchLiveTSDownloader('https://www.twitch.tv/videos/308743498', max_kb=250, seek=3*60+10)
    cap = TSFrameExtractor(tsdownloader.queue, 10, max_frames_per_chunk=1,  debug_frames=True)
    tsdownloader.start()
    cap.start()

    fourcc = cv2.VideoWriter_fourcc(*'DIVX')
    writer = cv2.VideoWriter('out.mp4', fourcc, 10, (1280, 720))

    while True:
        frame = cap.get()
        if isinstance(frame, Exception):
            raise frame
        if frame is None:
            break
        pipeline.process(frame)

        im = cv2.resize(frame.debug_image, (1280, 720))
        cv2.imshow('frame', im)

        if 'loading_map' in frame and frame.loading_map.teams:
            if not frame.loading_map.teams.blue_team[0]:
                current_teams = None
            if last_teams:
                if last_teams.blue_team == frame.loading_map.teams.blue_team and last_teams.red_team == frame.loading_map.teams.red_team:
                    current_teams = frame.loading_map.teams
            last_teams = frame.loading_map.teams

        if 'tab_screen' in frame or 'loading_map' in frame:
            # print(frame)
            cv2.imwrite('p.png', frame.image)
            cv2.waitKey(1)
            writer.write(im)
        else:
            cv2.waitKey(1)
        continue

        cv2.waitKey(1)
        if current_teams:
            if 'tab_screen' in frame:
                tab_screen: TabProcessor.TabScreen = frame.tab_screen
                save_images('tab_names', current_teams.blue_team, tab_screen.images.blue_team)
                save_images('tab_names', current_teams.red_team, tab_screen.images.red_team)
                # save_images('tab_ults', tab_screen.images.ult_images)
                # save_images('tab_hero_names', [tab_screen.images.player_hero_image])
                # save_images('tab_player_names', [tab_screen.images.player_name_image])

            if 'loading_map' in frame and frame.loading_map.teams:
                loading_map: LoadingMapProcessor.LoadingMap = frame.loading_map
                save_images('loading_names', current_teams.blue_team, loading_map.teams.images.blue_team)
                save_images('loading_names', current_teams.red_team, loading_map.teams.images.red_team)
                # save_images('loading_maps', [loading_map.images.map])
                # save_images('loading_modes', [loading_map.images.game_mode])

    writer.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    with tf.Session(config=tf.ConfigProto(log_device_placement=False, device_count={'GPU': 0})) as sess:
        main()
