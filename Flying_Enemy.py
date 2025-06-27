import pygame
import os
import random
from projectile import Projectile

class FlyingEnemy:
    def __init__(self, x, y, sprite_folder, tile_size):
        self.x = x
        self.y = y
        self.tile_size = tile_size
        self.speed = 2  # más rápido que los enemigos normales
        self.direction = random.choice(["up", "down", "left", "right"])
        self.rect = pygame.Rect(self.x, self.y, tile_size, tile_size)
        self.alive = True
        self.active = False  # <-- Nuevo atributo para controlar disparo y movimiento

        self.sprite_folder = sprite_folder
        self.frames = {d: [] for d in ["up", "down", "left", "right"]}
        self.load_sprites()

        self.frame_index = 0
        self.forward = True
        self.anim_delay = 6
        self.anim_counter = 0
        self.image = self.frames[self.direction][self.frame_index]

        self.projectiles = []
        self.last_shot_time = 0
        self.shoot_interval = random.randint(1500, 2500)

    def load_sprites(self):
        for direction in ["down", "up", "left", "right"]:
            for i in range(1, 5):
                filename = f"FE {direction.capitalize()} {i}.png"
                path = os.path.join(self.sprite_folder, filename)
                image = pygame.image.load(path).convert_alpha()
                image = pygame.transform.scale(image, (self.tile_size, self.tile_size))
                self.frames[direction].append(image)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.tile_size, self.tile_size)

    def move(self, level_map, start_x, start_y):
        if not self.alive or not self.active:
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

    def shoot(self):
        if not self.active:
            return  # No dispara si no está activo

        now = pygame.time.get_ticks()
        if now - self.last_shot_time >= self.shoot_interval:
            self.last_shot_time = now
            self.shoot_interval = random.randint(1500, 2500)

            dir_map = {
                "up": (0, -1),
                "down": (0, 1),
                "left": (-1, 0),
                "right": (1, 0)
            }

            dx, dy = dir_map[self.direction]
            proj_start_x = self.x + self.tile_size // 2
            proj_start_y = self.y + self.tile_size // 2
            target_x = proj_start_x + dx * 100
            target_y = proj_start_y + dy * 100

            projectile = Projectile(proj_start_x, proj_start_y, target_x, target_y)
            self.projectiles.append(projectile)

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

    def update(self, level_map, player, tile_size, start_x, start_y):
        if not self.alive or not self.active:
            return

        self.move(level_map, start_x, start_y)
        self.shoot()

        for projectile in self.projectiles[:]:
            projectile.update()
            if projectile.is_off_screen():
                self.projectiles.remove(projectile)
                continue

            if projectile.get_rect().colliderect(player.get_rect()):
                if not player.dying and player.alive:
                    player.lose_life()
                    self.projectiles.remove(projectile)
                    continue

            for row_idx, row in enumerate(level_map):
                for col_idx, tile in enumerate(row):
                    if tile in ["#", "?"]:
                        tile_rect = pygame.Rect(
                            start_x + col_idx * tile_size,
                            start_y + row_idx * tile_size,
                            tile_size,
                            tile_size
                        )
                        if projectile.get_rect().colliderect(tile_rect):
                            self.projectiles.remove(projectile)
                            break
                else:
                    continue
                break

    def draw(self, screen):
        if self.alive and self.active:
            screen.blit(self.image, (self.x, self.y))
            for projectile in self.projectiles:
                projectile.draw(screen)
