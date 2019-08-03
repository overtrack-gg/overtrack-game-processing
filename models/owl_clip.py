import datetime
import os
from typing import Dict, Any

from pynamodb.attributes import UnicodeAttribute, NumberAttribute, \
    ListAttribute, MapAttribute, BooleanAttribute
from pynamodb.models import Model


class VictimData(MapAttribute):
    name = UnicodeAttribute()
    hero = UnicodeAttribute()


class OWLClip(Model):
    class Meta:
        table_name = os.environ.get('OWL_CLIPS_TABLE', 'overtrack-owl-clips')
        region = os.environ.get('DYNAMODB_REGION', 'us-west-2')

    slug = UnicodeAttribute(hash_key=True)
    timestamp = NumberAttribute(range_key=True)

    type = UnicodeAttribute()
    pov = BooleanAttribute()

    player = UnicodeAttribute()
    hero = UnicodeAttribute()
    team = UnicodeAttribute()
    opponent_team = UnicodeAttribute()

    frames_uri = UnicodeAttribute()

    kill_count = NumberAttribute()
    duration = NumberAttribute()

    game_name = UnicodeAttribute()

    season = NumberAttribute()
    stage = NumberAttribute()
    week = NumberAttribute()
    day = NumberAttribute()

    victims = ListAttribute(of=VictimData)

    @property
    def time(self) -> datetime.datetime:
        return datetime.datetime.utcfromtimestamp(self.timestamp)

    def url(self) -> str:
        return f'https://clips.twitch.tv/{self.slug}'

    def jsonify(self) -> Dict[str, Any]:
        return {
            'url': self.url(),
            'time': self.timestamp,
            'type': self.type,
            'pov': self.pov,
            'player': self.player,
            'hero': self.hero,
            'team': self.team,
            'opponent_team': self.opponent_team,
            'kill_count': self.kill_count,
            'duration': self.duration,
            'game_name': self.game_name.strip(),
            'season': self.season,
            'stage': self.stage,
            'week': self.week,
            'day': self.day,
            'victims': [{
                'name': v.name,
                'hero': v.hero
            } for v in self.victims]
        }

    def __str__(self) -> str:
        return f'ClipData({self.slug}, time={self.timestamp}, type={self.type}, ' \
               f'player={self.player}, hero={self.hero}, kill_count={self.kill_count})'

    __repr__ = __str__


def create_table() -> None:
    if not OWLClip.exists():
        OWLClip.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)


if __name__ == '__main__':
    create_table()
