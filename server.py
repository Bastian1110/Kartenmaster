from flask import Flask, jsonify, request, session
from flask_cors import CORS
from uno import UnoEnv
from sb3_contrib.ppo_mask import MaskablePPO
from pymongo import MongoClient
from datetime import datetime
from threading import Thread
from time import sleep
import uuid

MODEL = "./models/ppo_uno_help"

app = Flask("UNO Playground")
CORS(app, supports_credentials=True)
app.secret_key = "your_secret_key"  # set a random secret key for session management

# Database Connection
conn = MongoClient('mongodb://localhost:27017')
database = conn["Kartenmaster"]
game_collection = database["Game"]

# Game environments 
games: dict[str, tuple[UnoEnv, datetime]] = {}
agents: dict[str, tuple[MaskablePPO, datetime]] = {}

def update_last_activity(game_id):
    if game_id in games:
        games[game_id] = (games[game_id][0], datetime.utcnow())
    if game_id in agents:
        agents[game_id] = (agents[game_id][0], datetime.utcnow())


@app.route("/", methods=["POST", "GET"])
def home():
    return jsonify({"message": "Hello world"}), 200


@app.route("/start-game", methods=["GET"])
def start_game():
    game_id = str(uuid.uuid4())  # generate a unique game ID
    games[game_id] = (UnoEnv(n_players=2), datetime.utcnow())  # initialize a new game environment with current time
    agents[game_id] = (MaskablePPO.load(MODEL), datetime.utcnow())  # initialize a new agent with current time
    session["game_id"] = game_id  # store game ID in session
    return jsonify({"game_id": game_id}), 200



@app.route("/reset", methods=["GET"])
def reset():
    game_id = session.get("game_id")
    if game_id and game_id in games:
        games[game_id][0].reset()
        update_last_activity(game_id)
        return jsonify({"message": "Environment reseted"}), 200
    return jsonify({"error": "Game not found"}), 400


@app.route("/game-state", methods=["GET"])
def get_game_state():
    game_id = session.get("game_id")
    if game_id and game_id in games:
        update_last_activity(game_id)
        return jsonify(games[game_id][0].jsonify_game_state()), 200
    return jsonify({"error": "Game not found"}), 400


@app.route("/make-action", methods=["POST"])
def post_make_action():
    game_id = session.get("game_id")
    if not (game_id and game_id in games):
        return jsonify({"error": "Game not found"}), 400

    try:
        data = request.get_json()
        action = data["action"]
        _obs, _reward, done, _truncated, info = games[game_id][0].step(action)
        update_last_activity(game_id)
        return jsonify({"info": info, "done": done}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/get-agent-action", methods=["GET"])
def get_agent_action():
    game_id = session.get("game_id")
    if not (game_id and game_id in games):
        return jsonify({"error": "Game not found"}), 400

    try:
        action = games[game_id][0].action_space.sample()
        obs = games[game_id][0]._get_obs()
        action, _ = agents[game_id][0].predict(
            obs, action_masks=games[game_id][0].valid_mask(little_help=True)
        )
        _obs, _reward, done, _truncated, info = games[game_id][0].step(action)
        update_last_activity(game_id)
        return jsonify({"info": info, "done": done}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route("/end-game", methods=["POST"])
def end_game():
    game_id = session.get("game_id")
    if not (game_id and game_id in games):
        return jsonify({"error": "Game not found"}), 400
    try:
        data = request.get_json()
        data["winner"] = "Kartenmaster" if  games[game_id][0].actual_player == 1 else data["username"]
        data["players"] = games[game_id][0].n_players
        data["draw"] = len(games[game_id][0].draw)
        game_collection.insert_one(data)
        update_last_activity(game_id)
        return jsonify({"info": "Game saved!", "done": True}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    

TIMEOUT_SECONDS = 600  # 10 minutes timeout

def cleanup_game(game_id):
    if game_id in games:
        del games[game_id]  # Remove the game environment
    if game_id in agents:
        del agents[game_id]  # Remove the game agent


def cleanup_scheduler():
    while True:
        current_time = datetime.utcnow()
        for game_id in list(games.keys()):
            _, last_activity = games[game_id]
            if (current_time - last_activity).total_seconds() > TIMEOUT_SECONDS:
                print("Cleaning up game : ", game_id)
                cleanup_game(game_id)
                print("Actual # Games : ", len(games))
        sleep(60)  # Check every minute


if __name__ == "__main__":
    scheduler_thread = Thread(target=cleanup_scheduler, daemon=True)
    scheduler_thread.start()
    app.run(port=8082, debug=True)
