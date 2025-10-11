import pytest
import pygame

# นำเข้าคลาสและค่าคงที่จากไฟล์เกมของคุณ
from frogger import (Frog, MovingObject, Turtle, Game, GRID_SIZE, TOTAL_HOMES,
                     SCREEN_WIDTH)

# ---- Fixtures ----
# Fixtures คือฟังก์ชันที่เตรียมข้อมูลหรือสถานะที่จำเป็นสำหรับการทดสอบ
# Pytest จะเรียกใช้ฟังก์ชันเหล่านี้โดยอัตโนมัติเมื่อ test function ร้องขอ


@pytest.fixture
def game(mocker):
    """
    สร้าง instance ของ Game พร้อมกับ mock การทำงานของ Pygame
    เพื่อไม่ให้มีการเปิดหน้าต่าง GUI ขึ้นมาระหว่างการเทส
    """
    mocker.patch("pygame.init")
    mocker.patch("pygame.display.set_mode")
    mocker.patch("pygame.display.set_caption")
    mocker.patch("pygame.font.Font")

    # Mock time.get_ticks() เพื่อให้ควบคุมเวลาในการทดสอบได้
    mock_ticks = mocker.patch("pygame.time.get_ticks")
    mock_ticks.return_value = 1000  # เริ่มต้นที่ 1000ms

    game_instance = Game()
    # ตั้งค่าเวลาเริ่มต้นของด่านให้ตรงกับ mock_ticks
    game_instance.start_time = mock_ticks.return_value
    return game_instance


# ---- Test Cases ----


class TestFrog:
    """TS001: ทดสอบการทำงานของคลาส Frog"""

    def test_frog_initialization(self, game):
        """ทดสอบการสร้างกบและตำแหน่งเริ่มต้น"""
        frog = game.frog
        assert frog.rect.x == (SCREEN_WIDTH - GRID_SIZE) // 2
        assert frog.rect.y == game.screen.get_height() - GRID_SIZE
        assert frog.attached_to is None

    def test_frog_movement(self, game):
        """ทดสอบการเคลื่อนที่ของกบ"""
        frog = game.frog
        initial_x, initial_y = frog.rect.topleft

        frog.move(0, -1)  # ขึ้น
        assert frog.rect.topleft == (initial_x, initial_y - GRID_SIZE)

        frog.move(0, 1)  # ลง
        assert frog.rect.topleft == (initial_x, initial_y)

        frog.move(-1, 0)  # ซ้าย
        assert frog.rect.topleft == (initial_x - GRID_SIZE, initial_y)

    def test_frog_attach_and_detach(self, game):
        """ทดสอบการเกาะและปล่อยจากวัตถุ"""
        frog = game.frog
        platform = MovingObject(100, 100, 80, 40, (0, 0, 0), 2)

        assert frog.attached_to is None
        frog.attach_to(platform)
        assert frog.attached_to is platform

        frog.detach()
        assert frog.attached_to is None

    def test_frog_moves_with_platform(self, game):
        """ทดสอบว่ากบเคลื่อนที่ตาม platform ที่เกาะอยู่"""
        frog = game.frog
        platform = MovingObject(100, 100, 80, 40, (0, 0, 0), speed=3)
        frog.rect.topleft = platform.rect.topleft

        frog.attach_to(platform)
        frog.update_position_on_platform()

        # กบควรเคลื่อนที่ไปทางขวา 3 pixels เหมือน platform
        assert frog.rect.x == platform.rect.x + 3


class TestMovingObjects:
    """TS005: ทดสอบการทำงานของวัตถุที่เคลื่อนที่"""

    def test_object_wraps_around_screen(self):
        """ทดสอบการวนกลับมาเมื่อวัตถุตกขอบจอ"""
        # วิ่งไปทางขวา
        obj_right = MovingObject(SCREEN_WIDTH, 100, 80, 40, (0, 0, 0), speed=5)
        obj_right.move()
        assert obj_right.rect.right == 5  # 0 (ขอบซ้าย) + 5 (speed)

        # วิ่งไปทางซ้าย
        obj_left = MovingObject(0 - 80, 100, 80, 40, (0, 0, 0), speed=-5)
        obj_left.move()
        assert obj_left.rect.left == SCREEN_WIDTH - 5

    def test_turtle_diving_cycle(self):
        """ทดสอบวงจรการดำน้ำของเต่า"""
        turtle = Turtle(100, 100, speed=1, dive_interval=3, dive_duration=2)
        assert not turtle.is_diving

        # เวลาผ่านไปจนถึงเวลาดำน้ำ
        turtle.update(dt=3.1)
        assert turtle.is_diving

        # เวลาผ่านไปจนโผล่ขึ้นมา
        turtle.update(dt=2.1)
        assert not turtle.is_diving


