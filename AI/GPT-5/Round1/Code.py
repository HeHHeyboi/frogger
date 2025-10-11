"""
Frogger - A grid-based 2D arcade game implemented with Pygame.

Overview:
- Resolution: 800x600 pixels, grid size 40px (20 columns x 15 rows).
- Zones:
  - Home Zone (top): 5 goal slots horizontally across row 0 (y: 0..40).
  - River Zone: 5 lanes (rows 1..5, y: 40..240) with moving platforms (logs/turtles).
  - Median Strip: 1 row (row 6, y: 240..280).
  - Road Zone: 5 lanes (rows 7..11, y: 280..480) with vehicles moving both directions.
  - Safe Start Zone: bottom row (row 12, y: 480..520).
- HUD: Shows lives (frog icons), score, time bar that decreases, and level.

Gameplay:
- Controls: Arrow keys move the frog by one grid step (40px).
- Death Conditions:
  - Hit by a vehicle.
  - Drowned in river (not on a platform).
  - Attempted jump out of screen bounds.
  - Timer depleted.
- Scoring:
  - +10 per forward jump (up arrow) if move is valid.
  - +50 when reaching an empty home slot.
  - +1000 bonus when all 5 home slots are filled.
- Lives: Start with 5; on death, lose 1 and reset the frog to start.
- Level-up: When all 5 homes are filled, reset homes, increase all obstacle/platform speeds by 10%, and continue to next level.

Game States:
- START: Shows title and “Press Enter to Start”.
- PLAYING: Main game loop.
- GAME_OVER: Shows final score and “Press Enter to Restart”.

This module is self-contained and renders using pygame.draw primitives and pygame.font for text.
Run this file to play locally. For testing in headless mode, the Game can be instantiated with headless=True.
"""

from __future__ import annotations

import math
import os
import sys
from typing import List, Optional, Sequence, Tuple

import pygame


# =========================
# Settings and Constants
# =========================

# Screen
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600
GRID_SIZE: int = 40
FPS: int = 60

# Gameplay
START_LIVES: int = 5
TIME_LIMIT_SECONDS: float = 45.0
FORWARD_SCORE: int = 10
HOME_SCORE: int = 50
ALL_HOME_BONUS: int = 1000
LEVEL_SPEED_MULTIPLIER: float = 1.10  # +10%

# Zones (in pixels)
HOME_Y_TOP: int = 0
HOME_Y_BOTTOM: int = GRID_SIZE  # 0..40
RIVER_Y_TOP: int = GRID_SIZE  # 40
RIVER_Y_BOTTOM: int = GRID_SIZE * 6  # 240
MEDIAN_Y_TOP: int = GRID_SIZE * 6  # 240
MEDIAN_Y_BOTTOM: int = GRID_SIZE * 7  # 280
ROAD_Y_TOP: int = GRID_SIZE * 7  # 280
ROAD_Y_BOTTOM: int = GRID_SIZE * 12  # 480
SAFE_Y_TOP: int = GRID_SIZE * 12  # 480
SAFE_Y_BOTTOM: int = GRID_SIZE * 13  # 520

# Colors
COLOR_BG: Tuple[int, int, int] = (20, 20, 20)
COLOR_SAFE: Tuple[int, int, int] = (32, 160, 50)
COLOR_MEDIAN: Tuple[int, int, int] = (50, 50, 50)
COLOR_ROAD: Tuple[int, int, int] = (30, 30, 30)
COLOR_RIVER: Tuple[int, int, int] = (20, 60, 160)
COLOR_HOME: Tuple[int, int, int] = (10, 100, 10)
COLOR_HOME_FILLED: Tuple[int, int, int] = (0, 180, 0)
COLOR_PLAYER: Tuple[int, int, int] = (60, 230, 60)
COLOR_VEHICLE_A: Tuple[int, int, int] = (220, 60, 60)
COLOR_VEHICLE_B: Tuple[int, int, int] = (220, 140, 60)
COLOR_VEHICLE_C: Tuple[int, int, int] = (160, 60, 220)
COLOR_LOG: Tuple[int, int, int] = (160, 110, 60)
COLOR_TURTLE: Tuple[int, int, int] = (60, 200, 200)
COLOR_TEXT: Tuple[int, int, int] = (240, 240, 240)
COLOR_TIMEBAR_BG: Tuple[int, int, int] = (60, 60, 60)
COLOR_TIMEBAR: Tuple[int, int, int] = (240, 200, 60)

