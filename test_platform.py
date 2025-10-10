import pytest
from game import frogger

game = frogger.Game(0, 1)


@pytest.mark.parametrize(["tick", "expected_size"], [(0, 1), (10, 0)])
def test_create_platform(tick, expected_size):
    ticks_plataforms = [tick]
    plataforms = []
    frogger.createPlataform(ticks_plataforms, plataforms, game)
    assert len(plataforms) == expected_size


@pytest.mark.parametrize(
    ["platform_pos_x_list", "expected_size", "expected_array"], [
        ([-101], 0, []),
        ([-100], 1, [-100]),
        ([449], 0, []),
        ([448], 1, [448]),
        ([-1000, 0, 9999], 1, [0]),
        ([-101, 0, -120, 10, 449, 20], 3, [0, 10, 20]),
        ([], 0, []),
        ([-99, 449, 448, -100], 3, [-99, 448, -100]),
    ])
def test_destroy_platform(platform_pos_x_list, expected_size, expected_array):
    result_pos_x = []
    platforms = []
    for i in platform_pos_x_list:
        platforms.append(
            frogger.Plataform([i, 0], frogger.sprite_plataform, "left"))

    frogger.destroyPlataforms(platforms)
    for platform in platforms:
        result_pos_x.append(platform.position[0])

    assert len(result_pos_x) == expected_size
    assert result_pos_x == expected_array


@pytest.mark.parametrize(
    ["platform_pos_x_list", "expected_size", "expected_array"], [
        ([-101, 0], 1, [0]),
    ])
def test_destroy_platfrom_multiple_time(platform_pos_x_list, expected_size,
                                        expected_array):
    result_pos_x = []
    platforms = []
    for i in platform_pos_x_list:
        platforms.append(
            frogger.Plataform([i, 0], frogger.sprite_plataform, "left"))

    frogger.destroyPlataforms(platforms)
    frogger.destroyPlataforms(platforms)
    for platform in platforms:
        result_pos_x.append(platform.position[0])

    assert len(result_pos_x) == expected_size
    assert result_pos_x == expected_array
