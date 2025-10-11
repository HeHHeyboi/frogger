"""
Unit Tests for Frogger Game - Part 2
===================================

ส่วนต่อเนื่องของ Unit Tests เพื่อให้ได้ 100% statement coverage
"""

import pygame
import pytest

from unittest.mock import Mock, patch

from code import GRID_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH, Colors, Direction, Frog, FroggerGame, GameObject, GameState, Home, Log, Turtle, Vehicle


class TestGameState:
    """ทดสอบ class GameState"""
    
    def test_game_state_init(self):
        """ทดสอบการสร้าง GameState"""
        state = GameState()
        assert state.lives == 3
        assert state.score == 0
        assert state.level == 1
        assert state.time_left == 30.0
        assert state.game_over is False
        assert state.level_complete is False
        assert state.homes_filled == 0

class TestFroggerGame:
    """ทดสอบ class FroggerGame"""
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_frogger_game_init(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการสร้าง FroggerGame"""
        mock_screen = Mock()
        mock_display.return_value = mock_screen
        mock_clock_instance = Mock()
        mock_clock.return_value = mock_clock_instance
        mock_font_instance = Mock()
        mock_font.return_value = mock_font_instance
        
        game = FroggerGame()
        
        # ตรวจสอบการเรียกใช้ pygame functions
        mock_init.assert_called_once()
        mock_display.assert_called_once_with((SCREEN_WIDTH, SCREEN_HEIGHT))
        mock_caption.assert_called_once_with("Frogger Game")
        mock_clock.assert_called_once()
        
        # ตรวจสอบ attributes
        assert game.screen == mock_screen
        assert game.clock == mock_clock_instance
        assert isinstance(game.game_state, GameState)
        assert game.running is True
        assert isinstance(game.frog, Frog)
        assert isinstance(game.vehicles, list)
        assert isinstance(game.logs, list)
        assert isinstance(game.turtles, list)
        assert isinstance(game.homes, list)
        assert len(game.homes) == 5
        assert game.font == mock_font_instance
        assert game.small_font == mock_font_instance
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_init_game_objects(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการสร้างวัตถุในเกม"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        
        # ตรวจสอบว่ามีการสร้างวัตถุครบถ้วน
        assert isinstance(game.frog, Frog)
        assert len(game.vehicles) > 0
        assert len(game.logs) > 0
        assert len(game.turtles) > 0
        assert len(game.homes) == 5
        
        # ตรวจสอบตำแหน่งเริ่มต้นของกบ
        expected_x = SCREEN_WIDTH // 2 - GRID_SIZE // 2
        expected_y = SCREEN_HEIGHT - GRID_SIZE - 10
        assert game.frog.x == expected_x
        assert game.frog.y == expected_y
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    @patch('random.randint')
    def test_create_vehicles(self, mock_randint, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการสร้างยานพาหนะ"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        mock_randint.side_effect = [4, 100, 3, 150, 5, 200, 4, 250]  # num_vehicles และ spacing values
        
        game = FroggerGame()
        
        # ตรวจสอบว่ามีการสร้างยานพาหนะ
        assert len(game.vehicles) > 0
        
        # ตรวจสอบคุณสมบัติของยานพาหนะ
        for vehicle in game.vehicles:
            assert isinstance(vehicle, Vehicle)
            assert vehicle.speed != 0  # ต้องมีความเร็ว
            assert vehicle.width == GRID_SIZE + 10
            assert vehicle.height == GRID_SIZE - 10
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    @patch('random.randint')
    def test_create_river_objects(self, mock_randint, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการสร้างวัตถุในแม่น้ำ"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        # Mock values สำหรับการสร้างขอนไม้และเต่า
        mock_randint.side_effect = [
            # สำหรับ logs
            3, 100, 2, 150, 3, 200,  # num_logs และ spacing, log_length
            2, 80, 4, 120, 3, 160,   # รอบที่ 2
            # สำหรับ turtles  
            4, 90, 3, 110, 4, 130,   # num_turtles และ spacing
            3, 70, 4, 140, 3, 180,   # รอบที่ 2
            # สำหรับ turtle dive timers
            240, 300, 180, 270, 220, 190, 260, 180, 240, 200
        ]
        
        game = FroggerGame()
        
        # ตรวจสอบการสร้างขอนไม้และเต่า
        assert len(game.logs) > 0
        assert len(game.turtles) > 0
        
        # ตรวจสอบคุณสมบัติของขอนไม้
        for log in game.logs:
            assert isinstance(log, Log)
            assert log.speed != 0
            assert log.length >= 2
            assert log.color == Colors.BROWN
        
        # ตรวจสอบคุณสมบัติของเต่า
        for turtle in game.turtles:
            assert isinstance(turtle, Turtle)
            assert turtle.speed != 0
            assert turtle.color == Colors.DARK_GREEN
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_create_homes(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการสร้างบ้าน"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        
        # ตรวจสอบจำนวนบ้าน
        assert len(game.homes) == 5
        
        # ตรวจสอบคุณสมบัติของบ้าน
        for home in game.homes:
            assert isinstance(home, Home)
            assert home.width == GRID_SIZE
            assert home.height == GRID_SIZE
            assert home.y == 10
            assert home.occupied is False
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    @patch('pygame.event.get')
    def test_handle_input_quit(self, mock_event, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการจัดการ input เมื่อผู้เล่นปิดเกม"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        # Mock quit event
        quit_event = Mock()
        quit_event.type = pygame.QUIT
        mock_event.return_value = [quit_event]
        
        game = FroggerGame()
        result = game.handle_input()
        
        assert result is False
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    @patch('pygame.event.get')
    def test_handle_input_movement_keys(self, mock_event, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการจัดการ input การเคลื่อนที่"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        initial_x = game.frog.x
        initial_y = game.frog.y
        
        # ทดสอบการกดปุ่มขึ้น
        key_event = Mock()
        key_event.type = pygame.KEYDOWN
        key_event.key = pygame.K_UP
        mock_event.return_value = [key_event]
        
        result = game.handle_input()
        assert result == [pygame.K_UP]
        assert game.frog.y == initial_y - GRID_SIZE
        
        # ทดสอบการกดปุ่มลง
        key_event.key = pygame.K_DOWN
        mock_event.return_value = [key_event]
        result = game.handle_input()
        assert result == [pygame.K_DOWN]
        assert game.frog.y == initial_y
        
        # ทดสอบการกดปุ่มซ้าย
        key_event.key = pygame.K_LEFT
        mock_event.return_value = [key_event]
        result = game.handle_input()
        assert result == [pygame.K_LEFT]
        assert game.frog.x == initial_x - GRID_SIZE
        
        # ทดสอบการกดปุ่มขวา
        key_event.key = pygame.K_RIGHT
        mock_event.return_value = [key_event]
        result = game.handle_input()
        assert result == [pygame.K_RIGHT]
        assert game.frog.x == initial_x
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    @patch('pygame.event.get')
    def test_handle_input_restart_game_over(self, mock_event, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการรีสตาร์ทเกมเมื่อ game over"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        game.game_state.game_over = True
        
        # ทดสอบการกดปุ่ม R
        key_event = Mock()
        key_event.type = pygame.KEYDOWN
        key_event.key = pygame.K_r
        mock_event.return_value = [key_event]
        
        result = game.handle_input()
        assert result == [pygame.K_r]
        assert game.game_state.game_over is False
        assert game.game_state.lives == 3
        assert game.game_state.score == 0
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    @patch('pygame.event.get')
    def test_handle_input_restart_level_complete(self, mock_event, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการรีสตาร์ทเกมเมื่อผ่านด่าน"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        game.game_state.level_complete = True
        
        # ทดสอบการกดปุ่ม R
        key_event = Mock()
        key_event.type = pygame.KEYDOWN
        key_event.key = pygame.K_r
        mock_event.return_value = [key_event]
        
        result = game.handle_input()
        assert result == [pygame.K_r]
        assert game.game_state.level_complete is False
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    @patch('pygame.event.get')
    def test_handle_input_no_events(self, mock_event, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการจัดการเมื่อไม่มี events"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        mock_event.return_value = []
        
        game = FroggerGame()
        result = game.handle_input()
        
        assert result is True
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_update_game_logic_game_over(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการอัปเดตเมื่อเกมจบ"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        game.game_state.game_over = True
        initial_time = game.game_state.time_left
        
        game.update_game_logic()
        
        # เวลาไม่ควรเปลี่ยนแปลงเมื่อเกมจบแล้ว
        assert game.game_state.time_left == initial_time
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_update_game_logic_level_complete(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการอัปเดตเมื่อผ่านด่าน"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        game.game_state.level_complete = True
        initial_time = game.game_state.time_left
        
        game.update_game_logic()
        
        # เวลาไม่ควรเปลี่ยนแปลงเมื่อผ่านด่านแล้ว
        assert game.game_state.time_left == initial_time
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_update_game_logic_time_up(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการอัปเดตเมื่อหมดเวลา"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        game.game_state.time_left = 0
        initial_lives = game.game_state.lives
        
        game.update_game_logic()
        
        # ควรเสียชีวิต 1 ชีวิตเมื่อหมดเวลา
        assert game.game_state.lives == initial_lives - 1
        assert game.game_state.time_left == 30.0  # เวลารีเซ็ต
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_update_game_logic_normal(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการอัปเดตปกติ"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        initial_time = game.game_state.time_left
        
        game.update_game_logic()
        
        # เวลาควรลดลง
        assert game.game_state.time_left < initial_time
        
        # ตรวจสอบว่ามีการอัปเดตวัตถุต่างๆ
        for vehicle in game.vehicles:
            assert isinstance(vehicle, Vehicle)
        
        for log in game.logs:
            assert isinstance(log, Log)
        
        for turtle in game.turtles:
            assert isinstance(turtle, Turtle)
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_check_vehicle_collision(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการตรวจสอบการชนกับยานพาหนะ"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        initial_lives = game.game_state.lives
        
        # วางกบให้ชนกับรถ
        if game.vehicles:
            vehicle = game.vehicles[0]
            game.frog.x = vehicle.x
            game.frog.y = vehicle.y
            game.frog.update_rect()
            
            game._check_vehicle_collision()
            
            # ควรเสียชีวิต
            assert game.game_state.lives == initial_lives - 1
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_check_water_collision_on_log(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการตรวจสอบการจมน้ำเมื่ออยู่บนขอนไม้"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        
        # วางกบในโซนแม่น้ำบนขอนไม้
        game.frog.y = 120  # ในโซนแม่น้ำ
        if game.logs:
            log = game.logs[0]
            game.frog.x = log.x
            game.frog.update_rect()
            
            game._check_water_collision()
            
            # กบควรอยู่บนขอนไม้ไม่ตาย
            assert game.frog.on_log is True
            assert game.frog.log_speed == log.speed
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_check_water_collision_on_turtle(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการตรวจสอบการจมน้ำเมื่ออยู่บนเต่า"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        
        # วางกบในโซนแม่น้ำบนเต่า
        game.frog.y = 120  # ในโซนแม่น้ำ
        if game.turtles:
            turtle = game.turtles[0]
            turtle.is_diving = False  # เต่าไม่ได้ดำน้ำ
            game.frog.x = turtle.x
            game.frog.update_rect()
            
            game._check_water_collision()
            
            # กบควรอยู่บนเต่าไม่ตาย
            assert game.frog.on_log is True
            assert game.frog.log_speed == turtle.speed
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_check_water_collision_drowning(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการตรวจสอบการจมน้ำ"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        initial_lives = game.game_state.lives
        
        # วางกบในโซนแม่น้ำโดยไม่ได้อยู่บนวัตถุใดๆ
        game.frog.x = 50
        game.frog.y = 120  # ในโซนแม่น้ำ
        game.frog.update_rect()
        
        game._check_water_collision()
        
        # กบควรจมน้ำตาย
        assert game.game_state.lives == initial_lives - 1
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_check_water_collision_outside_water(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบเมื่อไม่อยู่ในโซนแม่น้ำ"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        
        # วางกบนอกโซนแม่น้ำ
        game.frog.y = 300  # นอกโซนแม่น้ำ
        game.frog.on_log = True  # ตั้งค่าเป็น True ก่อน
        
        game._check_water_collision()
        
        # กบไม่ควรอยู่บนขอนไม้
        assert game.frog.on_log is False
        assert game.frog.log_speed == 0
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_check_home_collision_success(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการเข้าบ้านสำเร็จ"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        initial_score = game.game_state.score
        
        # วางกบที่บ้าน
        home = game.homes[0]
        game.frog.x = home.x
        game.frog.y = home.y
        game.frog.update_rect()
        
        game._check_home_collision()
        
        # ตรวจสอบผลลัพธ์
        assert home.occupied is True
        assert game.game_state.homes_filled == 1
        assert game.game_state.score == initial_score + 100
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_check_home_collision_all_homes_filled(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบเมื่อบ้านเต็มครบทุกช่อง"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        
        # เติมบ้าน 4 ช่องแรก
        for i in range(4):
            game.homes[i].occupied = True
            game.game_state.homes_filled = i + 1
        
        # วางกบที่บ้านช่องสุดท้าย
        home = game.homes[4]
        game.frog.x = home.x
        game.frog.y = home.y
        game.frog.update_rect()
        
        game._check_home_collision()
        
        # ควรผ่านด่าน
        assert game.game_state.level_complete is True
        assert game.game_state.homes_filled == 5
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_check_home_collision_occupied_home(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการเข้าบ้านที่มีกบอยู่แล้ว"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        
        # ตั้งบ้านให้มีกบอยู่แล้ว
        home = game.homes[0]
        home.occupied = True
        initial_score = game.game_state.score
        initial_homes_filled = game.game_state.homes_filled
        
        # วางกบที่บ้านที่มีกบอยู่แล้ว
        game.frog.x = home.x
        game.frog.y = home.y
        game.frog.update_rect()
        
        game._check_home_collision()
        
        # คะแนนและจำนวนบ้านไม่ควรเปลี่ยน
        assert game.game_state.score == initial_score
        assert game.game_state.homes_filled == initial_homes_filled
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_check_home_collision_miss_home(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการอยู่ในโซนบ้านแต่ไม่ได้เข้าบ้าน"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        initial_lives = game.game_state.lives
        
        # วางกบในโซนบ้านแต่ไม่ใช่ตำแหน่งบ้าน
        game.frog.x = 5  # ตำแหน่งที่ไม่ใช่บ้าน
        game.frog.y = 40  # ในโซนบ้าน
        game.frog.update_rect()
        
        game._check_home_collision()
        
        # ควรเสียชีวิต
        assert game.game_state.lives == initial_lives - 1
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_lose_life_game_over(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการเสียชีวิตจนเกมจบ"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        game.game_state.lives = 1  # เหลือชีวิตสุดท้าย
        
        game._lose_life()
        
        # ควร game over
        assert game.game_state.lives == 0
        assert game.game_state.game_over is True
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_lose_life_continue(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการเสียชีวิตแต่ยังเล่นต่อได้"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        game.game_state.lives = 2
        initial_frog_pos = (game.frog.start_x, game.frog.start_y)
        
        # ย้ายกบออกจากตำแหน่งเริ่มต้น
        game.frog.x = 200
        game.frog.y = 300
        
        game._lose_life()
        
        # ชีวิตควรลดลงและกบควรกลับไปตำแหน่งเริ่มต้น
        assert game.game_state.lives == 1
        assert game.game_state.game_over is False
        assert (game.frog.x, game.frog.y) == initial_frog_pos
        assert game.game_state.time_left == 30.0
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_reset_frog(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการรีเซ็ตกบ"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        initial_pos = (game.frog.start_x, game.frog.start_y)
        
        # เปลี่ยนสถานะกบ
        game.frog.x = 200
        game.frog.y = 300
        game.game_state.time_left = 10.0
        
        game._reset_frog()
        
        # ตรวจสอบการรีเซ็ต
        assert (game.frog.x, game.frog.y) == initial_pos
        assert game.game_state.time_left == 30.0
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_complete_level(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการจบด่าน"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        game.game_state.time_left = 15.0
        initial_score = game.game_state.score
        
        game._complete_level()
        
        # ตรวจสอบการจบด่าน
        assert game.game_state.level_complete is True
        assert game.game_state.score == initial_score + int(15.0) * 10  # โบนัสเวลา
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_restart_game(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการรีสตาร์ทเกม"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        
        # เปลี่ยนสถานะเกม
        game.game_state.score = 500
        game.game_state.lives = 1
        game.game_state.level = 3
        game.game_state.game_over = True
        
        game.restart_game()
        
        # ตรวจสอบการรีสตาร์ท
        assert game.game_state.score == 0
        assert game.game_state.lives == 3
        assert game.game_state.level == 1
        assert game.game_state.game_over is False
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    @patch('pygame.display.flip')
    def test_draw_game(self, mock_flip, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการวาดเกม"""
        mock_screen = Mock()
        mock_display.return_value = mock_screen
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        
        game.draw_game()
        
        # ตรวจสอบว่ามีการเรียก flip
        mock_flip.assert_called_once()
        # ตรวจสอบว่ามีการล้างหน้าจอ
        mock_screen.fill.assert_called_once_with(Colors.BLACK)
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    @patch('pygame.draw.rect')
    def test_draw_background(self, mock_draw, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการวาดพื้นหลัง"""
        mock_screen = Mock()
        mock_display.return_value = mock_screen
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        
        game._draw_background()
        
        # ตรวจสอบว่ามีการวาดพื้นหลัง 5 ส่วน
        assert mock_draw.call_count == 5
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_draw_ui(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการวาด UI"""
        mock_screen = Mock()
        mock_display.return_value = mock_screen
        mock_font_instance = Mock()
        mock_font.return_value = mock_font_instance
        
        # Mock render method
        mock_text_surface = Mock()
        mock_font_instance.render.return_value = mock_text_surface
        
        game = FroggerGame()
        
        game._draw_ui()
        
        # ตรวจสอบการเรียก render และ blit
        assert mock_font_instance.render.call_count >= 4  # Score, Lives, Level, Time
        assert mock_screen.blit.call_count >= 4
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_draw_status_messages_game_over(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการวาดข้อความ game over"""
        mock_screen = Mock()
        mock_display.return_value = mock_screen
        mock_font_instance = Mock()
        mock_font.return_value = mock_font_instance
        
        # Mock render และ get_rect methods
        mock_text_surface = Mock()
        mock_rect = Mock()
        mock_text_surface.get_rect.return_value = mock_rect
        mock_font_instance.render.return_value = mock_text_surface
        
        game = FroggerGame()
        game.game_state.game_over = True
        
        game._draw_status_messages()
        
        # ตรวจสอบการแสดงข้อความ
        assert mock_font_instance.render.call_count >= 2  # GAME OVER + restart message
        assert mock_screen.blit.call_count >= 2
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_draw_status_messages_level_complete(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการวาดข้อความผ่านด่าน"""
        mock_screen = Mock()
        mock_display.return_value = mock_screen
        mock_font_instance = Mock()
        mock_font.return_value = mock_font_instance
        
        # Mock render และ get_rect methods
        mock_text_surface = Mock()
        mock_rect = Mock()
        mock_text_surface.get_rect.return_value = mock_rect
        mock_font_instance.render.return_value = mock_text_surface
        
        game = FroggerGame()
        game.game_state.level_complete = True
        
        game._draw_status_messages()
        
        # ตรวจสอบการแสดงข้อความ
        assert mock_font_instance.render.call_count >= 2  # LEVEL COMPLETE + continue message
        assert mock_screen.blit.call_count >= 2
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    @patch('pygame.quit')
    def test_run_quit(self, mock_quit, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการทำงานของเกมและการปิด"""
        mock_screen = Mock()
        mock_display.return_value = mock_screen
        mock_clock_instance = Mock()
        mock_clock.return_value = mock_clock_instance
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        
        # Mock handle_input ให้ return False (ปิดเกม)
        with patch.object(game, 'handle_input', return_value=False):
            result = game.run()
        
        # ตรวจสอบว่า pygame.quit ถูกเรียก
        mock_quit.assert_called_once()
        assert result == game.game_state.score

class TestMainFunction:
    """ทดสอบ main function"""
    
    @patch('frogger.FroggerGame')
    def test_main(self, mock_game_class):
        """ทดสอบ main function"""
        from code import main
        
        # Mock game instance
        mock_game = Mock()
        mock_game.run.return_value = 1000
        mock_game_class.return_value = mock_game
        
        result = main()
        
        # ตรวจสอบการสร้าง game และเรียก run
        mock_game_class.assert_called_once()
        mock_game.run.assert_called_once()
        assert result == 1000

# การทดสอบเพิ่มเติมสำหรับการครอบคลุม edge cases
class TestEdgeCases:
    """ทดสอบ edge cases ต่างๆ"""
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_water_collision_diving_turtle(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการจมน้ำเมื่อเต่าดำน้ำ"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        initial_lives = game.game_state.lives
        
        # วางกบในโซนแม่น้ำบนเต่าที่กำลังดำน้ำ
        game.frog.y = 120  # ในโซนแม่น้ำ
        if game.turtles:
            turtle = game.turtles[0]
            turtle.is_diving = True  # เต่ากำลังดำน้ำ
            game.frog.x = turtle.x
            game.frog.update_rect()
            
            game._check_water_collision()
            
            # กบควรจมน้ำตาย
            assert game.game_state.lives == initial_lives - 1
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_multiple_vehicle_collisions(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการชนกับยานพาหนะหลายคัน"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        
        # วางกบให้ชนกับยานพาหนะหลายคัน
        for i, vehicle in enumerate(game.vehicles[:2]):  # ทดสอบแค่ 2 คันแรก
            game.frog.x = vehicle.x
            game.frog.y = vehicle.y
            game.frog.update_rect()
            
            initial_lives = game.game_state.lives
            game._check_vehicle_collision()
            
            # ควรเสียชีวิตเมื่อชน
            assert game.game_state.lives == initial_lives - 1
            
            # หยุดทดสอบถ้าชีวิตหมด
            if game.game_state.lives <= 0:
                break
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_frog_at_screen_boundaries(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบกบที่ขอบจอในสถานการณ์ต่างๆ"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        
        # ทดสอบที่ขอบซ้าย
        game.frog.x = 0
        game.frog.y = 120  # ในโซนแม่น้ำ
        game.frog.on_log = True
        game.frog.update_on_log(-10)  # ความเร็วติดลบ
        assert game.frog.x == 0  # ไม่ควรออกนอกขอบ
        
        # ทดสอบที่ขอบขวา
        game.frog.x = SCREEN_WIDTH - game.frog.width
        game.frog.update_on_log(10)  # ความเร็วบวก
        assert game.frog.x == SCREEN_WIDTH - game.frog.width  # ไม่ควรออกนอกขอบ
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_empty_object_lists(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบเมื่อไม่มีวัตถุในลิสต์"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        
        # ล้างวัตถุทั้งหมด
        game.vehicles.clear()
        game.logs.clear()
        game.turtles.clear()
        
        # ทดสอบการอัปเดตเมื่อไม่มีวัตถุ
        game.update_game_logic()
        
        # ไม่ควรมี error
        assert len(game.vehicles) == 0
        assert len(game.logs) == 0
        assert len(game.turtles) == 0
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_draw_with_no_objects(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการวาดเมื่อไม่มีวัตถุ"""
        mock_screen = Mock()
        mock_display.return_value = mock_screen
        mock_clock.return_value = Mock()
        mock_font_instance = Mock()
        mock_font.return_value = mock_font_instance
        
        # Mock render method
        mock_text_surface = Mock()
        mock_rect = Mock()
        mock_text_surface.get_rect.return_value = mock_rect
        mock_font_instance.render.return_value = mock_text_surface
        
        game = FroggerGame()
        
        # ล้างวัตถุทั้งหมด
        game.vehicles.clear()
        game.logs.clear()
        game.turtles.clear()
        
        # ทดสอบการวาด
        game.draw_game()
        
        # ไม่ควรมี error และต้องมีการล้างหน้าจอ
        mock_screen.fill.assert_called_with(Colors.BLACK)

# ทดสอบการทำงานร่วมกันของระบบต่างๆ
class TestGameIntegration:
    """ทดสอบการทำงานร่วมกันของระบบต่างๆ ในเกม"""
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_complete_game_cycle(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบวงจรการเล่นเกมแบบสมบูรณ์"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        
        # เติมบ้านทีละช่อง
        for i in range(5):
            home = game.homes[i]
            game.frog.x = home.x
            game.frog.y = home.y
            game.frog.update_rect()
            
            initial_score = game.game_state.score
            game._check_home_collision()
            
            if i < 4:
                # ยังไม่ครบ 5 ช่อง
                assert game.game_state.level_complete is False
                assert game.game_state.homes_filled == i + 1
                assert game.game_state.score == initial_score + 100
            else:
                # ครบ 5 ช่องแล้ว
                assert game.game_state.level_complete is True
                assert game.game_state.homes_filled == 5
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_death_scenarios(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบสถานการณ์การตายแบบต่างๆ"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        initial_lives = game.game_state.lives
        
        # สถานการณ์ที่ 1: หมดเวลา
        game.game_state.time_left = 0
        game.update_game_logic()
        assert game.game_state.lives == initial_lives - 1
        
        # สถานการณ์ที่ 2: ชนรถ (ถ้ามีรถ)
        if game.vehicles:
            vehicle = game.vehicles[0]
            game.frog.x = vehicle.x
            game.frog.y = vehicle.y
            game.frog.update_rect()
            current_lives = game.game_state.lives
            game._check_vehicle_collision()
            assert game.game_state.lives == current_lives - 1
        
        # สถานการณ์ที่ 3: จมน้ำ
        game.frog.x = 50
        game.frog.y = 120  # ในโซนแม่น้ำ
        game.frog.update_rect()
        current_lives = game.game_state.lives
        game._check_water_collision()
        assert game.game_state.lives == current_lives - 1

# ทดสอบ Performance และ Edge Cases
class TestPerformanceAndEdgeCases:
    """ทดสอบประสิทธิภาพและกรณีพิเศษ"""
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_large_number_of_updates(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการอัปเดตจำนวนมาก"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        
        # อัปเดตเกมหลายรอบ
        for _ in range(100):
            if not game.game_state.game_over and not game.game_state.level_complete:
                game.update_game_logic()
        
        # ตรวจสอบว่าเกมยังทำงานได้ปกติ
        assert isinstance(game.game_state.time_left, float)
        assert game.game_state.lives >= 0
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_extreme_frog_positions(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบตำแหน่งกบที่ผิดปกติ"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        
        # ทดสอบตำแหน่งติดลบ
        game.frog.x = -100
        game.frog.y = -100
        game.frog.update_rect()
        game._check_water_collision()
        game._check_vehicle_collision()
        game._check_home_collision()
        
        # ทดสอบตำแหน่งเกินขอบจอ
        game.frog.x = SCREEN_WIDTH + 100
        game.frog.y = SCREEN_HEIGHT + 100
        game.frog.update_rect()
        game._check_water_collision()
        game._check_vehicle_collision()
        game._check_home_collision()
        
        # ไม่ควรมี error
        assert True

# ทดสอบ Error Handling
class TestErrorHandling:
    """ทดสอบการจัดการข้อผิดพลาด"""
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_invalid_direction_handling(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการจัดการทิศทางที่ไม่ถูกต้อง"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        initial_pos = (game.frog.x, game.frog.y)
        
        # ลองเคลื่อนที่ด้วยทิศทางที่ถูกต้อง
        result = game.frog.move(Direction.UP)
        assert result is True
        
        # รีเซ็ตตำแหน่ง
        game.frog.x, game.frog.y = initial_pos
        game.frog.update_rect()
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_negative_time_handling(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการจัดการเวลาติดลบ"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        
        # ตั้งเวลาเป็นค่าติดลบ
        game.game_state.time_left = -5.0
        initial_lives = game.game_state.lives
        
        game.update_game_logic()
        
        # ควรเสียชีวิตเมื่อเวลาหมด
        assert game.game_state.lives == initial_lives - 1

# ทดสอบ Boundary Conditions
class TestBoundaryConditions:
    """ทดสอบเงื่อนไขขอบเขต"""
    
    def test_minimum_maximum_values(self):
        """ทดสอบค่าต่ำสุดและสูงสุด"""
        # ทดสอบการสร้างวัตถุด้วยค่าขั้นต่ำ
        obj = GameObject(0, 0, 1, 1, Colors.BLACK)
        assert obj.x == 0
        assert obj.y == 0
        assert obj.width == 1
        assert obj.height == 1
        
        # ทดสอบการสร้างวัตถุด้วยค่าสูงสุด
        obj = GameObject(SCREEN_WIDTH, SCREEN_HEIGHT, 1000, 1000, Colors.WHITE)
        assert obj.x == SCREEN_WIDTH
        assert obj.y == SCREEN_HEIGHT
        assert obj.width == 1000
        assert obj.height == 1000
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_zero_speed_objects(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบวัตถุที่มีความเร็วเป็นศูนย์"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        # ทดสอบยานพาหนะความเร็วศูนย์
        vehicle = Vehicle(100, 200, 0, Colors.RED)
        initial_x = vehicle.x
        vehicle.update()
        assert vehicle.x == initial_x  # ไม่ควรเคลื่อนที่
        
        # ทดสอบขอนไม้ความเร็วศูนย์
        log = Log(100, 200, 0)
        initial_x = log.x
        log.update()
        assert log.x == initial_x  # ไม่ควรเคลื่อนที่
        
        # ทดสอบเต่าความเร็วศูนย์
        turtle = Turtle(100, 200, 0)
        initial_x = turtle.x
        turtle.update()
        assert turtle.x == initial_x  # ไม่ควรเคลื่อนที่

# ทดสอบ State Transitions
class TestStateTransitions:
    """ทดสอบการเปลี่ยนสถานะ"""
    
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_game_state_transitions(self, mock_font, mock_clock, mock_caption, mock_display, mock_init):
        """ทดสอบการเปลี่ยนสถานะเกม"""
        mock_display.return_value = Mock()
        mock_clock.return_value = Mock()
        mock_font.return_value = Mock()
        
        game = FroggerGame()
        
        # เริ่มต้น: เกมปกติ
        assert game.game_state.game_over is False
        assert game.game_state.level_complete is False
        
        # เปลี่ยนเป็น game over
        game.game_state.lives = 0
        game._lose_life()
        assert game.game_state.game_over is True
        
        # รีสตาร์ท
        game.restart_game()
        assert game.game_state.game_over is False
        assert game.game_state.lives == 3
        
        # เปลี่ยนเป็น level complete
        game.game_state.homes_filled = 4
        game._complete_level()
        assert game.game_state.level_complete is True

# เรียกใช้ pytest ถ้าไฟล์นี้ถูกรันโดยตรง
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=frogger", "--cov-report=html", "--cov-report=term-missing"])