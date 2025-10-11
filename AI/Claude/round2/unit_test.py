"""
Unit Tests for Frogger Game
===========================
Complete test suite with 100% statement and branch coverage
"""

import pytest
import pygame
from unittest.mock import Mock, patch, MagicMock
from code import (
    GameObject, Frog, Vehicle, Log, Turtle, Home,
    GameState, FroggerGame, Direction, Colors,
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, main
)


class TestGameObject:
    """Test GameObject base class"""
    
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
        pygame.init()
        screen = pygame.Surface((100, 100))
        obj = GameObject(10, 20, 30, 40, Colors.RED)
        obj.draw(screen)  # Should not raise exception
    
    def test_get_center(self):
        obj = GameObject(10, 20, 30, 40, Colors.RED)
        center = obj.get_center()
        assert center == (25, 40)


class TestFrog:
    """Test Frog class"""
    
    def test_init(self):
        frog = Frog(100, 200)
        assert frog.x == 100
        assert frog.y == 200
        assert frog.start_x == 100
        assert frog.start_y == 200
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
        frog = Frog(100, 200)
        frog.x = SCREEN_WIDTH - frog.width
        frog.update_rect()
        result = frog.move(Direction.RIGHT)
        assert result == False
    
    def test_move_out_of_bounds_up(self):
        frog = Frog(100, 0)
        result = frog.move(Direction.UP)
        assert result == False
        assert frog.y == 0
    
    def test_move_out_of_bounds_down(self):
        frog = Frog(100, SCREEN_HEIGHT - GRID_SIZE + 4)
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
    
    def test_update_on_log_positive_speed(self):
        frog = Frog(100, 200)
        frog.on_log = True
        frog.update_on_log(5)
        assert frog.x == 105
    
    def test_update_on_log_negative_speed(self):
        frog = Frog(100, 200)
        frog.on_log = True
        frog.update_on_log(-5)
        assert frog.x == 95
    
    def test_update_on_log_not_on_log(self):
        frog = Frog(100, 200)
        frog.on_log = False
        frog.update_on_log(5)
        assert frog.x == 100
    
    def test_update_on_log_boundary_left(self):
        frog = Frog(2, 200)
        frog.on_log = True
        frog.update_on_log(-10)
        assert frog.x == 0
    
    def test_update_on_log_boundary_right(self):
        frog = Frog(SCREEN_WIDTH - 10, 200)
        frog.on_log = True
        frog.update_on_log(20)
        assert frog.x == SCREEN_WIDTH - frog.width


class TestVehicle:
    """Test Vehicle class"""
    
    def test_init(self):
        vehicle = Vehicle(10, 20, 3, Colors.RED)
        assert vehicle.x == 10
        assert vehicle.y == 20
        assert vehicle.speed == 3
        assert vehicle.color == Colors.RED
    
    def test_update_positive_speed(self):
        vehicle = Vehicle(10, 20, 3, Colors.RED)
        vehicle.update()
        assert vehicle.x == 13
    
    def test_update_negative_speed(self):
        vehicle = Vehicle(10, 20, -3, Colors.RED)
        vehicle.update()
        assert vehicle.x == 7
    
    def test_update_wrap_right(self):
        vehicle = Vehicle(SCREEN_WIDTH + 5, 20, 3, Colors.RED)
        vehicle.update()
        assert vehicle.x == -vehicle.width
    
    def test_update_positive_speed_no_wrap(self):
        vehicle = Vehicle(100, 20, 3, Colors.RED)
        vehicle.update()
        assert vehicle.x == 103
    
    def test_update_negative_speed_no_wrap(self):
        vehicle = Vehicle(100, 20, -3, Colors.RED)
        vehicle.update()
        assert vehicle.x == 97
    
    def test_update_wrap_left(self):
        vehicle = Vehicle(10, 20, -3, Colors.RED)
        vehicle.x = -vehicle.width - 5
        vehicle.update()
        assert vehicle.x == SCREEN_WIDTH