# Player
PLAYER_SIZE: int = 32
PLAYER_STEP: int = GRID_SIZE

# Vehicles: three archetypes (width, height, base_speed, color)
VEHICLE_TYPES: Tuple[Tuple[int, int, float, Tuple[int, int, int]], ...] = (
    (50, 30, 180.0, COLOR_VEHICLE_A),   # small fast car
    (70, 30, 140.0, COLOR_VEHICLE_B),   # medium car
    (120, 30, 100.0, COLOR_VEHICLE_C),  # truck
)

# Platforms: two archetypes (width, height, base_speed, color)
PLATFORM_TYPES: Tuple[Tuple[int, int, float, Tuple[int, int, int]], ...] = (
    (120, 30, 100.0, COLOR_LOG),
    (160, 30, 80.0, COLOR_TURTLE),
)

# Home slots
HOME_SLOTS_COUNT: int = 5


# =========================
# Utility
# =========================

def in_rect_bounds(rect: pygame.Rect, width: int, height: int) -> bool:
    """Return True if a rect is fully within screen bounds.

    Parameters:
        rect: pygame.Rect - rectangle to check.
        width: int - screen width.
        height: int - screen height.

    Returns:
        True if rect is fully within bounds, False otherwise.
    """
    return rect.left >= 0 and rect.right <= width and rect.top >= 0 and rect.bottom <= height


# =========================
# Entity Classes
# =========================

class Entity:
    """Base class for all moving objects with a rectangle and color."""
    def __init__(self, x: float, y: float, w: int, h: int, color: Tuple[int, int, int]) -> None:
        """Initialize an Entity.

        Parameters:
            x: float - initial x position (top-left).
            y: float - initial y position (top-left).
            w: int - width of the entity.
            h: int - height of the entity.
            color: Tuple[int, int, int] - RGB color for drawing.
        """
        self.x: float = float(x)
        self.y: float = float(y)
        self.w: int = w
        self.h: int = h
        self.color: Tuple[int, int, int] = color
        self.rect: pygame.Rect = pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def sync_rect(self) -> None:
        """Synchronize the pygame.Rect with current float position."""
        self.rect.x = int(round(self.x))
        self.rect.y = int(round(self.y))

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the entity on a given surface.

        Parameters:
            surface: pygame.Surface - surface to draw on.
        """
        pygame.draw.rect(surface, self.color, self.rect)


class Vehicle(Entity):
    """Vehicle obstacle that moves horizontally and wraps around screen."""
    def __init__(self, x: float, y: float, w: int, h: int, color: Tuple[int, int, int],
                 speed: float, direction: int) -> None:
        """Initialize a Vehicle.

        Parameters:
            x, y, w, h, color: See Entity.
            speed: float - speed in pixels per second (positive).
            direction: int - 1 for right, -1 for left.
        """
        super().__init__(x, y, w, h, color)
        self.speed: float = float(speed)
        self.direction: int = 1 if direction >= 0 else -1

    @property
    def vx(self) -> float:
        """Horizontal velocity in pixels per second."""
        return self.speed * self.direction

    def update(self, dt: float, screen_width: int) -> None:
        """Update position and wrap around if off-screen.

        Parameters:
            dt: float - delta time in seconds.
            screen_width: int - width for wrapping.
        """
        self.x += self.vx * dt
        # Wrap logic
        if self.direction > 0 and self.rect.left > screen_width:
            self.x = -self.w
        elif self.direction < 0 and self.rect.right < 0:
            self.x = screen_width
        self.sync_rect()


class Platform(Entity):
    """Floating platform in the river that carries the player."""
    def __init__(self, x: float, y: float, w: int, h: int, color: Tuple[int, int, int],
                 speed: float, direction: int) -> None:
        """Initialize a Platform.

        Parameters:
            x, y, w, h, color: See Entity.
            speed: float - speed in pixels per second (positive).
            direction: int - 1 for right, -1 for left.
        """
        super().__init__(x, y, w, h, color)
        self.speed: float = float(speed)
        self.direction: int = 1 if direction >= 0 else -1

    @property
    def vx(self) -> float:
        """Horizontal velocity in pixels per second."""
        return self.speed * self.direction

    def update(self, dt: float, screen_width: int) -> None:
        """Update position and wrap around if off-screen.

        Parameters:
            dt: float - delta time in seconds.
            screen_width: int - width for wrapping.
        """
        self.x += self.vx * dt
        # Wrap logic
        if self.direction > 0 and self.rect.left > screen_width:
            self.x = -self.w
        elif self.direction < 0 and self.rect.right < 0:
            self.x = screen_width
        self.sync_rect()


class HomeSlot:
    """A target slot at the top that can be filled by the player."""
    def __init__(self, rect: pygame.Rect) -> None:
        """Initialize a HomeSlot.

        Parameters:
            rect: pygame.Rect - rectangle area representing the slot.
        """
        self.rect: pygame.Rect = rect
        self.filled: bool = False

    def is_hit(self, player_rect: pygame.Rect) -> bool:
        """Return True if player rect overlaps this slot.

        Parameters:
            player_rect: pygame.Rect - player rectangle.

        Returns:
            True if colliding, else False.
        """
        return self.rect.colliderect(player_rect)

    def fill(self) -> None:
        """Mark this slot as filled."""
        self.filled = True

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the slot.

        Parameters:
            surface: pygame.Surface - surface to draw on.
        """
        color = COLOR_HOME_FILLED if self.filled else COLOR_HOME
        pygame.draw.rect(surface, color, self.rect)


