from flask import Flask, jsonify, request, session
from flask_cors import CORS
from uno import UnoEnv
from sb3_contrib.ppo_mask import MaskablePPO
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from threading import Thread
from time import sleep
import uuid

import ray
from ray.rllib.algorithms import PPO
from ray.rllib.algorithms.ppo import PPOConfig
from ray.rllib.models import ModelCatalog
from ray.rllib.policy.policy import PolicySpec
from uno import UnoEnv
from agent import TorchActionMaskModel
import uuid
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from threading import Thread
from time import sleep
from ray import tune

# Initialize Ray
ray.init(ignore_reinit_error=True)

MODEL_PATH = "./models/KartenmasterV2.0/"
MODEL_ID = "KartenMasterPPO&HelpV2.0"

app = Flask("UNO Playground")
CORS(app, supports_credentials=True)
app.secret_key = "your_secret_key"

# Database Connection
conn = MongoClient('mongodb://localhost:27017')
database = conn["Kartenmaster"]
game_collection = database["Game"]

# Register custom model and environment
ModelCatalog.register_custom_model("custom_action_mask_model", TorchActionMaskModel)
tune.register_env("uno_multiagent", lambda config: UnoEnv(config))

# Define the PPO Algorithm Configuration
def get_ppo_config():
    return PPOConfig()\
        .framework("torch")\
        .environment("uno_multiagent")\
        .multi_agent(
            policies={
                "alpha": PolicySpec(config={"gamma": 0.85, "model": {"custom_model": "custom_action_mask_model"}}),
                "bravo": PolicySpec(config={"gamma": 0.95, "model": {"custom_model": "custom_action_mask_model"}}),
            },
            policy_mapping_fn=lambda agent_id: "alpha" if agent_id == 1 else "bravo"
        )\
        .rollouts(num_rollout_workers=0)

# Store for games and agents
games: dict[str, tuple[UnoEnv, datetime]] = {}
agents: dict[str, tuple[PPO, datetime]] = {}

@app.route("/start-game", methods=["GET"])
def start_game():
    game_id = str(uuid.uuid4())
    env = UnoEnv()
    algo = get_ppo_config().build()
    algo.restore(MODEL_PATH)
    games[game_id] = (env, datetime.utcnow())
    agents[game_id] = (algo, datetime.utcnow())
    session["game_id"] = game_id
    return jsonify({"game_id": game_id}), 200

@app.route("/get-agent-action", methods=["GET"])
def get_agent_action():
    game_id = session.get("game_id")
    if not (game_id and game_id in games and game_id in agents):
        return jsonify({"error": "Game not found"}), 400

    try:
        env = games[game_id][0]
        algo = agents[game_id][0]
        obs = env._get_obs()
        action = algo.compute_single_action(obs, policy_id="alpha")  # Adjust policy_id based on your setup
        print("Action by robot : ", action)
        _obs, _reward, done, _truncated, info = games[game_id][0].step({games[game_id][0].actual_player: action})
        update_last_activity(game_id)
        return jsonify({"info": info, "done": done['__all__']}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400

def update_last_activity(game_id):
    if game_id in games:
        games[game_id] = (games[game_id][0], datetime.utcnow())
    if game_id in agents:
        agents[game_id] = (agents[game_id][0], datetime.utcnow())


@app.route("/", methods=["POST", "GET"])
def home():
    return jsonify({"message": "Hello world"}), 200

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
        print(data)
        action = data["action"]
        print({games[game_id][0].actual_player: action})
        _obs, _reward, done, _truncated, info = games[game_id][0].step({games[game_id][0].actual_player: action})
        update_last_activity(game_id)
        return jsonify({"info": info, "done": done['__all__']}), 200

    except Exception as e:
        print(e)
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
        data["model"] = MODEL_ID
        result = game_collection.insert_one(data)
        update_last_activity(game_id)
        return jsonify({"info": "Game saved!", "done": True, "record_id" : str(result.inserted_id)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route("/rate-model", methods=["POST"])
def rate_model():
    game_id = session.get("game_id")
    if not (game_id and game_id in games):
        return jsonify({"error": "Game not found"}), 400
    try:
        data = request.get_json()
        rate = data["rate"]
        idx = data["record_id"]
        game_collection.update_one({"_id": ObjectId(idx)}, {"$set": {"rate" : rate}})
        update_last_activity(game_id)
        return jsonify({"info": "Rate saved!", "done": True}), 200

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
    app.run(port=8082, debug=True, host="0.0.0.0")
