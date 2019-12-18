import logging
from typing import Any, ClassVar, Dict, List, Optional, Tuple, Union

import typedload
from dataclasses import dataclass

from overtrack.apex.collect.apex_game.squad import Squad
from overtrack.frame import Frame
from overtrack.util import s2ts, validate_fields, round_floats


@dataclass
@round_floats
class CombatEvent:
    timestamp: float
    type: str
    inferred: bool = False
    weapon: Optional[str] = None
    location: Optional[Tuple[int, int]] = None

    def __str__(self):
        r = f'CombatEvent(ts={s2ts(self.timestamp)}, type={self.type}'
        if self.inferred:
            r += f', inferred=True'
        if self.weapon:
            r += f', weapon={self.weapon}'
        if self.location:
            r += f', location={self.location}'
        return r + ')'

    __repr__ = __str__


@dataclass
@validate_fields
class Combat:
    eliminations: List[CombatEvent]
    knockdowns: List[CombatEvent]
    elimination_assists: List[CombatEvent]
    knockdown_assists: List[CombatEvent]

    logger: ClassVar[logging.Logger] = logging.getLogger(__qualname__)

    def __init__(self, frames: List[Frame], placed: int, squad: Squad, debug: Union[bool, str] = False):
        self.combat_timestamp = [f.timestamp - frames[0].timestamp for f in frames if 'combat_log' in f]
        self.combat_data = [f.combat_log for f in frames if 'combat_log' in f]
        self.logger.info(f'Resolving combat from {len(self.combat_data)} combat frames')

        if debug is True or debug == self.__class__.__name__:
            import matplotlib.pyplot as plt

            plt.figure()
            plt.title('Combat Log Widths')
            for t, l in zip(self.combat_timestamp, self.combat_data):
                plt.scatter([t] * len(l.events), [e.width for e in l.events])
            plt.show()

        self.events = []

        self.eliminations = []
        self.knockdowns = []
        self.elimination_assists = []
        self.knockdown_assists = []

        seen_events = []
        combatevent_to_event = {}
        for ts, combat in zip(self.combat_timestamp, self.combat_data):
            for event in combat.events:
                matching = [
                    other_ts for other_ts, other in seen_events if
                    ts - other_ts < 10 and event.type == other.type and abs(event.width - other.width) < 10
                ]
                if not len(matching):
                    # new event
                    self.logger.info(f'Got new event @ {ts:.1f}s: {event}')
                    combat_event = None
                    if event.type == 'ELIMINATED':
                        # If we see an ELIMINATED, it means we have also scored a knockdown on that player
                        # Because knocking and eliminating the last player is equivalent, only ELIMINATED will show
                        # Insert the missing knock down if needed
                        matching_knockdowns = [
                            (ts, other) for other_ts, other in seen_events if
                            ts - other_ts < 30 and other.type == 'KNOCKED DOWN' and abs(event.width - other.width) < 7
                        ]
                        if not len(matching_knockdowns):
                            # don't have a matching knockdown for this elim - create one now
                            knockdown = CombatEvent(ts, 'downed', inferred=True)
                            self.logger.info(f'Could not find knockdown for {event} - inserting {knockdown}')
                            self.knockdowns.append(knockdown)
                            self.events.append(knockdown)

                        # add after inferred event
                        combat_event = CombatEvent(ts, 'eliminated')
                        self.eliminations.append(combat_event)

                    elif event.type == 'KNOCKED DOWN':
                        combat_event = CombatEvent(ts, 'downed')
                        self.knockdowns.append(combat_event)
                    elif event.type == 'ASSIST, ELIMINATION':
                        combat_event = CombatEvent(ts, 'assist.eliminated')
                        self.elimination_assists.append(combat_event)
                    elif event.type == 'ASSIST, KNOCK DOWN':
                        combat_event = CombatEvent(ts, 'assist.downed')
                        self.knockdown_assists.append(combat_event)

                    assert combat_event

                    # add last so inferred events are inserted first
                    self.events.append(combat_event)
                    combatevent_to_event[id(combat_event)] = event

                else:
                    self.logger.info(f'Already seen event @ {ts:.1f}s: {event} {ts - matching[-1]:.1f}s ago')

                seen_events.append((ts, event))

        if placed == 1 and squad.player.stats and squad.player.stats.kills and squad.player.stats.kills > len(self.eliminations):
            match_status_frames = [f for f in frames if 'match_status' in f]
            if len(match_status_frames):
                last_timestamp = [f.timestamp - frames[0].timestamp for f in match_status_frames][-1]
                self.logger.warning(
                    f'Got won game with {squad.player.stats.kills} kills, but only saw {len(self.eliminations)} eliminations from combat - '
                    f'Trying to resolve final fight (ended {s2ts(last_timestamp)})'
                )
                # detect recent knockdowns that don't have elims after them, and add the elim as it should be a final elim
                for knock in self.knockdowns:
                    if last_timestamp - knock.timestamp < 60:
                        elims_following = [e for e in self.eliminations if e.timestamp > knock.timestamp]
                        if not len(elims_following):
                            final_elim = CombatEvent(last_timestamp, 'eliminated', inferred=True)
                            self.eliminations.append(final_elim)
                            self.events.append(final_elim)
                            self.logger.warning(f'Adding elim for final fight knockdown @{s2ts(knock.timestamp)}: {final_elim}')

                while squad.player.stats.kills > len(self.eliminations):
                    # still lacking on elims - this player got the final kill
                    final_down = CombatEvent(last_timestamp, 'downed')
                    self.knockdowns.append(final_down)
                    self.events.append(final_down)
                    final_elim = CombatEvent(last_timestamp, 'eliminated')
                    self.eliminations.append(final_elim)
                    self.events.append(final_elim)
                    self.logger.warning(f'Adding down+elim for final kill(s) of the match: {self.knockdowns[-1]}, {self.eliminations[-1]}')

            # if len(self.eliminations) > len(self.knockdowns):
            #     self.logger.warning(
            #         f'Still have outstanding knockdowns: elims={len(self.eliminations)}, knockdowns={len(self.knockdowns)} - '
            #         f'Adding down for final kill of the match'
            #     )

        self.logger.info(
            f'Resolved combat:\n'
            f'Eliminations: {self.eliminations}\n'
            f'Knockdowns: {self.knockdowns}\n'
            f'Elimination_assists: {self.elimination_assists}\n'
            f'Knockdown_assists: {self.knockdown_assists}\n'
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'eliminations': typedload.dump(self.eliminations, hidedefault=False),
            'knockdowns': typedload.dump(self.knockdowns, hidedefault=False),
            'elimination_assists': typedload.dump(self.elimination_assists, hidedefault=False),
            'knockdown_assists': typedload.dump(self.knockdown_assists, hidedefault=False),
        }
