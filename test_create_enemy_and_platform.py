import pytest
from game import frogger

game = frogger.Game(0, 1)


@pytest.mark.parametrize(["tick", "expected_size", "expected_tick"],
                         [(0, 1, 0), (3, 0, 2)])
def test_create_enemy(tick, expected_size, expected_tick):
    ticks_enemys = [tick]
    enemys = []
    frogger.createEnemys(ticks_enemys, enemys, game)
    assert len(enemys) == expected_size
    assert ticks_enemys[0] == expected_tick


@pytest.mark.parametrize(["tick", "expected_size"], [(0, 1), (10, 0)])
def test_create_platform(tick, expected_size):
    ticks_plataforms = [tick]
    plataforms = []
    frogger.createPlataform(ticks_plataforms, plataforms, game)
    assert len(plataforms) == expected_size
