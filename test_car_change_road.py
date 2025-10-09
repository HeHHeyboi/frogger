import pytest
from unittest.mock import patch
from game import frogger

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
