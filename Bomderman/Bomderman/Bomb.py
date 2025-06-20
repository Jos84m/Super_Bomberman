import pygame


import pygame
import time

import pygame
import time

class Bomb:
    def __init__(self, x, y, image_path, tile_size):
        self.x = x
        self.y = y
        self.tile_size = tile_size
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = pygame.Rect(self.x, self.y, tile_size, tile_size)
        self.start_time = time.time()
        self.timer = 3  # segundos para explotar
        self.exploded = False
        self.explosion_duration = 1  # segundos que dura la explosión
        self.explosion_start = 0
        self.explosion_tiles = []  # lista de tiles (col, row) afectados

    def can_place(self, level_map, start_x, start_y):
        # No poner bomba encima de muro ni otra bomba
        col = (self.x - start_x) // self.tile_size
        row = (self.y - start_y) // self.tile_size
        if level_map[row][col] == '#':
            return False
        return True

    def update(self, level_map, enemies, player):
        now = time.time()
        if not self.exploded and now - self.start_time >= self.timer:
            self.explode(level_map, enemies, player)
            self.exploded = True
            self.explosion_start = now
            return False
        if self.exploded and now - self.explosion_start >= self.explosion_duration:
            return True  # indica que la bomba debe desaparecer
        return False

    def explode(self, level_map, enemies, player):
        # Definir tiles afectados: bomba + 1 tile arriba, abajo, izquierda, derecha
        col = (self.x) // self.tile_size
        row = (self.y) // self.tile_size

        self.explosion_tiles = [(col, row)]
        directions = [(0,-1), (0,1), (-1,0), (1,0)]
        for dc, dr in directions:
            nc, nr = col + dc, row + dr
            if 0 <= nr < len(level_map) and 0 <= nc < len(level_map[0]):
                if level_map[nr][nc] != '#':
                    self.explosion_tiles.append((nc,nr))

        # Daño a enemigos
        for enemy in enemies:
            for c,r in self.explosion_tiles:
                ex = c * self.tile_size
                ey = r * self.tile_size
                explosion_rect = pygame.Rect(ex, ey, self.tile_size, self.tile_size)
                if enemy.alive and enemy.rect.colliderect(explosion_rect):
                    enemy.alive = False

        # Daño al jugador
        for c,r in self.explosion_tiles:
            ex = c * self.tile_size
            ey = r * self.tile_size
            explosion_rect = pygame.Rect(ex, ey, self.tile_size, self.tile_size)
            if player.rect.colliderect(explosion_rect):
                player.hurt()

    def draw(self, screen):
        if not self.exploded:
            screen.blit(self.image, (self.x, self.y))
        else:
            # Dibujar la explosión (simple rect rojo)
            for c,r in self.explosion_tiles:
                ex = c * self.tile_size
                ey = r * self.tile_size
                pygame.draw.rect(screen, (255, 0, 0), (ex, ey, self.tile_size, self.tile_size))
