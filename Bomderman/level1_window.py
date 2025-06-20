import pygame
import os
import random
import time
from PIL import Image, ImageSequence
from Player import Player
from Pet import Pet
from Bomb import Bomb
from Enemy import Enemy
from Hub import HUD
from Explosion import Explosion

class LevelWindow1:
    def __init__(self, screen, clock, gif_path, selected_character):
        self.screen = screen
        self.clock = clock
        self.running = True
        self.selected_character = selected_character

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
            list("#P            #"),
            list("# # # # # # # #"),
            list("#   ? ? ? ?   #"),
            list("# # # # # # # #"),
            list("#   ? ? ? ?   #"),
            list("# # # # # # # #"),
            list("#   ? ? ? ?   #"),
            list("# # # # # # # #"),
            list("#E          X #"),
            list("###############")
        ]

        screen_width, screen_height = self.screen.get_size()
        total_width = self.cols * self.tile_size
        total_height = self.rows * self.tile_size
        self.start_x = (screen_width - total_width) // 2
        self.start_y = (screen_height - total_height - 60) // 2

        # Jugador con personaje seleccionado
        player_gif = selected_character.get("gif_path", "assets/player.gif")
        self.player = Player(self.start_x + 1 * self.tile_size, self.start_y + 1 * self.tile_size, player_gif)

        self.enemies = [
            Enemy(self.start_x + 1 * self.tile_size, self.start_y + 9 * self.tile_size, "assets/enemy.png", self.tile_size),
            Enemy(self.start_x + 13 * self.tile_size, self.start_y + 9 * self.tile_size, "assets/enemy.png", self.tile_size)
        ]

        self.bombs = []
        self.explosions = []
        self.lives = selected_character.get("lives", 3)
        self.score = 0
        self.start_time = time.time()

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
            self.show_game_over_screen()
        else:
            self.player.x = self.start_x + 1 * self.tile_size
            self.player.y = self.start_y + 1 * self.tile_size

    def show_game_over_screen(self):
        font_big = pygame.font.SysFont("Arial", 72)
        font_small = pygame.font.SysFont("Arial", 36)
        msg = font_big.render("¡GAME OVER!", True, (255, 0, 0))
        score_msg = font_small.render(f"Puntaje final: {self.score}", True, (255, 255, 255))
        retry_msg = font_small.render("Presiona R para reintentar o ESC para salir", True, (200, 200, 200))

        while True:
            self.screen.fill((0, 0, 0))
            self.screen.blit(msg, msg.get_rect(center=(400, 200)))
            self.screen.blit(score_msg, score_msg.get_rect(center=(400, 300)))
            self.screen.blit(retry_msg, retry_msg.get_rect(center=(400, 400)))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        return
                    elif event.key == pygame.K_r:
                        self.restart_game()
                        return

    def restart_game(self):
        self.__init__(self.screen, self.clock, "assets/Bg2.gif", self.selected_character)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    bomb = Bomb(self.player.x, self.player.y)
                    self.bombs.append(bomb)

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

            # Actualizar y dibujar explosiones
            for explosion in self.explosions[:]:
                explosion.update()
                explosion.draw(self.screen)
                if explosion.finished:
                    self.explosions.remove(explosion)

            # Colisiones con jugador
            for explosion in self.explosions:
                if explosion.get_rect().colliderect(self.player.get_rect()):
                    self.handle_player_death()

            # Enemigos: mover, colisiones, y eliminar
            for enemy in self.enemies[:]:
                enemy.move(self.level_map, self.start_x, self.start_y)

                if enemy.get_rect().colliderect(self.player.get_rect()):
                    self.handle_player_death()

                for explosion in self.explosions:
                    for row_idx, row in enumerate(self.level_map):
                        for col_idx, tile in enumerate(row):
                            if tile == '?':
                                x = self.start_x + col_idx * self.tile_size
                                y = self.start_y + row_idx * self.tile_size
                                block_rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                                if explosion.get_rect().colliderect(block_rect):
                                 self.level_map[row_idx][col_idx] = ' '


            # Dibujar jugador y enemigos
            self.player.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)

            self.draw_hud()
            pygame.display.flip()
            self.clock.tick(60)
