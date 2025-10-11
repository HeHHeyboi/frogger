import pytest
import pygame
from unittest.mock import MagicMock, call
# Import classes from the game code
from code import (
    Game, Frog, MovingObject, Turtle, GameObject,
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, TOTAL_HOMES, MAX_LIVES
)

# --- Pytest Fixtures ---

@pytest.fixture(autouse=True)
def mock_pygame_init(mocker):
    """Auto-used fixture to mock all necessary Pygame modules."""
    mocker.patch('pygame.init', return_value=True)
    mocker.patch('pygame.display.set_mode', return_value=MagicMock())
    mocker.patch('pygame.display.set_caption', return_value=None)
    # Mock font rendering to prevent UI-related errors
    mock_font = MagicMock()
    mock_font.render.return_value = MagicMock(get_rect=lambda **kwargs: pygame.Rect(0, 0, 50, 20))
    mocker.patch('pygame.font.Font', return_value=mock_font)
    mocker.patch('pygame.quit', return_value=None)
    mocker.patch('sys.exit', side_effect=SystemExit) # Use side_effect to avoid stopping the test runner

@pytest.fixture
def game():
    """Provides a fresh instance of the Game class for each test."""
    return Game()

# --- Test Cases ---

class TestGameObject:
    def test_init(self):
        """Test GameObject initialization."""
        obj = GameObject(10, 20, 30, 40, (255, 0, 0))
        assert obj.rect == pygame.Rect(10, 20, 30, 40)
        assert obj.color == (255, 0, 0)

    def test_draw(self, mocker):
        """Test if the draw method calls pygame.draw.rect correctly."""
        mock_draw_rect = mocker.patch('pygame.draw.rect')
        screen = MagicMock()
        obj = GameObject(10, 20, 30, 40, (255, 0, 0))
        obj.draw(screen)
        mock_draw_rect.assert_called_once_with(screen, obj.color, obj.rect)

