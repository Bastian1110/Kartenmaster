from flask import Flask, jsonify, request, session
from flask_cors import CORS
from uno import UnoEnv
from sb3_contrib.ppo_mask import MaskablePPO
from pymongo import MongoClient
from random import choice
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
games: dict[str, UnoEnv] = {}  # to store game environments
agents: dict[str, MaskablePPO] = {}


@app.route("/", methods=["POST", "GET"])
def home():
    return jsonify({"message": "Hello world"}), 200


@app.route("/start-game", methods=["GET"])
def start_game():
    game_id = str(uuid.uuid4())  # generate a unique game ID
    games[game_id] = UnoEnv(n_players=2)  # initialize a new game environment
    agents[game_id] = MaskablePPO.load(MODEL)
    session["game_id"] = game_id  # store game ID in session
    print(len(games))
    return jsonify({"game_id": game_id}), 200


@app.route("/reset", methods=["GET"])
def reset():
    game_id = session.get("game_id")
    if game_id and game_id in games:
        games[game_id].reset()
        return jsonify({"message": "Environment reseted"}), 200
    return jsonify({"error": "Game not found"}), 400


@app.route("/game-state", methods=["GET"])
def get_game_state():
    game_id = session.get("game_id")
    if game_id and game_id in games:
        return jsonify(games[game_id].jsonify_game_state()), 200
    return jsonify({"error": "Game not found"}), 400


@app.route("/make-action", methods=["POST"])
def post_make_action():
    game_id = session.get("game_id")
    if not (game_id and game_id in games):
        return jsonify({"error": "Game not found"}), 400

    try:
        data = request.get_json()
        action = data["action"]
        _obs, _reward, done, _truncated, info = games[game_id].step(action)
        return jsonify({"info": info, "done": done}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/get-agent-action", methods=["GET"])
def get_agent_action():
    game_id = session.get("game_id")
    if not (game_id and game_id in games):
        return jsonify({"error": "Game not found"}), 400

    try:
        action = games[game_id].action_space.sample()
        obs = games[game_id]._get_obs()
        action, _ = agents[game_id].predict(
            obs, action_masks=games[game_id].valid_mask(little_help=True)
        )
        _obs, _reward, done, _truncated, info = games[game_id].step(action)
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
        data["winner"] = "Kartenmaster" if  games[game_id].actual_player == 1 else data["username"]
        data["players"] = games[game_id].n_players
        data["draw"] = len(games[game_id].draw)
        game_collection.insert_one(data)
        return jsonify({"info": "Game saved!", "done": True}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400



if __name__ == "__main__":
    app.run(port=8082, debug=True)
