import pytest
import pygame

# นำเข้าคลาสและค่าคงที่จากไฟล์เกมของคุณ
# สมมติว่าไฟล์เกมของคุณชื่อ frogger.py
from frogger import (Game, Player, Vehicle, Platform, FORWARD_SCORE,
                     HOME_SCORE, ALL_HOME_BONUS, LEVEL_SPEED_MULTIPLIER,
                     PLAYER_STEP, SCREEN_WIDTH, RIVER_Y_TOP, HOME_Y_TOP)

# ---- Fixtures ----
# Fixtures เป็นฟังก์ชันที่เตรียมข้อมูลหรือสถานะที่จำเป็นสำหรับการทดสอบ


@pytest.fixture
def game():
    """
    สร้าง instance ของ Game ในโหมด headless สำหรับการทดสอบ
    โหมดนี้จะไม่สร้างหน้าต่าง GUI ขึ้นมา
    """
    return Game(headless=True)


# ---- Test Cases ----


class TestGameState:
    """ทดสอบการจัดการสถานะของเกม (State Machine)"""

    def test_initial_state(self, game):
        """เกมควรเริ่มต้นในสถานะ 'START'"""
        assert game.state == "START"
        assert game.level == 1
        assert game.score == 0

    def test_start_game_transition(self, game):
        """ทดสอบการเปลี่ยนสถานะจาก START/GAME_OVER ไปเป็น PLAYING"""
        game.state = "GAME_OVER"
        game.score = 999
        game.start_game()

        assert game.state == "PLAYING"
        assert game.score == 0
        assert game.level == 1
        assert game.lives == 5
        assert all(not slot.filled for slot in game.home_slots)

    def test_game_over_transition(self, game):
        """ทดสอบการเปลี่ยนสถานะเป็น GAME_OVER เมื่อชีวิตหมด"""
        game.start_game()
        game.lives = 1
        game.die("testing")

        assert game.lives == 0
        assert game.state == "GAME_OVER"


class TestPlayerMovement:
    """TS001: ทดสอบการควบคุมและการเคลื่อนที่ของ Player"""

    def test_player_initial_position(self, game):
        """ผู้เล่นควรเริ่มต้นที่ตำแหน่งที่ถูกต้อง"""
        assert game.player.rect.centerx == pytest.approx(SCREEN_WIDTH / 2)
        assert game.player.rect.y > 480  # อยู่ในโซน Safe Start

    @pytest.mark.parametrize("key, dx, dy, should_score", [
        (pygame.K_UP, 0, -PLAYER_STEP, True),
        (pygame.K_DOWN, 0, PLAYER_STEP, False),
        (pygame.K_LEFT, -PLAYER_STEP, 0, False),
        (pygame.K_RIGHT, PLAYER_STEP, 0, False),
    ])
    def test_player_moves_and_scores(self, game, key, dx, dy, should_score):
        """ทดสอบการเคลื่อนที่ทุกทิศทางและการได้คะแนนจากการเดินขึ้น"""
        game.start_game()
        initial_pos = game.player.rect.copy()
        initial_score = game.score

        # สร้าง event การกดปุ่ม
        event = pygame.event.Event(pygame.KEYDOWN, key=key)
        game.handle_input([event])

        expected_score = initial_score + FORWARD_SCORE if should_score else initial_score

        assert game.player.rect.x == initial_pos.x + dx
        assert game.player.rect.y == initial_pos.y + dy
        assert game.score == expected_score

    def test_player_dies_moving_out_of_bounds(self, game):
        """ผู้เล่นควรเสียชีวิตเมื่อพยายามเดินออกจากขอบจอ"""
        game.start_game()
        initial_lives = game.lives
        game.player.set_position(0, game.player.rect.y)  # ย้ายไปขอบซ้ายสุด

        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
        game.handle_input([event])

        assert game.lives == initial_lives - 1
        assert game.last_death_reason == "out_of_bounds"


