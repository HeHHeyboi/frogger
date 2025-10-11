"""
Pytest-based unit tests for Frogger game logic.

Goals:
- Achieve 100% statement coverage across frogger.py (excluding the main guard).
- Validate Player movement, boundary constraints, and reset.
- Validate collision logic: vehicles, platforms, drowning, out-of-bounds, and timeout.
- Validate scoring: forward jump, reaching homes, full-home bonus, and level-up behavior.
- Validate game state transitions and obstacle/platform movement & wrapping.
"""

import os

# Enable headless mode for pygame before importing frogger/pygame
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import math
import pygame
import pytest

import code as frogger  # Import the game code to be tested


@pytest.fixture(autouse=True)
def pygame_init_teardown():
    """Initialize and quit pygame per test to ensure isolation."""
    pygame.init()
    pygame.font.init()
    yield
    pygame.quit()


@pytest.fixture
def game() -> frogger.Game:
    """Headless game fixture for logic testing."""
    g = frogger.Game(headless=True)
    g.state = "PLAYING"  # enter playing state directly
    g.time_left = frogger.TIME_LIMIT_SECONDS
    g.player.reset()
    # Ensure predictable initial score & lives per test
    g.score = 0
    g.lives = frogger.START_LIVES
    return g


def make_key_event(key):
    """Helper to create a KEYDOWN event."""
    return pygame.event.Event(pygame.KEYDOWN, {"key": key})


def test_player_move_all_directions_and_forward_score(game: frogger.Game):
    px, py = game.player.rect.topleft
    # Up (forward)
    game.handle_input([make_key_event(pygame.K_UP)])
    assert game.player.rect.y == py - frogger.GRID_SIZE
    assert game.score == frogger.FORWARD_SCORE

    # Left
    game.handle_input([make_key_event(pygame.K_LEFT)])
    assert game.player.rect.x == px - frogger.GRID_SIZE

    # Right
    game.handle_input([make_key_event(pygame.K_RIGHT)])
    assert game.player.rect.x == px

    # Down
    game.handle_input([make_key_event(pygame.K_DOWN)])
    assert game.player.rect.y == py


def test_player_boundary_restriction_and_out_of_bounds_death(game: frogger.Game):
    # Move down repeatedly until an out-of-bounds attempt occurs
    start_lives = game.lives
    # Place player near bottom so next DOWN triggers OOB attempt
    game.player.set_position(game.player.rect.x, frogger.SCREEN_HEIGHT - frogger.GRID_SIZE + 1)
    game.handle_input([make_key_event(pygame.K_DOWN)])
    assert game.lives == start_lives - 1
    assert game.last_death_reason == "out_of_bounds"
    # Player should be reset within bounds after death
    assert frogger.in_rect_bounds(game.player.rect, frogger.SCREEN_WIDTH, frogger.SCREEN_HEIGHT)


def test_player_reset_function(game: frogger.Game):
    game.player.move(100, -80)
    game.player.reset()
    assert game.player.rect.x == game.player.start_x
    assert game.player.rect.y == game.player.start_y
    assert game.player.on_platform is None


def move_player_to_row(game: frogger.Game, row_index: int):
    """Move player vertically to a specific grid row (0-based from top)."""
    target_y = row_index * frogger.GRID_SIZE + (frogger.GRID_SIZE - frogger.PLAYER_SIZE) // 2
    game.player.rect.y = target_y


def test_collision_with_vehicle_and_no_collision(game: frogger.Game):
    # Move player to road lane row 7
    move_player_to_row(game, 7)
    # Pick first road lane; place a vehicle onto player
    lane = game.road_lanes[0]
    veh = next(obj for obj in lane.objects if isinstance(obj, frogger.Vehicle))
    veh.x = game.player.rect.x
    veh.sync_rect()

    start_lives = game.lives
    game.update(0.016)
    assert game.lives == start_lives - 1
    assert game.last_death_reason == "vehicle"

    # Reset and ensure no collision when far away
    game.state = "PLAYING"
    game.player.reset()
    move_player_to_row(game, 7)
    veh.x = -1000  # far away
    veh.sync_rect()
    lives = game.lives
    game.update(0.016)
    assert game.lives == lives


def test_platform_carry_and_drowning(game: frogger.Game):
    # Move player to a river row (row 1)
    move_player_to_row(game, 1)
    lane = game.river_lanes[0]
    plat = next(obj for obj in lane.objects if isinstance(obj, frogger.Platform))
    # Align platform under player
    plat.x = game.player.rect.x
    plat.sync_rect()

    # Player should not drown and should be carried by platform velocity
    prev_x = game.player.rect.x
    game.update(1.0)  # dt = 1 second for clear movement
    assert game.state == "PLAYING"
    assert game.player.on_platform is not None
    expected_x = prev_x + int(round(plat.vx * 1.0))
    assert game.player.rect.x == expected_x

    # Now move player to a river row with no platform under
    game.player.reset()
    game.state = "PLAYING"
    move_player_to_row(game, 2)
    # Ensure no platforms overlap
    for lane in game.river_lanes:
        for p in lane.objects:
            if isinstance(p, frogger.Platform):
                p.x = -1000
                p.sync_rect()
    lives = game.lives
    game.update(0.016)
    assert game.lives == lives - 1
    assert game.last_death_reason == "drown"


