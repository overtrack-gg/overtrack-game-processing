from dataclasses import dataclass
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, ForeignKeyConstraint, CheckConstraint
from sqlalchemy.orm import relationship, composite
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


@dataclass
class PlayerKey:
    friendly: bool
    agent: str

    @classmethod
    def _from_db(cls, *args):
        return cls(*args)

    def __composite_values__(self):
        return self.friendly, self.agent


def playerkey_primaryjoin(killer_killed: str) -> str:
    if killer_killed not in ['killer', 'killed']:
        raise ValueError(f'playerkey_primaryjoin argument must be "killer" or "killed"')
    return (
        f'and_('
        f'ValorantPlayer.game_key == ValorantKill.game_key, '
        f'ValorantPlayer.friendly == ValorantKill._{killer_killed}_friendly, '
        f'ValorantPlayer.agent == ValorantKill._{killer_killed}_agent'
        ')'
    )


class ValorantKill(Base):
    __tablename__ = 'valorant_kills'

    game_key = Column(ForeignKey('valorant_games.key'), primary_key=True)
    round_index = Column(Integer, primary_key=True)
    index = Column(Integer, primary_key=True)
    round_timestamp = Column(Float, nullable=False)
    timestamp = Column(Float, nullable=False)
    weapon = Column(String)
    wallbang = Column(Boolean, default=False, nullable=False)
    headshot = Column(Boolean, default=False, nullable=False)
    killer_key = composite(
        PlayerKey._from_db,
        Column('_killer_friendly', Boolean, nullable=False),
        Column('_killer_agent', String, nullable=False),
    )
    killed_key = composite(
        PlayerKey._from_db,
        Column('_killed_friendly', Boolean, nullable=False),
        Column('_killed_agent', String, nullable=False),
    )

    __table_args__ = (
        ForeignKeyConstraint(
            (game_key, round_index),
            ('valorant_rounds.game_key', 'valorant_rounds.index'),
        ),
        ForeignKeyConstraint(
            (game_key, '_killer_friendly', '_killer_agent'),
            ('valorant_players.game_key', 'valorant_players.friendly', 'valorant_players.agent'),
        ),
        ForeignKeyConstraint(
            (game_key, '_killed_friendly', '_killed_agent'),
            ('valorant_players.game_key', 'valorant_players.friendly', 'valorant_players.agent'),
        ),
    )

    round = relationship('ValorantRound', viewonly=True)
    game = relationship('ValorantGame')
    killer = relationship(
        'ValorantPlayer',
        primaryjoin=playerkey_primaryjoin('killer'),
        uselist=False,
        viewonly=True,
    )
    killed = relationship(
        'ValorantPlayer',
        primaryjoin=playerkey_primaryjoin('killed'),
        uselist=False,
        viewonly=True,
    )


class ValorantUlt(Base):
    __tablename__ = 'valorant_ults'

    game_key = Column(ForeignKey('valorant_games.key'), primary_key=True)
    player_friendly = Column(Boolean, primary_key=True)
    player_agent = Column(String, primary_key=True)
    index = Column(Integer, primary_key=True)

    gained = Column(Float, nullable=False)
    lost = Column(Float, nullable=False)
    used = Column(Boolean, nullable=False)

    round_gained_index = Column(Integer, nullable=False)
    round_gained_timestamp = Column(Float, nullable=False)

    round_lost_index = Column(Integer, nullable=False)
    round_lost_timestamp = Column(Float, nullable=False)

    round_used_index = Column(Integer)

    __table_args__ = (
        ForeignKeyConstraint(
            (game_key, player_friendly, player_agent),
            ('valorant_players.game_key', 'valorant_players.friendly', 'valorant_players.agent'),
        ),
        ForeignKeyConstraint(
            (game_key, round_gained_index),
            ('valorant_rounds.game_key', 'valorant_rounds.index'),
        ),
        ForeignKeyConstraint(
            (game_key, round_lost_index),
            ('valorant_rounds.game_key', 'valorant_rounds.index'),
        ),
        ForeignKeyConstraint(
            (game_key, round_used_index),
            ('valorant_rounds.game_key', 'valorant_rounds.index'),
        ),
        CheckConstraint(
            'NOT used OR round_used_index IS NOT NULL'
        )
    )

    player = relationship('ValorantPlayer', back_populates='ults')
    round_used = relationship(
        'ValorantRound',
        foreign_keys=[game_key, round_used_index],
        back_populates='ults_used',
        viewonly=True,
    )
    game = relationship(
        'ValorantGame',
        back_populates='ults',
        viewonly=True,
    )


class ValorantPlayer(Base):
    __tablename__ = 'valorant_players'

    game_key = Column(ForeignKey('valorant_games.key'), primary_key=True)
    friendly = Column(Boolean, primary_key=True)
    agent = Column(String, primary_key=True)
    name = Column(String)

    kills = relationship(
        'ValorantKill',
        primaryjoin=playerkey_primaryjoin('killer'),
        uselist=True,
    )
    deaths = relationship(
        'ValorantKill',
        primaryjoin=playerkey_primaryjoin('killed'),
        uselist=True,
    )
    ults = relationship(
        'ValorantUlt',
        cascade="all, delete-orphan",
    )
    game = relationship(
        'ValorantGame',
        back_populates='players'
    )


