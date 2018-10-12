from typing import NamedTuple, List

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
