"""
Unit Tests for Frogger Game
ทดสอบทุก class และ method เพื่อให้ได้ coverage 100%
"""

import pytest
import pygame
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Import the game module
# สมมติว่าโค้ดเกมอยู่ในไฟล์ชื่อ frogger_game.py
# แก้ไข import path ตามโครงสร้างโปรเจคของคุณ

# Mock pygame before importing the game
sys.modules['pygame'] = MagicMock()
sys.modules['pygame.display'] = MagicMock()
sys.modules['pygame.font'] = MagicMock()

# จำลอง pygame constants
pygame.QUIT = 0
pygame.KEYDOWN = 1
pygame.K_UP = 2
pygame.K_DOWN = 3
pygame.K_LEFT = 4
pygame.K_RIGHT = 5
pygame.K_r = 6

# สร้าง mock Rect class
class MockRect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def colliderect(self, other):
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)

pygame.Rect = MockRect
pygame.Surface = MagicMock

# Now import game classes after mocking pygame
from frogger_game import (
    Colors, Direction, GameObject, Frog, Vehicle, Log, 
    Turtle, Home, GameState, FroggerGame,
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, FPS
)


class TestColors:
    """ทดสอบ Colors class"""
    
    def test_color_values(self):
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
    """ทดสอบ Direction enum"""
    
    def test_direction_values(self):
        assert Direction.UP.value == (0, -1)
        assert Direction.DOWN.value == (0, 1)
        assert Direction.LEFT.value == (-1, 0)
        assert Direction.RIGHT.value == (1, 0)


class TestGameObject:
    """ทดสอบ GameObject class"""
    
    def test_init(self):
        obj = GameObject(10, 20, 30, 40, Colors.RED)
        assert obj.x == 10
        assert obj.y == 20
        assert obj.width == 30
        assert obj.height == 40
        assert obj.color == Colors.RED
        assert obj.rect.x == 10
        assert obj.rect.y == 20
    
    def test_update_rect(self):
        obj = GameObject(10, 20, 30, 40, Colors.RED)
        obj.x = 50
        obj.y = 60
        obj.update_rect()
        assert obj.rect.x == 50
        assert obj.rect.y == 60
    
    def test_draw(self):
        obj = GameObject(10, 20, 30, 40, Colors.RED)
        mock_screen = Mock()
        with patch('pygame.draw.rect') as mock_draw:
            obj.draw(mock_screen)
            mock_draw.assert_called_once()
    
    def test_get_center(self):
        obj = GameObject(10, 20, 30, 40, Colors.RED)
        center = obj.get_center()
        assert center == (25, 40)


