import pygame
import time
import sys


class Bomb:
    def __init__(self, x, y, tile_size, placed_time, image_path):
        self.x = x
        self.y = y
        self.tile_size = tile_size
        self.placed_time = placed_time
        self.explode_time = placed_time + 2  # Explota en 2 segundos
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = pygame.Rect(x, y, tile_size, tile_size)

    def is_exploded(self, current_time):
        return current_time >= self.explode_time

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
