import pygame
import time
import os

class HUD:
    def __init__(self, screen, start_time, lives=3, score=0, level=1):
        self.screen = screen
        self.start_time = start_time
        self.lives = lives
        self.score = score
        self.level = level
        self.font = pygame.font.SysFont("Arial", 26)
        self.heart_img = pygame.image.load(os.path.join("assets", "heart.png")).convert_alpha()
        self.heart_img = pygame.transform.scale(self.heart_img, (32, 32))

    def update(self, elapsed_time):
        self.elapsed_time = int(elapsed_time)

    def draw(self):
        pygame.draw.rect(self.screen, (0, 0, 0), (0, self.screen.get_height() - 60, self.screen.get_width(), 60))

        for i in range(min(self.lives, 5)):
            x = 20 + i * 40
            y = self.screen.get_height() - 50
            self.screen.blit(self.heart_img, (x, y))

        hud_text = f"Puntos: {self.score}   Tiempo: {self.elapsed_time}s   Nivel: {self.level}"
        text_surface = self.font.render(hud_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 30))
        self.screen.blit(text_surface, text_rect)