class TestFrog:
    """ทดสอบ Frog class"""
    
    def test_init(self):
        frog = Frog(100, 200)
        assert frog.start_x == 100
        assert frog.start_y == 200
        assert frog.x == 100
        assert frog.y == 200
        assert frog.on_log == False
        assert frog.log_speed == 0
    
    def test_move_up_success(self):
        frog = Frog(100, 200)
        result = frog.move(Direction.UP)
        assert result == True
        assert frog.y == 200 - GRID_SIZE
    
    def test_move_down_success(self):
        frog = Frog(100, 200)
        result = frog.move(Direction.DOWN)
        assert result == True
        assert frog.y == 200 + GRID_SIZE
    
    def test_move_left_success(self):
        frog = Frog(100, 200)
        result = frog.move(Direction.LEFT)
        assert result == True
        assert frog.x == 100 - GRID_SIZE
    
    def test_move_right_success(self):
        frog = Frog(100, 200)
        result = frog.move(Direction.RIGHT)
        assert result == True
        assert frog.x == 100 + GRID_SIZE
    
    def test_move_out_of_bounds_left(self):
        frog = Frog(0, 200)
        result = frog.move(Direction.LEFT)
        assert result == False
        assert frog.x == 0
    
    def test_move_out_of_bounds_right(self):
        frog = Frog(SCREEN_WIDTH - frog.width, 200)
        result = frog.move(Direction.RIGHT)
        assert result == False
    
    def test_move_out_of_bounds_up(self):
        frog = Frog(100, 0)
        result = frog.move(Direction.UP)
        assert result == False
        assert frog.y == 0
    
    def test_move_out_of_bounds_down(self):
        frog = Frog(100, SCREEN_HEIGHT - frog.height)
        result = frog.move(Direction.DOWN)
        assert result == False
    
    def test_reset_position(self):
        frog = Frog(100, 200)
        frog.x = 300
        frog.y = 400
        frog.on_log = True
        frog.log_speed = 5
        
        frog.reset_position()
        
        assert frog.x == 100
        assert frog.y == 200
        assert frog.on_log == False
        assert frog.log_speed == 0
    
    def test_update_on_log_when_on_log(self):
        frog = Frog(100, 200)
        frog.on_log = True
        frog.update_on_log(5)
        assert frog.x == 105
    
    def test_update_on_log_boundary_left(self):
        frog = Frog(0, 200)
        frog.on_log = True
        frog.update_on_log(-10)
        assert frog.x == 0
    
    def test_update_on_log_boundary_right(self):
        frog = Frog(SCREEN_WIDTH, 200)
        frog.on_log = True
        frog.update_on_log(10)
        assert frog.x == SCREEN_WIDTH - frog.width
    
    def test_update_on_log_when_not_on_log(self):
        frog = Frog(100, 200)
        frog.on_log = False
        frog.update_on_log(5)
        assert frog.x == 100


class TestVehicle:
    """ทดสอบ Vehicle class"""
    
    def test_init(self):
        vehicle = Vehicle(10, 20, 3, Colors.RED)
        assert vehicle.x == 10
        assert vehicle.y == 20
        assert vehicle.speed == 3
        assert vehicle.color == Colors.RED
    
    def test_update_moving_right(self):
        vehicle = Vehicle(10, 20, 3, Colors.RED)
        vehicle.update()
        assert vehicle.x == 13
    
    def test_update_moving_left(self):
        vehicle = Vehicle(10, 20, -3, Colors.RED)
        vehicle.update()
        assert vehicle.x == 7
    
    def test_update_wrap_right(self):
        vehicle = Vehicle(SCREEN_WIDTH + 5, 20, 3, Colors.RED)
        vehicle.update()
        assert vehicle.x == -vehicle.width
    
    def test_update_wrap_left(self):
        vehicle = Vehicle(-vehicle.width - 5, 20, -3, Colors.RED)
        vehicle.update()
        assert vehicle.x == SCREEN_WIDTH


class TestLog:
    """ทดสอบ Log class"""
    
    def test_init(self):
        log = Log(10, 20, 2, 3)
        assert log.x == 10
        assert log.y == 20
        assert log.speed == 2
        assert log.length == 3
        assert log.width == 3 * GRID_SIZE
    
    def test_init_default_length(self):
        log = Log(10, 20, 2)
        assert log.length == 2
        assert log.width == 2 * GRID_SIZE
    
    def test_update_moving_right(self):
        log = Log(10, 20, 2, 3)
        log.update()
        assert log.x == 12
    
    def test_update_moving_left(self):
        log = Log(10, 20, -2, 3)
        log.update()
        assert log.x == 8
    
    def test_update_wrap_right(self):
        log = Log(SCREEN_WIDTH + 5, 20, 2, 3)
        log.update()
        assert log.x == -log.width
    
    def test_update_wrap_left(self):
        log = Log(-log.width - 5, 20, -2, 3)
        log.update()
        assert log.x == SCREEN_WIDTH