class Player:
    """The controllable frog character."""
    def __init__(self, start_x: int, start_y: int, size: int = PLAYER_SIZE) -> None:
        """Initialize a Player.

        Parameters:
            start_x: int - starting x coordinate (top-left).
            start_y: int - starting y coordinate (top-left).
            size: int - square size of the player.
        """
        self.size: int = size
        self.start_x: int = start_x
        self.start_y: int = start_y
        self.rect: pygame.Rect = pygame.Rect(start_x, start_y, self.size, self.size)
        self.on_platform: Optional[Platform] = None

    def reset(self) -> None:
        """Reset player to starting position and detach from platform."""
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.on_platform = None

    def move(self, dx: int, dy: int) -> None:
        """Move player by a delta.

        Parameters:
            dx: int - delta x in pixels.
            dy: int - delta y in pixels.
        """
        self.rect.move_ip(dx, dy)

    def set_position(self, x: int, y: int) -> None:
        """Set player's top-left position.

        Parameters:
            x: int - new x.
            y: int - new y.
        """
        self.rect.x = x
        self.rect.y = y

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the player.

        Parameters:
            surface: pygame.Surface - surface to draw on.
        """
        pygame.draw.rect(surface, COLOR_PLAYER, self.rect)
        # Simple eye details
        eye_w = max(2, self.size // 8)
        eye_h = eye_w
        left_eye = pygame.Rect(self.rect.x + self.size // 4, self.rect.y + self.size // 4, eye_w, eye_h)
        right_eye = pygame.Rect(self.rect.x + self.size // 2, self.rect.y + self.size // 4, eye_w, eye_h)
        pygame.draw.rect(surface, (0, 0, 0), left_eye)
        pygame.draw.rect(surface, (0, 0, 0), right_eye)


# =========================
# Level/Lane Construction
# =========================

class Lane:
    """A lane that contains multiple Vehicles or Platforms at the same Y coordinate."""
    def __init__(self, y: int, kind: str, direction: int, speed: float,
                 count: int, type_index: int = 0) -> None:
        """Initialize a Lane.

        Parameters:
            y: int - top y of the lane (objects are aligned with some padding).
            kind: str - 'road' or 'river'.
            direction: int - 1 for right, -1 for left.
            speed: float - base speed in pixels per second for objects in this lane.
            count: int - number of objects to place in this lane.
            type_index: int - index into VEHICLE_TYPES or PLATFORM_TYPES for size/color.
        """
        self.y: int = y
        self.kind: str = kind
        self.direction: int = 1 if direction >= 0 else -1
        self.base_speed: float = float(speed)
        self.count: int = count
        self.type_index: int = type_index
        self.objects: List[Entity] = []

    def build(self, speed_multiplier: float = 1.0, screen_width: int = SCREEN_WIDTH) -> None:
        """Create and place objects evenly spaced across the lane.

        Parameters:
            speed_multiplier: float - multiplier to adjust object speed.
            screen_width: int - used for spacing.
        """
        self.objects.clear()
        spacing = screen_width / float(self.count)
        if self.kind == "road":
            w, h, base, color = VEHICLE_TYPES[self.type_index % len(VEHICLE_TYPES)]
            speed = base * speed_multiplier
            y_center = self.y + (GRID_SIZE - h) // 2
            for i in range(self.count):
                x = spacing * i
                v = Vehicle(x, y_center, w, h, color, speed, self.direction)
                v.sync_rect()
                self.objects.append(v)
        elif self.kind == "river":
            w, h, base, color = PLATFORM_TYPES[self.type_index % len(PLATFORM_TYPES)]
            speed = base * speed_multiplier
            y_center = self.y + (GRID_SIZE - h) // 2
            for i in range(self.count):
                x = spacing * i
                p = Platform(x, y_center, w, h, color, speed, self.direction)
                p.sync_rect()
                self.objects.append(p)
        else:
            raise ValueError("Invalid lane kind; expected 'road' or 'river'")

    def increase_speed(self, factor: float) -> None:
        """Increase speed of all objects by a factor.

        Parameters:
            factor: float - multiplier for speed.
        """
        for obj in self.objects:
            if isinstance(obj, (Vehicle, Platform)):
                obj.speed *= factor

    def update(self, dt: float, screen_width: int) -> None:
        """Update all objects in the lane.

        Parameters:
            dt: float - delta time in seconds.
            screen_width: int - used for wrapping logic.
        """
        for obj in self.objects:
            if isinstance(obj, Vehicle):
                obj.update(dt, screen_width)
            elif isinstance(obj, Platform):
                obj.update(dt, screen_width)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw objects in the lane.

        Parameters:
            surface: pygame.Surface - surface to draw on.
        """
        for obj in self.objects:
            obj.draw(surface)


