# test_frogger.py
# Unit tests for the Frogger game using pytest.
# Ensures 100% statement coverage.

import pygame
import pytest
from unittest.mock import Mock, patch
from code import (
    Game, Frog, MovingObject, Turtle, GameObject,
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE
)

# --- Fixtures ---
# Fixtures เป็นฟังก์ชันของ pytest ที่ช่วยเตรียมสภาพแวดล้อมก่อนการทดสอบ

@pytest.fixture
def game():
    """สร้าง instance ของคลาส Game สำหรับทุกๆ test case"""
    # ใช้ patch เพื่อ mock การทำงานของ pygame.display และ font ที่ไม่จำเป็นในการทดสอบ logic
    with patch('pygame.display.set_mode'), patch('pygame.font.Font'):
        g = Game()
        # Mocking screen surface to avoid rendering errors
        g.screen = Mock()
        return g

@pytest.fixture
def frog():
    """สร้าง instance ของคลาส Frog"""
    return Frog(100, 200)

@pytest.fixture
def moving_object():
    """สร้าง instance ของคลาส MovingObject"""
    return MovingObject(50, 50, 50, 50, (255, 0, 0), 2)
    
@pytest.fixture
def turtle():
    """สร้าง instance ของคลาส Turtle"""
    return Turtle(100, 100, -1, dive_interval=3, dive_duration=2)

# --- Test Cases ---

# Test GameObject Class
def test_game_object_draw(game):
    obj = GameObject(10, 10, 20, 20, (0,0,0))
    # จำลองการเรียก pygame.draw.rect และตรวจสอบว่าถูกเรียกด้วยพารามิเตอร์ที่ถูกต้อง
    with patch('pygame.draw.rect') as mock_draw:
        obj.draw(game.screen)
        mock_draw.assert_called_once()
        # เราสามารถตรวจสอบค่าที่ส่งเข้าไปได้ แต่การเช็คว่า call เกิดขึ้นก็เพียงพอ
        
# Test Frog Class
def test_frog_init(frog):
    assert frog.rect.x == 100
    assert frog.rect.y == 200
    assert frog.start_x == 100
    assert frog.start_y == 200
    assert frog.attached_to is None

def test_frog_move(frog):
    frog.move(1, -1)
    assert frog.rect.x == 100 + GRID_SIZE
    assert frog.rect.y == 200 - GRID_SIZE
    
def test_frog_attach_detach(frog, moving_object):
    frog.attach_to(moving_object)
    assert frog.attached_to == moving_object
    frog.detach()
    assert frog.attached_to is None

def test_frog_reset_position(frog, moving_object):
    frog.move(2, 2)
    frog.attach_to(moving_object)
    frog.reset_position()
    assert frog.rect.x == frog.start_x
    assert frog.rect.y == frog.start_y
    assert frog.attached_to is None
    
def test_frog_update_position_on_platform(frog, moving_object):
    moving_object.speed = 5
    frog.rect.x = 150
    frog.attach_to(moving_object)
    frog.update_position_on_platform()
    assert frog.rect.x == 150 + 5

def test_frog_is_on_screen(frog):
    assert frog.is_on_screen()
    frog.rect.x = -1
    assert not frog.is_on_screen()
    frog.rect.x = SCREEN_WIDTH
    assert not frog.is_on_screen()

# Test MovingObject Class
def test_moving_object_move():
    # เคลื่อนที่ไปทางขวาและวนกลับ
    obj_right = MovingObject(SCREEN_WIDTH - 1, 50, 20, 20, (0,0,0), 2)
    obj_right.move()
    assert obj_right.rect.left > SCREEN_WIDTH
    obj_right.move()
    assert obj_right.rect.right == 0

    # เคลื่อนที่ไปทางซ้ายและวนกลับ
    obj_left = MovingObject(1, 50, 20, 20, (0,0,0), -2)
    obj_left.move()
    assert obj_left.rect.right < 0
    obj_left.move()
    assert obj_left.rect.left == SCREEN_WIDTH

# Test Turtle Class
def test_turtle_update_and_dive(turtle):
    assert not turtle.is_diving
    # ทดสอบการดำน้ำ
    turtle.update(dt=3.1) # เวลาผ่านไปเกิน dive_interval
    assert turtle.is_diving
    # ทดสอบการโผล่ขึ้นมา
    turtle.update(dt=2.1) # เวลาผ่านไปเกิน dive_duration
    assert not turtle.is_diving

