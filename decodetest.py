import time
from threading import Thread

import av

Thread(target=time.sleep, args=(100000, ))

for _ in range(100):
    container = av.open('../fahzix.mp4')
    frames = []
    for i, f in enumerate(container.demux(0)):
        frames.append(f)
        if i > 200:
            break
    print('.')


# decode = False

# t0 = time.time()
# for i, p in enumerate(container.demux(0)):
#     if p.is_keyframe:
#         decode = True
#     if decode:
#         f = p.decode_one()
#         if f:
#             decode = False
#             print(i)
#             f.to_rgb().to_ndarray()
#
#     if i > 1000:
#         break
#
# print(time.time() - t0)
#
# import cv2
# vid = cv2.VideoCapture('../fahzix.mp4')
# t0 = time.time()
# for i in range(1000):
#     vid.read()
#     if not i % 120:
#         print(i)
#         vid.grab()
# print(time.time() - t0)
