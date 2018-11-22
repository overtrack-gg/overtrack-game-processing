from enum import Enum
from typing import NamedTuple, List, Dict, Tuple, Optional

map_types = [
    'Escort',
    'Hybrid',
    'Assault',
    'Control'
]


class Map(NamedTuple):
    name: str
    type: str


class ControlStage(NamedTuple):
    letter: str
    name: str


class ControlMap(NamedTuple, Map):
    name: str
    type: str
    stages: List[ControlStage]

    def __str__(self):
        return f'{self.__class__.__name__}(name={self.name}, type={self.type}, stages=...)'

    @property
    def stage_dict(self) -> Dict[str, str]:
        return {
            l: f'{n} ({l})' for l, n in self.stages
        }


maps = [
    Map(
        name='Hanamura',
        type='Assault'
    ),
    Map(
        name='Horizon Lunar Colony',
        type='Assault'
    ),
    Map(
        name='Temple of Anubis',
        type='Assault'
    ),
    Map(
        name='Volskaya Industries',
        type='Assault'
    ),

    Map(
        name='Dorado',
        type='Escort'
    ),
    Map(
        name='Junkertown',
        type='Escort'
    ),
    Map(
        name='Rialto',
        type='Escort'
    ),
    Map(
        name='Route 66',
        type='Escort'
    ),
    Map(
        name='Watchpoint: Girialbraltar',
        type='Escort'
    ),

    Map(
        name='Blizzard World',
        type='Hybrid'
    ),
    Map(
        name='Eichenwalde',
        type='Hybrid'
    ),
    Map(
        name='Hollywood',
        type='Hybrid'
    ),
    Map(
        name="King's Row",
        type='Hybrid'
    ),
    Map(
        name='Numbani',
        type='Hybrid'
    ),

    ControlMap(
        name='Busan',
        type='Control',
        stages=[
            ControlStage(letter='A', name='Downtown'),
            ControlStage(letter='B', name='Sanctuary'),
            ControlStage(letter='C', name='Meka Base')
        ]
    ),
    ControlMap(
        name='Ilios',
        type='Control',
        stages=[
            ControlStage(letter='A', name='Lighthouse'),
            ControlStage(letter='B', name='Well'),
            ControlStage(letter='C', name='Ruins')
        ]
    ),
    ControlMap(
        name='Lijiang Tower',
        type='Control',
        stages=[
            ControlStage(letter='A', name='Night Market'),
            ControlStage(letter='B', name='Garden'),
            ControlStage(letter='C', name='Control Center')
        ]
    ),

    ControlMap(
        name='Oasis',
        type='Control',
        stages=[
            ControlStage(letter='A', name='City Center'),
            ControlStage(letter='B', name='University'),
            ControlStage(letter='C', name='Gardens')
        ]
    ),
    ControlMap(
        name='Nepal',
        type='Control',
        stages=[
            ControlStage(letter='A', name='Village'),
            ControlStage(letter='B', name='Shrine'),
            ControlStage(letter='C', name='Sanctum')
        ]
    ),

    # Map(
    #     name='Estádio das Rãs',
    #     type='Lúcioball'
    # ),
]


class StatType(Enum):
    CUMMULATIVE = 0
    AVERAGE = 1
    BEST = 2
    DURATION = 3


class Role(Enum):
    TANK = 0
    DAMAGE = 1
    SUPPORT = 2
    

class Stat(NamedTuple):
    name: str
    stat_type: StatType = StatType.CUMMULATIVE
    is_percent: bool = False


class Hero(NamedTuple):
    name: str
    role: Role
    ult: Optional[str]
    can_heal: bool

    stats: Tuple[List[Stat], List[Stat]]


generic_stats = [
    Stat(
        'eliminations',
    ),
    Stat(
        'objective kills',
    ),
    Stat(
        'objective time',
        stat_type=StatType.DURATION
    ),
    Stat(
        'hero damage done',
    ),
    Stat(
        'healing done',
    ),
    Stat(
        'deaths'
    ),
]