def test_timeout_death(game: frogger.Game):
    game.time_left = 0.01
    lives = game.lives
    game.update(0.02)
    assert game.lives == lives - 1
    assert game.last_death_reason == "timeout"


def test_home_scoring_and_level_up(game: frogger.Game):
    # Put player into each empty home slot center; ensure +50 each and +1000 bonus on last
    total_before = game.score
    base_speed_first_lane = game.road_lanes[0].objects[0].speed
    for i, slot in enumerate(game.home_slots):
        # Move to home row and slot center
        game.player.set_position(slot.rect.centerx - game.player.rect.width // 2,
                                 slot.rect.centery - game.player.rect.height // 2)
        # Ensure in playing state and timer reset
        game.state = "PLAYING"
        game.time_left = frogger.TIME_LIMIT_SECONDS
        prev_level = game.level
        # Update to trigger home collision logic
        game.update(0.016)
        assert slot.filled or game.level > prev_level

    # After filling all slots, level should have increased and bonus granted
    assert game.level == 2
    # Score should be 5 * 50 + 1000 bonus (forward move points not counted here)
    assert game.score == total_before + 5 * frogger.HOME_SCORE + frogger.ALL_HOME_BONUS
    # Speed should have increased by ~10% for objects
    new_speed = game.road_lanes[0].objects[0].speed
    assert new_speed == pytest.approx(base_speed_first_lane * frogger.LEVEL_SPEED_MULTIPLIER, rel=1e-6)


def test_game_over_state_transition(game: frogger.Game):
    game.lives = 1
    game.die("test")
    assert game.state == "GAME_OVER"
    assert game.lives == 0
    # Press Enter should restart game
    game.handle_input([pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN})])
    assert game.state == "PLAYING"
    assert game.lives == frogger.START_LIVES


def test_obstacle_and_platform_update_and_wrap(game: frogger.Game):
    # Vehicle wrapping to left when moving right
    lane_v = game.road_lanes[0]
    veh = next(obj for obj in lane_v.objects if isinstance(obj, frogger.Vehicle))
    veh.direction = 1
    veh.sync_rect()
    veh.x = frogger.SCREEN_WIDTH + 10  # beyond right
    veh.sync_rect()
    veh.update(0.016, frogger.SCREEN_WIDTH)
    assert veh.rect.right <= frogger.SCREEN_WIDTH or veh.rect.left <= 0

    # Platform wrapping to right when moving left
    lane_p = game.river_lanes[0]
    plat = next(obj for obj in lane_p.objects if isinstance(obj, frogger.Platform))
    plat.direction = -1
    plat.x = -plat.w - 10
    plat.sync_rect()
    plat.update(0.016, frogger.SCREEN_WIDTH)
    assert plat.rect.left >= 0 or plat.rect.right >= frogger.SCREEN_WIDTH

    # Also via game.update to cover lane update paths
    game.state = "PLAYING"
    game.update(0.016)  # should not crash


def test_start_screen_and_restart(game: frogger.Game):
    # Simulate starting from START state with Enter
    g = frogger.Game(headless=True)
    assert g.state == "START"
    g.handle_input([pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN})])
    assert g.state == "PLAYING"

    # Simulate game over and restart
    g.state = "GAME_OVER"
    g.handle_input([pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_RETURN})])
    assert g.state == "PLAYING"


def test_lane_build_and_increase_speed(game: frogger.Game):
    # Rebuild lanes with custom multiplier and ensure speeds changed
    g = game
    lane = frogger.Lane(y=frogger.ROAD_Y_TOP, kind="road", direction=1, speed=180, count=3, type_index=0)
    lane.build(speed_multiplier=1.25)
    speeds_before = [obj.speed for obj in lane.objects if isinstance(obj, frogger.Vehicle)]
    lane.increase_speed(1.10)
    speeds_after = [obj.speed for obj in lane.objects if isinstance(obj, frogger.Vehicle)]
    for b, a in zip(speeds_before, speeds_after):
        assert a == pytest.approx(b * 1.10, rel=1e-6)


def test_helper_in_rect_bounds():
    # Fully inside
    r = pygame.Rect(10, 10, 100, 100)
    assert frogger.in_rect_bounds(r, 200, 200)
    # Outside on right
    r2 = pygame.Rect(150, 10, 100, 100)
    assert not frogger.in_rect_bounds(r2, 200, 200)
    # Outside on top
    r3 = pygame.Rect(-1, 10, 2, 2)
    assert not frogger.in_rect_bounds(r3, 200, 200)