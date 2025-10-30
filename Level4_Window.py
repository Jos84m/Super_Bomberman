import pygame 
import os
import random
import time
from PIL import Image, ImageSequence
from Player import Player
from Bomb import Bomb
from Enemy import Enemy
from HUD import HUD
from Item import Item
from Flying_Enemy import FlyingEnemy
from Boss import Boss
from Fireball import Fireball

class LevelWindow4:
    def __init__(self, screen, clock, gif_path, selected_character, main_game, volume_settings):
        self.main_game = main_game
        self.screen = screen
        self.clock = clock
        self.running = True
        self.selected_character = selected_character
        self.completed = False
        self.volume_settings = volume_settings

        # GIF animado de fondo
        self.frames = []
        self.load_gif_frames(gif_path)
        self.current_frame = 0
        self.frame_delay = 5
        self.frame_counter = 0

        # Configuración mapa
        self.tile_size = 48
        self.rows = 11
        self.cols = 15

        # Imágenes para bloques y puerta
        self.block_image = pygame.image.load(os.path.join("assets", "SPRITES", "Wall.png")).convert_alpha()
        self.exit_image = pygame.image.load(os.path.join("assets", "SPRITES", "Door.png")).convert_alpha()
        self.block_images = {"#": self.block_image, "E": self.exit_image}

        # Imagen para HUD (vidas)
        self.heart_image = pygame.image.load(os.path.join("assets", "SPRITES", "Heart.png")).convert_alpha()
        self.heart_image = pygame.transform.scale(self.heart_image, (32, 32))

        # Tiempo para HUD
        self.start_time = None 
        self.end_time = None

        self.special_cooldown = 0  # En segundos
        self.special_max_cooldown = 30

        # Inicialización para la habilidad especial de Bomberman
        self.fireballs = []
        self.last_fireball_time = 0
        self.fireball_cooldown = 30

        # Inicialización para la habilidad especial de Black Bomberman
        self.last_invuln_time = 0
        self.invuln_cooldown = 30

        # Inicialización para la habilidad especial de Blue Bomberman
        self.last_speedboost_time = 0
        self.speedboost_cooldown = 30

        # Mapa básico (vacío, excepto paredes externas)
        self.level_map = [
            list("###############"),
            list("#      #      #"),
            list("#             #"),
            list("#             #"),
            list("#             #"),
            list("##     E     ##"),
            list("#             #"),
            list("#             #"),
            list("##           ##"),
            list("###    #    ###"),
            list("###############")
        ]

        screen_width, screen_height = self.screen.get_size()
        total_width = self.cols * self.tile_size
        total_height = self.rows * self.tile_size
        self.start_x = (screen_width - total_width) // 2
        self.start_y = (screen_height - total_height - 100) // 2

        # Carpeta y prefijo de sprites personaje seleccionado
        sprite_folder = os.path.join("assets", "SPRITES", "Characters", selected_character["sprite_folder"])
        sprite_prefix = selected_character["sprite_folder"]

        self.lives = selected_character.get("lives", 3)

        # Instancia jugador
        self.player = Player(
            self.start_x + 1 * self.tile_size,
            self.start_y + 1 * self.tile_size,
            sprite_folder,
            sprite_prefix,
            selected_character.get("speed", 2),
            self.lives,
            level=self
        )
        self.player.alive = True

        # Enemigos terrestres básicos
        enemy_sprite_folder = os.path.join("assets", "SPRITES", "Enemies", "Basic enemies")
        self.enemies = [
            Enemy(self.start_x + 1 * self.tile_size, self.start_y + 9 * self.tile_size, enemy_sprite_folder, self.tile_size),
            Enemy(self.start_x + 13 * self.tile_size, self.start_y + 9 * self.tile_size, enemy_sprite_folder, self.tile_size)            
        ]
        for enemy in self.enemies:
            enemy.active = False

        # Enemigos voladores
        flying_enemy_sprite_folder = os.path.join("assets", "SPRITES", "Enemies", "FlyingEnemy")
        self.flying_enemies = [
            FlyingEnemy(self.start_x + 5 * self.tile_size, self.start_y + 5 * self.tile_size, flying_enemy_sprite_folder, self.tile_size)
        ]
        self.flying_enemies[0].active = False
        # Lista global para proyectiles (enemigos voladores)
        self.projectiles = []

        # --- Cajas rompibles eliminadas ---
        self.breakable_boxes = []

        # --- Ítems que aparecen directamente ---
        self.items = []
        item_positions = [
            (self.start_x + 3 * self.tile_size, self.start_y + 3 * self.tile_size),
            (self.start_x + 10 * self.tile_size, self.start_y + 7 * self.tile_size),
            (self.start_x + 5 * self.tile_size, self.start_y + 9 * self.tile_size),
        ]
        item_types = ["accelerator", "extra_bombs", "explosion_expander", "heart", "damage_increase"]

        for pos, item_type in zip(item_positions, item_types):
            self.items.append(Item(pos[0], pos[1], self.tile_size, item_type))

        # Variables para controlar aparición de llave al morir el boss
        self.key_spawned = False

        self.bombs = []
        self.explosions = []

        self.score = 0
        self.start_time = time.time()

        self.level_started = False
        self.level_start_time = None
        self.level_start_duration = 0
        self.level_complete = False
        self.level_complete_time = None
        self.level_complete_duration = 0

        # Sonidos
        self.bomb_explode_sound = pygame.mixer.Sound(os.path.join("assets", "SOUNDS", "Bomb Explodes.mp3"))
        self.player_death_sound = pygame.mixer.Sound(os.path.join("assets", "SOUNDS", "Bomberman Dies.mp3"))

        # Guardar rect de puerta para optimización
        self.door_rect = None
        for row_idx, row in enumerate(self.level_map):
            for col_idx, tile in enumerate(row):
                if tile == 'E':
                    x = self.start_x + col_idx * self.tile_size
                    y = self.start_y + row_idx * self.tile_size
                    self.door_rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                    break
            if self.door_rect:
                break

        # Instancia del jefe (Boss)
        boss_sprite_folder = os.path.join("assets", "SPRITES", "Bosses", "Boss1")
        boss_start_x = self.start_x + 7 * self.tile_size
        boss_start_y = self.start_y + 5 * self.tile_size
        self.boss = Boss(boss_start_x, boss_start_y, boss_sprite_folder, self.tile_size, level=self)

        # Para spawn aleatorio de ítems con cooldown
        self.possible_item_positions = [
            (self.start_x + 2 * self.tile_size, self.start_y + 2 * self.tile_size),
            (self.start_x + 4 * self.tile_size, self.start_y + 3 * self.tile_size),
            (self.start_x + 8 * self.tile_size, self.start_y + 4 * self.tile_size),
            (self.start_x + 11 * self.tile_size, self.start_y + 6 * self.tile_size),
            (self.start_x + 6 * self.tile_size, self.start_y + 8 * self.tile_size),
            (self.start_x + 3 * self.tile_size, self.start_y + 7 * self.tile_size),
        ]

        self.available_item_types = ["accelerator", "extra_bombs", "explosion_expander", "heart", "damage_increase"]
        self.item_cooldowns = {item: 0 for item in self.available_item_types}
        self.last_item_spawn_time = time.time()

        self.hud = HUD(self.screen, pygame.time.get_ticks(), lives=self.lives, score=self.score, level=4)


    def load_gif_frames(self, gif_path):
        pil_gif = Image.open(gif_path)
        for frame in ImageSequence.Iterator(pil_gif):
            frame = frame.convert("RGBA")
            surface = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode).convert_alpha()
            self.frames.append(surface)

    def draw_hud(self, items_for_hud=None):
        font = pygame.font.SysFont("Arial", 20)
        HUD_HEIGHT = 40
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        pygame.draw.rect(self.screen, (0, 0, 0), (0, self.screen.get_height() - HUD_HEIGHT, self.screen.get_width(), HUD_HEIGHT))

        # Dibujar corazones (vidas)
        for i in range(min(self.player.lives, 5)):
            x = 15 + i * 30
            y = self.screen.get_height() - 34
            self.screen.blit(self.heart_image, (x, y))


        # Mostrar puntos y tiempo
        if self.start_time is not None:
            elapsed_time = int(time.time() - (self.end_time if self.end_time else self.start_time))
        else:
            elapsed_time = 0

        hud_text = f"Puntos: {self.score}   Tiempo: {elapsed_time}s"
        text_surface = font.render(hud_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(midleft=(150, screen_height - 20))
        self.screen.blit(text_surface, text_rect)

        # Mostrar ítems recogidos (solo usables)
        if items_for_hud:
            start_x = text_rect.right + 20
            y = screen_height - 35

        # Separar ítems usables y la llave (que se mostrará aparte)
        usable_items = [(name, count) for name, count in items_for_hud if name != "key"]
        has_key = any(name == "key" for name, count in items_for_hud)

        for i, (item_name, count) in enumerate(usable_items):
            display_count = f"{count}" if count > 0 else "Usado"
            item_text = f"{i+1}. {item_name} ({display_count})"
            item_surface = font.render(item_text, True, (255, 255, 255))
            self.screen.blit(item_surface, (start_x, y))
            start_x += item_surface.get_width() + 20

        # Mostrar llave aparte (sin número y sin contador)
        if has_key:
            key_text = "Llave obtenida"
            key_surface = font.render(key_text, True, (255, 215, 0))  # Dorado para destacar
            # Que no se salga de pantalla (limitar el máximo x)
            max_x = screen_width - key_surface.get_width() - 15
            key_x = min(start_x, max_x)
            self.screen.blit(key_surface, (key_x, y))

        # Mostrar habilidad especial
        ability_text = "E. Habilidad Especial ("
        if self.special_cooldown <= 0:
            ability_text += "Lista)"
        else:
            ability_text += f"{int(self.special_cooldown)}s)"
        
        ability_surface = font.render(ability_text, True, (173, 216, 230))  # celeste claro
        ability_rect = ability_surface.get_rect()
        ability_rect.topright = (screen_width - 15, screen_height - 35)
        self.screen.blit(ability_surface, ability_rect)


    def handle_player_death(self):
        if self.player.lives <= 0:
            self.player.alive = False
            self.player_death_sound.play()
            while pygame.mixer.get_busy():
                pygame.time.delay(100)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()

            result = self.show_game_over_screen()
            if result == "reload":
                return "reload"
            elif result == "quit":
                return "quit"
            else:
                self.running = False
        else:
            self.player.x = self.start_x + 1 * self.tile_size
            self.player.y = self.start_y + 1 * self.tile_size
            self.player.respawn()

    def show_game_over_screen(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.load(os.path.join("assets", "OST", "Game Over.mp3"))
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(self.volume_settings.get_music_volume())

        if not self.volume_settings.music_enabled:
            pygame.mixer.music.pause()     
        else:
            pygame.mixer.music.unpause()

        font_big = pygame.font.SysFont("Arial", 72)
        font_small = pygame.font.SysFont("Arial", 36)
        msg = font_big.render("¡GAME OVER!", True, (255, 0, 0))
        score_msg = font_small.render(f"Puntaje obtenido en este nivel: {self.score}", True, (255, 255, 255))
        retry_msg = font_small.render("Presiona R para reiniciar o ESC para salir", True, (200, 200, 200))

        while True:
            self.screen.fill((0, 0, 0))
            self.screen.blit(msg, msg.get_rect(center=(400, 200)))
            self.screen.blit(score_msg, score_msg.get_rect(center=(400, 300)))
            self.screen.blit(retry_msg, retry_msg.get_rect(center=(400, 400)))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    self.running = False
                    return "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.mixer.music.stop()
                        self.running = False
                        return "quit"
                    elif event.key == pygame.K_r:
                        pygame.mixer.music.stop()
                        return "reload"

    def show_victory_screen(self):
        font_big = pygame.font.SysFont("Arial", 60)
        font_small = pygame.font.SysFont("Arial", 36)
        msg = font_big.render("¡Nivel completado!", True, (0, 255, 0))
        continue_msg = font_small.render("Presiona C para continuar", True, (255, 255, 255))
        menu_msg = font_small.render("Presiona M para volver al menú", True, (200, 200, 200))

        while True:
            self.screen.fill((0, 0, 0))
            self.screen.blit(msg, msg.get_rect(center=(400, 200)))
            self.screen.blit(continue_msg, continue_msg.get_rect(center=(400, 300)))
            self.screen.blit(menu_msg, menu_msg.get_rect(center=(400, 400)))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_c:
                        self.completed = True
                        self.running = False
                        return
                    elif event.key == pygame.K_m:
                        self.running = False
                        return

    def update_items_spawn(self):
        now = time.time()

        # Intentar spawnear ítem nuevo cada 15 segundos
        if now - self.last_item_spawn_time >= 15:
            # Filtrar ítems que ya están en cooldown (todavía no pueden reaparecer)
            available_items = [item for item in self.available_item_types if self.item_cooldowns[item] <= now]

            # No spawnear si ya hay 3 ítems en el mapa (excluye llave)
            current_items = [item for item in self.items if item.item_type != "key"]
            if available_items and len(current_items) < 3:
                # Elegir ítem aleatorio disponible
                item_type = random.choice(available_items)

                # Buscar posición libre para spawn
                occupied_positions = {(item.x, item.y) for item in self.items}
                occupied_positions.add((self.player.x, self.player.y))  # Evitar spawnear donde está jugador

                free_positions = [pos for pos in self.possible_item_positions if pos not in occupied_positions]

                if free_positions:
                    spawn_pos = random.choice(free_positions)
                    new_item = Item(spawn_pos[0], spawn_pos[1], self.tile_size, item_type)
                    self.items.append(new_item)

                    # Poner ítem en cooldown 15 segundos
                    self.item_cooldowns[item_type] = now + 15

                    self.last_item_spawn_time = now  

    def draw_scene(self, move_enemies=True):
        # Fondo animado
        self.screen.blit(pygame.transform.scale(self.frames[self.current_frame], self.screen.get_size()), (0, 0))
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

        # Dibujar mapa
        for row_idx, row in enumerate(self.level_map):
            for col_idx, tile in enumerate(row):
                if tile in self.block_images:
                    x = self.start_x + col_idx * self.tile_size
                    y = self.start_y + row_idx * self.tile_size
                    self.screen.blit(self.block_images[tile], (x, y))

        # Dibujar bombas
        for bomb in self.bombs:
            bomb.draw(self.screen, self.start_x, self.start_y)

        # Dibujar explosiones
        for explosion in self.explosions[:]:
            explosion.update()
            explosion.draw(self.screen)
            if explosion.finished:
                self.explosions.remove(explosion)

        # Dibujar ítems
        for item in self.items:
            item.draw(self.screen)

        # Colisiones explosiones - jugador
        for explosion in self.explosions:
            if not explosion.finished and explosion.get_rect().colliderect(self.player.get_rect()):
                if not self.player.dying and self.player.alive and self.player.can_take_damage:
                    self.player.lose_life_from_explosion()
                    if self.player.lives <= 0:
                        result = self.handle_player_death()
                        if result == "reload":
                            raise StopIteration
                        elif result == "quit":
                            raise SystemExit

        # Movimiento y colisiones enemigos terrestres
        for enemy in self.enemies[:]:
            if move_enemies:
                enemy.move(self.level_map, self.start_x, self.start_y)
            if enemy.get_rect().colliderect(self.player.get_rect()):
                if not self.player.dying and self.player.alive and self.player.can_take_damage:
                    self.player.lose_life()
                    if self.player.lives <= 0:
                        result = self.handle_player_death()
                        if result == "reload":
                            raise StopIteration
                        elif result == "quit":
                            raise SystemExit
            for explosion in self.explosions:
                if explosion.get_rect().colliderect(enemy.get_rect()):
                    self.enemies.remove(enemy)
                    self.score += 100

        # Movimiento, disparo y colisiones enemigos voladores
        for f_enemy in self.flying_enemies[:]:
            if not f_enemy.alive:
                continue
            if move_enemies:
                f_enemy.move(self.level_map, self.start_x, self.start_y)
            f_enemy.shoot()

            for projectile in f_enemy.projectiles[:]:
                projectile.update()
                if projectile.is_off_screen():
                    f_enemy.projectiles.remove(projectile)
                    continue

                # Colisión con cajas irrompibles
                collided_with_block = False
                for row_idx, row in enumerate(self.level_map):
                    for col_idx, tile in enumerate(row):
                        if tile in ["#", "?"]:
                            tile_rect = pygame.Rect(
                                self.start_x + col_idx * self.tile_size,
                                self.start_y + row_idx * self.tile_size,
                                self.tile_size,
                                self.tile_size,
                            )
                            if projectile.get_rect().colliderect(tile_rect):
                                collided_with_block = True
                                break
                    if collided_with_block:
                        break
                if collided_with_block:
                    f_enemy.projectiles.remove(projectile)
                    continue

                # Colisión proyectil - jugador
                if projectile.get_rect().colliderect(self.player.get_rect()):
                    if not self.player.dying and self.player.alive:
                        self.player.lose_life()
                        if self.player.lives <= 0:
                            result = self.handle_player_death()
                            if result == "reload":
                                raise StopIteration
                            elif result == "quit":
                                raise SystemExit
                    f_enemy.projectiles.remove(projectile)
                
                # Colisión con explosiones
                for explosion in self.explosions:
                    if explosion.get_rect().colliderect(f_enemy.get_rect()):
                        self.flying_enemies.remove(f_enemy)
                        self.score += 200
                        break
        
        # Colisiones explosiones - jefe
        if self.boss.alive:
            for explosion in self.explosions:
                if not explosion.finished:
                    for row, col in explosion.affected_tiles:
                        x = self.start_x + col * self.tile_size
                        y = self.start_y + row * self.tile_size
                        rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                        if rect.colliderect(self.boss.rect):
                            self.boss.take_damage(self.player.damage)
                            break
                    
            # Dibujar proyectiles
        for f_enemy in self.flying_enemies:
            for projectile in f_enemy.projectiles:
                projectile.draw(self.screen)

        # Aquí dibujamos explícitamente los enemigos terrestres y voladores
        for enemy in self.enemies:
            if enemy.alive and enemy.active:
                enemy.draw(self.screen)

        for f_enemy in self.flying_enemies:
            if f_enemy.alive and f_enemy.active:
                f_enemy.draw(self.screen)

        # Actualizar y dibujar jefe
        if self.boss.alive:
            if move_enemies:
                self.boss.update(self.player)
            self.boss.draw(self.screen)

            # Cuando el jefe muere, aparece la llave
            if not self.boss.alive and not self.key_spawned:
                self.items.append(Item(self.boss.x, self.boss.y, self.tile_size, "key"))
                self.key_spawned = True
                self.score += 1000

        # Dibujar jugador
        self.player.draw(self.screen)

        # HUD moderno:
        self.hud.lives = self.player.lives
        self.hud.score = self.score
        self.hud.level = 4
        self.hud.bombs_left = self.player.bombs_available
        
        if self.level_complete and self.end_time is not None:
            elapsed = self.end_time - self.start_time
        else:
            elapsed = time.time() - self.start_time
        self.hud.update(elapsed)

        self.hud.draw(self.player.get_items_for_hud())

        # --- Mostrar cooldown habilidad especial en HUD ---
        self.draw_hud(self.player.get_items_for_hud())

        for fireball in self.fireballs:
            fireball.draw(self.screen)

    def update_game_state(self):
        if self.level_complete:
            return
        
        self.player.update()
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1

        if not self.player.dying and self.player.alive and not self.level_complete:
            if dx != 0 or dy != 0:
                self.player.move(dx, dy, self.level_map, self.tile_size, self.start_x, self.start_y, self.bombs)
                self.player.update_item_effect()
            else:
                self.player.moving = False
                self.player.anim_counter = 0
                self.player.walk_index = 1
                self.player.image = self.player.load_sprite("Walking", self.player.direction, 2)
        else:
            self.player.moving = False
            self.player.anim_counter = 0
            self.player.walk_index = 1
            self.player.image = self.player.load_sprite("Walking", self.player.direction, 2)

        # Actualizar bombas
        for bomb in self.bombs[:]:
            if self.level_complete:
                bomb.freeze()
            finished = bomb.update(self.level_map, self.enemies, self.flying_enemies, self.player, self.start_x, self.start_y, lambda points: setattr(self, 'score', self.score + points))
            if finished:
                self.bombs.remove(bomb)

        # Recoger ítems
        for item in self.items[:]:
            if item.get_rect().colliderect(self.player.get_rect()):
                if item.item_type == "key":
                    self.player.pick_key()
                    self.hud.has_key = True
                else:
                    self.player.collect_item(item.item_type)
                self.items.remove(item)

        # Verificar paso por puerta (requiere llave)
        if self.door_rect and self.door_rect.colliderect(self.player.get_rect()) and not self.level_complete:
            if self.player.has_key:
                self.level_complete = True
                self.level_complete_time = pygame.time.get_ticks()
                self.level_complete_duration = int(pygame.mixer.Sound(os.path.join("assets", "OST", "Level Complete.mp3")).get_length() * 1000)

                if self.start_time is not None:
                    self.end_time = time.time()

                pygame.mixer.music.stop()
                pygame.mixer.music.load(os.path.join("assets", "OST", "Level Complete.mp3"))
                pygame.mixer.music.play()
                pygame.mixer.music.set_volume(self.volume_settings.get_music_volume())

                if not self.volume_settings.music_enabled:
                    pygame.mixer.music.pause()     
                else:
                    pygame.mixer.music.unpause()

        # Actualizar bolas de fuego
        for fireball in self.fireballs[:]:
            result = fireball.update(self.enemies, self.flying_enemies, self.boss, self.screen.get_width(), self.screen.get_height())
            fireball.draw(self.screen)

            if result == "ground":
                self.score += 100
            elif result == "flying":
                self.score += 200
            elif result == "boss_killed":
                self.score += 1000
            if not fireball.active:
                self.fireballs.remove(fireball)

        # Filtrar solo las activas
        self.fireballs = [fb for fb in self.fireballs if fb.active]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return "quit"
                elif event.key == pygame.K_1:
                    self.player.use_item_by_key(1)
                elif event.key == pygame.K_2:
                    self.player.use_item_by_key(2)
                elif event.key == pygame.K_3:
                    self.player.use_item_by_key(3)
                elif event.key == pygame.K_SPACE:
                    if self.player.can_place_bomb():
                        bomb_x = self.start_x + ((self.player.x - self.start_x) // self.tile_size) * self.tile_size
                        bomb_y = self.start_y + ((self.player.y - self.start_y) // self.tile_size) * self.tile_size
                        bomb = Bomb(bomb_x, bomb_y, os.path.join("assets", "SPRITES", "Bomb"), self.tile_size, owner_player=self.player, explosion_sound=self.bomb_explode_sound)  
                        self.bombs.append(bomb)
                        self.player.place_bomb()

                elif event.key == pygame.K_e:
                    current_time = time.time()
                    character = self.selected_character["sprite_folder"]
                    
                    if character == "WB":
                        if current_time - self.last_fireball_time >= self.fireball_cooldown:
                            direction = self.player.last_direction
                            dx, dy = 0, 0
                            if direction == "Up":
                                dy = -1
                            elif direction == "Down":
                                dy = 1
                            elif direction == "Left":
                                dx = -1
                            elif direction == "Right":
                                dx = 1
                            if dx != 0 or dy != 0:
                                fireball_x = self.player.rect.centerx
                                fireball_y = self.player.rect.centery
                                fireball = Fireball(fireball_x, fireball_y, (dx, dy))
                                self.fireballs.append(fireball)
                                self.last_fireball_time = current_time
                                self.special_cooldown = 30  # <<< Agregado cooldown especial

                    elif character == "BB":
                        if current_time - self.last_invuln_time >= self.invuln_cooldown:
                            self.player.activate_invulnerability(duration=5)
                            self.last_invuln_time = current_time
                            self.special_cooldown = 30  # <<< Agregado cooldown especial
                            
                    elif character == "BLB":
                        if current_time - self.last_speedboost_time >= self.speedboost_cooldown:
                            self.player.activate_speedboost(duration=5, speed_increase=3)
                            self.last_speedboost_time = current_time
                            self.special_cooldown = 30  # <<< Agregado cooldown especial

                elif event.key == pygame.K_r:
                    return "reload"
        return None

    def run(self):
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(os.path.join("assets", "OST", "Level Start.mp3"))
            pygame.mixer.music.play()
            pygame.mixer.music.set_volume(self.volume_settings.get_music_volume())

            if not self.volume_settings.music_enabled:
                pygame.mixer.music.pause()     
            else:
                pygame.mixer.music.unpause()

            self.level_started = False
            self.level_start_time = pygame.time.get_ticks()
            self.level_start_duration = int(pygame.mixer.Sound(os.path.join("assets", "OST", "Level Start.mp3")).get_length() * 1000)
            self.level_complete = False
            self.level_complete_time = None
            self.level_complete_duration = 0
            self.running = True

            while self.running:
                dt = self.clock.get_time() / 1000  # <<< Agregado delta time

                if self.special_cooldown > 0:
                    self.special_cooldown = max(0, self.special_cooldown - dt)  # <<< Reducir cooldown

                now = pygame.time.get_ticks()
                if not self.level_started:
                    if now - self.level_start_time >= self.level_start_duration:
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load(os.path.join("assets", "OST", "Boss Fight.mp3"))
                        pygame.mixer.music.play(-1)
                        pygame.mixer.music.set_volume(self.volume_settings.get_music_volume())

                        if not self.volume_settings.music_enabled:
                            pygame.mixer.music.pause()     
                        else:
                            pygame.mixer.music.unpause()
                            
                        self.level_started = True
                        self.start_time = time.time()
                    else:
                        self.draw_scene(move_enemies=False)
                        pygame.display.flip()
                        self.clock.tick(60)
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                                self.running = False
                                return self.completed
                        continue

                event_result = self.handle_events()
                if event_result == "quit":
                    return self.completed

                self.update_game_state()

                # Actualizar spawn de ítems con cooldown y random
                self.update_items_spawn()

                if not self.player.alive:
                    result = self.handle_player_death()
                    if result == "reload":
                        raise StopIteration
                    elif result == "quit":
                        raise SystemExit

                if self.level_complete:
                        now = pygame.time.get_ticks()
                        self.draw_scene(move_enemies=False)
                        pygame.display.flip()

                        #Sumar puntaje y tiempo al total del juego antes de pasar al siguiente nivel
                        if not hasattr(self, '_score_added'):
                            if self.end_time is not None and self.start_time is not None:
                                self.main_game.total_time += int(self.end_time - self.start_time)
                            self.main_game.total_score += self.score
                            self._score_added = True
                        
                        if now - self.level_complete_time >= self.level_complete_duration:
                            self.show_victory_screen()
                            return self.completed
                        self.clock.tick(60)
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                                self.running = False
                                return self.completed
                        continue

                self.draw_scene(move_enemies=not self.level_complete)
                pygame.display.flip()
                self.clock.tick(60)

        except StopIteration:
            return "reload"
        except SystemExit:
            return None

        return self.completed
