"""
Uno game in python
By Sebastian Mora @bastian1110
"""

from random import choice, sample
import numpy as np

# S = skip, R = reverse, T = take two
COLORS = ["RED", "BLUE", "YELLOW", "GREEN"]
SYMBOLS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "S", "R", "T"]


def createDeck() -> dict:
    cards = {}
    i = 0
    for color in COLORS:
        cards[i] = {"color": color, "symbol": "0"}
        i += 1
        for symbol in SYMBOLS:
            cards[i] = {"color": color, "symbol": symbol}
            i += 1
            cards[i] = {"color": color, "symbol": symbol}
            i += 1
    for _ in range(4):
        cards[i] = {"color": "ANY", "symbol": "ANY"}
        i += 1
        cards[i] = {"color": "ANY", "symbol": "F"}
        i += 1
    return cards


class Game:
    def __init__(self, cards: dict, n_players: int = 3) -> None:
        self.cards = cards
        self.draw = list(self.cards.keys())
        first_card = choice(self.draw)
        self.draw.remove(first_card)
        self.stack = [first_card]
        self.direction = False
        self.top = self.cards[first_card]
        self.players = []
        for _ in range(n_players):
            self.players.append(self.create_player())
        print(f" First Card : {self.cards[first_card]}")
        print(f" Stack Top : {self.stack[-1]}")
        print(f" Draw Size : {len(self.draw)}")

    def play(self, rounds: int = 3):
        for _ in range(rounds):
            for player in range(len(self.players)):
                self.player_turn(player)

    def check_available(self, player: int) -> list:
        options = []
        for card in self.players[player]:
            card_info = self.cards[card]
            if (
                card_info["symbol"] == "ANY"
                or card_info["symbol"] == "F"
                or card_info["symbol"] == self.top["symbol"]
                or card_info["color"] == self.top["color"]
            ):
                options.append(card)
        return options

    def player_turn(self, player: int):
        print(f"Player {player} cards : ")
        self.print_cards(self.players[player])
        player_options = self.check_available(player)
        if player_options:
            print("Options : ")
            self.print_cards(self.check_available(player))
            player_card = int(input("Choice : "))
            # handle down correctly
            return
        draw_card = choice(self.draw)
        self.draw.remove(draw_card)
        self.players[player].append(draw_card)
        print(f"Player {player} take {self.cards[draw_card]}")

    def create_player(self) -> list:
        player_cards = sample(self.draw, 7)
        for card in player_cards:
            self.draw.remove(card)
        return player_cards

    def handle_down(self, card, player) -> bool:
        card_info = self.cards[card]
        if card_info["symbol"] == "R":
            self.direction = not self.direction
        if card_info["symbol"] == "S":
            pass
        if card_info["symbol"] == "T":
            pass
        if card_info["symbol"] == "F":
            pass
        if card_info["symbol"] == "ANY":
            pass
        self.top = card_info
        self.players[player].remove(card)
        print(f"New Top : {self.top}")
        return len(self.players[player]) == 0

    def print_cards(self, cards: list) -> None:
        for card in cards:
            card_info = self.cards[card]
            print(f"{card} : {card_info['color']} - {card_info['symbol']} ")


if __name__ == "__main__":
    cards = createDeck()
    g = Game(cards)
    g.play(10)
