import pygame
import os
import time

class Player:
    def __init__(self, x, y, sprite_folder, sprite_prefix, speed=2, lives=3, *, level=None):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.base_speed = speed
        self.speed = self.base_speed
        self.sprite_folder = sprite_folder
        self.sprite_prefix = sprite_prefix
        self.direction = "Down"
        self.walk_cycle = [1, 2, 3, 2]
        self.walk_index = 1
        self.last_direction = "Down"
        self.image = self.load_sprite("Walking", self.direction, self.walk_cycle[self.walk_index])
        self.rect = pygame.Rect(self.x, self.y, 48, 48)
        self.pet = None
        self.moving = False
        self.level = level
        self.anim_counter = 0
        self.anim_speed = 6
        self.bomb_cell = None

        self.lives = lives
        self.alive = True

        # Animación de muerte
        self.dying = False
        self.die_frames = self.load_die_sprites()
        self.die_index = 0
        self.die_timer = 0
        self.die_speed = 6

        self.die_sound = pygame.mixer.Sound(os.path.join("assets", "SOUNDS", "Bomberman Dies.mp3"))

        # Invulnerabilidad temporal después de reaparecer
        self.invulnerable = False
        self.invuln_timer = 0
        self.invuln_duration = 90  # 1.5 segundos a 60 FPS

        # NUEVAS VARIABLES PARA POWER-UPS Y LLAVE
        self.has_key = False

        self.max_bombs = 1
        self.bombs_placed = 0
        self.explosion_range = 1
        self.damage = 1

        self.can_take_damage = True
        self.damage_cooldown_timer = 0
        self.damage_cooldown_duration = 60  # frames (1 segundo aprox. a 60 FPS)
        self.damaged_by_explosion = False

        # Gestión de ítems (no power-ups)
        # Lista con dicts: {'type': nombre_item, 'count': cantidad, 'active': bool, 'start_time': float}
        self.collected_items = []  

    def load_sprite(self, action, direction, frame):
        filename = f"{self.sprite_prefix} {action} {direction} {frame}.png"
        path = os.path.join(self.sprite_folder, filename)
        return pygame.transform.scale(pygame.image.load(path).convert_alpha(), (48, 48))

    def load_die_sprites(self):
        frames = []
        for i in range(1, 8):
            filename = f"{self.sprite_prefix} Dies {i}.png"
            path = os.path.join(self.sprite_folder, filename)
            image = pygame.transform.scale(pygame.image.load(path).convert_alpha(), (48, 48))
            frames.append(image)
        return frames

    def check_collision(self, rect, level_map, tile_size, start_x, start_y, bombs):
        # Revisa colisiones con muros y cajas
        for row_idx, row in enumerate(level_map):
            for col_idx, tile in enumerate(row):
                if tile in ['#', '?']:
                    tile_rect = pygame.Rect(start_x + col_idx * tile_size,
                                            start_y + row_idx * tile_size,
                                            tile_size, tile_size)
                    if rect.colliderect(tile_rect):
                        return True

        # Revisa colisión con bombas
        for bomb in bombs:
            bomb_col = (bomb.x - start_x) // tile_size
            bomb_row = (bomb.y - start_y) // tile_size

            player_col = (rect.x - start_x) // tile_size
            player_row = (rect.y - start_y) // tile_size

            if bomb.rect.colliderect(rect):
                # Permite salir de la celda donde puso la bomba
                if self.bomb_cell == (bomb_col, bomb_row) and (player_col, player_row) == self.bomb_cell:
                    continue
                if not bomb.rect.colliderect(self.rect):
                    return True

        return False

    def move(self, dx, dy, level_map, tile_size, start_x, start_y, bombs):
        if self.dying or not self.alive:
            return

        # --- Alineamos la posición perpendicular al movimiento para evitar colisiones invisibles ---

        # Si hay movimiento horizontal, alineamos la coordenada Y a la cuadricula
        if dx != 0:
            aligned_y = start_y + round((self.y - start_y) / tile_size) * tile_size
            self.y = aligned_y
            self.rect.topleft = (self.x, self.y)

        # Movimiento separado en X
        new_x = self.x + dx * self.speed
        new_y = self.y
        new_rect_x = pygame.Rect(new_x, new_y, tile_size, tile_size)

        if not self.check_collision(new_rect_x, level_map, tile_size, start_x, start_y, bombs):
            self.x = new_x
            self.rect.topleft = (self.x, self.y)

        # Si hay movimiento vertical, alineamos la coordenada X a la cuadricula
        if dy != 0:
            aligned_x = start_x + round((self.x - start_x) / tile_size) * tile_size
            self.x = aligned_x
            self.rect.topleft = (self.x, self.y)

        # Movimiento separado en Y
        new_x = self.x
        new_y = self.y + dy * self.speed
        new_rect_y = pygame.Rect(new_x, new_y, tile_size, tile_size)

        if not self.check_collision(new_rect_y, level_map, tile_size, start_x, start_y, bombs):
            self.y = new_y
            self.rect.topleft = (self.x, self.y)

        # -------------------------------------------------------------

        if dx > 0:
            self.direction = "Right"
        elif dx < 0:
            self.direction = "Left"
        elif dy > 0:
            self.direction = "Down"
        elif dy < 0:
            self.direction = "Up"

        self.moving = dx != 0 or dy != 0

        # Animación
        if self.moving:
            self.anim_counter += 1
            if self.anim_counter >= self.anim_speed:
                self.walk_index = (self.walk_index + 1) % len(self.walk_cycle)
                self.anim_counter = 0
            frame = self.walk_cycle[self.walk_index]
            self.image = self.load_sprite("Walking", self.direction, frame)
            self.last_direction = self.direction
        else:
            self.anim_counter = 0
            self.image = self.load_sprite("Walking", self.direction, 2)

    def get_rect(self):
        self.rect.topleft = (self.x, self.y)
        return self.rect

    def draw(self, screen):
        if self.invulnerable:
            self.invuln_timer += 1
            if self.invuln_timer >= self.invuln_duration:
                self.invulnerable = False
                self.invuln_timer = 0

        if self.dying:
            self.die_timer += 1
            if self.die_timer >= self.die_speed:
                self.die_timer = 0
                self.die_index += 1
                if self.die_index >= len(self.die_frames):
                    self.dying = False
                    self.die_index = 0
                    if self.alive:
                        self.respawn()
            if self.die_index < len(self.die_frames):
                screen.blit(self.die_frames[self.die_index], (self.x, self.y))
        else:
            if self.image:
                screen.blit(self.image, (self.x, self.y))
        if self.pet:
            self.pet.draw(screen)

    def lose_life(self):
        if self.dying or self.invulnerable:
            return
        self.lives -= 1
        if self.lives <= 0:
            self.alive = False
        self.dying = True
        self.die_index = 0
        self.die_timer = 0
        self.die_sound.play()

        # Iniciar cooldown para que no pueda recibir daño inmediatamente
        self.can_take_damage = False
        self.damage_cooldown_timer = self.damage_cooldown_duration

    def respawn(self):
        self.x = self.start_x
        self.y = self.start_y
        self.rect.topleft = (self.x, self.y)
        self.image = self.load_sprite("Walking", self.direction, 2)
        self.moving = False
        self.bomb_cell = None
        self.alive = True
        self.invulnerable = True
        self.invuln_timer = 0
        # Reiniciar ítems al morir
        self.collected_items.clear()
        self.reset_item_effect()

    # Métodos para power-ups y llave

    def can_place_bomb(self):
        return self.bombs_placed < self.max_bombs

    def place_bomb(self):
        if self.can_place_bomb():
            self.bombs_placed += 1

    def bomb_exploded(self):
        if self.bombs_placed > 0:
            self.bombs_placed -= 1

    def pick_key(self):
        self.has_key = True

    def use_key(self):
        if self.has_key:
            self.has_key = False
            return True
        return False

    # --------------------- Gestión de ítems ---------------------

    def collect_item(self, item_type):
        # Power-ups que se activan inmediatamente al recoger
        if item_type in ["heart", "damage_increase"]:
            self.apply_item_effect(item_type)
            return
        
        # Buscar si ya tiene ese ítem en la lista (ítems activables manualmente)
        for item in self.collected_items:
            if item['type'] == item_type:
                item['count'] += 1
                return
            
        # Si no existe, agregar nuevo    
        self.collected_items.append({'type': item_type, 'count': 1, 'active': False, 'start_time': 0})

    def use_item_by_key(self, key_num):
        idx = key_num - 1
        if idx < 0 or idx >= len(self.collected_items):
            return  # No existe ítem para esa tecla
        item = self.collected_items[idx]
        if item['count'] <= 0 or item['active']:
            return  # No puede usar si no tiene o ya está activo

        # Activar efecto del ítem
        item['active'] = True
        item['count'] -= 1
        item['start_time'] = time.time()
        self.apply_item_effect(item['type'])

    def update_item_effect(self):
        # Revisa si hay algún ítem activo y su duración (15 segundos)
        current_time = time.time()
        for item in self.collected_items:
            if item['active']:
                elapsed = current_time - item['start_time']
                if elapsed >= 15:
                    # Termina efecto
                    item['active'] = False
                    self.reset_item_effect()

    def apply_item_effect(self, item_type):
        if item_type == "accelerator":
            self.speed += 2
        elif item_type == "extra_bombs":
            self.max_bombs += 2
        elif item_type == "explosion_expander":
            self.explosion_range += 2
        elif item_type == "heart":
            self.lives = min(self.lives + 1, 5)
        elif item_type == "damage_increase":
            self.damage += 1

    def reset_item_effect(self):
        # Reiniciar stats a valores base (puedes ajustarlo según tus valores)
        self.speed = self.base_speed
        self.max_bombs = 1
        self.explosion_range = 1

    def get_items_for_hud(self):
        # Retorna lista de tuplas (nombre, cantidad) de los ítems recogidos en orden
        return [(item['type'], item['count']) for item in self.collected_items[:3]]
    
    def update(self):
        # Reducir cooldown de daño cada frame
        if not self.can_take_damage:
            self.damage_cooldown_timer -= 1
            if self.damage_cooldown_timer <= 0:
                self.can_take_damage = True
                self.damaged_by_explosion = False  # Resetear para próximas explosiones

    def lose_life_from_explosion(self):
        if self.damaged_by_explosion:
            return  # Ya recibió daño por explosión en este cooldown
        self.lose_life()
        self.damaged_by_explosion = True