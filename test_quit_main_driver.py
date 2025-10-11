from game import frogger
import pygame


def test_quit():
    frogger.background = pygame.image.load(
        frogger.background_filename).convert()
    frogger.sprite_sapo = pygame.image.load(
        frogger.frog_filename).convert_alpha()
    frogger.sprite_arrived = pygame.image.load(
        frogger.arrived_filename).convert_alpha()
    frogger.sprite_car1 = pygame.image.load(
        frogger.car1_filename).convert_alpha()
    frogger.sprite_car2 = pygame.image.load(
        frogger.car2_filename).convert_alpha()
    frogger.sprite_car3 = pygame.image.load(
        frogger.car3_filename).convert_alpha()
    frogger.sprite_car4 = pygame.image.load(
        frogger.car4_filename).convert_alpha()
    frogger.sprite_car5 = pygame.image.load(
        frogger.car5_filename).convert_alpha()
    frogger.sprite_plataform = pygame.image.load(
        frogger.plataform_filename).convert_alpha()
    try:
        frogger.main()
    except SystemExit:
        pass