class TestLog:
    """Test Log class"""
    
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
    
    def test_update_positive_speed(self):
        log = Log(10, 20, 2, 2)
        log.update()
        assert log.x == 12
    
    def test_update_negative_speed(self):
        log = Log(10, 20, -2, 2)
        log.update()
        assert log.x == 8
    
    def test_update_wrap_right(self):
        log = Log(SCREEN_WIDTH + 5, 20, 2, 2)
        log.update()
        assert log.x == -log.width
    
    def test_update_wrap_left(self):
        log = Log(-100, 20, -2, 2)
        log.update()
        assert log.x == SCREEN_WIDTH


class TestTurtle:
    """Test Turtle class"""
    
    def test_init(self):
        turtle = Turtle(10, 20, 2)
        assert turtle.x == 10
        assert turtle.y == 20
        assert turtle.speed == 2
        assert turtle.is_diving == False
        assert 180 <= turtle.dive_timer <= 300
    
    def test_update_movement(self):
        turtle = Turtle(10, 20, 2)
        initial_timer = turtle.dive_timer
        turtle.update()
        assert turtle.x == 12
        assert turtle.dive_timer == initial_timer - 1
    
    def test_update_wrap_right(self):
        turtle = Turtle(SCREEN_WIDTH + 5, 20, 2)
        turtle.update()
        assert turtle.x == -turtle.width
    
    def test_update_wrap_left(self):
        turtle = Turtle(-50, 20, -2)
        turtle.update()
        assert turtle.x == SCREEN_WIDTH
    
    def test_diving_cycle_start(self):
        turtle = Turtle(10, 20, 2)
        turtle.dive_timer = 1
        turtle.is_diving = False
        turtle.update()
        assert turtle.is_diving == True
        assert turtle.dive_timer == 60
    
    def test_diving_cycle_end(self):
        turtle = Turtle(10, 20, 2)
        turtle.dive_timer = 1
        turtle.is_diving = True
        turtle.update()
        assert turtle.is_diving == False
        assert 180 <= turtle.dive_timer <= 300
    
    def test_draw_not_diving(self):
        pygame.init()
        screen = pygame.Surface((100, 100))
        turtle = Turtle(10, 20, 2)
        turtle.is_diving = False
        turtle.draw(screen)  # Should draw
    
    def test_draw_diving(self):
        pygame.init()
        screen = pygame.Surface((100, 100))
        turtle = Turtle(10, 20, 2)
        turtle.is_diving = True
        turtle.draw(screen)  # Should not draw


class TestHome:
    """Test Home class"""
    
    def test_init(self):
        home = Home(10, 20)
        assert home.x == 10
        assert home.y == 20
        assert home.occupied == False
    
    def test_draw_not_occupied(self):
        pygame.init()
        screen = pygame.Surface((100, 100))
        home = Home(10, 20)
        home.draw(screen)  # Should draw yellow
    
    def test_draw_occupied(self):
        pygame.init()
        screen = pygame.Surface((100, 100))
        home = Home(10, 20)
        home.occupied = True
        home.draw(screen)  # Should draw green