# =========================
# Game Class
# =========================

class Game:
    """Main game controller handling state, entities, updates, rendering, and input."""
    def __init__(self, headless: bool = False) -> None:
        """Initialize the Game.

        Parameters:
            headless: bool - if True, use an off-screen Surface instead of a display window.
        """
        self.headless: bool = headless
        pygame.init()
        pygame.font.init()
        flags = 0
        if self.headless:
            # Off-screen surface for tests
            self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
            pygame.display.set_caption("Frogger (OOP)")
        self.clock = pygame.time.Clock()

        # Fonts
        self.font = pygame.font.SysFont("Arial", 20)
        self.font_large = pygame.font.SysFont("Arial", 42, bold=True)

        # State
        self.state: str = "START"  # START, PLAYING, GAME_OVER
        self.level: int = 1
        self.score: int = 0
        self.lives: int = START_LIVES
        self.time_left: float = TIME_LIMIT_SECONDS
        self.last_death_reason: Optional[str] = None

        # Player
        start_x = (SCREEN_WIDTH // 2) - (PLAYER_SIZE // 2)
        start_y = SAFE_Y_TOP + (GRID_SIZE - PLAYER_SIZE) // 2
        self.player = Player(start_x, start_y)

        # Homes
        self.home_slots: List[HomeSlot] = self._create_home_slots()

        # Lanes
        self.road_lanes: List[Lane] = []
        self.river_lanes: List[Lane] = []
        self._build_lanes()

    def _create_home_slots(self) -> List[HomeSlot]:
        """Create 5 equally-spaced home slots across the top row.

        Returns:
            List of HomeSlot objects.
        """
        slots: List[HomeSlot] = []
        slot_w = SCREEN_WIDTH // HOME_SLOTS_COUNT
        for i in range(HOME_SLOTS_COUNT):
            x = i * slot_w + 10
            w = slot_w - 20
            rect = pygame.Rect(x, HOME_Y_TOP + 6, w, HOME_Y_BOTTOM - 12)
            slots.append(HomeSlot(rect))
        return slots

    def _build_lanes(self, speed_multiplier: float = 1.0) -> None:
        """Build or rebuild the lanes for road and river.

        Parameters:
            speed_multiplier: float - global multiplier for lane object speeds.
        """
        self.road_lanes.clear()
        self.river_lanes.clear()

        # Road lanes: rows 7..11, alternate directions, 5 lanes
        for i in range(5):
            row_y = ROAD_Y_TOP + i * GRID_SIZE
            direction = 1 if i % 2 == 0 else -1
            type_index = i % len(VEHICLE_TYPES)
            base_speed = VEHICLE_TYPES[type_index][2]
            lane = Lane(y=row_y, kind="road", direction=direction,
                        speed=base_speed, count=3 + (i % 2), type_index=type_index)
            lane.build(speed_multiplier=speed_multiplier, screen_width=SCREEN_WIDTH)
            self.road_lanes.append(lane)

        # River lanes: rows 1..5, alternate directions, 5 lanes
        for i in range(5):
            row_y = RIVER_Y_TOP + i * GRID_SIZE
            direction = -1 if i % 2 == 0 else 1
            type_index = i % len(PLATFORM_TYPES)
            base_speed = PLATFORM_TYPES[type_index][2]
            lane = Lane(y=row_y, kind="river", direction=direction,
                        speed=base_speed, count=3 + (i % 2), type_index=type_index)
            lane.build(speed_multiplier=speed_multiplier, screen_width=SCREEN_WIDTH)
            self.river_lanes.append(lane)

    def start_game(self) -> None:
        """Transition from START or GAME_OVER to PLAYING and reset all state."""
        self.state = "PLAYING"
        self.level = 1
        self.score = 0
        self.lives = START_LIVES
        self.time_left = TIME_LIMIT_SECONDS
        self.last_death_reason = None
        self.player.reset()
        for slot in self.home_slots:
            slot.filled = False
        self._build_lanes()

    def level_up(self) -> None:
        """Advance to the next level, reset homes, increase speeds by 10%."""
        self.level += 1
        # Increase speed of all existing objects
        for lane in (self.road_lanes + self.river_lanes):
            lane.increase_speed(LEVEL_SPEED_MULTIPLIER)
        # Reset all home slots
        for slot in self.home_slots:
            slot.filled = False
        # Reset player and timer
        self.player.reset()
        self.time_left = TIME_LIMIT_SECONDS

    def handle_input(self, events: Sequence[pygame.event.Event]) -> None:
        """Handle input events for player movement and state transitions.

        Parameters:
            events: sequence of pygame events.
        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.state in ("START", "GAME_OVER") and event.key == pygame.K_RETURN:
                    self.start_game()
                    continue
                if self.state != "PLAYING":
                    continue
                dx, dy = 0, 0
                if event.key == pygame.K_LEFT:
                    dx = -PLAYER_STEP
                elif event.key == pygame.K_RIGHT:
                    dx = PLAYER_STEP
                elif event.key == pygame.K_UP:
                    dy = -PLAYER_STEP
                elif event.key == pygame.K_DOWN:
                    dy = PLAYER_STEP
                else:
                    continue

                # Proposed new position
                proposed = self.player.rect.move(dx, dy)
                if not in_rect_bounds(proposed, SCREEN_WIDTH, SCREEN_HEIGHT):
                    # Attempt to move out-of-bounds results in death
                    self.die("out_of_bounds")
                    continue

                # Move is valid
                self.player.move(dx, dy)

                # Score for forward jumps (up)
                if dy < 0:
                    self.score += FORWARD_SCORE

    def _check_vehicle_collisions(self) -> bool:
        """Check collisions with vehicles.

        Returns:
            True if a collision occurred, else False.
        """
        for lane in self.road_lanes:
            for obj in lane.objects:
                if isinstance(obj, Vehicle) and obj.rect.colliderect(self.player.rect):
                    return True
        return False

    def _check_platform_under_player(self) -> Optional[Platform]:
        """Check if the player stands on a platform in the river zone.

        Returns:
            Platform if under player, else None.
        """
        if not (RIVER_Y_TOP <= self.player.rect.top < RIVER_Y_BOTTOM):
            return None
        for lane in self.river_lanes:
            for obj in lane.objects:
                if isinstance(obj, Platform) and obj.rect.colliderect(self.player.rect):
                    return obj
        return None

    def _check_home_collision(self) -> bool:
        """Check collision with a home slot and fill if empty.

        Returns:
            True if home reached and accepted; False otherwise.
        """
        if not (HOME_Y_TOP <= self.player.rect.top < HOME_Y_BOTTOM):
            return False
        for slot in self.home_slots:
            if not slot.filled and slot.is_hit(self.player.rect):
                slot.fill()
                self.score += HOME_SCORE
                self.player.reset()
                self.time_left = TIME_LIMIT_SECONDS
                # Bonus if all filled now
                if all(s.filled for s in self.home_slots):
                    self.score += ALL_HOME_BONUS
                    self.level_up()
                return True
        return False

    def die(self, reason: str) -> None:
        """Handle player death: decrement lives or transition to Game Over.

        Parameters:
            reason: str - reason for death, stored for diagnostics.
        """
        self.last_death_reason = reason
        self.lives -= 1
        if self.lives <= 0:
            self.state = "GAME_OVER"
            return
        # Reset for next life
        self.player.reset()
        self.time_left = TIME_LIMIT_SECONDS

    def update(self, dt: float) -> None:
        """Update game logic for a time step.

        Parameters:
            dt: float - delta time in seconds.
        """
        if self.state != "PLAYING":
            return

        # Update lanes
        for lane in self.road_lanes:
            lane.update(dt, SCREEN_WIDTH)
        for lane in self.river_lanes:
            lane.update(dt, SCREEN_WIDTH)

        # Vehicle collisions
        if self._check_vehicle_collisions():
            self.die("vehicle")
            return

        # River logic
        on_platform = self._check_platform_under_player()
        if RIVER_Y_TOP <= self.player.rect.top < RIVER_Y_BOTTOM:
            if on_platform is None:
                self.die("drown")
                return
            # Carry the player with platform
            self.player.on_platform = on_platform
            self.player.rect.x += int(round(on_platform.vx * dt))
            # Out-of-bounds due to carry?
            if not in_rect_bounds(self.player.rect, SCREEN_WIDTH, SCREEN_HEIGHT):
                self.die("out_of_bounds")
                return
        else:
            self.player.on_platform = None

        # Home collision
        self._check_home_collision()

        # Timer
        self.time_left -= dt
        if self.time_left <= 0.0:
            self.die("timeout")
            return

    def draw_hud(self) -> None:
        """Draw the heads-up display: lives, score, time bar, level."""
        # Lives
        for i in range(self.lives):
            x = 10 + i * (PLAYER_SIZE + 6)
            y = SAFE_Y_BOTTOM + 10
            pygame.draw.rect(self.screen, COLOR_PLAYER, pygame.Rect(x, y, 20, 20))

        # Score and Level
        text = self.font.render(f"Score: {self.score}   Level: {self.level}", True, COLOR_TEXT)
        self.screen.blit(text, (SCREEN_WIDTH - text.get_width() - 10, SAFE_Y_BOTTOM + 8))

        # Time bar
        bar_w = SCREEN_WIDTH - 20
        bar_h = 12
        bar_x = 10
        bar_y = SAFE_Y_BOTTOM + 40
        pygame.draw.rect(self.screen, COLOR_TIMEBAR_BG, pygame.Rect(bar_x, bar_y, bar_w, bar_h))
        ratio = max(0.0, min(1.0, self.time_left / TIME_LIMIT_SECONDS))
        fill_w = int(bar_w * ratio)
        pygame.draw.rect(self.screen, COLOR_TIMEBAR, pygame.Rect(bar_x, bar_y, fill_w, bar_h))

    def draw_background(self) -> None:
        """Draw static background zones and home slots."""
        self.screen.fill(COLOR_BG)
        # Home zone
        pygame.draw.rect(self.screen, COLOR_HOME, pygame.Rect(0, HOME_Y_TOP, SCREEN_WIDTH, HOME_Y_BOTTOM - HOME_Y_TOP))
        # River
        pygame.draw.rect(self.screen, COLOR_RIVER, pygame.Rect(0, RIVER_Y_TOP, SCREEN_WIDTH, RIVER_Y_BOTTOM - RIVER_Y_TOP))
        # Median
        pygame.draw.rect(self.screen, COLOR_MEDIAN, pygame.Rect(0, MEDIAN_Y_TOP, SCREEN_WIDTH, MEDIAN_Y_BOTTOM - MEDIAN_Y_TOP))
        # Road
        pygame.draw.rect(self.screen, COLOR_ROAD, pygame.Rect(0, ROAD_Y_TOP, SCREEN_WIDTH, ROAD_Y_BOTTOM - ROAD_Y_TOP))
        # Safe zone
        pygame.draw.rect(self.screen, COLOR_SAFE, pygame.Rect(0, SAFE_Y_TOP, SCREEN_WIDTH, SAFE_Y_BOTTOM - SAFE_Y_TOP))
        # Home slots
        for slot in self.home_slots:
            slot.draw(self.screen)

    def draw(self) -> None:
        """Draw the entire frame based on current game state."""
        if self.state == "START":
            self.screen.fill(COLOR_BG)
            title = self.font_large.render("Frogger", True, COLOR_TEXT)
            prompt = self.font.render("Press Enter to Start", True, COLOR_TEXT)
            self.screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 160))
            self.screen.blit(prompt, ((SCREEN_WIDTH - prompt.get_width()) // 2, 220))
        elif self.state == "GAME_OVER":
            self.screen.fill(COLOR_BG)
            title = self.font_large.render("Game Over", True, COLOR_TEXT)
            score_text = self.font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
            prompt = self.font.render("Press Enter to Restart", True, COLOR_TEXT)
            self.screen.blit(title, ((SCREEN_WIDTH - title.get_width()) // 2, 160))
            self.screen.blit(score_text, ((SCREEN_WIDTH - score_text.get_width()) // 2, 220))
            self.screen.blit(prompt, ((SCREEN_WIDTH - prompt.get_width()) // 2, 260))
        else:
            # PLAYING
            self.draw_background()
            # Draw objects
            for lane in self.road_lanes:
                lane.draw(self.screen)
            for lane in self.river_lanes:
                lane.draw(self.screen)
            # Player
            self.player.draw(self.screen)
            # HUD
            self.draw_hud()

        if not self.headless:
            pygame.display.flip()

    def run(self) -> None:
        """Run the main game loop (interactive mode)."""
        running = True
        while running:
            dt_ms = self.clock.tick(FPS)
            dt = dt_ms / 1000.0
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    running = False
            self.handle_input(events)
            self.update(dt)
            self.draw()
        pygame.quit()


def run_game() -> None:
    """Convenience function to create and run the game interactively."""
    game = Game(headless=False)
    game.run()


if __name__ == "__main__":  # pragma: no cover
    run_game()