class TestTurtle:
    """ทดสอบ Turtle class"""
    
    def test_init(self):
        with patch('random.randint', return_value=200):
            turtle = Turtle(10, 20, 2)
            assert turtle.x == 10
            assert turtle.y == 20
            assert turtle.speed == 2
            assert turtle.is_diving == False
            assert turtle.dive_timer == 200
            assert turtle.dive_duration == 60
    
    def test_update_moving(self):
        with patch('random.randint', return_value=200):
            turtle = Turtle(10, 20, 2)
            turtle.update()
            assert turtle.x == 12
            assert turtle.dive_timer == 199
    
    def test_update_start_diving(self):
        with patch('random.randint', return_value=200):
            turtle = Turtle(10, 20, 2)
            turtle.dive_timer = 1
            turtle.update()
            assert turtle.is_diving == True
            assert turtle.dive_timer == 60
    
    def test_update_end_diving(self):
        with patch('random.randint', return_value=250):
            turtle = Turtle(10, 20, 2)
            turtle.is_diving = True
            turtle.dive_timer = 1
            turtle.update()
            assert turtle.is_diving == False
            assert turtle.dive_timer == 250
    
    def test_update_wrap_right(self):
        with patch('random.randint', return_value=200):
            turtle = Turtle(SCREEN_WIDTH + 5, 20, 2)
            turtle.update()
            assert turtle.x == -turtle.width
    
    def test_update_wrap_left(self):
        with patch('random.randint', return_value=200):
            turtle = Turtle(-turtle.width - 5, 20, -2)
            turtle.update()
            assert turtle.x == SCREEN_WIDTH
    
    def test_draw_not_diving(self):
        with patch('random.randint', return_value=200):
            turtle = Turtle(10, 20, 2)
            turtle.is_diving = False
            mock_screen = Mock()
            
            with patch('pygame.draw.rect') as mock_draw:
                turtle.draw(mock_screen)
                mock_draw.assert_called_once()
    
    def test_draw_while_diving(self):
        with patch('random.randint', return_value=200):
            turtle = Turtle(10, 20, 2)
            turtle.is_diving = True
            mock_screen = Mock()
            
            with patch('pygame.draw.rect') as mock_draw:
                turtle.draw(mock_screen)
                mock_draw.assert_not_called()


class TestHome:
    """ทดสอบ Home class"""
    
    def test_init(self):
        home = Home(10, 20)
        assert home.x == 10
        assert home.y == 20
        assert home.occupied == False
    
    def test_draw_not_occupied(self):
        home = Home(10, 20)
        mock_screen = Mock()
        
        with patch('pygame.draw.rect') as mock_draw:
            home.draw(mock_screen)
            assert mock_draw.call_count == 2
    
    def test_draw_occupied(self):
        home = Home(10, 20)
        home.occupied = True
        mock_screen = Mock()
        
        with patch('pygame.draw.rect') as mock_draw:
            home.draw(mock_screen)
            assert mock_draw.call_count == 2


class TestGameState:
    """ทดสอบ GameState class"""
    
    def test_init(self):
        state = GameState()
        assert state.lives == 3
        assert state.score == 0
        assert state.level == 1
        assert state.time_left == 30.0
        assert state.game_over == False
        assert state.level_complete == False
        assert state.homes_filled == 0


