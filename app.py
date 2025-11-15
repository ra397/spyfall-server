from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
import eventlet
eventlet.monkey_patch()
from config.redis import redis_host
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, message_queue='') # TODO: provide redis host

from models import *

if __name__ == '__main__':

    # Example: Create a game
    game = Game(
        game_code="ABCD",
        current_round_duration=480,
        status="lobby",
        current_location="Tokyo",
        game_owner=""
    )
    game.save()
    print("Game created")
    #socketio.run(app, allow_unsafe_werkzeug=True)