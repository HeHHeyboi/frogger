"""
Unit Tests for Frogger Game
===========================
ทดสอบทุก component ของเกม Frogger เพื่อให้ได้ coverage 100%
"""

import pytest
import pygame
from unittest.mock import Mock, patch, MagicMock
from frogger import (
    GameObject, Frog, Vehicle, Log, Turtle, Home,
    GameState, FroggerGame, Direction, Colors,
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, FPS
)


class TestColors:
    """ทดสอบค่าสีต่างๆ"""
    
    def test_colors_defined(self):
        """ทดสอบว่ามีการกำหนดสีครบถ้วน"""
        assert Colors.BLACK == (0, 0, 0)
        assert Colors.WHITE == (255, 255, 255)
        assert Colors.GREEN == (0, 255, 0)
        assert Colors.BLUE == (0, 0, 255)
        assert Colors.RED == (255, 0, 0)
        assert Colors.YELLOW == (255, 255, 0)
        assert Colors.BROWN == (139, 69, 19)
        assert Colors.GRAY == (128, 128, 128)
        assert Colors.DARK_GREEN == (0, 128, 0)
        assert Colors.LIGHT_BLUE == (173, 216, 230)


class TestDirection:
    """ทดสอบ Direction Enum"""
    
    def test_direction_values(self):
        """ทดสอบค่าทิศทาง"""
        assert Direction.UP.value == (0, -1)
        assert Direction.DOWN.value == (0, 1)
        assert Direction.LEFT.value == (-1, 0)
        assert Direction.RIGHT.value == (1, 0)


class TestGameObject:
    """ทดสอบคลาส GameObject พื้นฐาน"""
    
    def test_game_object_init(self):
        """ทดสอบการสร้าง GameObject"""
        obj = GameObject(10, 20, 30, 40, Colors.RED)
        assert obj.x == 10
        assert obj.y == 20
        assert obj.width == 30
        assert obj.height == 40
        assert obj.color == Colors.RED
        assert obj.rect.x == 10
        assert obj.rect.y == 20
    
    def test_update_rect(self):
        """ทดสอบการอัปเดต rect"""
        obj = GameObject(10, 20, 30, 40, Colors.RED)
        obj.x = 50
        obj.y = 60
        obj.update_rect()
        assert obj.rect.x == 50
        assert obj.rect.y == 60
    
    def test_draw(self):
        """ทดสอบการวาดวัตถุ"""
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        obj = GameObject(10, 20, 30, 40, Colors.RED)
        
        # ควรไม่เกิด error
        obj.draw(screen)
        pygame.quit()
    
    def test_get_center(self):
        """ทดสอบการหาจุดกึ่งกลาง"""
        obj = GameObject(10, 20, 30, 40, Colors.RED)
        center_x, center_y = obj.get_center()
        assert center_x == 25  # 10 + 30//2
        assert center_y == 40  # 20 + 40//2


