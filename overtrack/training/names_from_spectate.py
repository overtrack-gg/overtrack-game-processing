# import cv2
# import logging
# import os
# from typing import List
#
# from overtrack.game import Frame
# from overtrack.game.killfeed import KillfeedProcessor
# from overtrack.game.processor import Processor
# from overtrack.game.spectator import SpectatorProcessor
#
# logger = logging.getLogger(__name__)
#
#
# class NamesFromSpectate(Processor):
#
#     SAVE_DIR = os.environ['NAME_IMAGE_SAVE_DIR']
#
#     def __init__(self, name: str, subname: str=None):
#         self.name = name
#         self.subname = subname
#
#     def process(self, frame: Frame) -> bool:
#         if 'killfeed' not in frame or 'spectator_bar' not in frame:
#             return False
#
#         kill: KillfeedProcessor.KillRow
#         for kill in frame.killfeed.kills:
#             for kill_player in (kill.left, kill.right):
#                 if not kill_player:
#                     continue
#
#                 team: List[SpectatorProcessor.Player]
#                 if kill_player.blue_team:
#                     team = frame.spectator_bar.left_team
#                 else:
#                     team = frame.spectator_bar.right_team
#
#                 hero2player = {p.hero: p for p in team if p}
#                 spec_player: SpectatorProcessor.Player = hero2player.get(kill_player.hero.split('.')[0])
#                 if not spec_player:
#                     logger.warning(
#                         'Could not find player on %s team playing %s (team was %s)',
#                         kill_player.hero,
#                         'blue' if kill_player.blue_team else 'red',
#                         [p.hero for p in team if p]
#                     )
#                 elif not spec_player.name:
#                     # name not parsed
#                     pass
#                 else:
#                     self._save_name(frame.killfeed.name_images[kill_player.index], kill_player.blue_team, spec_player.name, frame.timestamp * 1000)
#
#     def _save_name(self, image: 'np.ndarray', blue_team: bool, name: str, ms: int):
#         if '@' in name:
#             return
#         d = os.path.join(self.SAVE_DIR, self.name, self.subname or '0', 'rb'[blue_team] + '.' + name)
#         os.makedirs(d, exist_ok=True)
#         cv2.imwrite(os.path.join(d, f'{ ms :d}.png'), image)
#
