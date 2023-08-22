"""
Gym environment to model UNO agnets
By Sebastian Mora (@bastian1110)
"""

import gymnasium as gym
from gymnasium import spaces

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

        # Player's hand (108), top card (108), cards held by two opponents (2), game status (let's assume 5 flags)
        self.observation_space = spaces.Box(low=0, high=1, shape=(218,), dtype=int)

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

        return {
            "observation": player_hand_counts
            + top_card_encode
            + [self.direction, self.top_index / 108],
            "action_mask": self.valid_mask(),
        }

    def _get_info(self):
        pass

    def reset(self, seed=None):
        super().reset(seed=seed)

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
            if self.top_card["color"] != "ANY" and self.top_card["color"] not in [
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

    def step(self, action):
        validation_mask = self.valid_mask()
        if validation_mask[action] == 0:
            self.actual_player = self.get_next_player(self.actual_player)
            observation = self._get_obs()
            reward = -5
            done = len(self.draw) == 0
            info = {"reason": f"Invalid action {action} chosen!"}
            return observation, reward, done, info

        if self.top_card["color"] == "ANY":
            self.top_card = {"color": COLORS[action], "symbol": "ANY"}
            self.actual_player = self.get_next_player(self.actual_player)
            observation = self._get_obs()
            reward = 0.1
            done = len(self.draw) == 0
            info = {"reason": f"Color changed to {action} !"}
            return observation, reward, done, info

        if action == 112:
            new_card = self.deal_cards(1)
            self.players[self.actual_player] += new_card
            self.actual_player = self.get_next_player(self.actual_player)
            observation = self._get_obs()
            reward = -0.5
            done = len(self.draw) == 0
            info = {"reason": f"Player took a card !"}
            return observation, reward, done, info

        reward, done, info = self.play_card(action)
        observation = self._get_obs()
        return observation, reward, done, info

    def play_card(self, card_id):
        self.players[self.actual_player].remove(card_id)
        card = self.deck[card_id]
        if len(self.players[self.actual_player]) == 0:
            return 5, True, {"reason": f"Player {self.actual_player} won !"}
        if len(self.draw) == 0:
            return 0.1, True, {"reason": f"Draw stack out of cards"}
        self.top_card = card
        self.top_index = card_id
        if card["symbol"] == "ANY":
            # Do not go to the next player
            return 0.2, False, {"reason": f"Wild card palyed"}
        if card["symbol"] == "T":
            # Give the next player 2 cards
            target_player = self.get_next_player(self.actual_player)
            new_cards = self.deal_cards(2)
            self.players[target_player] += new_cards
            self.actual_player = self.get_next_player(self.actual_player)
            return 0.2, False, {"reason": f"Player {target_player} took 2 cards!"}
        if card["symbol"] == "F":
            # Give the next player 4 cards
            # Do not go to the next player
            target_player = self.get_next_player(self.actual_player)
            new_cards = self.deal_cards(4)
            self.players[target_player] += new_cards
            return 0.2, False, {"reason": f"Player {target_player} took 4 cards!"}
        if card["symbol"] == "S":
            # Skip the next player
            original_next_player = self.get_next_player(self.actual_player)
            new_next_player = self.get_next_player(original_next_player)
            self.actual_player = new_next_player
            return 0.2, False, {"reason": f"{original_next_player} was skipped!"}
        if card["symbol"] == "R":
            if self.direction == 0:
                self.direction = 1
                return (
                    0.2,
                    False,
                    {"reason": f"The game changed direction {self.direction}"},
                )
            if self.direction == 1:
                self.direction = (0,)
                return (
                    0.2,
                    False,
                    {"reason": f"The game changed direction {self.direction}"},
                )
        return 0.1, False, {"reason": f"Normal card played"}

    def get_next_player(self, actual):
        if self.direction == 0:
            return (actual + 1) % self.n_players
        else:
            return (actual - 1) % self.n_players

    def deal_cards(self, n_cards):
        if len(self.draw) > n_cards:
            selected_cards = self.np_random.choice(self.draw, n_cards, replace=False)
            for card in selected_cards:
                self.draw.remove(card)
            return selected_cards
        return []

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

    def valid_mask(self, little_help=True):
        # Return a vector(113) mask with 1 with the valid actions
        mask = [0] * 113
        # If the last card wasnt a wild card, mask the players hand, else, mask only the possible color
        if not self.top_card["color"] == "ANY":
            possible_cards = self.players[self.actual_player]
            if little_help:
                possible_cards = self.get_valid_cards()
            for card in possible_cards:
                mask[card] = 1
            mask[-1] = 1
        else:
            mask[-5:-1] = [1, 1, 1, 1]
        return mask

    def render(self):
        pass

    def close(self):
        pass