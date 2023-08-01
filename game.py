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
    def __init__(self, cards: dict, n_players: int = 4) -> None:
        self.cards = cards
        self.draw = list(self.cards.keys())
        first_card = choice(self.draw)
        self.draw.remove(first_card)
        self.stack = [first_card]
        self.top = self.cards[first_card]
        self.players = []
        for _ in range(n_players):
            self.players.append(self.create_player())
        print(f" First Card : {self.cards[first_card]}")
        print(f" Stack Top : {self.stack[-1]}")
        print(f" Draw Size : {len(self.draw)}")

    def play(self, rounds: int = 3):
        self.actual_player = 0
        self.direction = False
        for _ in range(rounds):
            print(f"Actual player : {self.actual_player}")
            if self.actual_player >= 4:
                self.actual_player = 0
            if self.actual_player <= -1:
                self.actual_player = 3
            self.player_turn(self.actual_player)
            next_player = 1
            if self.direction:
                next_player = -1
            self.actual_player += next_player

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
            self.handle_down(player_card, player)
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

    def get_next_player(self, player):
        if self.direction:
            if player == 0:
                return 4
            else:
                return player - 1
        else:
            if player == 4:
                return 0
            else:
                return player + 1

    def handle_down(self, card, player) -> bool:
        self.players[player].remove(card)
        card_info = self.cards[card]
        if card_info["symbol"] == "R":
            self.direction = not self.direction
        if card_info["symbol"] == "S":
            if self.direction:
                self.actual_player -= 1
            else:
                self.actual_player += 1
        if card_info["symbol"] == "T":
            player_affected = self.get_next_player(player)
            new_cards = sample(self.draw, 2)
            for card in new_cards:
                self.draw.remove(card)
            self.players[player_affected] = self.players[player_affected] + new_cards
            print(
                f" Player {player_affected} eats 2 cards {len(self.players[player_affected])}"
            )
        if card_info["symbol"] == "F":
            player_affected = self.get_next_player(player)
            new_cards = sample(self.draw, 4)
            for card in new_cards:
                self.draw.remove(card)
            self.players[player_affected] = self.players[player_affected] + new_cards
            print(
                f" Player {player_affected} eats 4 cards {len(self.players[player_affected])}"
            )
        if card_info["symbol"] == "ANY":
            card_info = self.top
        self.top = card_info
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
