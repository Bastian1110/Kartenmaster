"""
Gym environment to model UNO agnets
By Sebastian Mora (@bastian1110)
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np

# S = skip, R = reverse, T = take two
COLORS = ["RED", "BLUE", "YELLOW", "GREEN"]
SYMBOLS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "S", "R", "T"]


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


class UnoEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self, render_mode=None, n_players=3) -> None:
        # Action Space of 108 cards +  4 color choices + 1 draw action = 113 possible actions
        self.action_space = spaces.Discrete(113)

        # Player's hand (108), top card (108), actual color (1 norm), direction (1 norm), last player (1 norm), player with one (1 norm)
        self.observation_space = spaces.Box(low=0, high=1, shape=(220,), dtype=int)

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        # UNO Game deck
        self.deck = createDeck()
        self.n_players = n_players

    def _get_obs(self):
        player_hand_counts = [0] * 108
        for card in self.players[self.actual_player]:
            player_hand_counts[card] += 1

        top_card_encode = [0] * 108
        top_card_encode[self.top_index] = 1

        return (
            player_hand_counts
            + top_card_encode
            + [
                COLORS.index(self.top_card["color"]) / 4
                if self.top_card["color"] != "ANY"
                else -1,
                self.direction,
                self.last_player / self.n_players,
                self.nearest_uno(),
            ]
        )

    def _get_info(self):
        pass

    def reset(self, seed=None, options=None):
        # Create a draw cards stack (initially with all the cards)
        self.draw = list(range(len(self.deck)))

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
        return observation, {}

    def step(self, action):
        truncated = False  # WTF Stable baselines3 ?
        validation_mask = self.valid_mask(little_help=True)
        if validation_mask[action] == 0:
            self.last_player = self.actual_player
            self.actual_player = self.get_next_player(self.actual_player)
            observation = self._get_obs()
            reward = -5
            done = len(self.draw) == 0
            info = {"reason": f"Invalid action {action} chosen!"}
            return observation, reward, done, truncated, info

        if self.top_card["color"] == "ANY":
            self.top_card = {"color": COLORS[action - 108], "symbol": "ANY"}
            self.last_player = self.actual_player
            self.actual_player = self.get_next_player(self.actual_player)
            observation = self._get_obs()
            reward = 0.5
            done = len(self.draw) == 0
            info = {"reason": f"Color changed to {action} !"}
            return observation, reward, done, truncated, info

        if action == 112:
            new_card = self.deal_cards(1)
            self.players[self.actual_player] += new_card
            self.last_player = self.actual_player
            self.actual_player = self.get_next_player(self.actual_player)
            observation = self._get_obs()
            reward = -1
            done = len(self.draw) == 0
            info = {"reason": f"Player took a card !"}
            return observation, reward, done, truncated, info

        reward, done, info = self.play_card(action)
        observation = self._get_obs()
        return observation, reward, done, truncated, info

    def play_card(self, card_id):
        self.players[self.actual_player].remove(card_id)
        card = self.deck[card_id]
        if len(self.players[self.actual_player]) == 0:
            return 5, True, {"reason": f"Player {self.actual_player} won !"}
        if len(self.draw) == 0:
            return 0.5, True, {"reason": f"Draw stack out of cards"}
            # Calculate the winer and reward it
        self.top_card = card
        self.top_index = card_id
        if card["symbol"] == "ANY":
            # Do not go to the next player
            return 0.5, False, {"reason": f"Wild card palyed"}
        if card["symbol"] == "T":
            # Give the next player 2 cards
            target_player = self.get_next_player(self.actual_player)
            new_cards = self.deal_cards(2)
            self.players[target_player] += new_cards
            self.last_player = self.actual_player
            self.actual_player = self.get_next_player(self.actual_player)
            return 0.5, False, {"reason": f"Player {target_player} took 2 cards!"}
        if card["symbol"] == "F":
            # Give the next player 4 cards
            # Do not go to the next player
            target_player = self.get_next_player(self.actual_player)
            new_cards = self.deal_cards(4)
            self.players[target_player] += new_cards
            return 0.5, False, {"reason": f"Player {target_player} took 4 cards!"}
        if card["symbol"] == "S":
            # Skip the next player
            self.last_player = self.actual_player
            original_next_player = self.get_next_player(self.actual_player)
            new_next_player = self.get_next_player(original_next_player)
            self.actual_player = new_next_player
            return 0.5, False, {"reason": f"{original_next_player} was skipped!"}
        if card["symbol"] == "R":
            if self.direction == 0:
                self.direction = 1
                self.last_player = self.actual_player
                self.actual_player = self.get_next_player(self.actual_player)
                return (
                    0.5,
                    False,
                    {"reason": f"The game changed direction {self.direction}"},
                )
            if self.direction == 1:
                self.direction = 0
                self.last_player = self.actual_player
                self.actual_player = self.get_next_player(self.actual_player)
                return (
                    0.5,
                    False,
                    {"reason": f"The game changed direction {self.direction}"},
                )
        self.last_player = self.actual_player
        self.actual_player = self.get_next_player(self.actual_player)
        return 0.6, False, {"reason": f"Normal card played"}

    def get_next_player(self, actual):
        if self.direction == 0:
            return (actual + 1) % self.n_players
        else:
            return (actual - 1) % self.n_players

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

    def nearest_uno(self):
        for i in range(self.actual_player, len(self.players)):
            if len(self.players[i]) == 1:
                return i / self.n_players

        for i in range(self.actual_player - 1, -1, -1):
            if len(self.players[i]) == 1:
                return i / self.n_players
        return -1

    def action_to_human(self, action):
        if action >= 0 and action <= 107:
            return self.deck[action]
        if action >= 108 and action <= 111:
            return COLORS[action - 108]
        if action == 112:
            return "Took a card"

    def observation_to_human(self, obs):
        print(f"Actual Player : {self.actual_player}")
        action_mask = self.valid_mask(little_help=False)
        if action_mask[-2] == 1:
            for i in range(113):
                if action_mask[i] == 1:
                    print(f"{i} : {COLORS[i- 108]}")
            top = obs[108:215].index(1)
            print(f"Top Card : {self.deck[top]['color']} - {self.deck[top]['symbol']}")
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

    def render(self):
        pass

    def close(self):
        pass
