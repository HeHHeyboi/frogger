import pytest
from frogger import *

frog = Frog([0, 0], sprite_sapo)
CAR_POS = [100, 100]
enemy = Enemy(CAR_POS, sprite_car1, "right", 1)
game = Game(0, 0)


@pytest.mark.parametrize(["dir", "pos", "anim_counter", "expected"], [
    ("up", [100, 100], 0, [100, 87]),
    ("up", [100, 38], 0, [100, 38]),
    ("up", [100, 474], 0, [100, 461]),
    ("down", [100, 100], 0, [100, 113]),
    ("down", [100, 38], 0, [100, 51]),
    ("down", [100, 474], 0, [100, 474]),
    ("left", [100, 100], 0, [87, 100]),
    ("left", [100, 100], 2, [86, 100]),
    ("left", [1, 100], 0, [1, 100]),
    ("left", [402, 100], 0, [389, 100]),
    ("left", [402, 100], 2, [388, 100]),
    ("right", [100, 100], 0, [113, 100]),
    ("right", [100, 100], 2, [114, 100]),
    ("right", [1, 100], 0, [14, 100]),
    ("right", [1, 100], 2, [15, 100]),
    ("right", [402, 100], 0, [402, 100]),
])
def test_moveFrog(dir, pos, anim_counter, expected):
    frog.animation_counter = anim_counter
    frog.position = pos.copy()
    frog.moveFrog(dir, 1)
    assert frog.position == expected


@pytest.mark.parametrize(["frog_pos", "expected_pos", "expected_life"], [
    ([0, 0], [0, 0], 3),
    ([100, 0], [100, 0], 3),
    ([0, 100], [0, 100], 3),
    ([100, 100], [207, 475], 2),
    ([70, 100], [70, 100], 3),
    ([155, 100], [155, 100], 3),
    ([100, 70], [100, 70], 3),
    ([100, 130], [100, 130], 3),
])
def test_frog_collide_with_car(frog_pos, expected_pos, expected_life):
    frog.setPos(frog_pos)
    frog.lives = 3
    enemys = [enemy]
    frogOnTheStreet(frog, enemys, game)
    assert frog.position == expected_pos
    assert frog.lives == expected_life
