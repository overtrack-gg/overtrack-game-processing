import json
import logging
from collections import defaultdict
from functools import wraps
from typing import Iterable

from flask import Flask, Response, request, jsonify
from werkzeug.datastructures import Headers, MultiDict

from overtrack import data

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from ingest.game.player_events import m3u8_from, PlayerEvent

app = Flask('api')
logger = logging.getLogger(__name__)

ORIGIN_WHITELIST = [
    'localhost'
]


def cors(methods=('GET',)):
    def wrap(handler):
        @wraps(handler)
        def wrapped_lambda_handler(*args, **kwargs):

            headers = Headers()
            headers.add('Access-Control-Allow-Headers', 'x-api-key, Content-Type, x-requested-with')
            headers.add('Access-Control-Allow-Methods', ', '.join(list(methods) + ['OPTIONS']))
            if 'origin' in request.headers:
                hostname = urlparse.urlsplit(request.headers['origin']).hostname
                if hostname in ORIGIN_WHITELIST:
                    headers['Access-Control-Allow-Credentials'] = 'true'
                    headers['Access-Control-Allow-Origin'] = request.headers['origin']
                    logger.info('Checking CORS for %s: ALLOW', hostname)
                else:
                    logger.info('Checking CORS for %s: DISALLOW', hostname)
                    return Response(
                        json.dumps({
                            'message': 'origin disallowed'
                        }),
                        content_type='application/json',
                        status=400
                    )

            if request.method == 'OPTIONS':
                return Response(
                    headers=headers
                )

            response = handler(*args, **kwargs)

            if not isinstance(response, Response):
                response = Response(response)
            response.headers.extend(headers.items())

            return response

        return wrapped_lambda_handler

    return wrap


def search_filter(user_id: int, args: MultiDict) -> Iterable[PlayerEvent]:
    condition = None
    filter = None
    for key, field in ('type', PlayerEvent.type), ('hero', PlayerEvent.hero), ('other_hero', PlayerEvent.other_hero):
        values = args.getlist(key)
        if values:
            subfilter = field.does_not_exist() | field.is_in(*values)
            if filter is None:
                filter = subfilter
            else:
                filter &= subfilter
    return PlayerEvent.user_id_time_index.query(user_id, condition, filter)


@app.route('/video_search/video.m3u8')
@cors()
def video():
    user_id = 303577352
    return Response(
        m3u8_from(
            search_filter(user_id, request.args)
        )[0],
        mimetype='application/x-mpegURL'
    )


@app.route('/video_search/metadata.vtt')
@cors()
def metadata():
    user_id = 303577352
    return Response(
        m3u8_from(
            search_filter(user_id, request.args)
        )[1],
        mimetype='text/vtt'
    )


@app.route('/video_search/available')
@cors()
def hero_list():
    user_id = 303577352

    # TODO: cache this result for a decent length of time

    heroes = {}
    event: PlayerEvent
    for event in PlayerEvent.user_id_time_index.query(user_id):
        if event.hero not in heroes:
            heroes[event.hero] = {
                'type': defaultdict(int),
                'other_hero': defaultdict(int),
                'mode': defaultdict(int),
                'map': defaultdict(int)
            }

        # TODO: reenable once we track these properly in the new killfeed
        if event.type in ['destruction', 'destroyed']:
            continue

        heroes[event.hero]['type'][event.type] += 1
        heroes[event.hero]['mode'][event.mode] += 1
        heroes[event.hero]['map'][event.map] += 1
        if event.other_hero:
            heroes[event.hero]['other_hero'][event.other_hero] += 1

    return jsonify([
        {
            'id': id,
            'name': hero.name,
            'role': str(hero.role),

            'events': heroes.get(id)
        } for id, hero in data.heroes.items()
    ])


def main() -> None:
    # PlayerEvent.user_id_time_index.query(303577352, PlayerEvent.type == 'kill')
    app.run(port=1235, host='0.0.0.0', debug=True)


if __name__ == '__main__':
    main()
