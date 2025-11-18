# import eventlet
# eventlet.monkey_patch()

from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, join_room, emit
import uuid

from config.redis import redis_host
from models import *
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
    game_code = json_data['game_code']

    # TODO: validate length of player name
    if len(player_name) < 2 or len(player_name) > 12:
        return {
            "status": "error",
            "message": "Name must be between 2 and 12 characters long."
        }

    uid = str(uuid.uuid4())

    game = Game.find(Game.game_code == game_code).first()
    if game is None:
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

if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)