class TestCollisionsAndDeath:
    """TS002 & TS003: ทดสอบการชน, การตกน้ำ, และเงื่อนไขการตายอื่นๆ"""

    def test_death_by_vehicle_TS002(self, game):
        """ผู้เล่นควรเสียชีวิตเมื่อชนกับรถ"""
        game.start_game()
        initial_lives = game.lives

        # ย้ายผู้เล่นไปที่เลนถนนเลนแรก และสร้างรถทับตำแหน่ง
        road_lane = game.road_lanes[0]
        game.player.set_position(road_lane.y, road_lane.y)
        road_lane.objects[0].x = game.player.rect.x
        road_lane.objects[0].sync_rect()

        game.update(dt=0.01)  # เรียก update เพื่อเช็ค collision

        assert game.lives == initial_lives - 1
        assert game.last_death_reason == "vehicle"

    def test_safe_on_platform_TS003(self, game):
        """ผู้เล่นควรปลอดภัยและเคลื่อนที่ตามเมื่ออยู่บนขอนไม้"""
        game.start_game()
        initial_lives = game.lives

        platform_lane = game.river_lanes[0]
        platform = platform_lane.objects[0]
        game.player.set_position(platform.rect.x, platform.rect.y)
        initial_player_x = game.player.rect.x

        game.update(dt=1.0)  # update เป็นเวลา 1 วินาที

        assert game.lives == initial_lives  # ชีวิตไม่ลด
        assert game.player.on_platform is platform
        # ตรวจสอบว่าผู้เล่นเคลื่อนที่ไปพร้อมกับ platform
        expected_player_x = initial_player_x + platform.vx * 1.0
        assert game.player.rect.x == pytest.approx(expected_player_x)

    def test_death_by_drowning(self, game):
        """ผู้เล่นควรจมน้ำเมื่ออยู่ในโซนแม่น้ำและไม่ได้อยู่บน Platform"""
        game.start_game()
        initial_lives = game.lives
        game.player.set_position(100, RIVER_Y_TOP + 10)  # ย้ายไปกลางแม่น้ำ

        game.update(dt=0.01)

        assert game.lives == initial_lives - 1
        assert game.last_death_reason == "drown"

    def test_death_by_timeout(self, game):
        """ผู้เล่นควรเสียชีวิตเมื่อเวลาหมด"""
        game.start_game()
        initial_lives = game.lives
        game.time_left = 0.01

        game.update(dt=0.02)  # ให้เวลาผ่านไปเกินกำหนด

        assert game.lives == initial_lives - 1
        assert game.last_death_reason == "timeout"


class TestScoringAndLevels:
    """TS004 & TS005: ทดสอบการทำคะแนน, การเข้าบ้าน, และการเลื่อนเลเวล"""

    def test_reach_empty_home_TS004(self, game):
        """ผู้เล่นควรได้คะแนนและรีเซ็ตเมื่อเข้าบ้านที่ว่าง"""
        game.start_game()
        initial_score = game.score

        # ย้ายผู้เล่นไปที่บ้านหลังแรก
        target_slot = game.home_slots[0]
        game.player.set_position(target_slot.rect.centerx, HOME_Y_TOP)

        was_successful = game._check_home_collision()

        assert was_successful is True
        assert game.score == initial_score + HOME_SCORE
        assert target_slot.filled is True
        # ตรวจสอบว่าผู้เล่นกลับไปจุดเริ่มต้น
        assert game.player.rect.y > 480

    def test_reach_filled_home_is_ignored(self, game):
        """การเข้าบ้านที่เต็มแล้วไม่ควรเกิดอะไรขึ้น (ตามโค้ดปัจจุบัน)"""
        game.start_game()
        target_slot = game.home_slots[1]
        target_slot.fill()  # ทำให้บ้านเต็ม
        initial_score = game.score

        game.player.set_position(target_slot.rect.centerx, HOME_Y_TOP)
        was_successful = game._check_home_collision()

        assert was_successful is False
        assert game.score == initial_score  # คะแนนไม่เปลี่ยน

    def test_level_up_mechanic(self, game):
        """ทดสอบการเลื่อนเลเวลเมื่อบ้านเต็มทุกหลัง"""
        game.start_game()
        initial_speed = game.road_lanes[0].objects[0].speed

        # หาจำนวนบ้านทั้งหมดจาก object game
        num_homes = len(game.home_slots)

        # เติมบ้านเกือบทั้งหมดให้เต็ม (เว้นไว้หลังสุดท้าย)
        for i in range(num_homes - 1):
            game.home_slots[i].fill()

        # เข้าบ้านหลังสุดท้ายเพื่อเลื่อนเลเวล
        game.player.set_position(game.home_slots[-1].rect.centerx, HOME_Y_TOP)
        game._check_home_collision()

        assert game.level == 2
        assert game.score == HOME_SCORE + ALL_HOME_BONUS
        # ตรวจสอบว่าบ้านทุกหลังรีเซ็ต (กลับมาเป็น False)
        assert all(not slot.filled for slot in game.home_slots)

        # ตรวจสอบว่าความเร็วของรถในเลนแรกเพิ่มขึ้น
        new_speed = game.road_lanes[0].objects[0].speed
        assert new_speed == pytest.approx(initial_speed *
                                          LEVEL_SPEED_MULTIPLIER)
