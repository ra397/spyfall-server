# import eventlet
# eventlet.monkey_patch()

from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, emit
import uuid

from helper.spyfall_locations import spyfall_locations
import random

from config.redis import redis_host
from models import *
from redis_om.model.model import NotFoundError
from redis_om import Migrator

Migrator().run()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins='*') # TODO: provide redis host to message queue parameter

@socketio.on('connect')
def test_connect():
    print('Client connected ', request.sid)

@socketio.on('create_game')
def create_game(json_data):
    sid = request.sid
    player_name = json_data['player_name']

    if len(player_name) < 2 or len(player_name) > 12:
        return {
            "status": "error",
            "message": "Name must be between 2 and 12 characters long."
        }

    uid = str(uuid.uuid4())
    game_code = Game.generate_game_code()

    player = Player(
        player_name=player_name,
        socket_id=sid,
        uid=uid,
        game_id='',
        current_occupation='',
    )
    player.save()

    game = Game(
        game_code=game_code,
        current_round_duration=480,
        status='lobby',
        current_location='',
        game_owner=player.pk,
    )
    game.save()

    player.game_id = game.pk
    player.save()

    join_room(game_code)

    return {
        "status": "success",
        'uid': uid,
        'game_code': game_code,
        'game_owner': True,
        'players': [player_name],
    }

@socketio.on('join_game')
def join_game(json_data):
    sid = request.sid
    player_name = json_data['player_name']
    game_code = json_data['game_code'].upper()

    # TODO: validate length of player name
    if len(player_name) < 2 or len(player_name) > 12:
        return {
            "status": "error",
            "message": "Name must be between 2 and 12 characters long."
        }

    uid = str(uuid.uuid4())

    if not game_code or len(game_code) != 5:
        return {
            "status": "error",
            "message": "Invalid game code."
        }
    try:
        game = Game.find(Game.game_code == game_code).first()
    except NotFoundError:
        return {
            "status": "error",
            "message": "Game does not exist."
        }

    players = Player.find(Player.game_id == game.pk).all()
    player_names = [player.player_name for player in players]

    if len(player_names) >= 8:
        return {
            "status": "error",
            "message": "Game is already full."
        }

    if player_name in player_names:
        return {
            "status": "error",
            "message": "Player name is already in use."
        }

    player = Player(
        player_name=player_name,
        socket_id=sid,
        uid=uid,
        game_id=game.pk,
        current_occupation='',
    )
    player.save()

    players = Player.find(Player.game_id == game.pk).all()
    player_names = [player.player_name for player in players]

    join_room(game_code)

    emit('player_joined', {
        'players': player_names,
    }, room=game_code)

    return {
        "status": "success",
        'uid': uid,
        'game_code': game_code,
        'game_owner': False,
        'players': player_names,
    }

@socketio.on('start_round')
def start_round(json_data):
    request_uid = json_data['uid']
    game_duration = json_data['duration']

    requesting_player = Player.find(Player.uid == request_uid).first()
    if requesting_player is None:
        return {
            "status": "error",
            "message": "Player does not exist."
        }
    game_id = requesting_player.game_id

    players_in_game = Player.find(Player.game_id == game_id).all()
    if not (3 <= len(players_in_game) <= 8):
        return {
            "status": "error",
            "message": "Not enough players in game."
        }

    game = Game.get(game_id)
    if not game:
        return {
            "status": "error",
            "message": "Game does not exist."
        }

    # choose random location
    location = random.choice(list(spyfall_locations.keys()))
    occupations = spyfall_locations[location][:]

    game.current_location = location
    game.current_round_duration = game_duration
    game.status = 'game'
    game.save()

    spy = random.choice(players_in_game)

    for player in players_in_game:
        if player.pk == spy.pk:
            # spy gets no location info
            player.current_occupation = "SPY"
        else:
            if not occupations:
                # fallback if job list too small
                player.current_occupation = "Civilian"
            else:
                player.current_occupation = occupations.pop(random.randrange(len(occupations)))
        player.save()

    for player in players_in_game:
        if player.pk == spy.pk:
            # Spy receives no location
            emit('round_started', {
                "location": "UNKNOWN",
                "occupation": "SPY",
                "duration": game_duration
            }, to=player.socket_id)
        else:
            emit('round_started', {
                "location": location,
                "occupation": player.current_occupation,
                "duration": game_duration
            }, to=player.socket_id)

    return {
        "status": "success"
    }

@socketio.on('end_round')
def end_round(json_data):
    request_uid = json_data['uid']

    requesting_player = Player.find(Player.uid == request_uid).first()
    if requesting_player is None:
        return {
            "status": "error",
            "message": "Player does not exist."
        }
    game_id = requesting_player.game_id

    game = Game.get(game_id)
    if not game:
        return {
            "status": "error",
            "message": "Game does not exist."
        }

    game.current_location = ''
    game.status = 'lobby'
    game.save()

    players_in_game = Player.find(Player.game_id == game_id).all()
    for player in players_in_game:
        player.current_occupation = ''
        player.save()

    emit('round_ended', room=game.game_code)

    return {
        "status": "success"
    }

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)