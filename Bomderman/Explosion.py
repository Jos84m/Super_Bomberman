# Explosion.py
import pygame
import pygame

class Explosion:
    def __init__(self, x, y, size=64, max_radius=40, duration=15):
        self.x = x
        self.y = y
        self.size = size
        self.radius = 5
        self.max_radius = max_radius
        self.duration = duration
        self.frame = 0
        self.finished = False

    def update(self):
        if self.frame >= self.duration:
            self.finished = True
        else:
            self.radius = int(self.max_radius * (self.frame / self.duration))
            self.frame += 1

    def draw(self, surface):
        if not self.finished:
            alpha = max(255 - (self.frame * 15), 0)
            surface_ = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface_, (255, 150, 0, alpha), (self.size, self.size), self.radius)
            pygame.draw.circle(surface_, (255, 255, 0, alpha), (self.size, self.size), int(self.radius * 0.5))
            surface.blit(surface_, (self.x - self.size, self.y - self.size))

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