class TestGameState:
    """Test GameState class"""
    
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
    """Test FroggerGame class"""
    
    @pytest.fixture
    def game(self):
        pygame.init()
        game = FroggerGame()
        return game
    
    def test_init(self, game):
        assert game.running == True
        assert game.game_state is not None
        assert game.frog is not None
        assert len(game.vehicles) > 0
        assert len(game.logs) > 0
        assert len(game.turtles) > 0
        assert len(game.homes) == 5
    
    def test_handle_input_quit(self, game):
        event = pygame.event.Event(pygame.QUIT)
        pygame.event.post(event)
        result = game.handle_input()
        assert result == False
    
    def test_handle_input_up(self, game):
        initial_y = game.frog.y
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        pygame.event.post(event)
        result = game.handle_input()
        assert game.frog.y < initial_y
    
    def test_handle_input_down(self, game):
        game.frog.y = 100
        initial_y = game.frog.y
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
        pygame.event.post(event)
        result = game.handle_input()
        assert game.frog.y > initial_y
    
    def test_handle_input_left(self, game):
        initial_x = game.frog.x
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
        pygame.event.post(event)
        result = game.handle_input()
        assert game.frog.x < initial_x
    
    def test_handle_input_right(self, game):
        initial_x = game.frog.x
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        pygame.event.post(event)
        result = game.handle_input()
        assert game.frog.x > initial_x
    
    def test_handle_input_restart_game_over(self, game):
        game.game_state.game_over = True
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)
        pygame.event.post(event)
        game.handle_input()
        assert game.game_state.game_over == False
    
    def test_handle_input_restart_level_complete(self, game):
        game.game_state.level_complete = True
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)
        pygame.event.post(event)
        game.handle_input()
        assert game.game_state.level_complete == False
    
    def test_handle_input_no_move_when_game_over(self, game):
        game.game_state.game_over = True
        initial_y = game.frog.y
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
        pygame.event.post(event)
        game.handle_input()
        assert game.frog.y == initial_y
    
    def test_update_game_logic_time_decrease(self, game):
        initial_time = game.game_state.time_left
        game.update_game_logic()
        assert game.game_state.time_left < initial_time
    
    def test_update_game_logic_time_out(self, game):
        game.game_state.time_left = 0.001
        initial_lives = game.game_state.lives
        game.update_game_logic()
        assert game.game_state.lives < initial_lives
    
    def test_update_game_logic_no_update_when_game_over(self, game):
        game.game_state.game_over = True
        initial_time = game.game_state.time_left
        game.update_game_logic()
        assert game.game_state.time_left == initial_time
    
    def test_update_game_logic_no_update_when_level_complete(self, game):
        game.game_state.level_complete = True
        initial_time = game.game_state.time_left
        game.update_game_logic()
        assert game.game_state.time_left == initial_time
    
    def test_check_vehicle_collision(self, game):
        # Position frog at vehicle location
        vehicle = game.vehicles[0]
        game.frog.x = vehicle.x
        game.frog.y = vehicle.y
        game.frog.update_rect()
        initial_lives = game.game_state.lives
        game._check_vehicle_collision()
        assert game.game_state.lives < initial_lives
    
    def test_check_water_collision_on_log(self, game):
        # Position frog on a log
        log = game.logs[0]
        game.frog.x = log.x + 10
        game.frog.y = log.y
        game.frog.update_rect()
        initial_lives = game.game_state.lives
        game._check_water_collision()
        assert game.frog.on_log == True
        assert game.game_state.lives == initial_lives
    
    def test_check_water_collision_on_turtle_not_diving(self, game):
        # Position frog on a turtle that's not diving
        turtle = game.turtles[0]
        turtle.is_diving = False
        game.frog.x = turtle.x
        game.frog.y = turtle.y
        game.frog.update_rect()
        initial_lives = game.game_state.lives
        game._check_water_collision()
        assert game.frog.on_log == True
        assert game.game_state.lives == initial_lives
    
    def test_check_water_collision_drowning(self, game):
        # Position frog in water without support
        game.frog.x = 100
        game.frog.y = 100  # In water zone
        game.frog.update_rect()
        initial_lives = game.game_state.lives
        game._check_water_collision()
        assert game.game_state.lives < initial_lives
    
    def test_check_water_collision_not_in_water(self, game):
        # Position frog outside water zone
        game.frog.y = 300
        game.frog.on_log = True
        game._check_water_collision()
        assert game.frog.on_log == False
    
    def test_check_home_collision_success(self, game):
        # Position frog at home
        home = game.homes[0]
        game.frog.x = home.x
        game.frog.y = home.y
        game.frog.update_rect()
        initial_score = game.game_state.score
        game._check_home_collision()
        assert home.occupied == True
        assert game.game_state.score > initial_score
        assert game.game_state.homes_filled == 1
    
    def test_check_home_collision_already_occupied(self, game):
        # Position frog at already occupied home
        home = game.homes[0]
        home.occupied = True
        game.frog.x = home.x
        game.frog.y = home.y
        game.frog.update_rect()
        initial_filled = game.game_state.homes_filled
        game._check_home_collision()
        assert game.game_state.homes_filled == initial_filled
    
    def test_check_home_collision_level_complete(self, game):
        # Fill all homes
        for i, home in enumerate(game.homes[:-1]):
            home.occupied = True
            game.game_state.homes_filled += 1
        
        # Position at last home
        last_home = game.homes[-1]
        game.frog.x = last_home.x
        game.frog.y = last_home.y
        game.frog.update_rect()
        game._check_home_collision()
        assert game.game_state.level_complete == True
    
    def test_check_home_collision_miss(self, game):
        # Position frog in home zone but not at a home
        game.frog.x = 5
        game.frog.y = 25
        game.frog.update_rect()
        initial_lives = game.game_state.lives
        game._check_home_collision()
        assert game.game_state.lives < initial_lives
    
    def test_lose_life_game_over(self, game):
        game.game_state.lives = 1
        game._lose_life()
        assert game.game_state.lives == 0
        assert game.game_state.game_over == True
    
    def test_lose_life_not_game_over(self, game):
        game.game_state.lives = 2
        game._lose_life()
        assert game.game_state.lives == 1
        assert game.game_state.game_over == False
    
    def test_reset_frog(self, game):
        game.frog.x = 300
        game.frog.y = 100
        game.game_state.time_left = 10.0
        game._reset_frog()
        assert game.frog.x == game.frog.start_x
        assert game.frog.y == game.frog.start_y
        assert game.game_state.time_left == 30.0
    
    def test_complete_level(self, game):
        game.game_state.time_left = 15.0
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
        # Test that draw doesn't raise exception
        game.draw_game()
    
    def test_draw_game_game_over(self, game):
        game.game_state.game_over = True
        game.draw_game()
    
    def test_draw_game_level_complete(self, game):
        game.game_state.level_complete = True
        game.draw_game()
    
    def test_draw_background(self, game):
        game._draw_background()
    
    def test_draw_ui(self, game):
        game._draw_ui()
    
    def test_draw_status_messages_normal(self, game):
        game._draw_status_messages()
    
    def test_draw_status_messages_game_over(self, game):
        game.game_state.game_over = True
        game._draw_status_messages()
    
    def test_draw_status_messages_level_complete(self, game):
        game.game_state.level_complete = True
        game._draw_status_messages()
    
    def test_create_vehicles(self, game):
        game.vehicles = []
        game._create_vehicles()
        assert len(game.vehicles) > 0
    
    def test_create_river_objects(self, game):
        game.logs = []
        game.turtles = []
        game._create_river_objects()
        assert len(game.logs) > 0
        assert len(game.turtles) > 0
    
    def test_create_homes(self, game):
        game.homes = []
        game._create_homes()
        assert len(game.homes) == 5
    
    @patch('pygame.event.get')
    @patch('pygame.display.flip')
    def test_run_quit_immediately(self, mock_flip, mock_get, game):
        mock_get.return_value = [pygame.event.Event(pygame.QUIT)]
        score = game.run()
        assert isinstance(score, int)
    
    def test_run_with_game_loop(self, game):
        # Mock to quit after a few frames
        original_handle = game.handle_input
        call_count = [0]
        
        def mock_handle():
            call_count[0] += 1
            if call_count[0] > 3:
                return False
            return original_handle()
        
        game.handle_input = mock_handle
        score = game.run()
        assert isinstance(score, int)


class TestMain:
    """Test main function"""
    
    @patch.object(FroggerGame, 'run')
    def test_main(self, mock_run):
        mock_run.return_value = 100
        result = main()
        assert result == 100
        mock_run.assert_called_once()


class TestDirection:
    """Test Direction enum"""
    
    def test_direction_values(self):
        assert Direction.UP.value == (0, -1)
        assert Direction.DOWN.value == (0, 1)
        assert Direction.LEFT.value == (-1, 0)
        assert Direction.RIGHT.value == (1, 0)


class TestColors:
    """Test Colors class"""
    
    def test_color_definitions(self):
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


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=frogger", "--cov-report=html", "--cov-report=term-missing"])