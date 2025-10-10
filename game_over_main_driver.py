from game import frogger
from unittest.mock import patch


def normal():
    frogger.main()


def live_is_zero():
    original_init = frogger.Frog.__init__

    def new_init(self, position, sprite):
        original_init(self, position, sprite)
        self.lives = 0

    with patch.object(frogger.Frog, "__init__", new_init):
        frogger.main()


def time_up():
    original_game_init = frogger.Game.__init__
    original_frog_init = frogger.Frog.__init__

    def new_frog_init(self, position, sprite):
        original_frog_init(self, position, sprite)
        self.lives = 1

    with patch.object(frogger.Frog, "__init__", new_frog_init):
        frogger.game.time = 1
        frogger.main()


choice = input("select Scenario (1-3)\n")
match choice:
    case "1":
        normal()
    case "2":
        live_is_zero()
    case "3":
        time_up()
    case _:
        pass