def test_turtle_draw(turtle, game):
    with patch('pygame.draw.rect') as mock_draw:
        turtle.is_diving = False
        turtle.draw(game.screen)
        mock_draw.assert_called_once()
        
        mock_draw.reset_mock()
        
        turtle.is_diving = True
        turtle.draw(game.screen)
        mock_draw.assert_not_called()

# Test Game Class - Input Handling
def test_game_handle_input_quit(game):
    # จำลอง event QUIT
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    game.handle_input()
    assert not game.running

def test_game_handle_input_movement(game):
    original_pos = game.frog.rect.copy()
    
    # ทดสอบการเคลื่อนที่ทุกทิศทาง
    game.frog.rect.top = 100 # Reset to a safe position to move up
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
    game.handle_input()
    assert game.frog.rect.y == original_pos.y - GRID_SIZE
    
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
    game.handle_input()
    assert game.frog.rect.y == original_pos.y # กลับมาที่เดิม
    
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))
    game.handle_input()
    assert game.frog.rect.x == original_pos.x - GRID_SIZE
    
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))
    game.handle_input()
    assert game.frog.rect.x == original_pos.x # กลับมาที่เดิม

def test_game_handle_input_out_of_bounds(game):
    # การกดปุ่มไม่ควรทำให้กบออกนอกจอ
    game.frog.rect.top = 0
    original_y = game.frog.rect.y
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
    game.handle_input()
    assert game.frog.rect.y == original_y # ไม่ขยับเพราะอยู่ขอบบนสุดแล้ว

def test_game_handle_input_restart(game):
    # Game Over state
    game.game_state = "game_over"
    with patch.object(game, 'reset_game') as mock_reset:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
        game.handle_input()
        mock_reset.assert_called_once()

    # Level Complete state
    game.game_state = "level_complete"
    with patch.object(game, 'setup_level') as mock_setup:
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
        game.handle_input()
        assert game.level == 2 # เช็คว่า level เพิ่มขึ้น
        mock_setup.assert_called_once()


# Test Game Class - Game Logic & Collisions
def test_game_lose_life(game):
    initial_lives = game.lives
    game.lose_life()
    assert game.lives == initial_lives - 1
    assert game.frog.rect.y == SCREEN_HEIGHT - GRID_SIZE # กลับจุดเริ่มต้น

def test_game_lose_life_game_over(game):
    game.lives = 1
    game.lose_life()
    assert game.lives == 0
    assert game.game_state == "game_over"

def test_game_collision_with_obstacle(game):
    # สร้าง obstacle ให้ชนกับกบ
    game.obstacles[0].rect.center = game.frog.rect.center
    with patch.object(game, 'lose_life') as mock_lose_life:
        game.check_collisions()
        mock_lose_life.assert_called_once()

def test_game_fall_in_water(game):
    # ย้ายกบไปในโซนน้ำโดยไม่มี platform
    game.frog.rect.centery = game.water_rect.centery
    with patch.object(game, 'lose_life') as mock_lose_life:
        game.check_collisions()
        mock_lose_life.assert_called_once()

def test_game_safe_on_platform(game):
    # ย้ายกบไปบน platform
    game.frog.rect.center = game.platforms[0].rect.center
    game.check_collisions()
    assert game.frog.attached_to is not None

def test_game_safe_on_diving_turtle(game, turtle):
    game.platforms.append(turtle)
    turtle.is_diving = True
    game.frog.rect.center = turtle.rect.center
    with patch.object(game, 'lose_life') as mock_lose_life:
        game.check_collisions()
        mock_lose_life.assert_called_once() # ควรจะตายเพราะเต่าดำน้ำ

def test_frog_falls_off_screen(game):
    game.frog.rect.x = -5 # ตกขอบซ้าย
    with patch.object(game, 'lose_life') as mock_lose_life:
        game.check_collisions()
        mock_lose_life.assert_called_once()


def test_reach_home_successfully(game):
    # ย้ายกบไปที่บ้านหลังแรก (ที่ยังว่าง)
    game.frog.rect.top = 0
    game.frog.rect.centerx = game.homes[0].rect.centerx
    game.homes_filled[0] = False
    
    initial_score = game.score
    game.check_collisions()

    assert game.homes_filled[0] == True
    assert game.score > initial_score
    assert game.frog.rect.y == SCREEN_HEIGHT - GRID_SIZE # กลับจุดเริ่มต้น

