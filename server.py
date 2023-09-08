from flask import Flask, jsonify, request
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


@app.route("/make-action", methods=["POST"])
def post_make_action():
    try:
        data = request.get_json()
        action = data["action"]
        _obs, _reward, done, _truncated, info = env.step(action)
        return jsonify({"info": info, "done": done}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(port=8082, debug=True)
