import pygame
import math

class Projectile:
    def __init__(self, x, y, target_x, target_y, speed=5):
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = 6
        self.color = (255, 0, 0)

        dx = target_x - x
        dy = target_y - y
        distance = math.hypot(dx, dy)
        if distance == 0:
            distance = 1
        self.vel_x = self.speed * dx / distance
        self.vel_y = self.speed * dy / distance

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def is_off_screen(self):
        return self.x < 0 or self.y < 0 or self.x > 800 or self.y > 600
