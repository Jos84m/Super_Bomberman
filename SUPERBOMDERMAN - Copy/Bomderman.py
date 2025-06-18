import pygame

class BombermanGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Bomberman Ultimate")
        self.clock = pygame.time.Clock()
        self.running = True