class TestFrog:
    """ทดสอบคลาส Frog"""
    
    def test_frog_init(self):
        """ทดสอบการสร้างกบ"""
        frog = Frog(100, 200)
        assert frog.x == 100
        assert frog.y == 200
        assert frog.start_x == 100
        assert frog.start_y == 200
        assert frog.on_log == False
        assert frog.log_speed == 0
        assert frog.width == GRID_SIZE - 4
        assert frog.height == GRID_SIZE - 4
    
    def test_frog_move_up(self):
        """ทดสอบการเคลื่อนที่ขึ้น"""
        frog = Frog(100, 200)
        result = frog.move(Direction.UP)
        assert result == True
        assert frog.y == 200 - GRID_SIZE
    
    def test_frog_move_down(self):
        """ทดสอบการเคลื่อนที่ลง"""
        frog = Frog(100, 200)
        result = frog.move(Direction.DOWN)
        assert result == True
        assert frog.y == 200 + GRID_SIZE
    
    def test_frog_move_left(self):
        """ทดสอบการเคลื่อนที่ซ้าย"""
        frog = Frog(100, 200)
        result = frog.move(Direction.LEFT)
        assert result == True
        assert frog.x == 100 - GRID_SIZE
    
    def test_frog_move_right(self):
        """ทดสอบการเคลื่อนที่ขวา"""
        frog = Frog(100, 200)
        result = frog.move(Direction.RIGHT)
        assert result == True
        assert frog.x == 100 + GRID_SIZE
    
    def test_frog_move_out_of_bounds_left(self):
        """ทดสอบการเคลื่อนที่เกินขอบซ้าย"""
        frog = Frog(0, 200)
        result = frog.move(Direction.LEFT)
        assert result == False
        assert frog.x == 0
    
    def test_frog_move_out_of_bounds_right(self):
        """ทดสอบการเคลื่อนที่เกินขอบขวา"""
        # First, create the frog at a temporary position
        frog = Frog(0, 200)
        
        # Now that the frog exists, set its x position to the right edge
        frog.x = SCREEN_WIDTH - frog.width
        
        # Perform the move and assert the results
        result = frog.move(Direction.RIGHT)
        assert result == False
        assert frog.x == SCREEN_WIDTH - frog.width # Also check that its position didn't change
    
    def test_frog_move_out_of_bounds_top(self):
        """ทดสอบการเคลื่อนที่เกินขอบบน"""
        frog = Frog(100, 0)
        result = frog.move(Direction.UP)
        assert result == False
        assert frog.y == 0
    
    def test_frog_move_out_of_bounds_bottom(self):
        """ทดสอบการเคลื่อนที่เกินขอบล่าง"""
        # Create the frog at a temporary position first
        frog = Frog(100, 200)
        
        # Now, set its y position to the very bottom of the screen
        frog.y = SCREEN_HEIGHT - frog.height
        
        # Perform the move and check the results
        result = frog.move(Direction.DOWN)
        assert result == False
        assert frog.y == SCREEN_HEIGHT - frog.height # Good to also check it didn't move
    
    def test_frog_reset_position(self):
        """ทดสอบการรีเซ็ตตำแหน่ง"""
        frog = Frog(100, 200)
        frog.move(Direction.UP)
        frog.move(Direction.LEFT)
        frog.on_log = True
        frog.log_speed = 5
        
        frog.reset_position()
        
        assert frog.x == 100
        assert frog.y == 200
        assert frog.on_log == False
        assert frog.log_speed == 0
    
    def test_frog_update_on_log_when_on_log(self):
        """ทดสอบการอัปเดตตำแหน่งเมื่ออยู่บนขอนไม้"""
        frog = Frog(100, 200)
        frog.on_log = True
        frog.update_on_log(5)
        assert frog.x == 105
    
    def test_frog_update_on_log_when_not_on_log(self):
        """ทดสอบการอัปเดตเมื่อไม่ได้อยู่บนขอนไม้"""
        frog = Frog(100, 200)
        frog.on_log = False
        frog.update_on_log(5)
        assert frog.x == 100
    
    def test_frog_update_on_log_boundary_left(self):
        """ทดสอบการอัปเดตเมื่อเกินขอบซ้าย"""
        frog = Frog(5, 200)
        frog.on_log = True
        frog.update_on_log(-10)
        assert frog.x == 0
    
    def test_frog_update_on_log_boundary_right(self):
        """ทดสอบการอัปเดตเมื่อเกินขอบขวา"""
        frog = Frog(SCREEN_WIDTH - 10, 200)
        frog.on_log = True
        frog.update_on_log(20)
        assert frog.x == SCREEN_WIDTH - frog.width


