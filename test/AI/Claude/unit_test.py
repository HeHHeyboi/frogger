import pytest
import pygame

# สมมติว่าโค้ดเกมของคุณอยู่ในไฟล์ชื่อ frogger_game.py
from frogger import (
    Frog,
    Vehicle,
    Log,
    Turtle,
    FroggerGame,
    Direction,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    GRID_SIZE,
    Colors,
)

# ---- Fixtures ----
# Fixtures เป็นฟังก์ชันที่เตรียมข้อมูลหรือสถานะที่จำเป็นสำหรับการทดสอบ


@pytest.fixture
def frog():
    """สร้าง instance ของ Frog สำหรับใช้ในแต่ละเทส"""
    start_x = SCREEN_WIDTH // 2 - GRID_SIZE // 2
    start_y = SCREEN_HEIGHT - GRID_SIZE - 10
    return Frog(start_x, start_y)


@pytest.fixture
def game(mocker):
    """
    สร้าง instance ของ FroggerGame พร้อมกับ mock การทำงานของ Pygame
    เพื่อไม่ให้มีการเปิดหน้าต่าง GUI ขึ้นมาระหว่างการเทส
    """
    mocker.patch("pygame.init")
    mocker.patch("pygame.display.set_mode")
    mocker.patch("pygame.display.set_caption")
    mocker.patch("pygame.font.Font")
    game_instance = FroggerGame()
    # ตรวจสอบให้แน่ใจว่า rect ของกบถูกสร้างขึ้นเพื่อการทดสอบการชน
    game_instance.frog.update_rect()
    return game_instance


# ---- Test Cases ----


class TestFrog:
    """
    TS001: Test Case สำหรับการควบคุมการเดินของกบ
    """

    @pytest.mark.parametrize(
        "direction, expected_dx, expected_dy",
        [
            (Direction.UP, 0, -GRID_SIZE),
            (Direction.DOWN, 0, GRID_SIZE),
            (Direction.LEFT, -GRID_SIZE, 0),
            (Direction.RIGHT, GRID_SIZE, 0),
        ],
    )
    def test_frog_movement(self, frog, direction, expected_dx, expected_dy):
        """ทดสอบการเคลื่อนที่ในทุกทิศทาง"""
        initial_x, initial_y = frog.x, frog.y

        if direction == Direction.DOWN:
            frog.move(Direction.UP)
            initial_x, initial_y = frog.x, frog.y

        frog.move(direction)
        assert frog.x == initial_x + expected_dx
        assert frog.y == initial_y + expected_dy

    def test_move_outside_bounds(self, frog):
        """ทดสอบการเคลื่อนที่ออกนอกขอบเขตหน้าจอ"""
        frog.y = SCREEN_HEIGHT - frog.height
        moved = frog.move(Direction.DOWN)
        assert not moved
        assert frog.y == SCREEN_HEIGHT - frog.height

    def test_reset_position(self, frog):
        """ทดสอบการรีเซ็ตตำแหน่ง"""
        initial_x, initial_y = frog.x, frog.y
        frog.move(Direction.UP)
        frog.reset_position()
        assert frog.x == initial_x
        assert frog.y == initial_y
        assert not frog.on_log
        assert frog.log_speed == 0


class TestMovingObjects:
    """
    TS005: Test Case สำหรับการเคลื่อนที่ของวัตถุ (รถ, ขอนไม้, เต่า)
    """

    def test_vehicle_movement_and_wrap_around(self):
        """TS005: ทดสอบการเคลื่อนที่ของรถและการวนกลับมาที่ขอบจอ"""
        vehicle = Vehicle(x=SCREEN_WIDTH, y=100, speed=5, color=Colors.RED)
        vehicle.update()
        assert vehicle.x == -vehicle.width

    def test_log_movement_and_wrap_around(self):
        """ทดสอบการเคลื่อนที่ของขอนไม้และการวนกลับมาที่ขอบจอ"""
        log = Log(x=-100, y=100, speed=-5, length=3)
        log.update()
        assert log.x == SCREEN_WIDTH

    def test_turtle_diving_mechanic(self):
        """ทดสอบสถานะการดำน้ำของเต่า"""
        turtle = Turtle(x=100, y=100, speed=2)
        turtle.is_diving = False
        turtle.dive_timer = 1  # ตั้งเวลาให้น้อยเพื่อทดสอบการเปลี่ยนสถานะ

        turtle.update()  # เฟรมแรก, dive_timer <= 0, is_diving จะเป็น True
        assert turtle.is_diving

        turtle.dive_timer = 1
        turtle.update()  # เฟรมสอง, dive_timer <= 0, is_diving จะเป็น False
        assert not turtle.is_diving