class TestFroggerGame:
    """ทดสอบ FroggerGame class"""
    
    @pytest.fixture
    def game(self):
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.display.set_caption'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            game = FroggerGame()
            return game
    
    def test_init(self, game):
        assert game.running == True
        assert game.game_state.lives == 3
        assert game.frog is not None
        assert len(game.vehicles) > 0
        assert len(game.logs) > 0
        assert len(game.turtles) > 0
        assert len(game.homes) == 5
    
    def test_handle_input_quit(self, game):
        mock_event = Mock()
        mock_event.type = pygame.QUIT
        
        with patch('pygame.event.get', return_value=[mock_event]):
            result = game.handle_input()
            assert result == False
    
    def test_handle_input_move_up(self, game):
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_UP
        
        initial_y = game.frog.y
        
        with patch('pygame.event.get', return_value=[mock_event]):
            result = game.handle_input()
            assert pygame.K_UP in result
            assert game.frog.y < initial_y
    
    def test_handle_input_move_down(self, game):
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_DOWN
        
        initial_y = game.frog.y
        
        with patch('pygame.event.get', return_value=[mock_event]):
            result = game.handle_input()
            assert pygame.K_DOWN in result
    
    def test_handle_input_move_left(self, game):
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_LEFT
        
        initial_x = game.frog.x
        
        with patch('pygame.event.get', return_value=[mock_event]):
            result = game.handle_input()
            assert pygame.K_LEFT in result
    
    def test_handle_input_move_right(self, game):
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_RIGHT
        
        with patch('pygame.event.get', return_value=[mock_event]):
            result = game.handle_input()
            assert pygame.K_RIGHT in result
    
    def test_handle_input_restart_when_game_over(self, game):
        game.game_state.game_over = True
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_r
        
        with patch('pygame.event.get', return_value=[mock_event]):
            result = game.handle_input()
            assert game.game_state.game_over == False
    
    def test_handle_input_restart_when_level_complete(self, game):
        game.game_state.level_complete = True
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_r
        
        with patch('pygame.event.get', return_value=[mock_event]):
            result = game.handle_input()
            assert game.game_state.level_complete == False
    
    def test_handle_input_no_events(self, game):
        with patch('pygame.event.get', return_value=[]):
            result = game.handle_input()
            assert result == True
    
    def test_update_game_logic_when_game_over(self, game):
        game.game_state.game_over = True
        initial_time = game.game_state.time_left
        game.update_game_logic()
        assert game.game_state.time_left == initial_time
    
    def test_update_game_logic_when_level_complete(self, game):
        game.game_state.level_complete = True
        initial_time = game.game_state.time_left
        game.update_game_logic()
        assert game.game_state.time_left == initial_time
    
    def test_update_game_logic_time_decrease(self, game):
        initial_time = game.game_state.time_left
        game.update_game_logic()
        assert game.game_state.time_left < initial_time
    
    def test_update_game_logic_time_up(self, game):
        game.game_state.time_left = 0
        initial_lives = game.game_state.lives
        game.update_game_logic()
        assert game.game_state.lives == initial_lives - 1
    
    def test_check_vehicle_collision(self, game):
        game.frog.x = game.vehicles[0].x
        game.frog.y = game.vehicles[0].y
        game.frog.update_rect()
        
        initial_lives = game.game_state.lives
        game._check_vehicle_collision()
        assert game.game_state.lives == initial_lives - 1
    
    def test_check_water_collision_on_log(self, game):
        game.frog.y = 100
        game.frog.x = game.logs[0].x + 10
        game.frog.update_rect()
        
        game._check_water_collision()
        assert game.frog.on_log == True
    
    def test_check_water_collision_on_turtle(self, game):
        game.frog.y = 100
        game.frog.x = game.turtles[0].x + 10
        game.frog.update_rect()
        game.turtles[0].is_diving = False
        
        game._check_water_collision()
        assert game.frog.on_log == True
    
    def test_check_water_collision_on_diving_turtle(self, game):
        game.frog.y = 100
        game.frog.x = 300
        game.frog.update_rect()
        
        # ทำให้เต่าทุกตัวดำน้ำ
        for turtle in game.turtles:
            turtle.is_diving = True
        
        # ทำให้ไม่มี log ใกล้กบ
        for log in game.logs:
            log.x = 1000
            log.update_rect()
        
        initial_lives = game.game_state.lives
        game._check_water_collision()
        assert game.game_state.lives == initial_lives - 1
    
    def test_check_water_collision_in_water_no_platform(self, game):
        game.frog.y = 100
        game.frog.x = 0
        game.frog.update_rect()
        
        # ย้าย logs และ turtles ออกไป
        for log in game.logs:
            log.x = 1000
            log.update_rect()
        
        for turtle in game.turtles:
            turtle.x = 1000
            turtle.update_rect()
        
        initial_lives = game.game_state.lives
        game._check_water_collision()
        assert game.game_state.lives == initial_lives - 1
    
    def test_check_water_collision_not_in_water(self, game):
        game.frog.y = 300
        game.frog.on_log = True
        game._check_water_collision()
        assert game.frog.on_log == False
    
    def test_check_home_collision_success(self, game):
        game.frog.y = 30
        game.frog.x = game.homes[0].x
        game.frog.update_rect()
        
        initial_score = game.game_state.score
        game._check_home_collision()
        
        assert game.homes[0].occupied == True
        assert game.game_state.homes_filled == 1
        assert game.game_state.score > initial_score
    
    def test_check_home_collision_already_occupied(self, game):
        game.homes[0].occupied = True
        game.frog.y = 30
        game.frog.x = game.homes[0].x
        game.frog.update_rect()
        
        initial_homes = game.game_state.homes_filled
        game._check_home_collision()
        assert game.game_state.homes_filled == initial_homes
    
    def test_check_home_collision_all_homes_filled(self, game):
        for home in game.homes[:-1]:
            home.occupied = True
        
        game.game_state.homes_filled = 4
        game.frog.y = 30
        game.frog.x = game.homes[-1].x
        game.frog.update_rect()
        
        game._check_home_collision()
        assert game.game_state.level_complete == True
    
    def test_check_home_collision_miss_home(self, game):
        game.frog.y = 30
        game.frog.x = 0
        game.frog.update_rect()
        
        initial_lives = game.game_state.lives
        game._check_home_collision()
        assert game.game_state.lives == initial_lives - 1
    
    def test_lose_life_game_over(self, game):
        game.game_state.lives = 1
        game._lose_life()
        assert game.game_state.lives == 0
        assert game.game_state.game_over == True
    
    def test_lose_life_not_game_over(self, game):
        game.game_state.lives = 3
        initial_y = game.frog.y
        game.frog.y = 100
        
        game._lose_life()
        assert game.game_state.lives == 2
        assert game.game_state.game_over == False
    
    def test_reset_frog(self, game):
        game.frog.x = 300
        game.frog.y = 100
        game.game_state.time_left = 10
        
        game._reset_frog()
        assert game.game_state.time_left == 30.0
    
    def test_complete_level(self, game):
        game.game_state.time_left = 15.5
        initial_score = game.game_state.score
        
        game._complete_level()
        assert game.game_state.level_complete == True
        assert game.game_state.score > initial_score
    
    def test_restart_game(self, game):
        game.game_state.lives = 0
        game.game_state.game_over = True
        game.game_state.score = 500
        
        game.restart_game()
        assert game.game_state.lives == 3
        assert game.game_state.game_over == False
        assert game.game_state.score == 0
    
    def test_draw_game(self, game):
        with patch.object(game, '_draw_background'), \
             patch.object(game, '_draw_ui'), \
             patch.object(game, '_draw_status_messages'), \
             patch('pygame.display.flip'):
            game.draw_game()
    
    def test_draw_game_when_game_over(self, game):
        game.game_state.game_over = True
        
        with patch.object(game, '_draw_background'), \
             patch.object(game, '_draw_ui'), \
             patch.object(game, '_draw_status_messages'), \
             patch('pygame.display.flip'):
            game.draw_game()
    
    def test_draw_game_when_level_complete(self, game):
        game.game_state.level_complete = True
        
        with patch.object(game, '_draw_background'), \
             patch.object(game, '_draw_ui'), \
             patch.object(game, '_draw_status_messages'), \
             patch('pygame.display.flip'):
            game.draw_game()
    
    def test_draw_background(self, game):
        with patch('pygame.draw.rect') as mock_draw:
            game._draw_background()
            assert mock_draw.call_count == 5
    
    def test_draw_ui(self, game):
        mock_screen = Mock()
        game.screen = mock_screen
        
        with patch.object(game.font, 'render') as mock_render:
            mock_render.return_value = Mock()
            game._draw_ui()
            assert mock_render.call_count == 4
    
    def test_draw_status_messages_game_over(self, game):
        game.game_state.game_over = True
        mock_screen = Mock()
        game.screen = mock_screen
        
        with patch.object(game.font, 'render') as mock_render1, \
             patch.object(game.small_font, 'render') as mock_render2:
            mock_text = Mock()
            mock_text.get_rect = Mock(return_value=Mock())
            mock_render1.return_value = mock_text
            mock_render2.return_value = mock_text
            
            game._draw_status_messages()
            mock_render1.assert_called_once()
            mock_render2.assert_called_once()
    
    def test_draw_status_messages_level_complete(self, game):
        game.game_state.level_complete = True
        mock_screen = Mock()
        game.screen = mock_screen
        
        with patch.object(game.font, 'render') as mock_render1, \
             patch.object(game.small_font, 'render') as mock_render2:
            mock_text = Mock()
            mock_text.get_rect = Mock(return_value=Mock())
            mock_render1.return_value = mock_text
            mock_render2.return_value = mock_text
            
            game._draw_status_messages()
            mock_render1.assert_called_once()
            mock_render2.assert_called_once()
    
    def test_draw_status_messages_normal(self, game):
        game.game_state.game_over = False
        game.game_state.level_complete = False
        
        with patch.object(game.font, 'render') as mock_render1, \
             patch.object(game.small_font, 'render') as mock_render2:
            game._draw_status_messages()
            mock_render1.assert_not_called()
            mock_render2.assert_not_called()
    
    def test_run_quit_immediately(self, game):
        mock_event = Mock()
        mock_event.type = pygame.QUIT
        
        with patch('pygame.event.get', return_value=[mock_event]), \
             patch.object(game, 'update_game_logic'), \
             patch.object(game, 'draw_game'), \
             patch('pygame.quit'):
            score = game.run()
            assert score == game.game_state.score
    
    def test_run_one_iteration(self, game):
        call_count = [0]
        
        def mock_handle_input():
            call_count[0] += 1
            if call_count[0] > 1:
                return False
            return True
        
        with patch.object(game, 'handle_input', side_effect=mock_handle_input), \
             patch.object(game, 'update_game_logic'), \
             patch.object(game, 'draw_game'), \
             patch('pygame.quit'):
            score = game.run()
            assert call_count[0] == 2


