import pygame
from PIL import Image
import os

class LevelMap:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.frames = self.load_gif_frames(os.path.join("assets", "GIFS", "Mapa.gif"))
        self.running = True

    def load_gif_frames(self, path):
        gif = Image.open(path)
        frames = []
        for i in range(gif.n_frames):
            gif.seek(i)
            surf = pygame.image.fromstring(
                gif.convert("RGBA").tobytes(), gif.size, "RGBA")
            frames.append(pygame.transform.scale(surf, (800, 600)))
        return frames

    def run(self):
        frame_index = 0
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return "back"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.running = False
                        return "continue"
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                        return "back"
                    
            self.screen.blit(self.frames[frame_index], (0, 0))
            pygame.display.flip()
            frame_index = (frame_index + 1) % len(self.frames)
            self.clock.tick(8)