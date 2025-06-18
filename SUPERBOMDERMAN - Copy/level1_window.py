import pygame
from PIL import Image, ImageSequence
import os


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

        self.block_images = {
            "#": pygame.image.load(os.path.join("assets", "block.png")).convert_alpha(),
            "?": pygame.image.load(os.path.join("assets", "block_destroy.png")).convert_alpha(),
            ".": None  # espacio vacío
        }

        self.level_map = [
            "###############",
            "#.?..?..?..?..#",
            "#.###.###.###.#",
            "#.?..?..?..?..#",
            "#.###.###.###.#",
            "#.?..?..?..?..#",
            "#.###.###.###.#",
            "#.?..?..?..?..#",
            "#.###.###.###.#",
            "#.?..?..?..?..#",
            "###############"
        ]

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

    def update(self):
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def draw(self):
        # Fondo animado
        frame = pygame.transform.scale(self.frames[self.current_frame], self.screen.get_size())
        self.screen.blit(frame, (0, 0))

        # Dibujar bloques con leve perspectiva
        offset_y = 100  # para simular "profundidad"
        for row_idx, row in enumerate(self.level_map):
            for col_idx, cell in enumerate(row):
                img = self.block_images.get(cell)
                if img:
                    x = col_idx * self.tile_size
                    y = row_idx * self.tile_size
                    # aplicamos offset para que parezca una vista inferior
                    y += int((col_idx - self.cols / 2) * 2) + offset_y
                    self.screen.blit(img, (x, y))
