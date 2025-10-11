# frogger.py
# A Frogger game implementation using Pygame for Python 3.11.9

import pygame
import sys
import random
from typing import List, Tuple, Optional

# --- Game Constants ---
# Screen dimensions
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600
GRID_SIZE: int = 40  # Size of each grid cell (and character movement step)

# Colors (R, G, B)
COLOR_WATER: Tuple[int, int, int] = (20, 120, 200)
COLOR_ROAD: Tuple[int, int, int] = (40, 40, 40)
COLOR_SAFE_ZONE: Tuple[int, int, int] = (100, 200, 100)
COLOR_FROG: Tuple[int, int, int] = (34, 177, 76)
COLOR_HOME: Tuple[int, int, int] = (150, 75, 0)
COLOR_WHITE: Tuple[int, int, int] = (255, 255, 255)
COLOR_RED: Tuple[int, int, int] = (255, 0, 0)
COLOR_YELLOW: Tuple[int, int, int] = (255, 255, 0)

# Game settings
MAX_LIVES: int = 3
TOTAL_HOMES: int = 5
LEVEL_START_TIME: int = 60  # in seconds

# --- Class Definitions ---

class GameObject:
    """คลาสพื้นฐานสำหรับวัตถุทั้งหมดในเกม"""
    def __init__(self, x: int, y: int, width: int, height: int, color: Tuple[int, int, int]):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, screen: pygame.Surface) -> None:
        """วาดวัตถุลงบนหน้าจอ"""
        pygame.draw.rect(screen, self.color, self.rect)

class Frog(GameObject):
    """คลาสสำหรับผู้เล่น (กบ)"""
    def __init__(self, x: int, y: int):
        super().__init__(x, y, GRID_SIZE, GRID_SIZE, COLOR_FROG)
        self.start_x = x
        self.start_y = y
        self.attached_to: Optional[MovingObject] = None

    def move(self, dx: int, dy: int) -> None:
        """เคลื่อนที่กบตามการเปลี่ยนแปลง dx, dy"""
        self.rect.x += dx * GRID_SIZE
        self.rect.y += dy * GRID_SIZE
        self.detach()

    def update_position_on_platform(self) -> None:
        """อัปเดตตำแหน่งของกบ หากเกาะอยู่บนวัตถุที่เคลื่อนที่"""
        if self.attached_to:
            self.rect.x += self.attached_to.speed

    def attach_to(self, obj: 'MovingObject') -> None:
        """ทำให้กบเกาะติดกับวัตถุ (ขอนไม้/เต่า)"""
        self.attached_to = obj

    def detach(self) -> None:
        """ทำให้กบหลุดจากการเกาะ"""
        self.attached_to = None

    def reset_position(self) -> None:
        """รีเซ็ตตำแหน่งกบไปที่จุดเริ่มต้น"""
        self.rect.x = self.start_x
        self.rect.y = self.start_y
        self.detach()
        
    def is_on_screen(self) -> bool:
        """ตรวจสอบว่ากบยังอยู่ในขอบเขตหน้าจอหรือไม่"""
        return 0 <= self.rect.x < SCREEN_WIDTH

class MovingObject(GameObject):
    """คลาสสำหรับวัตถุที่เคลื่อนที่ (รถ, ขอนไม้, เต่า)"""
    def __init__(self, x: int, y: int, width: int, height: int, color: Tuple[int, int, int], speed: float):
        super().__init__(x, y, width, height, color)
        self.speed = speed

    def move(self) -> None:
        """เคลื่อนที่วัตถุตามความเร็ว"""
        self.rect.x += self.speed
        # วนกลับมาเมื่อตกขอบจอ
        if self.speed > 0 and self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0
        elif self.speed < 0 and self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH

