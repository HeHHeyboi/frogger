from game import frogger
import pygame


def all_sound_available():
    pygame.display.set_caption("All Sound")
    frogger.main()


def some_sound_available():
    # pygame.init()
    pygame.display.set_caption("Some sound")

    frogger.hit_sound = None
    frogger.main()


def all_sound_unavailable():
    # pygame.init()
    pygame.display.set_caption("Some sound")

    frogger.hit_sound = None
    frogger.agua_sound = None
    frogger.chegou_sound = None
    frogger.trilha_sound = None
    frogger.main()


if __name__ == "__main__":
    choice = input(
        "Run (1) all sound or (2) some sound? (3) all sound unavailable")
    match choice:
        case "1":
            all_sound_available()
        case "2":
            some_sound_available()
        case "3":
            all_sound_unavailable()
        case _:
            pass
