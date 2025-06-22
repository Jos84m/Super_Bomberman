import pygame
import random
import math
from proyectile import Projectile

class FlyingEnemy:
    def __init__(self, x, y, image_path, tile_size):
        self.x = x
        self.y = y
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size))
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.tile_size = tile_size

        self.speed = 2
        self.dive_speed = 6
        self.is_diving = False
        self.dive_cooldown = 0
        self.dive_duration = 30

        self.projectile_cooldown = 90
        self.projectiles = []

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.tile_size, self.tile_size)

    def update(self, player_pos):
        px, py = player_pos
        dx = px - self.x
        dy = py - self.y
        dist = math.hypot(dx, dy)

        if not self.is_diving and random.randint(0, 100) < 2 and self.dive_cooldown <= 0:
            self.is_diving = True
            self.dive_timer = self.dive_duration
        elif self.is_diving:
            if self.dive_timer > 0:
                self.x += self.dive_speed * dx / dist
                self.y += self.dive_speed * dy / dist
                self.dive_timer -= 1
            else:
                self.is_diving = False
                self.dive_cooldown = 60
        else:
            # Patrulla horizontal
            self.x += self.speed * random.choice([-1, 1])
            self.y += self.speed * random.choice([-1, 1])

        # Cooldowns
        if self.dive_cooldown > 0:
            self.dive_cooldown -= 1

        # Disparo
        if self.projectile_cooldown <= 0:
            proj = Projectile(self.x + self.tile_size // 2, self.y + self.tile_size // 2, px, py)
            self.projectiles.append(proj)
            self.projectile_cooldown = 90
        else:
            self.projectile_cooldown -= 1

        # Actualizar proyectiles
        for proj in self.projectiles:
            proj.update()

        # Limpiar proyectiles fuera de pantalla
        self.projectiles = [p for p in self.projectiles if not p.is_off_screen()]

        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
        for proj in self.projectiles:
            proj.draw(screen)
