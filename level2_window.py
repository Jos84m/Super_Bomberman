import pygame
import os
import random
import time
from PIL import Image, ImageSequence
from Player import Player
from Pet import Pet
from Bomb import Bomb
from Enemy import Enemy
from Hud import HUD
from Explosion import Explosion

class LevelWindow2:
    def __init__(self, screen, clock, gif_path, selected_character):
        self.screen = screen
        self.clock = clock
        self.running = True
        self.selected_character = selected_character
        self.completed = False

        self.frames = []
        self.load_gif_frames(gif_path)
        self.current_frame = 0
        self.frame_delay = 5
        self.frame_counter = 0

        self.tile_size = 48
        self.rows = 13
        self.cols = 15

        self.block_image = pygame.image.load(os.path.join("assets", "box.png")).convert_alpha()
        self.box_image = pygame.image.load(os.path.join("assets", "box.png")).convert_alpha()
        self.exit_image = pygame.image.load(os.path.join("assets", "door.png")).convert_alpha()
        self.block_images = {"#": self.block_image, "?": self.box_image, "E": self.exit_image}
        self.bomb_image = pygame.image.load(os.path.join("assets", "bomb.png")).convert_alpha()
        self.heart_image = pygame.image.load(os.path.join("assets", "heart.png")).convert_alpha()
        self.heart_image = pygame.transform.scale(self.heart_image, (32, 32))

        self.level_map = [
            list("###############"),
            list("#P   #   #   E#"),
            list("# # # # # # # #"),
            list("#   ?   ?   ? #"),
            list("### # ### # ###"),
            list("# ?   ?   ?  #"),
            list("# # ### # ### #"),
            list("#   ?   ?   ? #"),
            list("### # ### # ###"),
            list("# ?   ?   ?  #"),
            list("# # # # # # # #"),
            list("#X          X #"),
            list("###############")
        ]

        screen_width, screen_height = self.screen.get_size()
        total_width = self.cols * self.tile_size
        total_height = self.rows * self.tile_size
        self.start_x = (screen_width - total_width) // 2
        self.start_y = (screen_height - total_height - 60) // 2

        # Carga carpeta sprites del personaje seleccionado
        sprite_folder = os.path.join("assets", "SPRITES", "Characters", selected_character["sprite_folder"])
        sprite_prefix = selected_character["sprite_folder"]
        self.player = Player(
            self.start_x + 1 * self.tile_size,
            self.start_y + 1 * self.tile_size,
            sprite_folder,
            sprite_prefix,
            selected_character.get("speed", 2)
        )

        # Cambiado: enemigos usan carpeta SPRITES/Enemies/Basic enemies con animación ping-pong
        enemy_sprite_folder = os.path.join("assets", "SPRITES", "Enemies", "Basic enemies")
        self.enemies = [
            Enemy(self.start_x + 1 * self.tile_size, self.start_y + 11 * self.tile_size, enemy_sprite_folder, self.tile_size),
            Enemy(self.start_x + 13 * self.tile_size, self.start_y + 11 * self.tile_size, enemy_sprite_folder, self.tile_size)
        ]

        self.bombs = []
        self.explosions = []
        self.lives = selected_character.get("lives", 3)
        self.score = 0
        self.start_time = time.time()

        self.level_started = False
        self.level_start_time = None
        self.level_start_duration = 0
        self.level_complete = False
        self.level_complete_time = None
        self.level_complete_duration = 0

    def load_gif_frames(self, gif_path):
        pil_gif = Image.open(gif_path)
        for frame in ImageSequence.Iterator(pil_gif):
            frame = frame.convert("RGBA")
            surface = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode).convert_alpha()
            self.frames.append(surface)

    def draw_hud(self):
        font = pygame.font.SysFont("Arial", 26)
        elapsed_time = int(time.time() - self.start_time)
        pygame.draw.rect(self.screen, (0, 0, 0), (0, self.screen.get_height() - 60, self.screen.get_width(), 60))

        for i in range(min(self.lives, 5)):
            x = 20 + i * 40
            y = self.screen.get_height() - 50
            self.screen.blit(self.heart_image, (x, y))

        hud_text = f"Puntos: {self.score}   Tiempo: {elapsed_time}s"
        text_surface = font.render(hud_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 30))
        self.screen.blit(text_surface, text_rect)

    def handle_player_death(self):
        self.lives -= 1
        if self.lives <= 0:
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

    def show_game_over_screen(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.load(os.path.join("assets", "OST", "Game Over.mp3"))
        pygame.mixer.music.play()

        font_big = pygame.font.SysFont("Arial", 72)
        font_small = pygame.font.SysFont("Arial", 36)
        msg = font_big.render("¡GAME OVER!", True, (255, 0, 0))
        score_msg = font_small.render(f"Puntaje final: {self.score}", True, (255, 255, 255))
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

        for explosion in self.explosions[:]:
            explosion.update()
            explosion.draw(self.screen)
            if explosion.finished:
                self.explosions.remove(explosion)

        for explosion in self.explosions:
            if explosion.get_rect().colliderect(self.player.get_rect()):
                result = self.handle_player_death()
                if result == "reload":
                    raise StopIteration
                elif result == "quit":
                    raise SystemExit

        for enemy in self.enemies[:]:
            if move_enemies:
                enemy.move(self.level_map, self.start_x, self.start_y)
            if enemy.get_rect().colliderect(self.player.get_rect()):
                result = self.handle_player_death()
                if result == "reload":
                    raise StopIteration
                elif result == "quit":
                    raise SystemExit
            for explosion in self.explosions:
                if explosion.get_rect().colliderect(enemy.get_rect()):
                    self.enemies.remove(enemy)
                    self.score += 100

        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)

        self.draw_hud()

    def run(self):
        while True:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(os.path.join("assets", "OST", "Level Start.mp3"))
                pygame.mixer.music.play()
                self.level_started = False
                self.level_start_time = pygame.time.get_ticks()
                self.level_start_duration = int(pygame.mixer.Sound(os.path.join("assets", "OST", "Level Start.mp3")).get_length() * 1000)
                self.level_complete = False
                self.level_complete_time = None
                self.level_complete_duration = 0
                self.running = True

                while self.running:
                    now = pygame.time.get_ticks()
                    if not self.level_started:
                        if now - self.level_start_time >= self.level_start_duration:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load(os.path.join("assets", "OST", "Level 2.mp3"))
                            pygame.mixer.music.play(-1)
                            self.level_started = True
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
                            bomb = Bomb(self.player.x, self.player.y, os.path.join("assets", "bomb.png"), self.tile_size)
                            self.bombs.append(bomb)

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

                    if not self.level_complete:
                        if dx != 0 or dy != 0:
                            self.player.move(dx, dy, self.level_map, self.tile_size, self.start_x, self.start_y, self.bombs)
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
                        self.level_complete = True
                        self.level_complete_time = pygame.time.get_ticks()
                        self.level_complete_duration = int(pygame.mixer.Sound(os.path.join("assets", "OST", "Level Complete.mp3")).get_length() * 1000)
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load(os.path.join("assets", "OST", "Level Complete.mp3"))
                        pygame.mixer.music.play()

                    if self.level_complete:
                        now = pygame.time.get_ticks()
                        self.draw_scene(move_enemies=False)
                        pygame.display.flip()
                        if now - self.level_complete_time >= self.level_complete_duration:
                            self.show_victory_screen()
                            return self.completed
                        self.clock.tick(60)
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                                self.running = False
                                return self.completed
                        continue

                    try:
                        self.draw_scene(move_enemies=not self.level_complete)
                    except StopIteration:
                        return "reload"
                    except SystemExit:
                        return None
                    pygame.display.flip()
                    self.clock.tick(60)

            except StopIteration:
                return "reload"
            except SystemExit:
                return None

            return self.completed
