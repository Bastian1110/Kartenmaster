from flask import Flask, jsonify
from flask_cors import CORS
from uno import UnoEnv

app = Flask("UNO Playgorund")
CORS(app)
env = UnoEnv(n_players=2)


@app.route("/", methods=["POST", "GET"])
def home():
    return jsonify({"message": "Hello world"}), 200


@app.route("/reset", methods=["GET"])
def reset():
    env.reset()
    return jsonify({"message": "Enviroment reseted"}), 200


@app.route("/game-state", methods=["GET"])
def get_game_state():
    return jsonify(env.jsonify_game_state()), 200


if __name__ == "__main__":
    app.run(port=8082, debug=True)
