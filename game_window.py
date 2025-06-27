import pygame
import os
from PIL import Image
import time

class GameWindow:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.running = True
        self.nivel = 1  # si estás usando selección de niveles

    def set_level(self, nivel):
        self.nivel = nivel

        # Mapa guía
        self.map_frames = self.load_map_guide()
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_delay = 100  # velocidad de animación

        # Fuente para el nivel
        self.font = pygame.font.SysFont("Arial", 30, bold=True)
        self.current_level = 1

    def load_map_guide(self):
        frames = []
        try:
            gif_path = os.path.join("assets", "mapa_guia.gif")
            gif = Image.open(gif_path)
            for frame in range(gif.n_frames):
                gif.seek(frame)
                frame_surface = pygame.image.fromstring(
                    gif.convert("RGBA").tobytes(), gif.size, "RGBA"
                )
                frame_surface = pygame.transform.scale(frame_surface, (800, 600))
                frames.append(frame_surface)
        except Exception:
            surface = pygame.Surface((800, 600))
            surface.fill((0, 0, 0))
            frames.append(surface)
        return frames

    def show_loading_screen(self):
        self.screen.fill((0, 0, 0))
        loading_font = pygame.font.SysFont("Arial", 50, bold=True)
        loading_text = loading_font.render("Cargando...", True, (255, 255, 255))
        self.screen.blit(loading_text, loading_text.get_rect(center=(400, 300)))
        pygame.display.flip()
        time.sleep(2)

    def draw_level_info(self):
        text = self.font.render(f"Nivel actual: {self.current_level}", True, (255, 255, 0))
        self.screen.blit(text, (10, 10))

    def run(self):
        self.show_loading_screen()
        self.running = True  # por si se llama varias veces
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.screen.fill((0, 0, 0))
            pygame.display.flip()
            self.clock.tick(60)
        while self.running:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_RIGHT:
                        self.current_level += 1
                    elif event.key == pygame.K_LEFT and self.current_level > 1:
                        self.current_level -= 1

            # Actualizar animación
            now = pygame.time.get_ticks()
            if now - self.last_update > self.frame_delay:
                self.current_frame = (self.current_frame + 1) % len(self.map_frames)
                self.last_update = now

            # Dibujar
            self.screen.blit(self.map_frames[self.current_frame], (0, 0))
            self.draw_level_info()
            pygame.display.flip()