class TestMain:
    """ทดสอบ main function"""
    
    def test_main(self):
        with patch('frogger_game.FroggerGame') as MockGame:
            mock_instance = Mock()
            mock_instance.run.return_value = 100
            MockGame.return_value = mock_instance
            
            from frogger_game import main
            result = main()
            assert result == 100


class TestCreateVehicles:
    """ทดสอบการสร้างยานพาหนะ"""
    
    @pytest.fixture
    def game(self):
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.display.set_caption'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            game = FroggerGame()
            return game
    
    def test_create_vehicles(self, game):
        with patch('random.randint', return_value=3):
            game.vehicles = []
            game._create_vehicles()
            assert len(game.vehicles) > 0


class TestCreateRiverObjects:
    """ทดสอบการสร้างวัตถุในแม่น้ำ"""
    
    @pytest.fixture
    def game(self):
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.display.set_caption'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            game = FroggerGame()
            return game
    
    def test_create_river_objects_logs(self, game):
        with patch('random.randint', return_value=2):
            game.logs = []
            game.turtles = []
            game._create_river_objects()
            assert len(game.logs) > 0
    
    def test_create_river_objects_turtles(self, game):
        with patch('random.randint', return_value=3):
            game.logs = []
            game.turtles = []
            game._create_river_objects()
            assert len(game.turtles) > 0


