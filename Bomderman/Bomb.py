import pygame
import time



class Bomb:
    def __init__(self, x, y, image_path, tile_size):
        self.x = x - (x % tile_size)
        self.y = y - (y % tile_size)
        self.tile_size = tile_size
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (tile_size, tile_size))

        # Cargar imagen de explosión
        self.explosion_image = pygame.image.load("assets/bomb.png").convert_alpha()
        self.explosion_image = pygame.transform.scale(self.explosion_image, (tile_size, tile_size))

        self.rect = pygame.Rect(self.x, self.y, tile_size, tile_size)
        self.start_time = time.time()
        self.timer = 3  # segundos para explotar
        self.exploded = False
        self.explosion_duration = 1  # segundos que dura la explosión
        self.explosion_start = 0
        self.explosion_tiles = []

    def can_place(self, level_map, start_x, start_y):
        col = (self.x - start_x) // self.tile_size
        row = (self.y - start_y) // self.tile_size
        return level_map[row][col] != '#'

    def update(self, level_map, enemies, player, start_x, start_y, add_score_func):
        now = time.time()
        if not self.exploded and now - self.start_time >= self.timer:
            self.explode(level_map, enemies, player, start_x, start_y, add_score_func)
            self.exploded = True
            self.explosion_start = now
            return False
        if self.exploded and now - self.explosion_start >= self.explosion_duration:
            return True  # Bomba desaparece
        return False

    def explode(self, level_map, enemies, player, start_x, start_y, add_score_func):
        col = (self.x - start_x) // self.tile_size
        row = (self.y - start_y) // self.tile_size
        self.explosion_tiles = [(col, row)]
        directions = [(0,-1), (0,1), (-1,0), (1,0)]
        for dc, dr in directions:
            nc, nr = col + dc, row + dr
            if 0 <= nr < len(level_map) and 0 <= nc < len(level_map[0]):
                if level_map[nr][nc] != '#':
                    self.explosion_tiles.append((nc, nr))

        # Daño a enemigos
        for enemy in enemies:
            if not enemy.alive:
                continue
            for c, r in self.explosion_tiles:
                ex = start_x + c * self.tile_size
                ey = start_y + r * self.tile_size
                explosion_rect = pygame.Rect(ex, ey, self.tile_size, self.tile_size)
                if enemy.get_rect().colliderect(explosion_rect):
                    enemy.alive = False
                    add_score_func(10)

        # Daño al jugador
        for c, r in self.explosion_tiles:
            ex = start_x + c * self.tile_size
            ey = start_y + r * self.tile_size
            explosion_rect = pygame.Rect(ex, ey, self.tile_size, self.tile_size)
            if player.get_rect().colliderect(explosion_rect):
                player.hurt()

    def draw(self, screen, start_x, start_y):
        if not self.exploded:
            screen.blit(self.image, (self.x, self.y))
        else:
            for c, r in self.explosion_tiles:
                ex = start_x + c * self.tile_size
                ey = start_y + r * self.tile_size
                screen.blit(self.explosion_image, (ex, ey))
