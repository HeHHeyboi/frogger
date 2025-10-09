from frogger import *
import pytest

game = Game(3, 1)


@pytest.mark.parametrize(
    ["enemy_pos_x_list", "expected_size", "expected_array"], [
        ([-81], 0, []),
        ([-80], 1, [-80]),
        ([517], 0, []),
        ([516], 1, [516]),
        ([-1000, 0, 9999], 1, [0]),
        ([-81, 0, -82, 10, 517, 20], 3, [-0, 10, 20]),
        ([], 0, []),
        ([-79, 517, 516, -80], 3, [-79, 516, -80]),
    ])
def test_destroy_car(enemy_pos_x_list, expected_size, expected_array):
    result_pos_x = []
    enemys = []
    for i in enemy_pos_x_list:
        enemys.append(Enemy([i, 0], sprite_car1, "left", 1))

    destroyEnemys(enemys)
    for enemy in enemys:
        result_pos_x.append(enemy.position[0])

    assert len(result_pos_x) == expected_size
    assert result_pos_x == expected_array


@pytest.mark.parametrize(
    ["enemy_pos_x_list", "expected_size", "expected_array"], [
        ([-81, 0], 1, [0]),
    ])
def test_destroy_car_multiple_time(enemy_pos_x_list, expected_size,
                                   expected_array):
    result_pos_x = []
    enemys = []
    for i in enemy_pos_x_list:
        enemys.append(Enemy([i, 0], sprite_car1, "left", 1))
    destroyEnemys(enemys)
    destroyEnemys(enemys)
    for enemy in enemys:
        result_pos_x.append(enemy.position[0])
    assert len(result_pos_x) == expected_size
    assert result_pos_x == expected_array


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
        platforms.append(Plataform([i, 0], sprite_plataform, "left"))

    destroyPlataforms(platforms)
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
        platforms.append(Plataform([i, 0], sprite_plataform, "left"))

    destroyPlataforms(platforms)
    destroyPlataforms(platforms)
    for platform in platforms:
        result_pos_x.append(platform.position[0])

    assert len(result_pos_x) == expected_size
    assert result_pos_x == expected_array
