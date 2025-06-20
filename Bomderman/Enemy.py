import pygame

import pygame
import random

import pygame
import random

class Enemy:
    def __init__(self, x, y, image_path, tile_size):
        self.x = x
        self.y = y
        self.image = pygame.image.load(image_path).convert_alpha()
        self.tile_size = tile_size
        self.speed = 2
        self.direction = random.choice(["up", "down", "left", "right"])
        self.rect = pygame.Rect(self.x, self.y, tile_size, tile_size)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.tile_size, self.tile_size)

    def move(self, level_map, start_x, start_y):
        old_x, old_y = self.x, self.y
        dx, dy = 0, 0

        if self.direction == "up":
            dy = -self.speed
        elif self.direction == "down":
            dy = self.speed
        elif self.direction == "left":
            dx = -self.speed
        elif self.direction == "right":
            dx = self.speed

        # Nueva posición temporal
        new_rect = self.get_rect().move(dx, dy)

        # Colisión con el mapa
        collided = False
        for row_idx, row in enumerate(level_map):
            for col_idx, tile in enumerate(row):
                if tile in ["#", "?"]:
                    tile_rect = pygame.Rect(
                        start_x + col_idx * self.tile_size,
                        start_y + row_idx * self.tile_size,
                        self.tile_size,
                        self.tile_size
                    )
                    if new_rect.colliderect(tile_rect):
                        collided = True
                        break
            if collided:
                break

        if not collided:
            self.x += dx
            self.y += dy
        else:
            # Cambiar dirección aleatoria si colisiona
            self.direction = random.choice(["up", "down", "left", "right"])

        self.rect = pygame.Rect(self.x, self.y, self.tile_size, self.tile_size)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