class TestFrog:
    @pytest.fixture
    def frog(self):
        """Provides a standard Frog instance."""
        return Frog(SCREEN_WIDTH // 2, SCREEN_HEIGHT - GRID_SIZE)

    def test_init(self, frog):
        """Test Frog initialization."""
        assert frog.rect.size == (GRID_SIZE, GRID_SIZE)
        assert frog.start_x == frog.rect.x
        assert frog.start_y == frog.rect.y
        assert frog.attached_to is None

    def test_move(self, frog):
        """Test movement in all directions."""
        initial_x, initial_y = frog.rect.topleft
        
        # Move up
        frog.move(0, -1)
        assert frog.rect.topleft == (initial_x, initial_y - GRID_SIZE)
        
        # Move down
        frog.move(0, 1)
        assert frog.rect.topleft == (initial_x, initial_y) # Back to start
        
        # Move left
        frog.move(-1, 0)
        assert frog.rect.topleft == (initial_x - GRID_SIZE, initial_y)

        # Move right
        frog.move(1, 0)
        assert frog.rect.topleft == (initial_x, initial_y) # Back to start

    def test_attach_detach(self, frog):
        """Test attaching and detaching from a platform."""
        platform = MovingObject(0, 0, 100, 40, (0,0,0), 5)
        
        # Attach
        frog.attach_to(platform)
        assert frog.attached_to == platform
        
        # Detach
        frog.detach()
        assert frog.attached_to is None
        
        # Moving should also detach
        frog.attach_to(platform)
        frog.move(0, -1)
        assert frog.attached_to is None

    def test_update_position_on_platform(self, frog):
        """Test that frog moves with the platform it's attached to."""
        initial_x = frog.rect.x
        platform = MovingObject(0, 0, 100, 40, (0,0,0), 5)
        
        # Not attached
        frog.update_position_on_platform()
        assert frog.rect.x == initial_x

        # Attached
        frog.attach_to(platform)
        frog.update_position_on_platform()
        assert frog.rect.x == initial_x + platform.speed

    def test_reset_position(self, frog):
        """Test resetting frog's position."""
        platform = MovingObject(0, 0, 100, 40, (0,0,0), 5)
        frog.attach_to(platform)
        frog.move(0, -1) # Move away from start
        
        frog.reset_position()
        assert frog.rect.topleft == (frog.start_x, frog.start_y)
        assert frog.attached_to is None
        
    def test_is_on_screen(self, frog):
        """Test screen boundary checks."""
        assert frog.is_on_screen()
        frog.rect.x = -1
        assert not frog.is_on_screen()
        frog.rect.x = SCREEN_WIDTH
        assert not frog.is_on_screen()


class TestMovingObject:
    def test_move_and_wrap_positive_speed(self):
        """Test wrapping from right to left."""
        obj = MovingObject(-50, 100, 80, 40, (0,0,0), 5)
        obj.rect.right = SCREEN_WIDTH + 10 # Place it just off the right edge
        
        obj.move()
        # It should have moved and wrapped around
        assert obj.rect.right == 10 + 5

    def test_move_and_wrap_negative_speed(self):
        """Test wrapping from left to right."""
        obj = MovingObject(SCREEN_WIDTH + 50, 100, 80, 40, (0,0,0), -5)
        obj.rect.left = -10 # Place it just off the left edge
        
        obj.move()
        # It should have moved and wrapped around
        assert obj.rect.left == SCREEN_WIDTH - 10 - 5
        
class TestTurtle:
    def test_update_diving_cycle(self):
        """Test the full dive and surface cycle of a turtle."""
        # Turtle surfaces for 3s, dives for 2s
        turtle = Turtle(0, 0, 1, dive_interval=3, dive_duration=2)
        
        assert not turtle.is_diving
        
        # Time passes, but not enough to dive
        turtle.update(dt=2.9)
        assert not turtle.is_diving
        
        # Time passes enough to trigger a dive
        turtle.update(dt=0.2) # Total time is 3.1
        assert turtle.is_diving
        assert turtle.timer == 0 # Timer resets
        
        # Time passes, but not enough to surface
        turtle.update(dt=1.9)
        assert turtle.is_diving
        
        # Time passes enough to trigger surfacing
        turtle.update(dt=0.2) # Total time is 2.1
        assert not turtle.is_diving
        assert turtle.timer == 0 # Timer resets

    def test_draw(self, mocker):
        """Test that the turtle does not draw when diving."""
        mock_draw_rect = mocker.patch('pygame.draw.rect')
        screen = MagicMock()
        turtle = Turtle(0, 0, 1, 3, 2)
        
        # Should draw when not diving
        turtle.is_diving = False
        turtle.draw(screen)
        mock_draw_rect.assert_called_once()
        
        # Should not draw when diving
        mock_draw_rect.reset_mock()
        turtle.is_diving = True
        turtle.draw(screen)
        mock_draw_rect.assert_not_called()

class TestGame:
    def test_reset_game(self, game):
        """Test the state after resetting the game."""
        # Modify state
        game.lives = 0
        game.level = 5
        game.score = 1000
        game.homes_filled[0] = True
        
        # Reset and check
        game.reset_game()
        assert game.lives == MAX_LIVES
        assert game.level == 1
        assert game.score == 0
        assert all(h is False for h in game.homes_filled)

    def test_handle_input(self, game, mocker):
        """Test all branches of player input handling."""
        # 1. Test QUIT event
        mocker.patch('pygame.event.get', return_value=[pygame.event.Event(pygame.QUIT)])
        game.handle_input()
        assert not game.running

        # 2. Test frog movement
        game.running = True
        arrow_keys = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]
        for key in arrow_keys:
            mocker.patch('pygame.event.get', return_value=[pygame.event.Event(pygame.KEYDOWN, key=key)])
            with mocker.patch.object(game.frog, 'move') as mock_move:
                game.handle_input()
                mock_move.assert_called_once()
        
        # 3. Test movement boundaries (should not move)
        game.frog.rect.top = 0
        mocker.patch('pygame.event.get', return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)])
        with mocker.patch.object(game.frog, 'move') as mock_move:
             game.handle_input()
             mock_move.assert_not_called()

        # 4. Test Enter key on "game_over" screen
        game.game_state = "game_over"
        mocker.patch('pygame.event.get', return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)])
        with mocker.patch.object(game, 'reset_game') as mock_reset:
            game.handle_input()
            mock_reset.assert_called_once()
        
        # 5. Test Enter key on "level_complete" screen
        game.game_state = "level_complete"
        mocker.patch('pygame.event.get', return_value=[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)])
        with mocker.patch.object(game, 'setup_level') as mock_setup:
            game.handle_input()
            mock_setup.assert_called_once()
            assert game.level == 2 # Level should increment
            assert all(h is False for h in game.homes_filled)

    def test_update_non_playing_state(self, game, mocker):
        """Test that update does nothing if game is not in 'playing' state."""
        mock_check_collisions = mocker.patch.object(game, 'check_collisions')
        game.game_state = "game_over"
        game.update()
        mock_check_collisions.assert_not_called()

    def test_lose_life(self, game, mocker):
        """Test the logic for losing a life."""
        mock_reset_frog = mocker.patch.object(game.frog, 'reset_position')
        
        # Lose a life, but game continues
        initial_lives = game.lives
        game.lose_life()
        assert game.lives == initial_lives - 1
        assert game.game_state == "playing"
        mock_reset_frog.assert_called_once()
        
        # Lose the final life
        game.lives = 1
        game.lose_life()
        assert game.lives == 0
        assert game.game_state == "game_over"

    def test_check_time_out(self, game, mocker):
        """Test that the player loses a life when time runs out."""
        mocker.patch('pygame.time.get_ticks', side_effect=[0, game.time_limit + 1])
        game.setup_level() # Resets start_time
        with mocker.patch.object(game, 'lose_life') as mock_lose_life:
            game.check_time()
            mock_lose_life.assert_called_once()

    def test_collisions(self, game, mocker):
        """A comprehensive test for all collision scenarios."""
        mock_lose_life = mocker.patch.object(game, 'lose_life')

        # 1. Collision with a car
        game.obstacles[0].rect.colliderect = lambda x: True
        game.check_collisions()
        mock_lose_life.assert_called_once()
        game.obstacles[0].rect.colliderect = lambda x: False
        mock_lose_life.reset_mock()

        # 2. Drowning in water (no platform)
        game.frog.rect.centery = game.water_rect.centery
        game.check_collisions()
        mock_lose_life.assert_called_once()
        mock_lose_life.reset_mock()

        # 3. Landing safely on a platform
        platform = game.platforms[0]
        platform.is_diving = False # Ensure it's not a diving turtle
        game.frog.rect.center = platform.rect.center
        game.check_collisions()
        assert game.frog.attached_to == platform
        mock_lose_life.assert_not_called()
        
        # 4. Landing on a diving turtle
        turtle = game.platforms[0]
        if isinstance(turtle, Turtle):
            turtle.is_diving = True
            game.frog.rect.center = turtle.rect.center
            game.check_collisions()
            mock_lose_life.assert_called_once()
            mock_lose_life.reset_mock()

        # 5. Frog is carried off-screen by a platform
        game.frog.rect.x = -5
        game.check_collisions()
        mock_lose_life.assert_called_once()
        mock_lose_life.reset_mock()
        game.frog.reset_position()

        # 6. Reaching an empty home
        mocker.patch('pygame.time.get_ticks', return_value=game.start_time + 10000) # 10s elapsed
        game.frog.rect.top = 0
        home_index = 2
        game.frog.rect.centerx = game.homes[home_index].rect.centerx
        game.check_collisions()
        assert game.homes_filled[home_index] is True
        assert game.score > 0
        mock_lose_life.assert_not_called()

        # 7. Reaching a filled home
        game.check_collisions() # Try to land on the same home again
        mock_lose_life.assert_called_once()
        mock_lose_life.reset_mock()

        # 8. Hitting the wall between homes
        game.frog.rect.top = 0
        game.frog.rect.centerx = (game.homes[0].rect.right + game.homes[1].rect.left) / 2
        game.check_collisions()
        mock_lose_life.assert_called_once()

    def test_level_complete(self, game):
        """Test the logic for completing a level."""
        game.score = 100
        game.homes_filled = [True] * (TOTAL_HOMES - 1) + [False]
        
        # Reach the final home
        game.frog.rect.top = 0
        game.frog.rect.centerx = game.homes[-1].rect.centerx
        
        game.check_collisions()
        
        assert all(game.homes_filled)
        assert game.score > 1100 # 100 + 50 (home) + time_bonus + 1000 (level bonus)
        assert game.game_state == "level_complete"

    def test_draw_methods(self, game, mocker):
        """Test the main draw method and its helpers."""
        mock_draw_rect = mocker.patch('pygame.draw.rect')
        mock_blit = mocker.patch.object(game.screen, 'blit')
        
        # 1. Draw filled home
        game.homes_filled[0] = True
        game.draw()
        # Expect calls for background, water, road, homes, and a filled home frog
        assert mock_draw_rect.call_count > TOTAL_HOMES 
        
        # 2. Draw UI Time Bar
        game.game_state = "playing"
        mocker.patch('pygame.time.get_ticks', return_value=game.start_time)
        game.draw_ui()
        # Expect rects for time bar background and fill
        assert any("time_bar" in str(c) for c in mock_draw_rect.call_args_list)

        # 3. Draw Overlays
        game.game_state = "game_over"
        game.draw()
        assert any("Game Over" in str(c) for c in mock_blit.call_args_list)
        
        mock_blit.reset_mock()
        game.game_state = "level_complete"
        game.draw()
        assert any(f"Level {game.level} Complete!" in str(c) for c in mock_blit.call_args_list)

    def test_run_loop_exit(self, game, mocker):
        """Ensure the game loop terminates correctly."""
        mock_sys_exit = mocker.patch('sys.exit')
        mock_pygame_quit = mocker.patch('pygame.quit')

        # Simulate the loop running once and then exiting
        mocker.patch.object(game, 'handle_input', side_effect=lambda: setattr(game, 'running', False))
        
        with pytest.raises(SystemExit):
            game.run()

        # Verify that cleanup functions were called
        mock_pygame_quit.assert_called_once()
        mock_sys_exit.assert_called_once()