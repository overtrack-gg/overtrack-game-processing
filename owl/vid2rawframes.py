import os

from plugin_rig.video_capture import VideoFrameExtractor


def main() -> None:
    path = "M:/owl/{4 4 2019} {BOS vs ATL} Player 03 POV-brloDDAP_t8.mp4"
    video = VideoFrameExtractor(
        path,
        extract_fps=1,
        debug_frames=False,
    )

    dest = path.rsplit('.', 1)[0]
    os.makedirs(dest, exist_ok=True)
    for frame in video.tqdm():
        with open(f'{dest}/{frame.relative_timestamp}.raw', 'wb') as f:
            f.write(frame.image.flatten())

if __name__ == '__main__':
    main()