class TestGameLogicAndCollisions:
    """
    Test Cases สำหรับ Logic และการชนต่างๆ (TS002, TS003, TS004 และอื่นๆ)
    """

    def test_frog_collides_with_vehicle_TS002(self, game):
        """TS002: ทดสอบเมื่อกบโดนรถชน"""
        initial_lives = game.game_state.lives
        vehicle = Vehicle(game.frog.x, game.frog.y, 2, Colors.RED)
        game.vehicles = [vehicle]

        game._check_vehicle_collision()

        assert game.game_state.lives == initial_lives - 1
        assert game.frog.x == game.frog.start_x

    def test_frog_on_log_TS003(self, game):
        """TS003: ทดสอบเมื่อกบอยู่บนขอนไม้ (รอดชีวิต)"""
        initial_lives = game.game_state.lives
        game.frog.y = 180  # ย้ายกบไปโซนแม่น้ำ
        game.frog.update_rect()
        log = Log(x=game.frog.x, y=game.frog.y, speed=3)
        game.logs = [log]
        initial_frog_x = game.frog.x

        game._check_water_collision()

        assert game.game_state.lives == initial_lives  # ชีวิตไม่ลด
        assert game.frog.on_log
        assert game.frog.x == initial_frog_x + log.speed  # กบเคลื่อนที่ตามขอนไม้

    def test_frog_on_safe_turtle(self, game):
        """ทดสอบเมื่อกบอยู่บนเต่าที่ยังไม่ดำน้ำ (รอดชีวิต)"""
        initial_lives = game.game_state.lives
        game.frog.y = 140
        game.frog.update_rect()
        turtle = Turtle(x=game.frog.x, y=game.frog.y, speed=-2)
        turtle.is_diving = False  # เต่ายังไม่ดำน้ำ
        game.turtles = [turtle]

        game._check_water_collision()

        assert game.game_state.lives == initial_lives

    def test_frog_drowns_on_diving_turtle(self, game):
        """ทดสอบเมื่อกบอยู่บนเต่าที่กำลังดำน้ำ (เสียชีวิต)"""
        initial_lives = game.game_state.lives
        game.frog.y = 140
        game.frog.update_rect()
        turtle = Turtle(x=game.frog.x, y=game.frog.y, speed=-2)
        turtle.is_diving = True  # เต่ากำลังดำน้ำ!
        game.turtles = [turtle]

        game._check_water_collision()

        assert game.game_state.lives == initial_lives - 1

    def test_frog_drowns_in_empty_water(self, game):
        """ทดสอบเมื่อกบตกน้ำในบริเวณที่ไม่มีอะไรเลย (เสียชีวิต)"""
        initial_lives = game.game_state.lives
        game.frog.y = 180  # ย้ายไปโซนแม่น้ำ
        game.frog.update_rect()
        game.logs = []
        game.turtles = []

        game._check_water_collision()

        assert game.game_state.lives == initial_lives - 1

    def test_frog_reaches_empty_home_TS004(self, game):
        """TS004: ทดสอบเมื่อกบเดินไปถึงบ้านที่ว่าง"""
        initial_score = game.game_state.score
        initial_homes_filled = game.game_state.homes_filled
        home = game.homes[0]
        game.frog.x, game.frog.y = home.x, home.y
        game.frog.update_rect()

        game._check_home_collision()

        assert game.game_state.score == initial_score + 100
        assert game.game_state.homes_filled == initial_homes_filled + 1
        assert home.occupied
        assert game.frog.x == game.frog.start_x

    def test_frog_reaches_occupied_home(self, game):
        """ทดสอบเมื่อกบเดินไปถึงบ้านที่มีกบอยู่แล้ว (เสียชีวิต)"""
        initial_lives = game.game_state.lives
        home = game.homes[0]
        home.occupied = True
        game.frog.x, game.frog.y = home.x, home.y
        game.frog.update_rect()

        game._check_home_collision()

        assert game.game_state.lives == initial_lives - 1

    def test_time_runs_out(self, game):
        """ทดสอบเมื่อเวลาในเกมหมดลง (เสียชีวิต)"""
        initial_lives = game.game_state.lives
        game.game_state.time_left = 0.01

        game.update_game_logic()  # เรียก logic หลักที่เช็คเวลา

        assert game.game_state.lives == initial_lives - 1
        assert game.game_state.time_left == 30.0  # เวลาถูกรีเซ็ต
