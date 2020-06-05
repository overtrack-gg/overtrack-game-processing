from collections import defaultdict

import logging
import os
from sqlalchemy import func, cast, Integer, and_, or_
from sqlalchemy.orm import Session, Query
from typing import Optional

from overtrack.util.logging_config import config_logger
from overtrack.util.prettyprint import pprint
from overtrack.valorant.collect.relational import *
from overtrack.valorant.data import game_modes
from overtrack_models.queries.valorant.winrates import MapAgentWinrates, Winrates


def _filter_game_version(existing_query: Query, game_version: Optional[str], game_version_atleast: Optional[str] = None) -> Query:
    if game_version_atleast:
        if game_version:
            raise ValueError('Cannot filter game version by both specific and at least')
        elif game_version_atleast == '00.00.0-beta':
            # earliest version so matches all, also games of this version may have null game_version
            return existing_query
        else:
            return existing_query.filter(
                ValorantGame.game_version >= game_version_atleast
            )
    elif game_version:
        if game_version == '00.00.0-beta':
            return existing_query.filter(
                or_(
                    ValorantGame.game_version == game_version,
                    ValorantGame.game_version.is_(None),
                )
            )
        else:
            return existing_query.filter(
                ValorantGame.game_version == game_version
            )
    else:
        return existing_query


def _join_players(existing_query: Query, user_id: Optional[int] = None) -> Query:
    if user_id is None:
        # All 10 players per game
        return existing_query.join(
            ValorantPlayer,
            ValorantPlayer.game_key == ValorantGame.key,
        )
    else:
        # Only the firstperson player and only for games matching the user ID
        return existing_query.join(
            ValorantPlayer,
            and_(
                ValorantPlayer.game_key == ValorantGame.key,
                ValorantPlayer.friendly == True,
                ValorantPlayer.agent == ValorantGame.firstperson_agent,
            )
        ).filter(
            ValorantGame.user_id == user_id
        )


def agent_map_winrates(
    session: Session,
    user_id: Optional[int] = None,
    game_version: Optional[str] = None,
    game_version_atleast: Optional[str] = None,
) -> MapAgentWinrates:
    winrates = MapAgentWinrates(defaultdict(Winrates))

    round_results_q = session.query(
        ValorantGame.map,
        ValorantPlayer.agent,
        (ValorantRound.attacking == ValorantPlayer.friendly).label('attacking'),
        func.count().label('rounds'),
        func.sum(cast(ValorantRound.won == ValorantPlayer.friendly, Integer)).label('wins'),
    ).select_from(
        ValorantGame
    ).join(
        ValorantRound,
        ValorantRound.game_key == ValorantGame.key,
    ).filter(
        and_(
            ValorantRound.won.isnot(None),
            ValorantGame.map.isnot(None),
            ValorantGame.game_mode != game_modes.spike_rush,
        )
    ).group_by(
        ValorantGame.map,
        ValorantPlayer.agent,
        (ValorantRound.attacking == ValorantPlayer.friendly),
    ).order_by(
        ValorantPlayer.agent,
        ValorantGame.map,
        (ValorantRound.attacking == ValorantPlayer.friendly),
    )
    round_results_q = _filter_game_version(round_results_q, game_version, game_version_atleast)
    round_results_q = _join_players(round_results_q, user_id)

    for map_, agent, attacking, rounds, wins in session.execute(round_results_q):
        for wr in winrates.all(), winrates.map(map_), winrates.agent(agent), winrates.map_agent(map_, agent):
            wr.rounds.total += rounds
            wr.rounds.wins += wins
            if attacking:
                wr.attacking_rounds.total += rounds
                wr.attacking_rounds.wins += wins
            else:
                wr.defending_rounds.total += rounds
                wr.defending_rounds.wins += wins

    # Filter down to only one entry per game per player (player = friendy, agent)
    map_results_q = session.query(
        ValorantGame.map,
        ValorantPlayer.agent,
        func.count().label('games'),
        func.sum(cast(ValorantGame.won == ValorantPlayer.friendly, Integer)).label('wins'),
    ).select_from(
        ValorantGame
    ).filter(
        and_(
            ValorantGame.won.isnot(None),
            ValorantGame.map.isnot(None),
            ValorantGame.game_mode != game_modes.spike_rush,
        )
    ).group_by(
        ValorantGame.map,
        ValorantPlayer.agent,
    )
    map_results_q = _filter_game_version(map_results_q, game_version, game_version_atleast)
    map_results_q = _join_players(map_results_q, user_id)

    # Extract game data
    for map_, agent, games, wins in session.execute(map_results_q):
        for wr in winrates.all(), winrates.map(map_), winrates.agent(agent), winrates.map_agent(map_, agent):
            wr.games.total += games
            wr.games.wins += wins

    winrates.maps_agents = dict(winrates.maps_agents)
    return winrates


def main():
    config_logger(os.path.basename(__file__), logging.DEBUG)

    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    import time
    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement,
                              parameters, context, executemany):
        conn.info.setdefault('query_start_time', []).append(time.time())
        logging.debug("Start Query: %s", statement)

    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement,
                             parameters, context, executemany):
        total = time.time() - conn.info['query_start_time'].pop(-1)
        logging.debug("Query Complete!")
        logging.debug("Total Time: %f", total)

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    # engine = create_engine('sqlite:///games.db', echo=True)
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

    _Session = sessionmaker(bind=engine)
    pprint(
        agent_map_winrates(
            _Session(),
            -3,
            game_version='01.00.0',
        ),
        width=120
    )


if __name__ == '__main__':
    main()