class TestCreateHomes:
    """ทดสอบการสร้างบ้าน"""
    
    @pytest.fixture
    def game(self):
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.display.set_caption'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            game = FroggerGame()
            return game
    
    def test_create_homes(self, game):
        game.homes = []
        game._create_homes()
        assert len(game.homes) == 5


class TestEdgeCases:
    """ทดสอบ edge cases ต่างๆ"""
    
    @pytest.fixture
    def game(self):
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.display.set_caption'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            game = FroggerGame()
            return game
    
    def test_frog_at_exact_boundary(self, game):
        frog = Frog(0, 0)
        assert frog.x == 0
        assert frog.y == 0
    
    def test_vehicle_exact_screen_width(self):
        vehicle = Vehicle(SCREEN_WIDTH, 100, 2, Colors.RED)
        vehicle.update()
        assert vehicle.x == -vehicle.width
    
    def test_log_exact_negative_width(self):
        log = Log(-GRID_SIZE * 2, 100, -2, 2)
        log.update()
        assert log.x == SCREEN_WIDTH
    
    def test_multiple_lives_loss(self, game):
        game.game_state.lives = 3
        game._lose_life()
        game._lose_life()
        assert game.game_state.lives == 1
        assert game.game_state.game_over == False
        
        game._lose_life()
        assert game.game_state.lives == 0
        assert game.game_state.game_over == True
    
    def test_score_calculation_on_level_complete(self, game):
        game.game_state.score = 0
        game.game_state.time_left = 20.7
        game._complete_level()
        assert game.game_state.score == 20 * 10
    
    def test_frog_movement_at_boundaries(self):
        # Test exact boundary conditions
        frog = Frog(GRID_SIZE, GRID_SIZE)
        
        # Move to left boundary
        while frog.x > 0:
            frog.move(Direction.LEFT)
        
        # Try to move past boundary
        result = frog.move(Direction.LEFT)
        assert result == False
        assert frog.x == 0
    
    def test_turtle_dive_cycle(self):
        with patch('random.randint', return_value=1):
            turtle = Turtle(100, 100, 2)
            
            # Not diving initially
            assert turtle.is_diving == False
            
            # Update to start diving
            turtle.update()
            assert turtle.is_diving == True
            
            # Update through dive duration
            for _ in range(59):
                turtle.update()
            
            assert turtle.is_diving == True
            
            # End diving
            turtle.update()
            assert turtle.is_diving == False
    
    def test_handle_input_multiple_keys(self, game):
        events = []
        
        # Create multiple key events
        for key in [pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT]:
            mock_event = Mock()
            mock_event.type = pygame.KEYDOWN
            mock_event.key = key
            events.append(mock_event)
        
        with patch('pygame.event.get', return_value=events):
            result = game.handle_input()
            assert len(result) == 3
    
    def test_water_collision_edge_between_zones(self, game):
        # Test at exact boundary of water zone
        game.frog.y = 50
        game.frog.x = 100
        game.frog.update_rect()
        
        # Should not check water collision at boundary
        game._check_water_collision()
    
    def test_water_collision_just_inside_zone(self, game):
        # Test just inside water zone
        game.frog.y = 51
        game.frog.x = 100
        game.frog.update_rect()
        
        # Move all platforms away
        for log in game.logs:
            log.x = 2000
            log.update_rect()
        
        for turtle in game.turtles:
            turtle.x = 2000
            turtle.update_rect()
        
        initial_lives = game.game_state.lives
        game._check_water_collision()
        assert game.game_state.lives == initial_lives - 1
    
    def test_water_collision_at_upper_boundary(self, game):
        # Test at upper boundary of water zone
        game.frog.y = 199
        game.frog.x = 100
        game.frog.update_rect()
        
        # Move all platforms away
        for log in game.logs:
            log.x = 2000
            log.update_rect()
        
        for turtle in game.turtles:
            turtle.x = 2000
            turtle.update_rect()
        
        initial_lives = game.game_state.lives
        game._check_water_collision()
        assert game.game_state.lives == initial_lives - 1
    
    def test_water_collision_just_outside_upper(self, game):
        # Test just outside upper boundary
        game.frog.y = 200
        game.frog.x = 100
        game.frog.update_rect()
        
        initial_lives = game.game_state.lives
        game._check_water_collision()
        # Should not lose life as it's outside water zone
        assert game.frog.on_log == False
    
    def test_home_collision_between_homes(self, game):
        # Position frog between two homes
        game.frog.y = 30
        game.frog.x = (game.homes[0].x + game.homes[1].x) // 2
        game.frog.update_rect()
        
        initial_lives = game.game_state.lives
        game._check_home_collision()
        # Should lose life if not hitting a home
        assert game.game_state.lives == initial_lives - 1
    
    def test_frog_on_log_moving_speed_change(self, game):
        game.frog.y = 100
        game.frog.x = game.logs[0].x + 10
        game.frog.update_rect()
        
        # First check - should be on log
        game._check_water_collision()
        assert game.frog.on_log == True
        
        old_speed = game.frog.log_speed
        
        # Move frog to another log with different speed
        if len(game.logs) > 1:
            game.frog.x = game.logs[1].x + 10
            game.frog.update_rect()
            game._check_water_collision()
            
            # Speed should update to new log's speed
            assert game.frog.on_log == True
    
    def test_collision_rect_overlap_partial(self):
        # Test partial overlap collision
        obj1 = GameObject(10, 10, 30, 30, Colors.RED)
        obj2 = GameObject(25, 25, 30, 30, Colors.BLUE)
        
        assert obj1.rect.colliderect(obj2.rect) == True
    
    def test_collision_rect_no_overlap(self):
        # Test no overlap
        obj1 = GameObject(10, 10, 30, 30, Colors.RED)
        obj2 = GameObject(100, 100, 30, 30, Colors.BLUE)
        
        assert obj1.rect.colliderect(obj2.rect) == False
    
    def test_collision_rect_edge_touching(self):
        # Test edge touching
        obj1 = GameObject(10, 10, 30, 30, Colors.RED)
        obj2 = GameObject(40, 10, 30, 30, Colors.BLUE)
        
        result = obj1.rect.colliderect(obj2.rect)
        # Edge touching should not collide
        assert result == False