class TestGameCollisionsAndLogic:
    """ทดสอบ Logic การชนและสถานะต่างๆ ของเกม"""

    def test_frog_hit_by_car_TS002(self, game):
        """TS002: กบถูกรถชนแล้วเสียชีวิต"""
        initial_lives = game.lives
        game.frog.rect.y = game.road_rect.y  # ย้ายกบไปที่ถนน
        # สร้างรถทับตำแหน่งกบ
        car = MovingObject(game.frog.rect.x, game.frog.rect.y, 80, 40,
                           (255, 0, 0), 2)
        game.obstacles.append(car)

        game.check_collisions()

        assert game.lives == initial_lives - 1
        # ตรวจสอบว่ากบกลับไปจุดเริ่มต้น
        assert game.frog.rect.topleft == (game.frog.start_x, game.frog.start_y)

    def test_frog_safe_on_log_TS003(self, game):
        """TS003: กบปลอดภัยเมื่ออยู่บนขอนไม้"""
        initial_lives = game.lives
        game.frog.rect.y = game.water_rect.y  # ย้ายกบไปที่แม่น้ำ
        log = MovingObject(game.frog.rect.x, game.frog.rect.y, 120, 40,
                           (150, 75, 0), 2)
        game.platforms.append(log)

        game.check_collisions()

        assert game.lives == initial_lives  # ชีวิตไม่ลด
        assert game.frog.attached_to is log  # เกาะติดกับขอนไม้

    def test_frog_drowns_in_water(self, game):
        """กบจมน้ำเมื่ออยู่ในแม่น้ำโดยไม่มีที่เกาะ"""
        initial_lives = game.lives
        game.frog.rect.y = game.water_rect.y
        game.platforms = []  # ไม่มี platform เลย

        game.check_collisions()

        assert game.lives == initial_lives - 1

    def test_frog_drowns_on_diving_turtle(self, game):
        """กบจมน้ำเมื่ออยู่บนเต่าที่กำลังดำน้ำ"""
        initial_lives = game.lives
        game.frog.rect.y = game.water_rect.y
        diving_turtle = Turtle(game.frog.rect.x, game.frog.rect.y, 1, 3, 2)
        diving_turtle.is_diving = True  # บังคับให้เต่าดำน้ำ
        game.platforms.append(diving_turtle)

        game.check_collisions()

        assert game.lives == initial_lives - 1

    def test_frog_reaches_empty_home_TS004(self, game):
        """TS004: กบถึงบ้านที่ยังว่าง"""
        initial_score = game.score
        game.frog.rect.top = 0  # ย้ายกบไปแถวบนสุด
        # จัดตำแหน่งให้อยู่กลางบ้านหลังแรก
        home_center_x = game.homes[0].rect.centerx
        game.frog.rect.centerx = home_center_x

        game.check_collisions()

        assert game.score > initial_score
        assert game.homes_filled[0] is True
        assert game.frog.rect.topleft == (game.frog.start_x, game.frog.start_y)

    def test_frog_hits_filled_home(self, game):
        """กบชนบ้านที่เต็มแล้ว (เสียชีวิต)"""
        initial_lives = game.lives
        game.homes_filled[2] = True  # ทำให้บ้านหลังที่ 3 เต็ม
        game.frog.rect.top = 0
        game.frog.rect.centerx = game.homes[2].rect.centerx

        game.check_collisions()

        assert game.lives == initial_lives - 1

    def test_level_complete(self, game):
        """ทดสอบเมื่อผ่านด่าน (ทุกบ้านเต็ม)"""
        initial_score = game.score
        game.homes_filled = [True] * (TOTAL_HOMES - 1) + [False
                                                          ]  # เหลือบ้านสุดท้าย
        game.frog.rect.top = 0
        game.frog.rect.centerx = game.homes[-1].rect.centerx

        game.check_collisions()

        assert all(game.homes_filled) is True
        assert game.game_state == "level_complete"
        assert game.score == initial_score + 50 + 1000 + 60  # score + time bonus + level bonus

    def test_time_runs_out(self, game, mocker):
        """ทดสอบเมื่อเวลาหมด (เสียชีวิต)"""
        initial_lives = game.lives
        # จำลองว่าเวลาผ่านไปเกินกำหนด
        mock_ticks = mocker.patch("pygame.time.get_ticks")
        mock_ticks.return_value = game.start_time + game.time_limit + 100

        game.check_time()

        assert game.lives == initial_lives - 1

    def test_game_over(self, game):
        """ทดสอบสถานะ Game Over"""
        game.lives = 1
        game.lose_life()
        assert game.lives == 0
        assert game.game_state == "game_over"
