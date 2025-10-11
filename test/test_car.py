import pytest
from game import frogger
from unittest.mock import patch

game = frogger.Game(3, 1)


@pytest.mark.parametrize(["tick", "expected_size", "expected_tick"], [
    (0, 1, 120),
    (3, 0, 2),
])
def test_create_enemy(tick, expected_size, expected_tick):
    ticks_enemys = [tick]
    enemys = []
    frogger.createEnemys(ticks_enemys, enemys, game)
    assert len(enemys) == expected_size
    assert ticks_enemys[0] == expected_tick


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
        enemys.append(frogger.Enemy([i, 0], frogger.sprite_car1, "left", 1))

    frogger.destroyEnemys(enemys)
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
        enemys.append(frogger.Enemy([i, 0], frogger.sprite_car1, "left", 1))
    frogger.destroyEnemys(enemys)
    frogger.destroyEnemys(enemys)
    for enemy in enemys:
        result_pos_x.append(enemy.position[0])
    assert len(result_pos_x) == expected_size
    assert result_pos_x == expected_array


WAY = "left"
FACTOR = 1


@pytest.mark.parametrize(
    ["car_pos_y_list", "target_index", "random_int", "expected_y"], [
        ([357], 0, 2, [396]),
        ([357], 0, 1, [318]),
        ([436], 0, 2, [436]),
        ([436], 0, 1, [397]),
        ([280], 0, 1, [280]),
        ([280], 0, 2, [319]),
        ([318, 357, 397], 1, 2, [318, 396, 397]),
    ])
def test_car_change_road(car_pos_y_list, target_index, random_int, expected_y):
    result = []
    enemys = []
    for y in car_pos_y_list:
        enemys.append(frogger.Enemy([0, y], frogger.sprite_car1, "left", 1))

    with (patch("random.choice", return_value=enemys[target_index]),
          patch("random.randint", return_value=random_int)):
        frogger.carChangeRoad(enemys)

    for car in enemys:
        result.append(car.position[1])

    target_enemy = enemys[target_index]
    assert result == expected_y
    assert target_enemy.factor == FACTOR
    assert target_enemy.position[0] == 0
    assert target_enemy.way == WAY


def test_empty_car_list():

    car_list = []
    with (pytest.raises(IndexError) as
          excinfo, patch("random.randint", return_value=0)):
        frogger.carChangeRoad(car_list)

    assert str(excinfo.value) == "Cannot choose from an empty sequence"


@pytest.mark.parametrize(
    ["car_pos_y_list", "target_index", "random_int", "expected_y"], [
        ([300], 0, [2, 1], [339, 300]),
    ])
def test_car_change_road_multiple_time(car_pos_y_list, target_index,
                                       random_int, expected_y):
    result = []
    enemys = []
    for y in car_pos_y_list:
        enemys.append(frogger.Enemy([0, y], frogger.sprite_car1, "left", 1))

    for i in random_int:
        with (patch("random.choice", return_value=enemys[target_index]),
              patch("random.randint", return_value=i)):
            frogger.carChangeRoad(enemys)
            result.append(enemys[target_index].position[1])

    target_enemy = enemys[target_index]
    assert result == expected_y
    assert target_enemy.factor == FACTOR
    assert target_enemy.position[0] == 0
    assert target_enemy.way == WAY
