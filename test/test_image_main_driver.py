from game import frogger


def test_all_image_load():
    try:
        frogger.main()
    except SystemExit:
        pass


def test_some_image_load():
    frogger.background = None
    try:
        frogger.main()
    except SystemExit:
        pass
    except TypeError:
        pass


def test_all_image_null():
    frogger.background = None
    frogger.sprite_sapo = None
    frogger.sprite_arrived = None
    frogger.sprite_car1 = None
    frogger.sprite_car2 = None
    frogger.sprite_car3 = None
    frogger.sprite_car4 = None
    frogger.sprite_car5 = None
    frogger.sprite_plataform = None
    try:
        frogger.main()
    except SystemExit:
        pass
    except TypeError:
        pass


# choice = input(
#     "Run (1) all image load or (2) some image load (3) all image unavailable\n"
# )
# match choice:
#     case "1":
#         all_image_load()
#     case "2":
#         some_image_load()
#     case "3":
#         all_image_null()
#     case _:
#         pass