TANKS = {
    'dva': Hero(
        name='dva',
        role=Role.DAMAGE,
        ult=None,
        can_heal=False,
        stats=(
            [
                Stat(
                    'weapon accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'damage blocked'
                )
            ],
            [
                Stat(
                    'self-destruct kills'
                ),
                Stat(
                    'mechs called'
                )
            ]
        )
    ),
    'orisa': Hero(
        name='orisa',
        role=Role.TANK,
        ult=None,
        can_heal=False,
        stats=(
            [
                Stat(
                    'weapon accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'damage blocked'
                )
            ],
            [
                Stat(
                    'offensive assists'
                ),
                Stat(
                    'damage amplified'
                )
            ]
        )
    ),
    'reinhardt': Hero(
        name='reinhardt',
        role=Role.TANK,
        ult=None,
        can_heal=False,
        stats=(
            [
                Stat(
                    'damage blocked'
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'charge kills'
                )
            ],
            [
                Stat(
                    'fire strike kills'
                ),
                Stat(
                    'earthshatter kills'
                )
            ]
        )
    ),
    'roadhog': Hero(
        name='roadhog',
        role=Role.TANK,
        ult=None,
        can_heal=False,
        stats=(
            [
                Stat(
                    'weapon accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'enemies hooked'
                )
            ],
            [
                Stat(
                    'hook accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'self healing'
                ),
                Stat(
                    'whole hog kills'
                )
            ]
        )
    ),
    'winston': Hero(
        name='winston',
        role=Role.TANK,
        ult=None,
        can_heal=False,
        stats=(
            [
                Stat(
                    'damage blocked'
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'melee kills'
                )
            ],
            [
                Stat(
                    'players knocked back'
                ),
                Stat(
                    'primal rage kills'
                ),
            ]
        )
    ),
    'hammond': Hero(
        name='hammond',
        role=Role.TANK,
        ult=None,
        can_heal=False,
        stats=(
            [
                Stat(
                    'weapon accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'final blows'
                )
            ],
            [
                Stat(
                    'grappling claw kills',
                ),
                Stat(
                    'piledriver kills'
                ),
                Stat(
                    'minefield kills'
                )
            ]
        )
    ),
    'zarya': Hero(
        name='zarya',
        role=Role.TANK,
        ult=None,
        can_heal=False,
        stats=(
            [
                Stat(
                    'damage blocked'
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'high energy kills'
                )
            ],
            [
                Stat(
                    'average energy'
                ),
                Stat(
                    'graviton surge kills'
                )
            ]
        )
    ),
}
SUPPORTS: Dict[str, Hero] = {
    'ana': Hero(
        name='ana',
        role=Role.SUPPORT,
        ult=None,
        can_heal=True,
        stats=(
            [
                Stat(
                    'unscoped accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'scoped accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'defensive assists'
                )
            ],
            [
                Stat(
                    'nano boost assists'
                ),
                Stat(
                    'enemies slept'
                )
            ]
        )
    ),
    'brigitte': Hero(
        name='brigitte',
        role=Role.SUPPORT,  # ehhh
        ult=None,
        can_heal=True,
        stats=(
            [
                Stat(
                    'offensive assists'
                ),
                Stat(
                    'defensive assists'
                ),
                Stat(
                    'damage blocked'
                )
            ],
            [
                Stat(
                    'armor provided'
                ),
                Stat(
                    'inspire uptime percentage',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                )
            ]
        )
    ),
    'lucio': Hero(
        name='lucio',
        role=Role.SUPPORT,
        ult=None,
        can_heal=True,
        stats=(
            [
                Stat(
                    'weapon accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'sound barriers provided'
                )
            ],
            [
                Stat(
                    'offensive assists'
                ),
                Stat(
                    'defensive assists'
                )
            ]
        )
    ),
    'mercy': Hero(
        name='mercy',
        role=Role.SUPPORT,
        ult=None,
        can_heal=True,
        stats=(
            [
                Stat(
                    'offensive assists'
                ),
                Stat(
                    'defensive assists'
                ),
                Stat(
                    'players resurrected'
                )
            ],
            [
                Stat(
                    'blaster kills'
                ),
                Stat(
                    'damage amplified'
                )
            ]
        )
    ),
    'moira': Hero(
        name='moira',
        role=Role.SUPPORT,
        ult=None,
        can_heal=True,
        stats=(
            [
                Stat(
                    'secondary fire accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'defensive assists'
                )
            ],
            [
                Stat(
                    'coalescence kills'
                ),
                Stat(
                    'coalescence healing'
                ),
                Stat(
                    'self healing'
                )
            ]
        )
    ),
}
DPS: Dict[str, Hero] = {
    # 'ashe': Hero(
    #     name='ashe',
    #     role=Role.DAMAGE,
    #     ult=None,
    #     can_heal=False,
    #     stats=([
    #             # TODO: ashe stats
    #         ],
    #         [
    #
    #         ]
    #     )
    # ),

    'bastion': Hero(
        name='bastion',
        role=Role.DAMAGE,
        ult=None,
        can_heal=True,
        stats=(
            [
                Stat(
                    'weapon accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'recon kills'
                )
            ],
            [
                Stat(
                    'sentry kills'
                ),
                Stat(
                    'tank kills'
                ),
                Stat(
                    'self healing'
                )
            ]
        )
    ),
    'doomfist': Hero(
        name='doomfist',
        role=Role.DAMAGE,
        ult=None,
        can_heal=False,
        stats=(
            [
                Stat(
                    'weapon accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'final blows'
                )
            ],
            [
                Stat(
                    'ability damage done'
                ),
                Stat(
                    'meteor strike kills'
                ),
                Stat(
                    'shields created'
                )
            ]
        )
    ),
    'genji': Hero(
        name='genji',
        role=Role.DAMAGE,
        ult=None,
        can_heal=False,
        stats=(
            [
                Stat(
                    'weapon accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'final blows'
                )
            ],
            [
                Stat(
                    'damage reflected'
                ),
                Stat(
                    'dragonblade kills'
                )
            ]
        )
    ),
    'hanzo': Hero(
        name='hanzo',
        role=Role.DAMAGE,
        ult=None,
        can_heal=False,
        stats=(
            [
                Stat(
                    'weapon accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'final blows'
                )
            ],
            [
                Stat(
                    'critical hits'
                ),
                Stat(
                    'recon assists'
                ),
                Stat(
                    'dragonstrike kills'
                )
            ]
        )
    ),
    'junkrat': Hero(
        name='junkrat',
        role=Role.DAMAGE,
        ult=None,
        can_heal=False,
        stats=(
            [
                Stat(
                    'weapon accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'final blows'
                )
            ],
            [
                Stat(
                    'enemies trapped'
                ),
                Stat(
                    'rip-tire kills'
                )
            ]
        )
    ),
    'mccree': Hero(
        name='mccree',
        role=Role.DAMAGE,
        ult=None,
        can_heal=False,
        stats=(
            [
                Stat(
                    'weapon accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'final blows'
                )
            ],
            [
                Stat(
                    'critical hits'
                ),
                Stat(
                    'deadeye kills'
                ),
                Stat(
                    'fan the hammer kills'
                )
            ]
        )
    ),
    'mei': Hero(
        name='mei',
        role=Role.DAMAGE,
        ult=None,
        can_heal=True,
        stats=(
            [
                Stat(
                    'damage blocked'
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'enemies frozen'
                )
            ],
            [
                Stat(
                    'blizzard kills'
                ),
                Stat(
                    'self healing'
                )
            ]
        )
    ),
    'pharah': Hero(
        name='pharah',
        role=Role.DAMAGE,
        ult=None,
        can_heal=False,
        stats=(
            [
                Stat(
                    'weapon accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'final blows'
                )
            ],
            [
                Stat(
                    'barrage kills'
                ),
                Stat(
                    'rocket direct hits'
                )
            ]
        )
    ),
    'reaper': Hero(
        name='reaper',
        role=Role.DAMAGE,
        ult=None,
        can_heal=True,
        stats=(
            [
                Stat(
                    'weapon accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'final blows'
                )
            ],
            [
                Stat(
                    'death blossom kills'
                ),
                Stat(
                    'self healing'
                )
            ]
        )
    ),
    'soldier': Hero(
        name='soldier',
        role=Role.DAMAGE,
        ult=None,
        can_heal=True,
        stats=(
            [
                Stat(
                    'weapon accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'final blows'
                )
            ],
            [
                Stat(
                    'helix rocket kills'
                ),
                Stat(
                    'tactical visor kills'
                )
            ]
        )
    ),
    'sombra': Hero(
        name='sombra',
        role=Role.DAMAGE,
        ult=None,
        can_heal=True,
        stats=(
            [
                Stat(
                    'weapon accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'offensive assists'
                )
            ],
            [
                Stat(
                    'enemies hacked'
                ),
                Stat(
                    "enemies emp'd"
                )
            ]
        )
    ),
    'symmetra': Hero(
        name='symmetra',
        role=Role.DAMAGE,
        ult=None,
        can_heal=False,
        stats=(
            [
                Stat(
                    'sentry turret kills'
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'damage blocked'
                )
            ],
            [
                Stat(
                    'players teleported'
                ),
                Stat(
                    'primary fire accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'secondary fire accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                )
            ]
        )
    ),
    'torbjorn': Hero(
        name='torbjorn',
        role=Role.DAMAGE,
        ult=None,
        can_heal=False,
        stats=(
            [
                Stat(
                    'weapon accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'torbjorn kills'
                )
            ],
            [
                Stat(
                    'turret kills'
                ),
                Stat(
                    'molten core kills'
                ),
                Stat(
                    'turret damage'
                )
            ]
        )
    ),
    'tracer': Hero(
        name='tracer',
        role=Role.DAMAGE,
        ult=None,
        can_heal=True,
        stats=(
            [
                Stat(
                    'weapon accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'final blows'
                )
            ],
            [
                Stat(
                    'pulse bomb kills'
                ),
                Stat(
                    'pulse bombs attached'
                )
            ]
        )
    ),
    'widowmaker': Hero(
        name='widowmaker',
        role=Role.DAMAGE,
        ult=None,
        can_heal=False,
        stats=(
            [
                Stat(
                    'recon assists'
                ),
                Stat(
                    'kill streak - best',
                    stat_type=StatType.BEST
                ),
                Stat(
                    'final blows'
                )
            ],
            [
                Stat(
                    'scoped accuracy',
                    stat_type=StatType.AVERAGE,
                    is_percent=True
                ),
                Stat(
                    'scoped critical hits'
                )
            ]
        )
    )
}

HEROES: Dict[str, Hero] = dict()
HEROES.update(TANKS)
HEROES.update(DPS)
HEROES.update(SUPPORTS)
