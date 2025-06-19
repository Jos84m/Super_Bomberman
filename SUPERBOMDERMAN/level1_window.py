import pygame
import os
import random
from PIL import Image, ImageSequence
from Player import Player
from Pet import Pet
import pygame
import os
import random
import time
from PIL import Image, ImageSequence
from Player import Player
from Pet import Pet
from Bomb import Bomb

class LevelWindow1:
    def __init__(self, screen, clock, gif_path):
        self.screen = screen
        self.clock = clock
        self.running = True

        self.frames = []
        self.load_gif_frames(gif_path)
        self.current_frame = 0
        self.frame_delay = 5
        self.frame_counter = 0

        self.tile_size = 48
        self.rows = 11
        self.cols = 15

        self.block_image = pygame.image.load(os.path.join("assets", "block.png")).convert_alpha()

        self.block_images = {
            "#": self.block_image,
            "?": self.block_image,
            ".": None
        }

        self.bomb_image = pygame.image.load(os.path.join("assets", "bomb.png")).convert_alpha()

        self.level_map = [
            list("###############"),
            list("#.?..?..?..?..#"),
            list("#.###.###.###.#"),
            list("#.?..?..?..?..#"),
            list("#.###.###.###.#"),
            list("#.?..?..?..?..#"),
            list("#.###.###.###.#"),
            list("#.?..?..?..?..#"),
            list("#.###.###.###.#"),
            list("#.?..?..?..?..#"),
            list("###############")
        ]

        screen_width, screen_height = self.screen.get_size()
        total_width = self.cols * self.tile_size
        total_height = self.rows * self.tile_size
        self.start_x = (screen_width - total_width) // 2
        self.start_y = (screen_height - total_height) // 2 + 50

        player_x = self.start_x + 1 * self.tile_size
        player_y = self.start_y + 1 * self.tile_size
        self.player = Player(player_x, player_y, os.path.join("assets", "player.png"))

        self.bombs = []

    def load_gif_frames(self, gif_path):
        pil_gif = Image.open(gif_path)
        for frame in ImageSequence.Iterator(pil_gif):
            frame = frame.convert("RGBA")
            surface = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode).convert_alpha()
            self.frames.append(surface)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.place_bomb()

    def place_bomb(self):
        col = (self.player.x - self.start_x) // self.tile_size
        row = (self.player.y - self.start_y) // self.tile_size
        x = self.start_x + col * self.tile_size
        y = self.start_y + row * self.tile_size
        current_time = time.time()
        self.bombs.append(Bomb(x, y, self.tile_size, current_time, os.path.join("assets", "bomb.png")))

    def explode_bomb(self, bomb):
        col = (bomb.x - self.start_x) // self.tile_size
        row = (bomb.y - self.start_y) // self.tile_size

        # Afecta la cruz: centro, arriba, abajo, izquierda, derecha
        for dx, dy in [(0,0), (1,0), (-1,0), (0,1), (0,-1)]:
            r = row + dy
            c = col + dx
            if 0 <= r < self.rows and 0 <= c < self.cols:
                if self.level_map[r][c] == "?":
                    self.level_map[r][c] = "."
                    # Posibilidad de mascota
                    if random.random() < 0.4 and not self.player.pet:
                        px = self.start_x + c * self.tile_size
                        py = self.start_y + r * self.tile_size
                        self.player.pet = Pet(px, py, os.path.join("assets", "cat_pet.png"))

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)

        if self.player.pet:
            self.player.pet.follow(self.player.x - 30, self.player.y - 30)

        current_time = time.time()
        exploded_bombs = [b for b in self.bombs if b.is_exploded(current_time)]
        for bomb in exploded_bombs:
            self.explode_bomb(bomb)
            self.bombs.remove(bomb)

        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def draw(self):
        frame = pygame.transform.scale(self.frames[self.current_frame], self.screen.get_size())
        self.screen.blit(frame, (0, 0))

        for row_idx, row in enumerate(self.level_map):
            for col_idx, cell in enumerate(row):
                img = self.block_images.get(cell)
                if img:
                    x = self.start_x + col_idx * self.tile_size
                    y = self.start_y + row_idx * self.tile_size
                    y += int((col_idx - self.cols / 2) * 1.5)
                    self.screen.blit(img, (x, y))

        for bomb in self.bombs:
            bomb.draw(self.screen)

        if self.player.pet:
            self.player.pet.draw(self.screen)

        self.player.draw(self.screen)
