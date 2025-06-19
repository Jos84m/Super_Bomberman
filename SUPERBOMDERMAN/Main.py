import pygame
import os
import sys
from PIL import Image
from volume_settings import VolumeSettings
from volume_window import VolumeConfigWindow
from about_window import AboutWindow
from game_window import GameWindow   
from loading_screen import LoadingScreen
from level_map import LevelMap
from level1_window import LevelWindow1
from Pet import Pet


class BombermanGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Bomberman Ultimate")
        self.clock = pygame.time.Clock()
        self.running = True

        # Ventanas adicionales
        self.about_window = AboutWindow(self.screen)
        self.volume_settings = VolumeSettings()
        self.font = pygame.font.SysFont("Arial", 32, bold=True)

        # Sonidos y música
        self.load_resources()
        self.volume_window = VolumeConfigWindow(
            self.screen,
            self.volume_settings,
            [self.click_sound, self.hover_sound]
        )
        pygame.mixer.music.set_volume(self.volume_settings.music_volume)

        # Fondo animado del menú
        self.bg_frames = self.load_background_gif()
        self.current_bg_frame = 0
        self.last_bg_time = pygame.time.get_ticks()
        self.bg_delay = 100
        self.bg_scroll_x = 0

        # Botones del menú
        self.start_button = None
        self.options_button = None
        self.exit_button = None
        self.about_button = None

        self.game_window = GameWindow(self.screen, self.clock)
        self.last_hover = None

    def load_resources(self):
        ap = "assets"
        self.click_sound = pygame.mixer.Sound(os.path.join(ap, "Cursor.mp3"))
        self.hover_sound = pygame.mixer.Sound(os.path.join(ap, "Select.mp3"))
        pygame.mixer.music.load(os.path.join(ap, "Music.mp3"))
        pygame.mixer.music.play(-1)

    def load_background_gif(self):
        try:
            gif = Image.open(os.path.join("assets", "Bg1.gif"))
            frames = []
            for i in range(gif.n_frames):
                gif.seek(i)
                surf = pygame.image.fromstring(gif.convert("RGBA").tobytes(), gif.size, "RGBA")
                frames.append(pygame.transform.scale(surf, (800, 600)))
            return frames
        except Exception as e:
            print("Fallo al cargar el fondo GIF:", e)
            return [pygame.Surface((800, 600))]

    def draw_button(self, text, center):
        rect = pygame.Rect(0, 0, 280, 60)
        rect.center = center
        mpos = pygame.mouse.get_pos()
        over = rect.collidepoint(mpos)
        color = (70, 70, 70) if over else (30, 30, 30)
        pygame.draw.rect(self.screen, (200, 200, 200), rect, border_radius=12)
        pygame.draw.rect(self.screen, color, rect.inflate(-4, -4), border_radius=10)
        lbl = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(lbl, lbl.get_rect(center=center))
        if over and self.last_hover != text:
            self.hover_sound.play()
            self.last_hover = text
        elif not over and self.last_hover == text:
            self.last_hover = None
        return rect

    def draw_buttons(self):
        self.start_button = self.draw_button("Iniciar Juego", (400, 230))
        self.options_button = self.draw_button("Opciones", (400, 310))
        self.about_button = self.draw_button("Acerca de", (400, 390))
        self.exit_button = self.draw_button("Salir", (400, 470))

    def update_background(self):
        now = pygame.time.get_ticks()
        if now - self.last_bg_time > self.bg_delay:
            self.current_bg_frame = (self.current_bg_frame + 1) % len(self.bg_frames)
            self.last_bg_time = now
        frame = self.bg_frames[self.current_bg_frame]
        self.bg_scroll_x = (self.bg_scroll_x + 1) % 800
        self.screen.blit(frame, (-self.bg_scroll_x, 0))
        self.screen.blit(frame, (800 - self.bg_scroll_x, 0))

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if self.start_button and self.start_button.collidepoint(mouse_pos):
                    self.click_sound.play()

                    # Pantalla de carga
                    loader = LoadingScreen(self.screen)
                    loader.run()

                    # Mapa de selección de nivel (opcional)
                    mapa = LevelMap(self.screen)
                    mapa.run()

                    # Iniciar el Nivel 1 con bombas y mascota
                    level1 = LevelWindow1(self.screen, self.clock, os.path.join("assets", "Bg2.gif"))
                    level1.run()

                    # Al volver del juego, reiniciar música
                    pygame.mixer.music.play(-1)

                elif self.options_button and self.options_button.collidepoint(mouse_pos):
                    self.click_sound.play()
                    self.volume_window.run()

                elif self.about_button and self.about_button.collidepoint(mouse_pos):
                    self.click_sound.play()
                    self.about_window.run()

                elif self.exit_button and self.exit_button.collidepoint(mouse_pos):
                    self.click_sound.play()
                    self.running = False

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.update_background()
            self.draw_buttons()
            self.handle_events()
            pygame.display.flip()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = BombermanGame()
    game.run()
