from random import choice
import numpy as np

COLORS = ["RED", "BLUE", "YELLOW", "GREEN"]
NUMBERS = list(
    range(
        0,
        10,
    )
)


class Player:
    def __init__(self, solution, n_cards=3) -> None:
        self.id = 0
        self.cards = {}
        for i in range(n_cards):
            self.cards[self.id] = {"color": choice(COLORS), "number": choice(NUMBERS)}
            self.id += 1
        self.solution = solution

    def take_card(self) -> None:
        if len(self.cards) == 3:
            return
        self.cards[self.id] = {"color": choice(COLORS), "number": choice(NUMBERS)}
        self.id += 1

    def leave_card(self, index) -> bool:
        self.cards.pop(index)
        return len(self.cards) == 0

    def check_available(self, actual) -> dict:
        options = {}
        for key, value in self.cards.items():
            if value["color"] == actual["color"] or value["number"] == actual["number"]:
                options[key] = value
        return options

    def automatic_play(self, actual) -> int:
        options = self.check_available(actual)
        if options:
            scores = [
                self.solution[COLORS.index(actual["color"])][actual["number"]][
                    COLORS.index(card["color"])
                ][card["number"]]
                for card in options.values()
            ]
            return list(options.keys())[np.argmax(scores)]
        return -1

    def print_cards(self) -> None:
        for key, value in self.cards.items():
            print(f"Index :  {key} : {value}")


class Game:
    def __init__(self, n_rounds=25) -> None:
        solution1 = np.random.rand(len(COLORS), len(NUMBERS), len(COLORS), len(NUMBERS))
        self.player1 = Player(solution=solution1)
        solution2 = np.random.rand(len(COLORS), len(NUMBERS), len(COLORS), len(NUMBERS))
        self.player2 = Player(solution=solution2)
        self.actual_card = {"color": choice(COLORS), "number": choice(NUMBERS)}

        for _ in range(0, n_rounds):
            print("= PLAYER ONE ", "=" * 8)
            print("Actual Top : ", self.actual_card)
            if self.player_one_move():
                print("Player One Wins! 😘")
                return
            print("= PLAYER TWO ", "=" * 8)
            print("Actual Top : ", self.actual_card)
            if self.player_two_move(True):
                print("Player Two Wins! 😘")
                return
        print("No one got 0 cards")
        if len(self.player1.cards) < len(self.player2.cards):
            print("Game over! Player One Wins! ")
        elif len(self.player2.cards) < len(self.player1.cards):
            print("Game over! Player Two Wins! ")
        else:
            print("Game Over! Draw ")
        return

    def player_one_move(self) -> bool:
        print("Player One Turn, Cards : ", len(self.player1.cards))
        print("Player One Cards : ")
        self.player1.print_cards()
        avialable_options = self.player1.check_available(self.actual_card)
        if avialable_options:
            print("Cards : ")
            for key, value in avialable_options.items():
                print(f"{key} : {value}")
            option = -1
            while option == -1:
                new_option = int(input("Choice : "))
                new_card = self.player1.cards[new_option]
                if (
                    new_card["number"] == self.actual_card["number"]
                    or new_card["color"] == self.actual_card["color"]
                ):
                    self.actual_card = new_card
                    return self.player1.leave_card(new_option)
            return False
        if len(self.player1.cards) < 5:
            print("No cards available, you take one card")
            self.player1.take_card()
            input("Undestand (Enter) :")
            return False
        print("No cards available, no available space")
        return False

    def player_two_move(self, auto=False) -> bool:
        print("Player Two Turn, Cards : ", len(self.player2.cards))
        print("Player Two Cards : ")
        self.player2.print_cards()
        if not auto:
            avialable_options = self.player2.check_available(self.actual_card)
            if self.player2.check_available(self.actual_card):
                print("Cards : ")
                for key, value in avialable_options.items():
                    print(f"{key} : {value}")
                option = -1
                while option == -1:
                    new_option = int(input("Choice : "))
                    new_card = self.player2.cards[new_option]
                    if (
                        new_card["number"] == self.actual_card["number"]
                        or new_card["color"] == self.actual_card["color"]
                    ):
                        self.actual_card = new_card
                        return self.player2.leave_card(new_option)
                return False
            if len(self.player2.cards) < 5:
                print("No cards available, you take one card")
                self.player2.take_card()
                input("Undestand (Enter) :")
                return False
            print("No cards available, no available space")
            return False
        computer_choice = self.player2.automatic_play(self.actual_card)
        if computer_choice != -1:
            computer_card = self.player2.cards[computer_choice]
            print(f"Player two choosed {computer_card}")
            self.actual_card = computer_card
            return self.player2.leave_card(computer_choice)
        print("Player two has no card, he took one")
        self.player2.take_card()
        return False


if __name__ == "__main__":
    Game()