class ValorantRound(Base):
    __tablename__ = 'valorant_rounds'

    game_key = Column(ForeignKey('valorant_games.key'), primary_key=True)
    index = Column(Integer, primary_key=True)
    buy_phase_start = Column(Float, nullable=False)
    start = Column(Float, nullable=False)
    end = Column(Float, nullable=False)
    attacking = Column(Boolean, nullable=False)
    won = Column(Boolean)
    spike_planted = Column(Float)
    spike_planter_key = composite(
        PlayerKey._from_db,
        Column('_spike_planter_friendly', Boolean),
        Column('_spike_planter_agent', String),
    )
    win_type = Column(String)

    __table_args__ = (
        ForeignKeyConstraint(
            (game_key, '_spike_planter_friendly', '_spike_planter_agent'),
            ('valorant_players.game_key', 'valorant_players.friendly', 'valorant_players.agent'),
        ),
    )

    spike_planter = relationship(
        'ValorantPlayer',
        primaryjoin='and_('
                    'ValorantRound.game_key == ValorantPlayer.game_key, '
                    'ValorantRound._spike_planter_friendly == True, '
                    'ValorantRound._spike_planter_agent == ValorantPlayer.agent'
                    ')',
        uselist=False,
    )
    kills = relationship('ValorantKill')
    ults_used = relationship(
        'ValorantUlt',
        primaryjoin=f'and_('
                    f'ValorantRound.game_key == ValorantUlt.game_key, '
                    f'ValorantRound.index == ValorantUlt.round_used_index'
                    ')',
        sync_backref=False,
    )


class ValorantClip(Base):
    __tablename__ = 'valorant_clips'

    url = Column(String, primary_key=True)
    game_key = Column(ForeignKey('valorant_games.key'))
    round_index = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)
    # metadata = Column(Json, nullable=False)


class ValorantGame(Base):
    __tablename__ = 'valorant_games'
    key = Column(String, primary_key=True)
    user_id = Column(Integer, nullable=False)

    timestamp = Column(Float, nullable=False)
    duration = Column(Float, nullable=False)
    spectated = Column(Boolean, nullable=False)
    map = Column(String, nullable=False)
    game_mode = Column(String, nullable=False)
    season_mode_id = Column(Integer, nullable=False)
    frames_count = Column(Integer, nullable=False)
    version = Column(String, nullable=False)
    game_version = Column(String)

    won = Column(Boolean)
    start_pts = Column(Float)
    vod = Column(String)

    final_score_friendly = Column(Integer)
    final_score_enemy = Column(Integer)
    attacking_first = Column(Boolean, nullable=False)
    attack_wins = Column(Integer, nullable=False)
    defence_wins = Column(Integer, nullable=False)
    has_game_resets = Column(Boolean, nullable=False)

    firstperson_agent = Column(String)

    clips = relationship(
        'ValorantClip',
        cascade="all, delete-orphan",
    )
    players = relationship(
        'ValorantPlayer',
        cascade="all, delete-orphan",
    )
    firstperson = relationship(
        'ValorantPlayer',
        primaryjoin='and_('
                    'ValorantPlayer.game_key == ValorantGame.key, '
                    'ValorantPlayer.friendly == True, '
                    'ValorantPlayer.agent == ValorantGame.firstperson_agent'
                    ')',
        uselist=False,
    )
    kills = relationship(
        'ValorantKill',
        cascade="all, delete-orphan",
    )
    rounds = relationship(
        'ValorantRound',
        cascade="all, delete-orphan",
    )
    ults = relationship(
        'ValorantUlt',
        cascade="all, delete-orphan",
        sync_backref=False,
    )


def main():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, Session as SessionType
    import requests
    from overtrack.valorant.relational import record_game
    import overtrack_models.dataclasses.valorant
    import os

    # engine = create_engine('sqlite:///models_test.db', echo=True)
    # Base.metadata.drop_all(engine)
    # Base.metadata.create_all(engine)

    engine = create_engine((
        f'postgresql://'
        f'overtrack'
        f':'
        f'{os.environ["PSQL_PASSWORD"]}'
        f'@'
        f'54.69.252.81'
        f':'
        f'{os.environ["PSQL_PORT"]}'
        f'/overtrack'
    ),
        echo=True,
        executemany_mode='batch',
    )

    Session = sessionmaker(bind=engine)

    with requests.get('https://overtrack-valorant-games.s3.amazonaws.com/mendo/2020-06-16-04-37-jjPQM2.json') as r:
        data = r.json()
    g = overtrack_models.dataclasses.ValorantGame.from_dict(data)

    s = Session()

    dg = s.query(ValorantGame).filter(ValorantGame.key == g.key).first()
    print(dg)
    s.delete(dg)
    s.commit()

    record_game(s, g, 0)
    s.commit()


if __name__ == '__main__':
    main()
