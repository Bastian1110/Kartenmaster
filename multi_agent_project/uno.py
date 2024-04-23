"""
Ray RL MultiAgent environment to train UNO agents
By Sebastian Mora (@bastian1110)
"""

from typing import Dict
import gymnasium as gym
from random import shuffle
from ray.rllib.env.multi_agent_env import MultiAgentEnv
import numpy as np


# S = skip, R = reverse, T = take two, F = take four
COLORS = ["red", "blue", "yellow", "green"]
SYMBOLS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "S", "R", "T"]

# Function to create a deck of UNO
def createDeck() -> list[dict]:
    cards = []
    for color in COLORS:
        cards.append({"color": color, "symbol": "0"})
        for symbol in SYMBOLS:
            cards.append({"color": color, "symbol": symbol})
            cards.append({"color": color, "symbol": symbol})
    for _ in range(4):
        cards.append({"color": "ANY", "symbol": "ANY"})
        cards.append({"color": "ANY", "symbol": "F"})
    return cards


class UnoEnv(MultiAgentEnv):
    MAX_STEPS = 112
    N_PLAYERS = 2

    def __init__(self, config=None):
        # Action Space of 108 cards +  4 color choices + 1 draw action = 113 possible actions
        self.action_space = gym.spaces.Discrete(113)

        # Player's hand (108), top card (108), color top (5), symbol top (14), game direction (1), uno (1), n cards (1) norm = 238
        self.observation_space =  gym.spaces.Dict({
            "action_mask": gym.spaces.Box(0, 1, shape=(113, )),
            "real_obs" : gym.spaces.Box(low=0, high=1, shape=(238,), dtype=np.float32)
        })
        # UNO Game deck
        self.deck = createDeck()
        self.n_players = 2

    def _get_obs(self):
        # Player's hand (108)
        player_hand_counts = [0] * 108
        for card in self.players[self.actual_player]:
            player_hand_counts[card] += 1

        # Top card (108)
        top_card_encode = [0] * 108
        top_card_encode[self.top_index] = 1

        # Color top (5)
        top_color_encode = [0] * 5
        try:
            top_color_encode[COLORS.index(self.top_card["color"])] = 1
        except:
            top_color_encode[-1] = 1

        # Symbol top (14)
        top_symbol_encode = [0] * 14
        try:
            top_symbol_encode[SYMBOLS.index(self.top_card["symbol"])] = 1
        except:
            if self.top_card["symbol"] == "ANY":
                top_symbol_encode[-1] = 1
            else:
                top_symbol_encode[-2] = 1

        # Palayer with UNO
        one_card_player = 0 if self.nearest_uno() == -1 else 1

        # Normalized player ammount of cards
        norm_player_cards = len(self.players[self.actual_player]) / 108

        return {
            "action_mask": [1 if i else 0 for i in self.valid_mask(little_help=True)],
            "real_obs" : player_hand_counts+ top_card_encode+ top_color_encode+ top_symbol_encode+ [self.direction]+ [one_card_player]+ [norm_player_cards]
        }
        

    def _get_info(self):
        pass

    def reset(self, *, seed=None, options=None):
        # Create a draw cards stack (initially with all the cards)
        self.draw = list(range(len(self.deck)))
        shuffle(self.draw)

        # Take out a card to be the top card
        self.top_index = None
        self.top_card = None
        while True:
            self.top_index = self.np_random.integers(
                0, len(self.deck), size=1, dtype=int
            )[0]
            self.top_card = self.deck[self.top_index]
            if self.top_card["color"] != "ANY" and self.top_card["symbol"] not in [
                "ANY",
                "R",
                "S",
                "T",
                "F",
            ]:
                break
        self.draw.remove(self.top_index)

        # Give each player 7 cards
        self.players = []
        for _ in range(self.n_players):
            self.players.append(self.deal_cards(7))

        # Flag to describe the direction of the game
        self.direction = 0

        # Set actual player
        self.actual_player = 0
        self.last_player = 0

        observation = self._get_obs()
        return {self.actual_player : self._get_obs()}, {}

    def step(self, action_dict):
        player_now = self.actual_player
        rewards = {i : 0 for i in range(self.n_players)}
        action = action_dict[self.actual_player]
        truncated = False
        # Get an array that represents what cards the player has, that are valid to put on the top
        validation_mask = self.valid_mask(little_help=True)
        played_card = self.deck[action] if action < 108 else {}
        # Check if the action is invalid (the selected card cant go on top)
        if validation_mask[action] == 0:
            # Check this logic in the future (give the player a card i wrong action)
            new_card = self.deal_cards(1)
            new_card_info = self.deck[new_card[0]] if new_card else {}
            self.players[self.actual_player] += new_card
            self.last_player = self.actual_player
            self.actual_player = self.get_next_player(self.actual_player)
            observation = self._get_obs()
            rewards[player_now] = -5
            done = len(self.draw) == 0
            terminated = {self.actual_player : done, "__all__" : done}
            truncated = {self.actual_player : done, "__all__" : done}
            info = {
                "valid_action": False,
                "type": "invalid",
                "card": played_card,
                "message": f"invalid action ",
            }
            return {self.actual_player : self._get_obs()}, rewards, terminated, truncated, {}

        # If the las card, was a wild card, let the player select a color
        if self.top_card["color"] == "ANY":
            self.top_card = {"color": COLORS[action - 108], "symbol": "ANY"}
            self.last_player = self.actual_player
            self.actual_player = self.get_next_player(self.actual_player)
            observation = self._get_obs()
            rewards[player_now] = 0.5
            done = len(self.draw) == 0
            terminated = {self.actual_player : done, "__all__" : done}
            truncated = {self.actual_player : done, "__all__" : done}
            info = {
                "valid_action": True,
                "type": "color",
                "card": played_card,
                "message": f"color changed to {COLORS[action - 108]}",
            }
            return {self.actual_player : self._get_obs()}, rewards, terminated, truncated, {}

        # Handle if the action slected is to draw a card
        if action == 112:
            new_card = self.deal_cards(1)
            new_card_info = self.deck[new_card[0]] if new_card else {}
            self.players[self.actual_player] += new_card
            self.last_player = self.actual_player
            self.actual_player = self.get_next_player(self.actual_player)
            new_card_data = new_card_info
            if new_card:
                new_card_data["id"] = new_card[0]
            observation = self._get_obs()
            rewards[player_now] = -1
            done = len(self.draw) == 0
            terminated = {self.actual_player : done, "__all__" : done}
            truncated = {self.actual_player : done, "__all__" : done}
            info = {
                "valid_action": True,
                "type": "draw",
                "card": new_card_data,
                "message": f"player took a card",
            }
            return {self.actual_player : self._get_obs()}, rewards, terminated, truncated, {}

        # If the action is a normal card
        reward, done, info = self.play_card(action, played_card)
        observation = self._get_obs()
        rewards[player_now] = reward
        terminated = {self.actual_player : done, "__all__" : done}
        truncated = {self.actual_player : done, "__all__" : done}
        return {self.actual_player : self._get_obs()}, rewards, terminated, truncated, {}

    def play_card(self, card_id, card_info):
        # Remove the card from the players hand, get de card details
        self.players[self.actual_player].remove(card_id)
        card = self.deck[card_id]
        # Check if the actual player won
        if len(self.players[self.actual_player]) == 0:
            info = {
                "valid_action": True,
                "type": "normal",
                "card": card_info,
                "message": f"player won!",
            }
            return 5, True, info
        # Check if the draw stack is empty
        if len(self.draw) == 0:
            info = {
                "valid_action": True,
                "type": "normal",
                "card": card_info,
                "message": f"Draw stack out of cards",
            }
            return 0.5, True, info
            # Calculate the winer and reward it
        # Put the played card on the top
        self.top_card = card
        self.top_index = card_id
        # Handle the card
        if card["symbol"] == "ANY":
            # Do not go to the next player, wait for color selection
            info = {
                "valid_action": True,
                "type": "wild",
                "card": card_info,
                "message": f"wild card palyed",
            }
            return 0.5, False, info
        if card["symbol"] == "T":
            # Give the next player 2 cards
            target_player = self.get_next_player(self.actual_player)
            new_cards = self.deal_cards(2)
            self.players[target_player] += new_cards
            self.last_player = self.actual_player
            self.actual_player = self.get_next_player(self.actual_player)
            info = {
                "valid_action": True,
                "type": "normal",
                "card": card_info,
                "message": f"Player {target_player} took 2 cards!",
            }
            return 0.5, False, info
        if card["symbol"] == "F":
            # Give the next player 4 cards
            # Do not go to the next player, wait for color selection
            target_player = self.get_next_player(self.actual_player)
            new_cards = self.deal_cards(4)
            self.players[target_player] += new_cards
            info = {
                "valid_action": True,
                "type": "wild",
                "card": card_info,
                "message": f"Player {target_player} took 4 cards!",
            }
            return 0.5, False, info
        if card["symbol"] == "S":
            # Skip the next player
            self.last_player = self.actual_player
            original_next_player = self.get_next_player(self.actual_player)
            new_next_player = self.get_next_player(original_next_player)
            self.actual_player = new_next_player
            info = {
                "valid_action": True,
                "type": "normal",
                "card": card_info,
                "message": f"Player {original_next_player} was skipped!",
            }
            return 0.5, False, info
        if card["symbol"] == "R":
            if self.direction == 0:
                self.direction = 1
                self.last_player = self.actual_player
                self.actual_player = self.get_next_player(self.actual_player)
                info = {
                    "valid_action": True,
                    "type": "normal",
                    "card": card_info,
                    "message": f"The game changed direction",
                }
                return (0.5, False, info)
            if self.direction == 1:
                self.direction = 0
                self.last_player = self.actual_player
                self.actual_player = self.get_next_player(self.actual_player)
                info = {
                    "valid_action": True,
                    "type": "normal",
                    "card": card_info,
                    "message": f"The game changed direction",
                }
                return (0.5, False, info)
        self.last_player = self.actual_player
        self.actual_player = self.get_next_player(self.actual_player)
        info = {
            "valid_action": True,
            "type": "normal",
            "card": card_info,
            "message": f"Normal card played",
        }
        return 0.6, False, info

    # Helper function to calculate which is the next player, based on an actual player
    def get_next_player(self, actual):
        if self.direction == 0:
            return (actual + 1) % self.n_players
        else:
            return (actual - 1) % self.n_players

    # Get a random sample of n cards and delete them from the draw stack
    def deal_cards(self, n_cards):
        if len(self.draw) > n_cards:
            selected_cards = self.np_random.choice(
                self.draw, n_cards, replace=False
            ).tolist()
        else:
            selected_cards = self.draw
        for card in selected_cards:
            self.draw.remove(card)
        return selected_cards

    # Make a list of what cards can a player use (valid moves only)
    def get_valid_cards(self):
        options = []
        for card in self.players[self.actual_player]:
            card_info = self.deck[card]
            if (
                card_info["symbol"] == "ANY"
                or card_info["symbol"] == "F"
                or card_info["symbol"] == self.top_card["symbol"]
                or card_info["color"] == self.top_card["color"]
            ):
                options.append(card)
        return options

    # Create a 113 valid mask depending on the action, can also take into account only valid cards on the actual players hand with the "little_help" parameter
    def valid_mask(self, little_help=False):
        # Return a vector(113) mask with 1 with the valid actions
        mask = [False] * 113
        # If the last card wasnt a wild card, mask the players hand, else, mask only the possible color
        if not self.top_card["color"] == "ANY":
            possible_cards = self.players[self.actual_player]
            if little_help:
                possible_cards = self.get_valid_cards()
            for card in possible_cards:
                mask[card] = True
            mask[-1] = True
        else:
            mask[-5:-1] = [True, True, True, True]
        return mask

    # Helper function that return which is the nearest player with only one card left (normalized)
    def nearest_uno(self):
        for i in range(self.actual_player, len(self.players)):
            if len(self.players[i]) == 1:
                return i

        for i in range(self.actual_player - 1, -1, -1):
            if len(self.players[i]) == 1:
                return i
        return -1

    # Function that caonverts an action (from the 113 possible) to human text
    def action_to_human(self, action):
        if action >= 0 and action <= 107:
            return self.deck[action]
        if action >= 108 and action <= 111:
            return COLORS[action - 108]
        if action == 112:
            return "Took a card"

    # Function that prints the actual observation in a human-readable way
    def observation_to_human(self, obs):
        print(f"Actual Player : {self.actual_player}")
        action_mask = self.valid_mask(little_help=False)
        if action_mask[-2] == 1:
            for i in range(113):
                if action_mask[i] == 1:
                    print(f"{i} : {COLORS[i- 108]}")
            top = obs[108:215].index(1)
            print(f"Top Card (Env): {self.top_card}")
            return
        for i in range(108):
            if obs[i] == 1:
                card = self.deck[i]
                print(f"{i} : {card['symbol']} - {card['color']}")
        if action_mask[-1] == 1:
            print("112 : Draw a card")
        top = obs[108:215].index(1)
        print(f"Top Card (Obs): {self.deck[top]['color']} - {self.deck[top]['symbol']}")
        print(f"Top Card (Env): {self.top_card}")

    def jsonify_player_cards(self, player):
        cards = []
        for card in self.players[player]:
            card_data = self.deck[card]
            card_data["id"] = card
            cards.append(card_data)
        return cards

    def jsonify_game_state(self):
        top_card = dict(self.top_card)
        top_card["id"] = int(self.top_index)
        players = {}
        for i in range(len(self.players)):
            players[i] = self.jsonify_player_cards(i)

        return {
            "players": players,
            "actual": self.actual_player,
            "top": top_card,
        }

    def render(self):
        pass

    def close(self):
        pass
