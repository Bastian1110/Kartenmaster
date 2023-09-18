from flask import Flask, jsonify, request, session
from flask_cors import CORS
from uno import UnoEnv
import uuid

app = Flask("UNO Playground")
CORS(app, supports_credentials=True)
app.secret_key = "your_secret_key"  # set a random secret key for session management

games = {}  # to store game environments


@app.route("/", methods=["POST", "GET"])
def home():
    return jsonify({"message": "Hello world"}), 200


@app.route("/start-game", methods=["GET"])
def start_game():
    game_id = str(uuid.uuid4())  # generate a unique game ID
    games[game_id] = UnoEnv(n_players=2)  # initialize a new game environment
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


# ... your /cookie endpoint remains unchanged ...

if __name__ == "__main__":
    app.run(port=8082, debug=True)
