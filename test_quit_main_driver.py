from game import frogger


def test_quit():
    try:
        frogger.main()
    except SystemExit:
        pass
