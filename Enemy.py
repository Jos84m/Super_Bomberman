import pygame
import random
import os

class Enemy:
    def __init__(self, x, y, sprite_folder, tile_size):
        self.x = x
        self.y = y
        self.tile_size = tile_size
        self.speed = 2
        self.direction = random.choice(["up", "down", "left", "right"])
        self.rect = pygame.Rect(self.x, self.y, tile_size, tile_size)
        self.alive = True

        self.sprite_folder = sprite_folder  # carpeta con los sprites de BE
        self.frames = {
            "up": [],
            "down": [],
            "left": [],
            "right": []
        }
        # Cargar sprites para cada dirección
        self.load_sprites()

        # Animación ping-pong
        self.frame_index = 0
        self.forward = True

        # Control velocidad animación
        self.anim_delay = 6  # Ajusta este valor para hacer la animación más lenta o rápida (mayor = más lenta)
        self.anim_counter = 0

        # Inicialmente asignar la imagen correcta
        self.image = self.frames[self.direction][self.frame_index]

    def load_sprites(self):
        # Cantidad de frames por dirección (según tu info)
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
        if not self.alive:
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
            # Resetear animación para la nueva dirección
            self.frame_index = 0
            self.forward = True

        self.rect.topleft = (self.x, self.y)

        # Actualizar animación controlando velocidad
        self.update_animation()

    def update_animation(self):
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

    def draw(self, screen):
        if self.alive:
            screen.blit(self.image, (self.x, self.y))
