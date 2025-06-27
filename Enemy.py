import pygame
import os
import random

class Enemy:
    def __init__(self, x, y, sprite_folder, tile_size):
        self.x = x
        self.y = y
        self.tile_size = tile_size
        self.speed = 2
        self.direction = random.choice(["up", "down", "left", "right"])
        self.rect = pygame.Rect(self.x, self.y, tile_size, tile_size)
        self.alive = True
        self.active = False  # Nuevo atributo para controlar si está activo o no

        self.sprite_folder = sprite_folder
        self.frames = {
            "up": [],
            "down": [],
            "left": [],
            "right": []
        }
        self.load_sprites()

        self.frame_index = 0
        self.forward = True
        self.anim_delay = 6
        self.anim_counter = 0
        self.image = self.frames[self.direction][self.frame_index]

    def load_sprites(self):
        frame_counts = {
            "down": 10,
            "up": 4,
            "left": 6,
            "right": 6
        }

        for direction, count in frame_counts.items():
            for i in range(1, count + 1):
                filename = f"BE {direction.capitalize()} {i}.png"
                path = os.path.join(self.sprite_folder, filename)
                image = pygame.image.load(path).convert_alpha()
                image = pygame.transform.scale(image, (self.tile_size, self.tile_size))
                self.frames[direction].append(image)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.tile_size, self.tile_size)

    def move(self, level_map, start_x, start_y):
        if not self.alive or not self.active:  # Solo se mueve si está activo y vivo
            return

        dx, dy = 0, 0
        if self.direction == "up":
            dy = -self.speed
        elif self.direction == "down":
            dy = self.speed
        elif self.direction == "left":
            dx = -self.speed
        elif self.direction == "right":
            dx = self.speed

        new_rect = self.get_rect().move(dx, dy)

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
            self.direction = random.choice(["up", "down", "left", "right"])
            self.frame_index = 0
            self.forward = True

        self.rect.topleft = (self.x, self.y)
        self.update_animation()

    def update_animation(self):
        if not self.active or not self.alive:  # No animar si no está activo o está muerto
            return

        self.anim_counter += 1
        if self.anim_counter >= self.anim_delay:
            self.anim_counter = 0
            frames = self.frames[self.direction]
            if self.forward:
                self.frame_index += 1
                if self.frame_index >= len(frames) - 1:
                    self.forward = False
            else:
                self.frame_index -= 1
                if self.frame_index <= 0:
                    self.forward = True
            self.image = frames[self.frame_index]

    def update(self, level_map, player, tile_size, start_x, start_y):
        """Este método es necesario para que funcione con LevelWindow"""
        self.move(level_map, start_x, start_y)

    def draw(self, screen):
        if self.alive and self.active:
            screen.blit(self.image, (self.x, self.y))
