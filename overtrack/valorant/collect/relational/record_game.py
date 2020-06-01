from sqlalchemy.orm import Session

from overtrack.valorant.collect import ValorantGame
from overtrack.valorant.collect import relational
from overtrack.valorant.collect.valorant_game.kills import Kill
from overtrack.valorant.collect.valorant_game.teams import Player


def record_game(session: Session, game_data: ValorantGame, user_id: int, commit: bool = True) -> None:
    game = relational.ValorantGame(
        key=game_data.key,
        user_id=user_id,

        timestamp=game_data.timestamp,
        duration=game_data.duration,

        spectated=game_data.spectated,
        won=game_data.won,
        map=game_data.map,
        game_mode=game_data.game_mode,

        start_pts=game_data.start_pts,
        vod=game_data.vod,

        season_mode_id=game_data.season_mode_id,
        frames_count=game_data.frames_count,
        version=game_data.version,

        final_score_friendly=game_data.rounds.final_score[0] if game_data.rounds.final_score else None,
        final_score_enemy=game_data.rounds.final_score[1] if game_data.rounds.final_score else None,
        attacking_first=game_data.rounds.attacking_first,
        attack_wins=game_data.rounds.attack_wins,
        defence_wins=game_data.rounds.defence_wins,
        has_game_resets=game_data.rounds.has_game_resets,

        firstperson_agent=game_data.teams.firstperson.agent if game_data.teams.firstperson else None,
    )

    players = {}
    for friendly in True, False:
        player: Player
        for player in game_data.teams.teams[not friendly].players:
            players[(friendly, player.agent)] = relational.ValorantPlayer(
                game_key=game.key,
                friendly=player.friendly,
                agent=player.agent,

                name=player.name,
            )

    rounds = []
    kills = []

    for round_data in game_data.rounds:
        rounds.append(relational.ValorantRound(
            game_key=game.key,
            index=round_data.index,

            buy_phase_start=round_data.buy_phase_start,
            start=round_data.start,
            end=round_data.end,
            attacking=round_data.attacking,
            won=round_data.won,
        ))
        kill: Kill
        for i, kill in enumerate(round_data.kills):
            kills.append(relational.ValorantKill(
                game_key=game.key,
                round_index=round_data.index,
                index=i,

                round_timestamp=kill.round_timestamp,
                timestamp=kill.timestamp,

                killer_key=relational.PlayerKey(kill.killer.friendly, kill.killer.agent),
                killed_key=relational.PlayerKey(kill.killed.friendly, kill.killed.agent),
                weapon=kill.weapon,
                wallbang=kill.wallbang,
                headshot=kill.headshot,
            ))

    session.add_all(
        [game] + list(players.values()) + rounds + kills
    )
    if commit:
        session.commit()