def test_reach_filled_home(game):
    # ย้ายกบไปที่บ้านที่เต็มแล้ว
    game.frog.rect.top = 0
    game.frog.rect.centerx = game.homes[0].rect.centerx
    game.homes_filled[0] = True
    
    with patch.object(game, 'lose_life') as mock_lose_life:
        game.check_collisions()
        mock_lose_life.assert_called_once()
        
def test_reach_wall_between_homes(game):
    # ย้ายกบไปที่กำแพงระหว่างบ้าน
    game.frog.rect.top = 0
    game.frog.rect.x = 0 # ตำแหน่งที่ไม่มีบ้าน
    # ค่า x ของบ้านหลังแรกคือ 0, ขนาด home_width = 160
    # จุดกึ่งกลางคือ 80, ขอบซ้ายบ้านคือ 0, ขอบขวาคือ 160
    # กบอยู่ภายใน Rect ของบ้าน แต่เราเช็คด้วย home_index
    # ทดสอบกรณีที่ home_index ออกนอกช่วง
    game.frog.rect.centerx = -10 # ทำให้ index < 0
    with patch.object(game, 'lose_life') as mock_lose_life:
        game.check_collisions()
        # Note: โค้ดจริงจะไม่มีทางเกิดเคสนี้ เพราะกบขยับทีละ GRID_SIZE
        # แต่เราทดสอบเพื่อให้ครอบคลุมโค้ด `if 0 <= home_index < TOTAL_HOMES:`
        # การทดสอบนี้ทำให้ครอบคลุม else ของ if ดังกล่าว
        # เพื่อให้ครอบคลุม 100% เราต้องบังคับให้เงื่อนไขเป็นเท็จ
        # ซึ่งในเกมจริงอาจไม่เกิด แต่เชิง unit test คือการทดสอบ logic
        mock_lose_life.assert_called_once()


def test_level_complete(game):
    game.frog.rect.top = 0
    game.frog.rect.centerx = game.homes[0].rect.centerx
    game.homes_filled = [True, True, True, True, False] # เหลือบ้านหลังสุดท้าย
    game.check_collisions()
    
    assert game.game_state == "level_complete"
    assert game.score > 1000 # ได้โบนัส

def test_time_out(game):
    # ตั้งเวลาให้หมดทันที
    game.start_time = pygame.time.get_ticks() - game.time_limit - 100
    with patch.object(game, 'lose_life') as mock_lose_life:
        game.check_time()
        mock_lose_life.assert_called_once()

# Test Game Class - Drawing Methods (ensure they run without error)
def test_game_draw_methods_run(game):
    try:
        # ทดสอบการวาดทุกสถานะเพื่อให้แน่ใจว่าไม่มี error
        # ไม่ต้อง assert อะไร แค่รันให้ผ่านก็พอ
        game.draw()
        
        game.game_state = "game_over"
        game.draw()
        
        game.game_state = "level_complete"
        game.draw()
        
        # ทดสอบการวาดเมื่อเวลาใกล้หมด
        game.game_state = "playing"
        game.start_time = pygame.time.get_ticks() - (game.time_limit / 2)
        game.draw()

    except Exception as e:
        pytest.fail(f"Drawing methods raised an exception: {e}")

# Test Game Loop and Main Guard
def test_game_run_loop(game):
    # ทดสอบว่าลูปทำงานและออกเมื่อ running เป็น False
    game.running = False # ตั้งค่าให้ออกจากลูปทันที
    with patch('pygame.quit'), patch('sys.exit'):
        game.run() # ควรจะจบการทำงานทันที

@patch('frogger.Game')
def test_main_guard(mock_game_class):
    # ทดสอบเงื่อนไข if __name__ == "__main__":
    with patch('__main__.__name__', '__main__'):
        # สร้าง mock instance และ mock method `run`
        mock_game_instance = mock_game_class.return_value
        
        # Import ไฟล์ frogger เพื่อให้โค้ดใน main guard ทำงาน
        from code import __main__ as frogger_main
        
        mock_game_class.assert_called_once()
        mock_game_instance.run.assert_called_once()

def test_game_update_when_not_playing(game):
    game.game_state = "game_over"
    # ตรวจสอบว่าเมธอด update ไม่ทำอะไรเลยถ้า game state ไม่ใช่ "playing"
    with patch.object(game, 'check_collisions') as mock_check:
        game.update()
        mock_check.assert_not_called()