class Turtle(MovingObject):
    """คลาสสำหรับเต่า (สามารถดำน้ำได้)"""
    def __init__(self, x: int, y: int, speed: float, dive_interval: int, dive_duration: int):
        super().__init__(x, y, GRID_SIZE * 2, GRID_SIZE, COLOR_YELLOW, speed)
        self.dive_interval = dive_interval
        self.dive_duration = dive_duration
        self.timer = 0
        self.is_diving = False

    def update(self, dt: float) -> None:
        """อัปเดตสถานะการดำน้ำของเต่า"""
        self.timer += dt
        if self.is_diving:
            if self.timer >= self.dive_duration:
                self.is_diving = False
                self.timer = 0
        else:
            if self.timer >= self.dive_interval:
                self.is_diving = True
                self.timer = 0

    def draw(self, screen: pygame.Surface) -> None:
        """วาดเต่า (จะไม่วาดถ้ากำลังดำน้ำ)"""
        if not self.is_diving:
            super().draw(screen)

class Game:
    """คลาสหลักสำหรับจัดการสถานะและลูปของเกม"""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Frogger by AI Expert")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.game_over_font = pygame.font.Font(None, 72)
        self.running = True
        self.game_state = "playing" # "playing", "game_over", "level_complete"
        self.reset_game()

    def reset_game(self) -> None:
        """รีเซ็ตค่าทั้งหมดเพื่อเริ่มเกมใหม่"""
        self.lives = MAX_LIVES
        self.homes_filled = [False] * TOTAL_HOMES
        self.level = 1
        self.score = 0
        self.setup_level()

    def setup_level(self) -> None:
        """ตั้งค่าสำหรับด่านปัจจุบัน"""
        self.game_state = "playing"
        self.start_time = pygame.time.get_ticks() 
        self.time_limit = LEVEL_START_TIME * 1000 # milliseconds

        start_x = (SCREEN_WIDTH - GRID_SIZE) // 2
        start_y = SCREEN_HEIGHT - GRID_SIZE
        self.frog = Frog(start_x, start_y)

        # กำหนดโซนต่างๆ
        self.water_rect = pygame.Rect(0, GRID_SIZE, SCREEN_WIDTH, GRID_SIZE * 6)
        self.road_rect = pygame.Rect(0, GRID_SIZE * 8, SCREEN_WIDTH, GRID_SIZE * 6)
        self.safe_zone_rect = pygame.Rect(0, GRID_SIZE * 7, SCREEN_WIDTH, GRID_SIZE)

        # สร้างบ้าน
        self.homes = self._create_homes()
        
        # สร้างสิ่งกีดขวาง
        self.obstacles: List[MovingObject] = self._create_obstacles()
        self.platforms: List[MovingObject] = self._create_platforms()
        
    def _create_homes(self) -> List[GameObject]:
        """สร้างช่องบ้านที่ด้านบนของจอ"""
        homes = []
        home_width = SCREEN_WIDTH // TOTAL_HOMES
        for i in range(TOTAL_HOMES):
            x = i * home_width
            y = 0
            homes.append(GameObject(x, y, home_width, GRID_SIZE, COLOR_HOME))
        return homes

    def _create_obstacles(self) -> List[MovingObject]:
        """สร้างรถในโซนถนน"""
        obstacles = []
        # Lane 1 (bottom)
        for i in range(3):
            obstacles.append(MovingObject(i * 250, 13 * GRID_SIZE, GRID_SIZE * 2, GRID_SIZE, COLOR_RED, 2 + self.level * 0.5))
        # Lane 2
        for i in range(2):
            obstacles.append(MovingObject(i * 400, 12 * GRID_SIZE, GRID_SIZE * 3, GRID_SIZE, COLOR_WHITE, -2 - self.level * 0.5))
        # Lane 3
        for i in range(4):
            obstacles.append(MovingObject(i * 200, 11 * GRID_SIZE, GRID_SIZE, GRID_SIZE, COLOR_YELLOW, 3 + self.level * 0.5))
        # Lane 4
        for i in range(2):
            obstacles.append(MovingObject(i * 350, 10 * GRID_SIZE, GRID_SIZE*4, GRID_SIZE, COLOR_RED, -3 - self.level * 0.5))
        # Lane 5 (top)
        for i in range(3):
            obstacles.append(MovingObject(i * 280, 9 * GRID_SIZE, GRID_SIZE*2, GRID_SIZE, COLOR_WHITE, 1.5 + self.level * 0.5))
        return obstacles

    def _create_platforms(self) -> List[MovingObject]:
        """สร้างขอนไม้และเต่าในโซนแม่น้ำ"""
        platforms = []
        # Lane 1 (bottom of river) - Turtles
        for i in range(4):
            platforms.append(Turtle(i * 200, 6 * GRID_SIZE, -1 - self.level * 0.2, 3, 2))
        # Lane 2 - Logs
        for i in range(3):
            platforms.append(MovingObject(i * 300, 5 * GRID_SIZE, GRID_SIZE * 4, GRID_SIZE, COLOR_HOME, 2 + self.level * 0.2))
        # Lane 3 - Turtles
        for i in range(3):
            platforms.append(Turtle(i * 270, 4 * GRID_SIZE, -2 - self.level * 0.2, 4, 1.5))
        # Lane 4 - Logs
        for i in range(2):
            platforms.append(MovingObject(i * 450, 3 * GRID_SIZE, GRID_SIZE * 6, GRID_SIZE, COLOR_HOME, 3 + self.level * 0.2))
        # Lane 5 (top of river) - Logs
        for i in range(3):
            platforms.append(MovingObject(i * 250, 2 * GRID_SIZE, GRID_SIZE * 3, GRID_SIZE, COLOR_HOME, -2 - self.level * 0.2))
        return platforms

    def handle_input(self) -> None:
        """จัดการ Input จากผู้เล่น"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if self.game_state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.frog.rect.top > 0:
                        self.frog.move(0, -1)
                    elif event.key == pygame.K_DOWN and self.frog.rect.bottom < SCREEN_HEIGHT:
                        self.frog.move(0, 1)
                    elif event.key == pygame.K_LEFT and self.frog.rect.left > 0:
                        self.frog.move(-1, 0)
                    elif event.key == pygame.K_RIGHT and self.frog.rect.right < SCREEN_WIDTH:
                        self.frog.move(1, 0)
            elif self.game_state in ["game_over", "level_complete"]:
                 if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    if self.game_state == "game_over":
                        self.reset_game()
                    else: # level_complete
                        self.level += 1
                        self.homes_filled = [False] * TOTAL_HOMES
                        self.setup_level()


    def update(self) -> None:
        """อัปเดตสถานะของทุกวัตถุในเกม"""
        if self.game_state != "playing":
            return
            
        dt = self.clock.get_time() / 1000.0 # Delta time in seconds

        # Update movable objects
        for obj in self.obstacles + self.platforms:
            obj.move()
            if isinstance(obj, Turtle):
                obj.update(dt)

        self.frog.update_position_on_platform()
        
        self.check_collisions()
        self.check_time()

    def check_collisions(self) -> None:
        """ตรวจสอบการชนและสถานะต่างๆ ของกบ"""
        # ชนรถ
        if self.frog.rect.collidelist(self.obstacles) != -1:
            self.lose_life()
            return

        # เช็คในโซนแม่น้ำ
        if self.water_rect.contains(self.frog.rect):
            on_platform = False
            for p in self.platforms:
                # ถ้ากบอยู่บน platform ที่มองเห็นได้
                is_diving_turtle = isinstance(p, Turtle) and p.is_diving
                if p.rect.colliderect(self.frog.rect) and not is_diving_turtle:
                    self.frog.attach_to(p)
                    on_platform = True
                    break
            if not on_platform:
                self.lose_life()
                return
        else: # ไม่ได้อยู่ในโซนน้ำ ต้อง detach
            self.frog.detach()
            
        # กบออกจากขอบจอ (ขณะอยู่บน platform)
        if not self.frog.is_on_screen():
            self.lose_life()
            return
            
        # กบถึงบ้าน
        if self.frog.rect.top < GRID_SIZE:
            home_index = self.frog.rect.centerx // (SCREEN_WIDTH // TOTAL_HOMES)
            if 0 <= home_index < TOTAL_HOMES:
                if not self.homes_filled[home_index]:
                    self.score += 50 # คะแนนเมื่อถึงบ้าน
                    # คะแนนโบนัสตามเวลาที่เหลือ
                    time_bonus = int((self.time_limit - (pygame.time.get_ticks() - self.start_time)) / 1000)
                    self.score += time_bonus
                    
                    self.homes_filled[home_index] = True
                    self.frog.reset_position()
                    
                    if all(self.homes_filled):
                        self.score += 1000 # โบนัสผ่านด่าน
                        self.game_state = "level_complete"
                else: # ชนบ้านที่เต็มแล้ว
                    self.lose_life()
            else: # ชนกำแพงระหว่างบ้าน
                self.lose_life()

    def check_time(self) -> None:
        """ตรวจสอบเวลาที่เหลือ"""
        elapsed_time = pygame.time.get_ticks() - self.start_time
        if elapsed_time >= self.time_limit:
            self.lose_life()

    def lose_life(self) -> None:
        """จัดการเมื่อกบเสียชีวิต"""
        self.lives -= 1
        if self.lives <= 0:
            self.game_state = "game_over"
        else:
            self.frog.reset_position()
            self.start_time = pygame.time.get_ticks() # Reset timer for the new life

    def draw(self) -> None:
        """วาดทุกอย่างลงบนหน้าจอ"""
        # พื้นหลัง
        self.screen.fill(COLOR_SAFE_ZONE)
        pygame.draw.rect(self.screen, COLOR_WATER, self.water_rect)
        pygame.draw.rect(self.screen, COLOR_ROAD, self.road_rect)
        
        # บ้าน
        for i, home in enumerate(self.homes):
            home.draw(self.screen)
            if self.homes_filled[i]:
                filled_rect = pygame.Rect(home.rect.x, home.rect.y, GRID_SIZE, GRID_SIZE)
                filled_rect.center = home.rect.center
                pygame.draw.rect(self.screen, COLOR_FROG, filled_rect)

        # วัตถุ
        for obj in self.obstacles + self.platforms:
            obj.draw(self.screen)

        # กบ
        self.frog.draw(self.screen)
        
        # UI (Text)
        self.draw_ui()

        # หน้าจอ Game Over / Level Complete
        if self.game_state == "game_over":
            self.draw_overlay("Game Over")
        elif self.game_state == "level_complete":
            self.draw_overlay(f"Level {self.level} Complete!")

        pygame.display.flip()
        
    def draw_ui(self) -> None:
        """วาดส่วนติดต่อผู้ใช้ (ชีวิต, คะแนน, เวลา)"""
        # Lives
        lives_text = self.font.render(f"Lives: {self.lives}", True, COLOR_WHITE)
        self.screen.blit(lives_text, (10, SCREEN_HEIGHT - 35))
        
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_WHITE)
        score_rect = score_text.get_rect(centerx=SCREEN_WIDTH / 2, y=SCREEN_HEIGHT - 35)
        self.screen.blit(score_text, score_rect)
        
        # Time bar
        elapsed_time = pygame.time.get_ticks() - self.start_time
        time_ratio = 1.0 - (elapsed_time / self.time_limit)
        if self.game_state == "playing" and time_ratio > 0:
            bar_width = 200
            fill_width = int(bar_width * time_ratio)
            time_bar_bg = pygame.Rect(SCREEN_WIDTH - bar_width - 10, SCREEN_HEIGHT - 30, bar_width, 20)
            time_bar_fill = pygame.Rect(SCREEN_WIDTH - bar_width - 10, SCREEN_HEIGHT - 30, fill_width, 20)
            pygame.draw.rect(self.screen, COLOR_RED, time_bar_bg)
            pygame.draw.rect(self.screen, COLOR_YELLOW, time_bar_fill)
            
    def draw_overlay(self, message: str) -> None:
        """วาดข้อความทับบนหน้าจอ (เช่น Game Over)"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        
        text = self.game_over_font.render(message, True, COLOR_WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40))
        
        prompt_font = pygame.font.Font(None, 30)
        prompt_text = prompt_font.render("Press ENTER to continue", True, COLOR_WHITE)
        prompt_rect = prompt_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 30))

        self.screen.blit(overlay, (0, 0))
        self.screen.blit(text, text_rect)
        self.screen.blit(prompt_text, prompt_rect)

    def run(self) -> None:
        """เมธอดหลักในการรันเกมลูป"""
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)  # จำกัด Frame rate ที่ 60 FPS
        
        # หากออกจากลูป ให้ปิด Pygame
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()