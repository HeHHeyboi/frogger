import pygame
import pytest
from unittest.mock import MagicMock, patch
from code import (
    Game, Frog, MovingObject, Turtle, GameObject,
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, TOTAL_HOMES, MAX_LIVES, LEVEL_START_TIME
)

# --- Fixtures ---
# Fixture สำหรับสร้าง instance ของ Game แบบใช้แล้วทิ้งสำหรับแต่ละ test function
# ช่วยให้มั่นใจว่าแต่ละ test เริ่มต้นด้วย state ที่สะอาด ไม่ขึ้นต่อกัน
@pytest.fixture
def game_instance():
    """สร้าง instance ของ Game สำหรับการทดสอบ"""
    # ใช้ patch เพื่อ mock การทำงานของ Pygame ที่เกี่ยวข้องกับการแสดงผล
    # เนื่องจาก unit test ไม่จำเป็นต้องวาดภาพจริงๆ บนหน้าจอ
    with patch('pygame.display.set_mode'), patch('pygame.font.Font'):
        game = Game()
        # Mock screen โดยตรงเพื่อป้องกัน error เวลาเรียกใช้ฟังก์ชัน draw
        game.screen = MagicMock()
        return game

# Fixture สำหรับสร้าง instance ของ Frog
@pytest.fixture
def frog_instance():
    """สร้าง instance ของ Frog สำหรับการทดสอบ"""
    return Frog(SCREEN_WIDTH // 2, SCREEN_HEIGHT - GRID_SIZE)

# Fixture สำหรับสร้าง instance ของ Turtle
@pytest.fixture
def turtle_instance():
    """สร้าง instance ของ Turtle สำหรับการทดสอบ"""
    return Turtle(x=100, y=100, speed=2, dive_interval=3, dive_duration=2)


# --- Test Cases ---

class TestGameObject:
    """ทดสอบคลาส GameObject"""
    def test_init(self):
        """ทดสอบการสร้าง object และการกำหนดค่าเริ่มต้น"""
        obj = GameObject(10, 20, 30, 40, (255, 0, 0))
        assert obj.rect.x == 10
        assert obj.rect.y == 20
        assert obj.rect.width == 30
        assert obj.rect.height == 40
        assert obj.color == (255, 0, 0)

    def test_draw(self):
        """ทดสอบการวาด object (ตรวจสอบว่า pygame.draw.rect ถูกเรียกด้วยค่าที่ถูกต้อง)"""
        mock_screen = MagicMock()
        obj = GameObject(10, 20, 30, 40, (255, 0, 0))
        with patch('pygame.draw.rect') as mock_draw_rect:
            obj.draw(mock_screen)
            # ตรวจสอบว่า `draw.rect` ถูกเรียก 1 ครั้ง
            mock_draw_rect.assert_called_once()
            # ตรวจสอบว่า argument ที่ส่งให้ `draw.rect` ถูกต้อง
            mock_draw_rect.assert_called_with(mock_screen, obj.color, obj.rect)

class TestFrog:
    """ทดสอบคลาส Frog"""
    def test_init(self, frog_instance):
        """ทดสอบการสร้าง Frog และค่าเริ่มต้น"""
        assert frog_instance.rect.width == GRID_SIZE
        assert frog_instance.rect.height == GRID_SIZE
        assert frog_instance.start_x == frog_instance.rect.x
        assert frog_instance.start_y == frog_instance.rect.y
        assert frog_instance.attached_to is None

    def test_move(self, frog_instance):
        """ทดสอบการเคลื่อนที่ของกบ"""
        original_x, original_y = frog_instance.rect.x, frog_instance.rect.y
        # เคลื่อนที่ขึ้น
        frog_instance.move(0, -1)
        assert frog_instance.rect.x == original_x
        assert frog_instance.rect.y == original_y - GRID_SIZE
        # เคลื่อนที่ขวา
        frog_instance.move(1, 0)
        assert frog_instance.rect.x == original_x + GRID_SIZE
        assert frog_instance.rect.y == original_y - GRID_SIZE

    def test_attach_detach(self, frog_instance):
        """ทดสอบการเกาะและปล่อยจาก platform"""
        platform = MovingObject(100, 100, 80, 40, (0,0,0), 2)
        frog_instance.attach_to(platform)
        assert frog_instance.attached_to == platform
        frog_instance.detach()
        assert frog_instance.attached_to is None

    def test_update_position_on_platform(self, frog_instance):
        """ทดสอบการอัปเดตตำแหน่งเมื่อเกาะบน platform"""
        platform = MovingObject(100, 100, 80, 40, (0,0,0), speed=2.5)
        frog_instance.rect.x = 110
        frog_instance.attach_to(platform)
        
        # กบควรเคลื่อนที่ตามความเร็วของ platform
        frog_instance.update_position_on_platform()
        assert frog_instance.rect.x == 110 + 2.5

    def test_update_position_not_on_platform(self, frog_instance):
        """ทดสอบว่าตำแหน่งไม่อัปเดตหากไม่ได้เกาะ platform"""
        original_x = frog_instance.rect.x
        frog_instance.update_position_on_platform()
        assert frog_instance.rect.x == original_x

    def test_reset_position(self, frog_instance):
        """ทดสอบการรีเซ็ตตำแหน่ง"""
        platform = MovingObject(100, 100, 80, 40, (0,0,0), 2)
        frog_instance.attach_to(platform)
        frog_instance.move(2, 2) # เคลื่อนที่ไปตำแหน่งอื่น
        
        frog_instance.reset_position()
        assert frog_instance.rect.x == frog_instance.start_x
        assert frog_instance.rect.y == frog_instance.start_y
        assert frog_instance.attached_to is None

    def test_is_on_screen(self, frog_instance):
        """ทดสอบการตรวจสอบว่ากบอยู่ในจอหรือไม่"""
        assert frog_instance.is_on_screen()
        frog_instance.rect.x = -1
        assert not frog_instance.is_on_screen()
        frog_instance.rect.x = SCREEN_WIDTH
        assert not frog_instance.is_on_screen()
        frog_instance.rect.x = SCREEN_WIDTH - 1
        assert frog_instance.is_on_screen()


class TestMovingObject:
    """ทดสอบคลาส MovingObject"""
    def test_move_positive_speed_wrap(self):
        """ทดสอบการเคลื่อนที่ไปทางขวาและวนกลับมาเมื่อตกขอบ"""
        obj = MovingObject(SCREEN_WIDTH - 1, 100, 50, 40, (0,0,0), speed=2)
        obj.move()
        # เมื่อเคลื่อนที่จน rect.left > SCREEN_WIDTH, rect.right ควรจะเท่ากับ 0
        assert obj.rect.right == 0

    def test_move_negative_speed_wrap(self):
        """ทดสอบการเคลื่อนที่ไปทางซ้ายและวนกลับมาเมื่อตกขอบ"""
        obj = MovingObject(1, 100, 50, 40, (0,0,0), speed=-2)
        # เคลื่อนที่จน rect.right < 0
        obj.rect.right = -1
        obj.move()
        assert obj.rect.left == SCREEN_WIDTH

class TestTurtle:
    """ทดสอบคลาส Turtle"""
    def test_update_diving_logic(self, turtle_instance):
        """ทดสอบสถานะการดำน้ำและโผล่ของเต่าตามเวลา"""
        # เริ่มต้น: ยังไม่ดำน้ำ
        assert not turtle_instance.is_diving
        
        # เวลาผ่านไปจนถึง dive_interval -> ควรจะดำน้ำ
        turtle_instance.update(dt=turtle_instance.dive_interval)
        assert turtle_instance.is_diving
        
        # เวลาผ่านไปอีกเล็กน้อย -> ยังคงดำน้ำอยู่
        turtle_instance.update(dt=turtle_instance.dive_duration / 2)
        assert turtle_instance.is_diving

        # เวลาผ่านไปจนครบ dive_duration -> ควรจะโผล่ขึ้นมา
        turtle_instance.update(dt=turtle_instance.dive_duration / 2)
        assert not turtle_instance.is_diving
        assert turtle_instance.timer == 0 # Timer ถูกรีเซ็ต

    def test_draw_while_diving(self, turtle_instance):
        """ทดสอบว่าเต่าจะไม่ถูกวาดขณะดำน้ำ"""
        mock_screen = MagicMock()
        turtle_instance.is_diving = True
        with patch('pygame.draw.rect') as mock_draw_rect:
            turtle_instance.draw(mock_screen)
            mock_draw_rect.assert_not_called()

    def test_draw_while_not_diving(self, turtle_instance):
        """ทดสอบว่าเต่าจะถูกวาดเมื่อไม่ได้ดำน้ำ"""
        mock_screen = MagicMock()
        turtle_instance.is_diving = False
        with patch('pygame.draw.rect') as mock_draw_rect:
            turtle_instance.draw(mock_screen)
            mock_draw_rect.assert_called_once()


class TestGame:
    """ทดสอบคลาส Game ซึ่งเป็นคลาสหลักของเกม"""

    def test_reset_game(self, game_instance):
        """ทดสอบการรีเซ็ตเกมกลับสู่สถานะเริ่มต้น"""
        # เปลี่ยนค่าต่างๆ ให้ไม่เหมือนค่าเริ่มต้น
        game_instance.lives = 1
        game_instance.score = 1000
        game_instance.level = 5
        game_instance.homes_filled[0] = True
        
        # เรียก reset_game
        game_instance.reset_game()
        
        # ตรวจสอบว่าค่ากลับเป็นค่าเริ่มต้นทั้งหมด
        assert game_instance.lives == MAX_LIVES
        assert game_instance.score == 0
        assert game_instance.level == 1
        assert not any(game_instance.homes_filled)

    def test_handle_input_quit(self, game_instance):
        """ทดสอบการปิดเกมเมื่อได้รับ Event QUIT"""
        with patch('pygame.event.get', return_value=[pygame.event.Event(pygame.QUIT)]):
            game_instance.handle_input()
            assert not game_instance.running

    @pytest.mark.parametrize("key, dx, dy", [
        (pygame.K_UP, 0, -1),
        (pygame.K_DOWN, 0, 1),
        (pygame.K_LEFT, -1, 0),
        (pygame.K_RIGHT, 1, 0),
    ])
    def test_handle_input_frog_move(self, game_instance, key, dx, dy):
        """ทดสอบการจัดการ input เพื่อเคลื่อนที่กบ"""
        # Mock frog.move เพื่อตรวจสอบการเรียกใช้
        game_instance.frog.move = MagicMock()
        
        # สร้าง event กดปุ่ม
        event = pygame.event.Event(pygame.KEYDOWN, key=key)
        
        # ป้องกันไม่ให้กบเคลื่อนที่ออกนอกจอในการทดสอบนี้
        game_instance.frog.rect.top = GRID_SIZE
        game_instance.frog.rect.bottom = SCREEN_HEIGHT - GRID_SIZE
        game_instance.frog.rect.left = GRID_SIZE
        game_instance.frog.rect.right = SCREEN_WIDTH - GRID_SIZE

        with patch('pygame.event.get', return_value=[event]):
            game_instance.handle_input()
            game_instance.frog.move.assert_called_once_with(dx, dy)

    def test_handle_input_frog_move_at_boundaries(self, game_instance):
        """ทดสอบว่ากบไม่เคลื่อนที่เมื่ออยู่ที่ขอบจอ"""
        game_instance.frog.move = MagicMock()
        
        # ทดสอบขอบบน
        game_instance.frog.rect.top = 0
        event_up = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        with patch('pygame.event.get', return_value=[event_up]):
            game_instance.handle_input()
            game_instance.frog.move.assert_not_called()
            
        # ทดสอบขอบล่าง
        game_instance.frog.rect.bottom = SCREEN_HEIGHT
        event_down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        with patch('pygame.event.get', return_value=[event_down]):
            game_instance.handle_input()
            game_instance.frog.move.assert_not_called()

        # ทดสอบขอบซ้าย
        game_instance.frog.rect.left = 0
        event_left = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
        with patch('pygame.event.get', return_value=[event_left]):
            game_instance.handle_input()
            game_instance.frog.move.assert_not_called()
            
        # ทดสอบขอบขวา
        game_instance.frog.rect.right = SCREEN_WIDTH
        event_right = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        with patch('pygame.event.get', return_value=[event_right]):
            game_instance.handle_input()
            game_instance.frog.move.assert_not_called()

    @pytest.mark.parametrize("state", ["game_over", "level_complete"])
    def test_handle_input_restart(self, game_instance, state):
        """ทดสอบการกด Enter เพื่อเริ่มเกมใหม่/ด่านต่อไป"""
        game_instance.game_state = state
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        
        # Mock method ที่จะถูกเรียก
        game_instance.reset_game = MagicMock()
        game_instance.setup_level = MagicMock()
        
        with patch('pygame.event.get', return_value=[event]):
            game_instance.handle_input()
            if state == "game_over":
                game_instance.reset_game.assert_called_once()
            else: # level_complete
                game_instance.setup_level.assert_called_once()
                assert game_instance.level == 2 # เช็คว่า level เพิ่มขึ้น

    def test_update_calls_move_and_check(self, game_instance):
        """ทดสอบว่า `update` เรียก method อื่นๆ ที่จำเป็น"""
        game_instance.check_collisions = MagicMock()
        game_instance.check_time = MagicMock()
        
        # ทดสอบเมื่อ game_state ไม่ใช่ "playing"
        game_instance.game_state = "game_over"
        game_instance.update()
        game_instance.check_collisions.assert_not_called()

        # ทดสอบเมื่อ game_state เป็น "playing"
        game_instance.game_state = "playing"
        with patch.object(game_instance.clock, 'get_time', return_value=16): # 16ms ~ 60fps
            game_instance.update()
            game_instance.check_collisions.assert_called_once()
            game_instance.check_time.assert_called_once()
    
    def test_collision_with_obstacle(self, game_instance):
        """ทดสอบการชนกับรถ"""
        # สร้างรถที่ตำแหน่งเดียวกับกบ
        game_instance.obstacles[0].rect = game_instance.frog.rect.copy()
        game_instance.lose_life = MagicMock()
        game_instance.check_collisions()
        game_instance.lose_life.assert_called_once()

    def test_drown_in_water(self, game_instance):
        """ทดสอบการตกน้ำตาย"""
        # ย้ายกบไปอยู่ในโซนน้ำ โดยไม่อยู่บน platform ใดๆ
        game_instance.frog.rect.centery = game_instance.water_rect.centery
        game_instance.lose_life = MagicMock()
        game_instance.check_collisions()
        game_instance.lose_life.assert_called_once()

    def test_safe_on_platform(self, game_instance):
        """ทดสอบเมื่อกบอยู่บน platform อย่างปลอดภัย"""
        # ย้ายกบไปอยู่บน platform แรก
        platform = game_instance.platforms[0]
        game_instance.frog.rect.center = platform.rect.center
        game_instance.lose_life = MagicMock()
        game_instance.check_collisions()
        
        # ไม่ควรเสียชีวิต และควsเกาะบน platform
        game_instance.lose_life.assert_not_called()
        assert game_instance.frog.attached_to == platform
        
        # ทดสอบการหลุดจากการเกาะเมื่อออกจากโซนน้ำ
        game_instance.frog.rect.y = game_instance.road_rect.y
        game_instance.check_collisions()
        assert game_instance.frog.attached_to is None
        
    def test_drown_on_diving_turtle(self, game_instance):
        """ทดสอบการตกน้ำเมื่อเต่าดำน้ำ"""
        # หาเต่าตัวแรก
        turtle = next(p for p in game_instance.platforms if isinstance(p, Turtle))
        turtle.is_diving = True #บังคับให้เต่าดำน้ำ
        game_instance.frog.rect.center = turtle.rect.center
        
        game_instance.lose_life = MagicMock()
        game_instance.check_collisions()
        game_instance.lose_life.assert_called_once()
        
    def test_frog_off_screen(self, game_instance):
        """ทดสอบเมื่อกบตกขอบจอ"""
        game_instance.frog.rect.x = -1 # ย้ายกบออกนอกจอ
        game_instance.lose_life = MagicMock()
        game_instance.check_collisions()
        game_instance.lose_life.assert_called_once()
        
    def test_reach_empty_home(self, game_instance):
        """ทดสอบเมื่อกบเข้าบ้านที่ยังว่าง"""
        initial_score = game_instance.score
        home_index = 2
        
        # ย้ายกบไปที่บ้านหลังที่ 2
        game_instance.frog.rect.top = 0
        game_instance.frog.rect.centerx = game_instance.homes[home_index].rect.centerx
        
        game_instance.check_collisions()
        
        assert game_instance.homes_filled[home_index]
        assert game_instance.score > initial_score
        # กบควรรีเซ็ตตำแหน่ง
        assert game_instance.frog.rect.y == game_instance.frog.start_y

    def test_reach_filled_home(self, game_instance):
        """ทดสอบเมื่อกบเข้าบ้านที่เต็มแล้ว"""
        home_index = 3
        game_instance.homes_filled[home_index] = True
        
        # ย้ายกบไปที่บ้านหลังที่ 3
        game_instance.frog.rect.top = 0
        game_instance.frog.rect.centerx = game_instance.homes[home_index].rect.centerx
        
        game_instance.lose_life = MagicMock()
        game_instance.check_collisions()
        game_instance.lose_life.assert_called_once()
    
    def test_reach_wall_between_homes(self, game_instance):
        """ทดสอบเมื่อกบชนกำแพงระหว่างบ้าน (พื้นที่ที่ไม่ใช่บ้าน)"""
        # คำนวณตำแหน่งกึ่งกลางระหว่างบ้าน 2 หลังแรก
        center_x = (game_instance.homes[0].rect.right + game_instance.homes[1].rect.left) / 2
        game_instance.frog.rect.top = 0
        game_instance.frog.rect.centerx = center_x
        
        # คำนวณ home_index จากตำแหน่งนี้ ซึ่งจะไม่อยู่ในขอบเขต 0-4
        home_width = SCREEN_WIDTH // TOTAL_HOMES
        calculated_index = int(center_x // home_width)
        assert not (0 <= calculated_index < TOTAL_HOMES)

        game_instance.lose_life = MagicMock()
        game_instance.check_collisions()
        game_instance.lose_life.assert_called_once()


    def test_level_complete(self, game_instance):
        """ทดสอบเงื่อนไขการผ่านด่าน"""
        # เติมบ้านทุกหลังยกเว้นหลังสุดท้าย
        for i in range(TOTAL_HOMES - 1):
            game_instance.homes_filled[i] = True
            
        # ย้ายกบเข้าบ้านหลังสุดท้าย
        game_instance.frog.rect.top = 0
        game_instance.frog.rect.centerx = game_instance.homes[-1].rect.centerx
        
        game_instance.check_collisions()
        
        assert all(game_instance.homes_filled)
        assert game_instance.game_state == "level_complete"
        assert game_instance.score >= 1000 # ต้องได้โบนัสผ่านด่าน

    def test_time_out(self, game_instance):
        """ทดสอบเมื่อเวลาหมด"""
        # Mock `get_ticks` ให้คืนค่าที่ทำให้เวลาหมด
        with patch('pygame.time.get_ticks', return_value=game_instance.start_time + game_instance.time_limit):
            game_instance.lose_life = MagicMock()
            game_instance.check_time()
            game_instance.lose_life.assert_called_once()

    def test_no_time_out(self, game_instance):
        """ทดสอบเมื่อเวลายังไม่หมด"""
        with patch('pygame.time.get_ticks', return_value=game_instance.start_time):
             game_instance.lose_life = MagicMock()
             game_instance.check_time()
             game_instance.lose_life.assert_not_called()

    def test_lose_life_and_reset(self, game_instance):
        """ทดสอบการเสียชีวิตและรีเซ็ตตำแหน่ง"""
        initial_lives = game_instance.lives
        game_instance.frog.reset_position = MagicMock()
        
        game_instance.lose_life()
        
        assert game_instance.lives == initial_lives - 1
        game_instance.frog.reset_position.assert_called_once()
        assert game_instance.game_state == "playing"

    def test_lose_last_life_game_over(self, game_instance):
        """ทดสอบการเสียชีวิตสุดท้ายและเกมโอเวอร์"""
        game_instance.lives = 1
        game_instance.lose_life()
        assert game_instance.lives == 0
        assert game_instance.game_state == "game_over"

    def test_draw(self, game_instance):
        """ทดสอบฟังก์ชัน `draw` เพื่อให้ครอบคลุมการวาดทั้งหมด"""
        # ทดสอบการวาดสถานะปกติ
        game_instance.draw()
        game_instance.screen.fill.assert_called()
        
        # ทดสอบการวาดเมื่อบ้านเต็ม
        game_instance.homes_filled[0] = True
        game_instance.draw()
        
        # ทดสอบการวาดหน้าจอ Game Over
        game_instance.game_state = "game_over"
        game_instance.draw_overlay = MagicMock()
        game_instance.draw()
        game_instance.draw_overlay.assert_called_once_with("Game Over")
        
        # ทดสอบการวาดหน้าจอ Level Complete
        game_instance.game_state = "level_complete"
        game_instance.draw()
        game_instance.draw_overlay.assert_called_with(f"Level {game_instance.level} Complete!")

    def test_draw_ui(self, game_instance):
        """ทดสอบฟังก์ชัน `draw_ui` เพื่อให้ครอบคลุมการวาด UI"""
        # Mock blit และ draw.rect เพื่อตรวจสอบการเรียกใช้
        game_instance.screen.blit = MagicMock()
        
        with patch('pygame.draw.rect') as mock_draw:
            # ทดสอบสถานะปกติ
            game_instance.game_state = "playing"
            game_instance.draw_ui()
            assert game_instance.screen.blit.call_count == 2
            assert mock_draw.call_count == 2 # time bar bg and fill

            # ทดสอบเมื่อเวลาหมด (time_ratio <= 0)
            with patch('pygame.time.get_ticks', return_value=game_instance.start_time + game_instance.time_limit):
                mock_draw.reset_mock()
                game_instance.draw_ui()
                mock_draw.assert_not_called() # ไม่ควรวาด time bar

    def test_run_loop_and_exit(self, game_instance):
        """ทดสอบลูปหลักของเกมและการออกจากลูป"""
        # ตั้งค่าให้ `running` เป็น False หลังจากวนลูป 2 ครั้ง เพื่อให้ test จบ
        side_effects = [True, True, False]
        def mock_handle_input():
            game_instance.running = side_effects.pop(0)

        game_instance.handle_input = MagicMock(side_effect=mock_handle_input)
        game_instance.update = MagicMock()
        game_instance.draw = MagicMock()
        game_instance.clock.tick = MagicMock()
        
        # Mock sys.exit เพื่อป้องกันไม่ให้ test runner หยุดทำงาน
        with patch('sys.exit') as mock_exit:
            game_instance.run()
            # ควรจะวนลูป 2 ครั้งก่อนที่ `running` จะเป็น False
            assert game_instance.handle_input.call_count == 3
            assert game_instance.update.call_count == 2
            assert game_instance.draw.call_count == 2
            mock_exit.assert_called_once()

# Entry point สำหรับการรันเกม (เพื่อให้ coverage tool มองเห็น)
# ส่วนนี้จะไม่ถูกทดสอบโดยตรง แต่จำเป็นเพื่อให้ coverage นับรวม
def test_main_entry_point():
    """ทดสอบ entry point `if __name__ == "__main__"` """
    with patch('frogger.Game') as mock_game_class:
        # Mock instance ที่จะถูกสร้าง
        mock_game_instance = MagicMock()
        mock_game_class.return_value = mock_game_instance
        
        # ใช้ runpy เพื่อรันสคริปต์ใน context ของ `__main__`
        import runpy
        runpy.run_path('frogger.py', run_name='__main__')
        
        # ตรวจสอบว่าคลาส Game ถูกสร้าง และเมธอด run ถูกเรียก
        mock_game_class.assert_called_once()
        mock_game_instance.run.assert_called_once()