class TestVehicle:
    """ทดสอบคลาส Vehicle"""
    
    def test_vehicle_init(self):
        """ทดสอบการสร้างยานพาหนะ"""
        vehicle = Vehicle(100, 200, 3, Colors.RED)
        assert vehicle.x == 100
        assert vehicle.y == 200
        assert vehicle.speed == 3
        assert vehicle.color == Colors.RED
    
    def test_vehicle_update_moving_right(self):
        """ทดสอบการเคลื่อนที่ไปทางขวา"""
        vehicle = Vehicle(100, 200, 3, Colors.RED)
        vehicle.update()
        assert vehicle.x == 103
    
    def test_vehicle_update_moving_left(self):
        """ทดสอบการเคลื่อนที่ไปทางซ้าย"""
        vehicle = Vehicle(100, 200, -3, Colors.RED)
        vehicle.update()
        assert vehicle.x == 97
    
    def test_vehicle_wrap_around_right(self):
        """ทดสอบการวนกลับเมื่อออกจากขอบขวา"""
        vehicle = Vehicle(SCREEN_WIDTH + 10, 200, 3, Colors.RED)
        vehicle.update()
        assert vehicle.x == -vehicle.width
    
    def test_vehicle_wrap_around_left(self):
        """ทดสอบการวนกลับเมื่อออกจากขอบซ้าย"""
        vehicle = Vehicle(-100, 200, -3, Colors.RED)
        vehicle.update()
        assert vehicle.x == SCREEN_WIDTH


class TestLog:
    """ทดสอบคลาส Log"""
    
    def test_log_init(self):
        """ทดสอบการสร้างขอนไม้"""
        log = Log(100, 200, 2, 3)
        assert log.x == 100
        assert log.y == 200
        assert log.speed == 2
        assert log.length == 3
        assert log.width == 3 * GRID_SIZE
    
    def test_log_init_default_length(self):
        """ทดสอบการสร้างขอนไม้ด้วยความยาวเริ่มต้น"""
        log = Log(100, 200, 2)
        assert log.length == 2
        assert log.width == 2 * GRID_SIZE
    
    def test_log_update_moving_right(self):
        """ทดสอบการเคลื่อนที่ไปทางขวา"""
        log = Log(100, 200, 2, 3)
        log.update()
        assert log.x == 102
    
    def test_log_update_moving_left(self):
        """ทดสอบการเคลื่อนที่ไปทางซ้าย"""
        log = Log(100, 200, -2, 3)
        log.update()
        assert log.x == 98
    
    def test_log_wrap_around_right(self):
        """ทดสอบการวนกลับเมื่อออกจากขอบขวา"""
        log = Log(SCREEN_WIDTH + 10, 200, 2, 3)
        log.update()
        assert log.x == -log.width
    
    def test_log_wrap_around_left(self):
        """ทดสอบการวนกลับเมื่อออกจากขอบซ้าย"""
        log = Log(-200, 200, -2, 3)
        log.update()
        assert log.x == SCREEN_WIDTH


