import pygame 
import os
import random
import time
from PIL import Image, ImageSequence
from Player import Player
from Bomb import Bomb
from Enemy import Enemy
from Hud import HUD
from Breakable_Box import BreakableBox
from Item import Item
from Trap import Trap  # Importamos la clase Trap

class LevelWindow1:
    def __init__(self, screen, clock, gif_path, selected_character, main_game, volume_settings):
        self.main_game = main_game
        self.screen = screen
        self.clock = clock
        self.running = True
        self.selected_character = selected_character
        self.completed = False
        self.volume_settings = volume_settings

        self.frames = []
        self.load_gif_frames(gif_path)
        self.current_frame = 0
        self.frame_delay = 5
        self.frame_counter = 0

        self.tile_size = 48
        self.rows = 11
        self.cols = 15

        self.block_image = pygame.image.load(os.path.join("assets", "box.png")).convert_alpha()
        self.box_image = pygame.image.load(os.path.join("assets", "box.png")).convert_alpha()
        self.exit_image = pygame.image.load(os.path.join("assets", "door.png")).convert_alpha()
        self.block_images = {"#": self.block_image, "?": self.box_image, "E": self.exit_image}

        self.heart_image = pygame.image.load(os.path.join("assets", "heart.png")).convert_alpha()
        self.heart_image = pygame.transform.scale(self.heart_image, (32, 32))

        self.start_time = None 
        self.end_time = None

        # Aquí, en el mapa, agregamos 'S' para las trampas de pinchos
        self.level_map = [
            list("###############"),
            list("#P     S      #"),
            list("# # # # # # # #"),
            list("#   ? # # ? S #"),
            list("#?### # # ###?#"),
            list("#  S  # #     #"),
            list("# # # # # # # #"),
            list("# S ? # # ?   #"),
            list("# # # # # # # #"),
            list("#E S  ? ?  S  #"),
            list("###############")
        ]

        screen_width, screen_height = self.screen.get_size()
        total_width = self.cols * self.tile_size
        total_height = self.rows * self.tile_size
        self.start_x = (screen_width - total_width) // 2
        self.start_y = (screen_height - total_height - 100) // 2

        sprite_folder = os.path.join("assets", "SPRITES", "Characters", selected_character["sprite_folder"])
        sprite_prefix = selected_character["sprite_folder"]

        self.lives = selected_character.get("lives", 3)

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

        enemy_sprite_folder = os.path.join("assets", "SPRITES", "Enemies", "Basic enemies")
        self.enemies = [
            Enemy(self.start_x + 1 * self.tile_size, self.start_y + 9 * self.tile_size, enemy_sprite_folder, self.tile_size),
            Enemy(self.start_x + 13 * self.tile_size, self.start_y + 9 * self.tile_size, enemy_sprite_folder, self.tile_size)
        ]
        for enemy in self.enemies:
            enemy.active = True

        self.breakable_boxes = []
        cajas_posiciones = []
        for row_idx, row in enumerate(self.level_map):
            for col_idx, tile in enumerate(row):
                if tile == "?":
                    cajas_posiciones.append((row_idx, col_idx))

        caja_llave_pos = random.choice(cajas_posiciones) if cajas_posiciones else None

        for row_idx, col_idx in cajas_posiciones:
            x = self.start_x + col_idx * self.tile_size
            y = self.start_y + row_idx * self.tile_size
            
            if (row_idx, col_idx) == caja_llave_pos:
                contenido = "key"
            else:
                contenido = random.choice(["accelerator", "extra_bombs", "explosion_expander", "heart"])

            box = BreakableBox(x, y, self.tile_size, contenido)
            self.breakable_boxes.append(box)

        self.bombs = []
        self.explosions = []
        self.items = []

        # Aquí inicializamos las trampas de pinchos según el mapa (con 'S')
        self.traps = []
        for row_idx, row in enumerate(self.level_map):
            for col_idx, tile in enumerate(row):
                if tile == 'S':
                    x = self.start_x + col_idx * self.tile_size
                    y = self.start_y + row_idx * self.tile_size
                    sprite_base_path = os.path.join("assets", "SPRITES", "Traps")
                    trap = Trap(x, y, self.tile_size, trap_type="spike", sprite_base_path=sprite_base_path)
                    self.traps.append(trap)

        self.score = 0
        self.start_time = time.time()

        self.level_started = False
        self.level_start_time = None
        self.level_start_duration = 0
        self.level_complete = False
        self.level_complete_time = None
        self.level_complete_duration = 0

        self.bomb_explode_sound = pygame.mixer.Sound(os.path.join("assets", "SOUNDS", "Bomb Explodes.mp3"))
        self.player_death_sound = pygame.mixer.Sound(os.path.join("assets", "SOUNDS", "Bomberman Dies.mp3"))

        # Inicializamos el HUD aquí
        self.hud = HUD(self.screen, pygame.time.get_ticks(), lives=self.lives, score=self.score, level=1)

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
            self.player.start_x = self.start_x + 1 * self.tile_size
            self.player.start_y = self.start_y + 1 * self.tile_size
            self.player.respawn()

    def show_game_over_screen(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.load(os.path.join("assets", "OST", "Game Over.mp3"))
        pygame.mixer.music.play()
        pygame.mixer.music.set_volume(self.volume_settings.get_music_volume())
        
        # Pausar música si está desactivada
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

    def draw_scene(self, move_enemies=True):
        self.screen.blit(pygame.transform.scale(self.frames[self.current_frame], self.screen.get_size()), (0, 0))
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

        for row_idx, row in enumerate(self.level_map):
            for col_idx, tile in enumerate(row):
                if tile in self.block_images:
                    x = self.start_x + col_idx * self.tile_size
                    y = self.start_y + row_idx * self.tile_size
                    self.screen.blit(self.block_images[tile], (x, y))

        for box in self.breakable_boxes:
            if not box.destroyed:
                box.draw(self.screen)

        for bomb in self.bombs:
            bomb.draw(self.screen, self.start_x, self.start_y)

        for explosion in self.explosions[:]:
            explosion.update()
            explosion.draw(self.screen)
            if explosion.finished:
                self.explosions.remove(explosion)

        for item in self.items:
            item.draw(self.screen)

        # Dibuja trampas
        for trap in self.traps:
            trap.draw(self.screen)

        # Colisiones explosiones - jugador
        for explosion in self.explosions:
            if not explosion.finished and explosion.get_rect().colliderect(self.player.get_rect()):
                if not self.player.dying and self.player.alive:
                    self.player.lose_life_from_explosion()
                    if self.player.lives <= 0:
                        result = self.handle_player_death()
                        if result == "reload":
                            raise StopIteration
                        elif result == "quit":
                            raise SystemExit

        # Movimiento y colisiones enemigos
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

        # Colisiones jugador - ítems
        for item in self.items[:]:
            if item.get_rect().colliderect(self.player.get_rect()) and not item.is_collected():
                item.collect()
                if item.item_type == "key":
                    self.player.pick_key()
                    self.hud.has_key = True
                elif item.item_type in {"heart"}:
                    self.player.apply_item_effect(item.item_type)
                else:
                    self.player.collect_item(item.item_type)

                self.items.remove(item)
                self.score += 50

        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Dibuja el HUD moderno
        self.hud.lives = self.player.lives
        self.hud.score = self.score
        self.hud.level = 1  # Cambia según el nivel
        self.hud.update(time.time() - self.start_time)
        self.hud.draw(self.player.get_items_for_hud())

    def run(self):
        while True:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(os.path.join("assets", "OST", "Level Start.mp3"))
                pygame.mixer.music.play()
                pygame.mixer.music.set_volume(self.volume_settings.get_music_volume())

                # Pausar música si está desactivada
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
                    now = pygame.time.get_ticks()
                    dt = self.clock.get_time() / 1000.0
                    if not self.level_started:
                        if now - self.level_start_time >= self.level_start_duration:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load(os.path.join("assets", "OST", "Level 1.mp3"))
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

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                            self.running = False
                            return self.completed
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                            if not self.player.dying and self.player.alive:
                                if self.player.can_place_bomb():
                                    relative_x = self.player.x - self.start_x
                                    relative_y = self.player.y - self.start_y

                                    bomb_col = relative_x // self.tile_size
                                    bomb_row = relative_y // self.tile_size

                                    bomb_x = self.start_x + bomb_col * self.tile_size
                                    bomb_y = self.start_y + bomb_row * self.tile_size

                                    bomb = Bomb(bomb_x, bomb_y, os.path.join("assets", "SPRITES", "Bomb"), self.tile_size, owner_player=self.player, explosion_sound=self.bomb_explode_sound)            
                                    bomb.level = self

                                    self.bombs.append(bomb)
                                    self.player.place_bomb()
                                    self.player.bomb_cell = (bomb_col, bomb_row)
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_1:
                                self.player.use_item_by_key(1)
                            elif event.key == pygame.K_2:
                                self.player.use_item_by_key(2)
                            elif event.key == pygame.K_3:
                                self.player.use_item_by_key(3)  
                    
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

                    door_rect = None
                    for row_idx, row in enumerate(self.level_map):
                        for col_idx, tile in enumerate(row):
                            if tile == 'E':
                                x = self.start_x + col_idx * self.tile_size
                                y = self.start_y + row_idx * self.tile_size
                                door_rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                                break
                        if door_rect:
                            break

                    if door_rect and door_rect.colliderect(self.player.get_rect()) and not self.level_complete:
                        if self.player.has_key:
                            self.level_complete = True
                            self.level_complete_time = pygame.time.get_ticks()
                            self.hud.timer_active = False
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

                    for bomb in self.bombs[:]:
                        if self.level_complete:
                            bomb.freeze()
                        finished = bomb.update(self.level_map, self.enemies, player=self.player, start_x=self.start_x, start_y=self.start_y, score_callback=lambda points: setattr(self, 'score', self.score + points))

                        if finished:
                            self.bombs.remove(bomb)
                            self.player.bomb_exploded()

                    for box in self.breakable_boxes:
                        if box.destroyed and not box.content_spawned:
                            new_item = Item(box.x, box.y, self.tile_size, box.get_content())
                            self.items.append(new_item)
                            box.content_spawned = True

                            col = (box.x - self.start_x) // self.tile_size
                            row = (box.y - self.start_y) // self.tile_size
                            self.level_map[row][col] = " "

                    # Actualizamos trampas y daño por pinchos
                    player_rect = self.player.get_rect()
                    for trap in self.traps:
                        trap.update(self.player)
                        # Daño solo si está en frame peligroso y colisiona y jugador vivo
                        if trap.is_dangerous_frame() and trap.rect.colliderect(player_rect) and not self.player.dying and self.player.alive:
                            self.player.lose_life()
                            if self.player.lives <= 0:
                                result = self.handle_player_death()
                                if result == "reload":
                                    raise StopIteration
                                elif result == "quit":
                                    raise SystemExit

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

                    # Al actualizar el tiempo:
                    self.hud.lives = self.player.lives
                    self.hud.score = self.score
                    self.hud.level = 1  # Cambia según el nivel
                    self.hud.update(time.time() - self.start_time)

                    self.draw_scene(move_enemies=not self.level_complete)
                    pygame.display.flip()
                    self.clock.tick(60)

            except StopIteration:
                return "reload"
            except SystemExit:
                return None

            return self.completed
