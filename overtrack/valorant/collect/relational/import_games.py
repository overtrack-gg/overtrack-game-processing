import queue

import time

import requests
import requests_cache
from queue import Queue

import logging

import itertools

from threading import Thread

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as SessionType
import os

from overtrack.util.logging_config import config_logger
from overtrack.valorant.collect import relational
from overtrack.valorant.collect.relational import record_game
from overtrack_models.dataclasses.valorant import ValorantGame
from overtrack_models.orm.valorant_game_summary import ValorantGameSummary


requests_cache.install_cache('requests_cache')


class GameScanner(Thread):

    cnt = itertools.count()
    logger = logging.getLogger(__qualname__)

    def __init__(self, database_session: SessionType, segment: int, total_segments: int, filter_condition = None):
        self.segment = segment
        self.total_segments = total_segments
        self.filter_condition = filter_condition

        self.database_session = database_session
        self.requests_session = requests.Session()
        self._continue = True

        super().__init__(name=f'GameScanner({next(self.cnt)}, {segment} of {total_segments})', daemon=False)

    def stop(self) -> None:
        self._continue = False

    def run(self) -> None:
        for summary in ValorantGameSummary.scan(filter_condition=self.filter_condition, segment=self.segment, total_segments=self.total_segments):
            if not self._continue:
                break

            if summary.version < '1.0.0':
                assert False

            self.logger.info(f'Downloading {summary.key!r} {summary.version}: {summary.url!r}')
            try:
                with self.requests_session.get(summary.url) as r:
                    data = r.json()
                game = ValorantGame.from_dict(data)

            except:
                self.logger.exception(f'Failed to download/load {summary.key!r}')
            else:
                if len(self.database_session.
                    query(relational.ValorantGame).
                    filter(relational.ValorantGame.key == game.key).
                    limit(1).
                    all()
                ):
                    continue

                if any(p.name is None for p in game.teams.players):
                    continue

                logging.info(f'Recording {game.key}')
                t0 = time.perf_counter()
                record_game(self.database_session, game, user_id=summary.user_id)
                logging.info(f'Took {time.perf_counter() - t0:.3f}s')


def import_all():
    config_logger(os.path.basename(__file__))

    # engine = create_engine((
    #     f'postgresql://'
    #     f'overtrack'
    #     f':'
    #     f'{os.environ["PSQL_PASSWORD"]}'
    #     f'@'
    #     f'54.69.252.81'
    #     f':'
    #     f'{os.environ["PSQL_PORT"]}'
    #     f'/overtrack'
    # ),
    #     echo=True,
    #     executemany_mode='batch',
    # )
    engine = create_engine('sqlite:///games.db')
    Session = sessionmaker(bind=engine)

    from overtrack.valorant.collect.relational.models import Base
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    SHARDS = 1
    threads = [
        GameScanner(Session(), i, SHARDS, ValorantGameSummary.version >= '1.0.0') for i in range(SHARDS)
    ]
    if SHARDS == 1:
        threads[0].run()
    else:
        for t in threads:
            logging.info(f'Starting {t}')
            t.start()


if __name__ == '__main__':
    import_all()
