import bisect
import logging
import string
from typing import ClassVar, List, Optional, Sequence, Tuple, Union

import numpy as np
from dataclasses import dataclass

from overtrack_cv.games.apex import data
from overtrack.apex.collect.apex_game.combat import Combat
from overtrack_cv.frame import Frame
from overtrack.util import arrayops, s2ts, textops, validate_fields, round_floats


@dataclass
@round_floats
class WeaponStats:
    weapon: str
    time_held: float = 0
    time_active: float = 0

    knockdowns: int = 0


@dataclass
@validate_fields
class Weapons:
    weapon_stats: List[WeaponStats]

    logger: ClassVar[logging.Logger] = logging.getLogger(__qualname__)

    WEAPON_COLOURS_SELECTED = {
        # Light
        (45, 84, 125): (True, 'Light'),
        (28, 42, 60): (False, 'Light'),

        # Heavy
        (89, 107, 56): (True, 'Heavy'),
        (42, 51, 34): (False, 'Heavy'),

        # Energy
        (40, 110, 90): (True, 'Energy'),
        (29, 55, 46): (False, 'Energy'),

        # Shotgun
        (7, 32, 107): (True, 'Shotgun'),
        (10, 17, 48): (False, 'Shotgun'),

        # Sniper
        (126, 42, 53): (True, 'Shotgun'),
        (57, 20, 24): (False, 'Shotgun'),

        # Special
        (17, 149, 178): (True, 'Special'),
        (39, 78, 90): (False, 'Special'),
    }
    WEAPON_COLOUR_MATCH_THRESHOLD = 30

    def __init__(self, frames: List[Frame], combat: Combat, debug: Union[bool, str] = False):
        self.weapon_timestamp = [round(f.timestamp - frames[0].timestamp, 2) for f in frames if f.apex.weapons]
        self.weapon_data = [f.apex.weapons for f in frames if f.apex.weapons]
        self.logger.info(f'Resolving weapons from {len(self.weapon_data)} weapon frames')

        weapon1 = self._get_weapon_map(0)
        weapon1_selected_vals = np.array([w.selected_weapons[0] for w in self.weapon_data])
        if len(weapon1_selected_vals):
            if len(weapon1_selected_vals.shape) == 2 and weapon1_selected_vals.shape[1] == 3:
                # v2: colours
                weapon1_selected = np.array([wid != -1 and self._is_weapon_selected(c) for wid, c in zip(weapon1, weapon1_selected_vals)])
            else:
                # v1: key hint brigtness
                weapon1_selected = (arrayops.medfilt(weapon1_selected_vals, 3) < 200) & np.not_equal(weapon1, -1)
        else:
            weapon1_selected = np.array((0,), dtype=np.bool)
        clip1 = [wep.clip if sel and wep.clip is not None else np.nan for sel, wep in zip(weapon1_selected, self.weapon_data)]
        ammo1 = [wep.ammo if sel and wep.ammo is not None else np.nan for sel, wep in zip(weapon1_selected, self.weapon_data)]

        weapon2 = self._get_weapon_map(1)
        weapon2_selected_vals = np.array([w.selected_weapons[1] for w in self.weapon_data])
        if len(weapon2_selected_vals):
            if len(weapon2_selected_vals.shape) == 2 and weapon2_selected_vals.shape[1] == 3:
                weapon2_selected = np.array([wid != -1 and self._is_weapon_selected(c) for wid, c in zip(weapon2, weapon2_selected_vals)])
            else:
                weapon2_selected = (arrayops.medfilt(weapon2_selected_vals, 3) < 200) & np.not_equal(weapon2, -1)
        else:
            weapon2_selected = np.array((0,), dtype=np.bool)
        clip2 = [wep.clip if sel and wep.clip is not None else np.nan for sel, wep in zip(weapon2_selected, self.weapon_data)]
        ammo2 = [wep.ammo if sel and wep.ammo is not None else np.nan for sel, wep in zip(weapon2_selected, self.weapon_data)]

        if len(weapon1) and len(weapon2):
            have_weapon = np.convolve(np.not_equal(weapon1, -1) + np.not_equal(weapon2, -1), np.ones((10,)), mode='valid')
            self.first_weapon_timestamp = self._get_firstweapon_pickup_time(have_weapon)
        else:
            have_weapon = np.array((0,), dtype=np.bool)
            self.first_weapon_timestamp = frames[-1].timestamp

        self.weapon_stats: List[WeaponStats] = []
        self.selected_weapon_at: List[Optional[WeaponStats]] = [None for _ in self.weapon_timestamp]
        self._add_weapon_stats(weapon1, weapon1_selected)
        self._add_weapon_stats(weapon2, weapon2_selected)
        self._add_combat_weaponstats(combat)
        self.weapon_stats = sorted(self.weapon_stats, key=lambda stat: (stat.knockdowns, stat.time_active), reverse=True)
        for w in self.weapon_stats:
            w.time_active = round(w.time_active, 1)
            w.time_held = round(w.time_held, 1)
        self.logger.info(f'Resolved weapon stats: {self.weapon_stats}')

        if debug is True or debug == self.__class__.__name__:
            self._debug(combat, have_weapon, weapon1, weapon1_selected_vals, weapon1_selected, weapon2, weapon2_selected_vals, weapon2_selected, clip1, clip2)

    def _is_weapon_selected(self, colour: np.ndarray) -> bool:
        best = None
        for target, (selected, ammo_type) in self.WEAPON_COLOURS_SELECTED.items():
            diff = np.linalg.norm(colour - target)
            if best is None or best[0] > diff:
                best = diff, target, selected, ammo_type
            if diff < self.WEAPON_COLOUR_MATCH_THRESHOLD:
                return selected
        self.logger.debug(f'Could not resolve weapon colour={tuple(colour)}, best={best[1]}, diff={best[0]:.2f}, weapon={best[3]}, selected={best[2]}')
        return False

    def _debug(self, combat, have_weapon, weapon1, weapon1_selected_vals, weapon1_selected, weapon2, weapon2_selected_vals, weapon2_selected, clip1, clip2):
        import matplotlib.pyplot as plt
        import cv2

        plt.figure()
        plt.title('Weapon Cols')
        im = np.vstack([
            np.repeat(np.expand_dims(weapon1_selected_vals, 0), 30, 0),
            np.repeat(np.expand_dims(weapon2_selected_vals, 0), 30, 0),
        ]).astype(np.uint8)
        plt.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB), interpolation='none')

        plt.figure()
        plt.title('Selected Weapon')
        plt.plot(self.weapon_timestamp, weapon1_selected.astype(np.float) + 0.1)
        plt.plot(self.weapon_timestamp, weapon2_selected)

        plt.figure()
        plt.title('Clip')
        plt.scatter(self.weapon_timestamp, clip1)
        plt.scatter(self.weapon_timestamp, clip2)

        def make_weaponplot():
            for event in combat.events:
                c = None
                if event.type == 'KNOCKED DOWN':
                    c = 'red'
                elif event.type == 'ASSIST, ELIMINATION':
                    c = 'orange'
                if c:
                    plt.axvline(event.timestamp, color=c)
            for i, n in enumerate(data.weapon_names):
                plt.text(0, i + 0.25, n)

        plt.figure()
        plt.title('Weapon 1')
        plt.scatter(self.weapon_timestamp, weapon1)
        plt.plot(self.weapon_timestamp, weapon1_selected * 5)
        make_weaponplot()
        plt.figure()

        plt.title('Weapon 2')
        plt.scatter(self.weapon_timestamp, weapon2)
        plt.plot(self.weapon_timestamp, weapon2_selected * 5)
        make_weaponplot()

        plt.figure('Have Weapon')
        plt.plot(have_weapon)
        plt.axhline(6, color='r')
        plt.show()

    def _get_weapon_map(self, index: int) -> np.ndarray:
        def stripname(s: str) -> str:
            return textops.strip_string(s, string.ascii_uppercase + string.digits + '- ')

        weapon = np.full((len(self.weapon_data, )), fill_value=-1, dtype=np.int)
        name2index = {stripname(n): i for i, n in enumerate(data.weapon_names)}
        for i, weapons in enumerate(self.weapon_data):
            name = weapons.weapon_names[index]
            ratio, match = textops.matches_ratio(
                stripname(name),
                data.weapon_names
            )
            if ratio > 0.75:
                weapon[i] = name2index[match]
        return weapon

    def _get_firstweapon_pickup_time(self, have_weapon: np.ndarray) -> Optional[float]:
        have_weapon_inds = np.where(have_weapon > 4)[0]
        if len(have_weapon_inds):
            first_weapon_index = have_weapon_inds[0] + 5
            if 0 <= first_weapon_index < len(self.weapon_timestamp):
                ts = self.weapon_timestamp[first_weapon_index]
                self.logger.info(f'Got first weapon pickup at {s2ts(ts)}')
                return ts
            else:
                self.logger.warning(f'Got weapon pickup at invalid index: {first_weapon_index}')
                return None
        else:
            self.logger.warning(f'Did not see any weapons')
            return None

    def _add_weapon_stats(self, weapon: Sequence[int], weapon_selected: Sequence[bool]) -> None:
        weapon_stats_lookup = {
            s.weapon: s for s in self.weapon_stats
        }

        last: Optional[Tuple[float, int, bool]] = None
        for i, (ts, weapon_index, selected) in enumerate(zip(self.weapon_timestamp, weapon, weapon_selected)):
            if weapon_index == -1:
                continue
            if last is not None:
                weapon_name = data.weapons[weapon_index].name
                weapon_stats = weapon_stats_lookup.get(weapon_name)
                if not weapon_stats:
                    weapon_stats = WeaponStats(weapon_name)
                    self.weapon_stats.append(weapon_stats)
                    weapon_stats_lookup[weapon_name] = weapon_stats

                if last[1] == weapon_index:
                    weapon_stats.time_held += ts - last[0]

                if selected:
                    self.selected_weapon_at[i] = weapon_stats
                    if last[2]:
                        weapon_stats.time_active += ts - last[0]

            last = ts, weapon_index, selected

    def _add_combat_weaponstats(self, combat: Combat):
        # n.b. the weapon is only relevant for knockdowns and elimination_assists, and only useful for knockdowns of these
        # knockdowns: we knocked someone down - don't know who will finish or how
        # elimination_assists: we eliminated someone ourselves with a weapon
        for event in combat.knockdowns:
            weapon_stats = self._get_weapon_at(event.timestamp)
            if weapon_stats:
                weapon_stats.knockdowns += 1
                event.weapon = weapon_stats.weapon
                self.logger.info(f'Found weapon={weapon_stats.weapon} for {event}')

    def _get_weapon_at(self, timestamp: float, max_distance: float = 10) -> Optional[WeaponStats]:
        index = bisect.bisect(self.weapon_timestamp, timestamp) - 1
        if not (0 <= index < len(self.weapon_timestamp)):
            self.logger.error(f'Got invalid index trying to find weapon @ {timestamp:.1f}s', exc_info=True)
            return None

        self.logger.debug(
            f'Trying to resolve weapon at {timestamp:.1f}s - '
            f'got weapon index={index} -> {self.weapon_timestamp[index]:.1f}s'
        )
        for ofs in range(-5, 6):
            check = index + ofs
            if 0 <= check < len(self.weapon_timestamp):
                weap = self.selected_weapon_at[check]
                self.logger.debug(f'ofs={ofs:+d} > ind={check} ts={self.weapon_timestamp[check]:.1f} > weap={weap.weapon if weap else None}')

        for fan_out in range(20):
            for sign in -1, 1:
                check = index + sign * fan_out
                if 0 <= check < len(self.weapon_timestamp):
                    ts = self.weapon_timestamp[check]
                    distance = abs(timestamp - ts)
                    if distance < max_distance:
                        stat = self.selected_weapon_at[check]
                        if stat:
                            self.logger.debug(f'Found {stat} at {ts:.1f}s - distance {distance}')
                            return stat

        self.logger.warning(f'Could not find weapon for ts={timestamp:.1f}s')