class TestTurtle:
    """ทดสอบคลาส Turtle"""
    
    def test_turtle_init(self):
        """ทดสอบการสร้างเต่า"""
        turtle = Turtle(100, 200, 2)
        assert turtle.x == 100
        assert turtle.y == 200
        assert turtle.speed == 2
        assert turtle.is_diving == False
        assert 180 <= turtle.dive_timer <= 300
    
    def test_turtle_update_moving(self):
        """ทดสอบการเคลื่อนที่ของเต่า"""
        turtle = Turtle(100, 200, 2)
        initial_timer = turtle.dive_timer
        turtle.update()
        assert turtle.x == 102
        assert turtle.dive_timer == initial_timer - 1
    
    def test_turtle_wrap_around_right(self):
        """ทดสอบการวนกลับเมื่อออกจากขอบขวา"""
        turtle = Turtle(SCREEN_WIDTH + 10, 200, 2)
        turtle.update()
        assert turtle.x == -turtle.width
    
    def test_turtle_wrap_around_left(self):
        """ทดสอบการวนกลับเมื่อออกจากขอบซ้าย"""
        turtle = Turtle(-100, 200, -2)
        turtle.update()
        assert turtle.x == SCREEN_WIDTH
    
    def test_turtle_start_diving(self):
        """ทดสอบการเริ่มดำน้ำ"""
        turtle = Turtle(100, 200, 2)
        turtle.dive_timer = 1
        turtle.is_diving = False
        
        turtle.update()
        
        assert turtle.is_diving == True
        assert turtle.dive_timer == turtle.dive_duration
    
    def test_turtle_finish_diving(self):
        """ทดสอบการกลับขึ้นจากการดำน้ำ"""
        turtle = Turtle(100, 200, 2)
        turtle.dive_timer = 1
        turtle.is_diving = True
        
        turtle.update()
        
        assert turtle.is_diving == False
        assert 180 <= turtle.dive_timer <= 300
    
    def test_turtle_draw_not_diving(self):
        """ทดสอบการวาดเต่าเมื่อไม่ได้ดำน้ำ"""
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        turtle = Turtle(100, 200, 2)
        turtle.is_diving = False
        
        # ควรวาดได้โดยไม่มี error
        turtle.draw(screen)
        pygame.quit()
    
    def test_turtle_draw_diving(self):
        """ทดสอบการวาดเต่าเมื่อกำลังดำน้ำ"""
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        turtle = Turtle(100, 200, 2)
        turtle.is_diving = True
        
        # ควรไม่วาดแต่ไม่มี error
        turtle.draw(screen)
        pygame.quit()


class TestHome:
    """ทดสอบคลาส Home"""
    
    def test_home_init(self):
        """ทดสอบการสร้างบ้าน"""
        home = Home(100, 200)
        assert home.x == 100
        assert home.y == 200
        assert home.occupied == False
        assert home.color == Colors.YELLOW
    
    def test_home_draw_unoccupied(self):
        """ทดสอบการวาดบ้านที่ว่าง"""
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        home = Home(100, 200)
        home.occupied = False
        
        home.draw(screen)
        pygame.quit()
    
    def test_home_draw_occupied(self):
        """ทดสอบการวาดบ้านที่ถูกครอบครอง"""
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        home = Home(100, 200)
        home.occupied = True
        
        home.draw(screen)
        pygame.quit()


class TestGameState:
    """ทดสอบคลาส GameState"""
    
    def test_game_state_init(self):
        """ทดสอบการสร้าง GameState"""
        state = GameState()
        assert state.lives == 3
        assert state.score == 0
        assert state.level == 1
        assert state.time_left == 30.0
        assert state.game_over == False
        assert state.level_complete == False
        assert state.homes_filled == 0