class TestCompleteGameFlow:
    """ทดสอบ game flow แบบสมบูรณ์"""
    
    @pytest.fixture
    def game(self):
        with patch('pygame.init'), \
             patch('pygame.display.set_mode'), \
             patch('pygame.display.set_caption'), \
             patch('pygame.time.Clock'), \
             patch('pygame.font.Font'):
            game = FroggerGame()
            return game
    
    def test_complete_game_to_level_complete(self, game):
        # Fill all homes except one
        for i in range(4):
            game.homes[i].occupied = True
        game.game_state.homes_filled = 4
        
        # Move frog to last home
        game.frog.y = 30
        game.frog.x = game.homes[4].x
        game.frog.update_rect()
        
        game._check_home_collision()
        
        assert game.game_state.level_complete == True
        assert game.game_state.homes_filled == 5
    
    def test_complete_game_to_game_over(self, game):
        game.game_state.lives = 1
        
        # Trigger loss of last life
        game._lose_life()
        
        assert game.game_state.game_over == True
        assert game.game_state.lives == 0
    
    def test_restart_after_game_over(self, game):
        game.game_state.lives = 0
        game.game_state.game_over = True
        game.game_state.score = 500
        game.game_state.homes_filled = 3
        
        game.restart_game()
        
        assert game.game_state.lives == 3
        assert game.game_state.game_over == False
        assert game.game_state.score == 0
        assert game.game_state.homes_filled == 0
    
    def test_time_runs_out_scenario(self, game):
        game.game_state.time_left = 0.01
        initial_lives = game.game_state.lives
        
        game.update_game_logic()
        
        assert game.game_state.lives == initial_lives - 1
        assert game.game_state.time_left == 30.0


# Run tests with coverage
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=frogger_game", "--cov-report=html", "--cov-report=term"])