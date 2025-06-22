import pygame
from PIL import Image
import os

class LoadingScreen:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.frames = self.load_gif_frames(os.path.join("assets", "GIFS", "loading.gif"))

    def load_gif_frames(self, path):
        gif = Image.open(path)
        frames = []
        for i in range(getattr(gif, "n_frames", 1)):
            gif.seek(i)
            surf = pygame.image.fromstring(
                gif.convert("RGBA").tobytes(), gif.size, "RGBA")
            surf = pygame.transform.scale(surf, (800, 600))
            frames.append(surf)
        return frames

    def run(self, duration=3000):
        start = pygame.time.get_ticks()
        frame_index = 0
        while pygame.time.get_ticks() - start < duration:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            self.screen.blit(self.frames[frame_index], (0, 0))
            pygame.display.flip()
            frame_index = (frame_index + 1) % len(self.frames)
            self.clock.tick(6)  