class TestFroggerGame:
    """ทดสอบคลาสหลัก FroggerGame"""
    
    @pytest.fixture
    def game(self):
        """สร้างเกมสำหรับทดสอบ"""
        pygame.init()
        game = FroggerGame()
        yield game
        pygame.quit()
    
    def test_game_init(self, game):
        """ทดสอบการสร้างเกม"""
        assert game.running == True
        assert game.game_state.lives == 3
        assert game.game_state.score == 0
        assert game.frog is not None
        assert len(game.vehicles) > 0
        assert len(game.logs) > 0
        assert len(game.turtles) > 0
        assert len(game.homes) == 5
    
    def test_create_vehicles(self, game):
        """ทดสอบการสร้างยานพาหนะ"""
        assert len(game.vehicles) > 0
        for vehicle in game.vehicles:
            assert isinstance(vehicle, Vehicle)
    
    def test_create_river_objects(self, game):
        """ทดสอบการสร้างวัตถุในแม่น้ำ"""
        assert len(game.logs) > 0
        assert len(game.turtles) > 0
        
        for log in game.logs:
            assert isinstance(log, Log)
        
        for turtle in game.turtles:
            assert isinstance(turtle, Turtle)
    
    def test_create_homes(self, game):
        """ทดสอบการสร้างบ้าน"""
        assert len(game.homes) == 5
        
        for home in game.homes:
            assert isinstance(home, Home)
            assert home.occupied == False
    
    def test_handle_input_quit(self, game):
        """ทดสอบการปิดเกม"""
        with patch('pygame.event.get') as mock_event:
            mock_event.return_value = [Mock(type=pygame.QUIT)]
            result = game.handle_input()
            assert result == False
    
    def test_handle_input_move_up(self, game):
        """ทดสอบการกดปุ่มขึ้น"""
        initial_y = game.frog.y
        
        with patch('pygame.event.get') as mock_event:
            mock_event.return_value = [Mock(type=pygame.KEYDOWN, key=pygame.K_UP)]
            game.handle_input()
            
            assert game.frog.y == initial_y - GRID_SIZE
    
    def test_handle_input_move_down(self, game):
        """ทดสอบการกดปุ่มลง"""
        initial_y = game.frog.y
        
        with patch('pygame.event.get') as mock_event:
            mock_event.return_value = [Mock(type=pygame.KEYDOWN, key=pygame.K_DOWN)]
            game.handle_input()
            
            # อาจจะเกินขอบล่าง
            assert game.frog.y >= initial_y
    
    def test_handle_input_move_left(self, game):
        """ทดสอบการกดปุ่มซ้าย"""
        initial_x = game.frog.x
        
        with patch('pygame.event.get') as mock_event:
            mock_event.return_value = [Mock(type=pygame.KEYDOWN, key=pygame.K_LEFT)]
            game.handle_input()
            
            assert game.frog.x == initial_x - GRID_SIZE
    
    def test_handle_input_move_right(self, game):
        """ทดสอบการกดปุ่มขวา"""
        initial_x = game.frog.x
        
        with patch('pygame.event.get') as mock_event:
            mock_event.return_value = [Mock(type=pygame.KEYDOWN, key=pygame.K_RIGHT)]
            game.handle_input()
            
            assert game.frog.x == initial_x + GRID_SIZE
    
    def test_handle_input_restart_on_game_over(self, game):
        """ทดสอบการกด R เมื่อเกมจบ"""
        game.game_state.game_over = True
        
        with patch('pygame.event.get') as mock_event:
            mock_event.return_value = [Mock(type=pygame.KEYDOWN, key=pygame.K_r)]
            game.handle_input()
            
            assert game.game_state.game_over == False
            assert game.game_state.lives == 3
    
    def test_handle_input_restart_on_level_complete(self, game):
        """ทดสอบการกด R เมื่อจบด่าน"""
        game.game_state.level_complete = True
        
        with patch('pygame.event.get') as mock_event:
            mock_event.return_value = [Mock(type=pygame.KEYDOWN, key=pygame.K_r)]
            game.handle_input()
            
            assert game.game_state.level_complete == False
    
    def test_handle_input_no_move_when_game_over(self, game):
        """ทดสอบว่าไม่สามารถเคลื่อนที่ได้เมื่อเกมจบ"""
        game.game_state.game_over = True
        initial_y = game.frog.y
        
        with patch('pygame.event.get') as mock_event:
            mock_event.return_value = [Mock(type=pygame.KEYDOWN, key=pygame.K_UP)]
            game.handle_input()
            
            assert game.frog.y == initial_y
    
    def test_handle_input_no_move_when_level_complete(self, game):
        """ทดสอบว่าไม่สามารถเคลื่อนที่ได้เมื่อจบด่าน"""
        game.game_state.level_complete = True
        initial_y = game.frog.y
        
        with patch('pygame.event.get') as mock_event:
            mock_event.return_value = [Mock(type=pygame.KEYDOWN, key=pygame.K_UP)]
            game.handle_input()
            
            assert game.frog.y == initial_y
    
    def test_update_game_logic_when_game_over(self, game):
        """ทดสอบว่าไม่อัปเดตตรรกะเมื่อเกมจบ"""
        game.game_state.game_over = True
        initial_time = game.game_state.time_left
        
        game.update_game_logic()
        
        assert game.game_state.time_left == initial_time
    
    def test_update_game_logic_when_level_complete(self, game):
        """ทดสอบว่าไม่อัปเดตตรรกะเมื่อจบด่าน"""
        game.game_state.level_complete = True
        initial_time = game.game_state.time_left
        
        game.update_game_logic()
        
        assert game.game_state.time_left == initial_time
    
    def test_update_game_logic_time_decrease(self, game):
        """ทดสอบการลดลงของเวลา"""
        initial_time = game.game_state.time_left
        
        game.update_game_logic()
        
        assert game.game_state.time_left < initial_time
    
    def test_update_game_logic_time_out(self, game):
        """ทดสอบการหมดเวลา"""
        game.game_state.time_left = 0
        initial_lives = game.game_state.lives
        
        game.update_game_logic()
        
        assert game.game_state.lives == initial_lives - 1
    
    def test_check_vehicle_collision(self, game):
        """ทดสอบการชนกับรถ"""
        # วางกบให้ชนกับรถ
        vehicle = game.vehicles[0]
        game.frog.x = vehicle.x
        game.frog.y = vehicle.y
        game.frog.update_rect()
        
        initial_lives = game.game_state.lives
        
        game._check_vehicle_collision()
        
        assert game.game_state.lives == initial_lives - 1
    
    def test_check_water_collision_on_log(self, game):
        """ทดสอบการอยู่บนขอนไม้"""
        log = game.logs[0]
        game.frog.x = log.x + 10
        game.frog.y = log.y
        game.frog.update_rect()
        
        game._check_water_collision()
        
        assert game.frog.on_log == True
    
    def test_check_water_collision_on_turtle(self, game):
        """ทดสอบการอยู่บนเต่า"""
        turtle = game.turtles[0]
        turtle.is_diving = False
        game.frog.x = turtle.x
        game.frog.y = turtle.y
        game.frog.update_rect()
        
        game._check_water_collision()
        
        assert game.frog.on_log == True
    
    def test_check_water_collision_drowning(self, game):
        """ทดสอบการจมน้ำ"""
        # วางกบในแม่น้ำโดยไม่มีขอนไม้หรือเต่า
        game.frog.y = 100
        game.frog.x = 10
        game.frog.update_rect()
        
        initial_lives = game.game_state.lives
        
        game._check_water_collision()
        
        assert game.game_state.lives == initial_lives - 1
    
    def test_check_water_collision_not_in_water(self, game):
        """ทดสอบการไม่อยู่ในแม่น้ำ"""
        game.frog.y = 400  # โซนปลอดภัย
        game.frog.on_log = True
        game.frog.update_rect()
        
        game._check_water_collision()
        
        assert game.frog.on_log == False
    
    def test_check_home_collision_success(self, game):
        """ทดสอบการเข้าบ้านสำเร็จ"""
        home = game.homes[0]
        game.frog.x = home.x
        game.frog.y = home.y
        game.frog.update_rect()
        
        initial_score = game.game_state.score
        
        game._check_home_collision()
        
        assert home.occupied == True
        assert game.game_state.homes_filled == 1
        assert game.game_state.score > initial_score
    
    def test_check_home_collision_already_occupied(self, game):
        """ทดสอบการเข้าบ้านที่ถูกครอบครองแล้ว"""
        home = game.homes[0]
        home.occupied = True
        
        game.frog.x = home.x
        game.frog.y = home.y
        game.frog.update_rect()
        
        initial_homes = game.game_state.homes_filled
        
        game._check_home_collision()
        
        assert game.game_state.homes_filled == initial_homes
    
    def test_check_home_collision_level_complete(self, game):
        """ทดสอบการจบด่านเมื่อบ้านเต็ม"""
        # ทำให้บ้าน 4 ช่องเต็ม
        for i in range(4):
            game.homes[i].occupied = True
        game.game_state.homes_filled = 4
        
        # เข้าบ้านช่องสุดท้าย
        home = game.homes[4]
        game.frog.x = home.x
        game.frog.y = home.y