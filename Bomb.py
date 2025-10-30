import pygame
import os

class Bomb:
    def __init__(self, x, y, sprite_folder, tile_size, owner_player=None, explosion_sound=None):
        self.x = x
        self.y = y
        self.tile_size = tile_size
        self.owner_player = owner_player
        self.explosion_sound = explosion_sound

        self.affected_tiles = []

        self.sprite_folder = sprite_folder
        self.exploded = False
        self.finished = False
        self.timer = 1800  # milisegundos antes de explotar
        self.explosion_duration = 700

        self.start_time = pygame.time.get_ticks()
        self.explosion_start_time = None

        self.bomb_sprites = []
        self.load_sprites()

        self.current_bomb_frame = 0
        self.bomb_frame_delay = 200
        self.bomb_frame_counter = 0

        self.rect = pygame.Rect(self.x, self.y, tile_size, tile_size)
        self.frozen = False

    def load_sprites(self):
        bomb_sprite_names = ["Bomb 1.png", "Bomb 2.png"]
        for name in bomb_sprite_names:
            path = os.path.join(self.sprite_folder, name)
            if os.path.exists(path):
                image = pygame.image.load(path).convert_alpha()
                image = pygame.transform.scale(image, (self.tile_size, self.tile_size))
                self.bomb_sprites.append(image)
        if not self.bomb_sprites:
            raise Exception(f"No se cargaron sprites de bomba desde {self.sprite_folder}")

    def draw(self, screen, start_x, start_y):
        if not self.exploded:
            screen.blit(self.bomb_sprites[self.current_bomb_frame], (self.x, self.y))
        else:
            for row, col in self.affected_tiles:
                x = start_x + col * self.tile_size
                y = start_y + row * self.tile_size

                # Explosión central: color más intenso
                if (row, col) == self.affected_tiles[0]:
                    color = (255, 140, 0)  # naranja intenso
                else:
                    color = (255, 200, 0)  # amarillo-naranja

                pygame.draw.rect(screen, color, (x, y, self.tile_size, self.tile_size))

    def update(self, level_map, enemies, flying_enemies=None, player=None, start_x=0, start_y=0, score_callback=None):
        now = pygame.time.get_ticks()

        if self.frozen:
            return False
        
        if flying_enemies is None:
            flying_enemies = []

        if not self.exploded:
            if now - self.start_time >= self.timer:
                self.exploded = True
                self.explosion_start_time = now
                self.explode(level_map, enemies, flying_enemies, player, start_x, start_y, score_callback)
            else:
                self.bomb_frame_counter += 1
                if self.bomb_frame_counter >= self.bomb_frame_delay // 16:
                    self.bomb_frame_counter = 0
                    self.current_bomb_frame = (self.current_bomb_frame + 1) % len(self.bomb_sprites)
        else:
            if now - self.explosion_start_time >= self.explosion_duration:
                self.finished = True
                return True

        return False

    def explode(self, level_map, enemies, flying_enemies, player, start_x, start_y, score_callback):
        if self.explosion_sound:
            self.explosion_sound.play()

        bomb_col = (self.x - start_x) // self.tile_size
        bomb_row = (self.y - start_y) // self.tile_size
        explosion_range = self.owner_player.explosion_range if self.owner_player else 1

        self.affected_tiles = [(bomb_row, bomb_col)]

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            for dist in range(1, explosion_range + 1):
                r = bomb_row + dr * dist
                c = bomb_col + dc * dist
                if 0 <= r < len(level_map) and 0 <= c < len(level_map[0]):
                    tile = level_map[r][c]
                    if tile == "#":
                        break
                    self.affected_tiles.append((r, c))
                    if tile == "?":
                        for box in self.owner_player.level.breakable_boxes:
                            box_col = (box.x - start_x) // self.tile_size
                            box_row = (box.y - start_y) // self.tile_size
                            if box_row == r and box_col == c and not box.destroyed:
                                box.destroyed = True
                                score_callback(100)
                        break
                else:
                    break

        explosion_rects = []
        level_offset_x = self.owner_player.level.start_x
        level_offset_y = self.owner_player.level.start_y
        
        for r, c in self.affected_tiles:
            x = level_offset_x + c * self.tile_size
            y = level_offset_y + r * self.tile_size
            explosion_rects.append(pygame.Rect(x, y, self.tile_size, self.tile_size))

        # Enemigos terrestres
        for enemy in enemies[:]:
            enemy_rect = enemy.get_rect()
            for rect in explosion_rects:
                if rect.colliderect(enemy_rect):
                    enemies.remove(enemy)
                    score_callback(100)
                    break

        # Enemigos voladores
        for f_enemy in flying_enemies[:]:
            if not f_enemy.alive:
                continue
            enemy_rect = f_enemy.get_rect()
            for rect in explosion_rects:
                if rect.colliderect(enemy_rect):
                    flying_enemies.remove(f_enemy)
                    f_enemy.alive = False
                    score_callback(200)
                    break

        # Jugador
        if player.alive and not player.dying:
            player_rect = player.get_rect()
            for rect in explosion_rects:
                if rect.colliderect(player_rect):
                    player.lose_life()
                    break

        # Jefe
        if hasattr(self.owner_player.level, 'boss') and self.owner_player.level.boss.alive:
            boss = self.owner_player.level.boss
            boss_rect = boss.rect
            for rect in explosion_rects:
                if rect.colliderect(boss_rect):
                    boss.take_damage(self.owner_player.damage)
                    break

    def freeze(self):
        self.frozen = True

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.tile_size, self.tile_size)
