import pygame
import os
from PIL import Image
from volume_settings import VolumeSettings
from volume_window import VolumeConfigWindow
from about_window import AboutWindow
from loading_screen import LoadingScreen
from level_map import LevelMap
from level1_window import LevelWindow1
from level2_window import LevelWindow2
from level3_window import LevelWindow3
from Seleccion import CharacterSelectWindow

class BombermanGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Bomberman Ultimate")
        icon = pygame.image.load(os.path.join("assets", "icon.png"))
        pygame.display.set_icon(icon)
        self.clock = pygame.time.Clock()
        self.running = True

        self.about_window = AboutWindow(self.screen)
        self.volume_settings = VolumeSettings()
        self.font = pygame.font.SysFont("Arial", 32, bold=True)
        self.load_resources()

        self.volume_window = VolumeConfigWindow(
            self.screen,
            self.volume_settings,
            [self.click_sound, self.hover_sound]
        )
        pygame.mixer.music.set_volume(self.volume_settings.music_volume)

        self.bg_frames = self.load_background_gif()
        self.current_bg_frame = 0
        self.last_bg_time = pygame.time.get_ticks()
        self.bg_delay = 100
        self.bg_scroll_x = 0

        self.start_button = None
        self.options_button = None
        self.exit_button = None
        self.about_button = None

    def load_resources(self):
        sounds_path = os.path.join("assets", "SOUNDS")
        ost_path = os.path.join("assets", "OST")
        self.click_sound = pygame.mixer.Sound(os.path.join(sounds_path, "Cursor.mp3"))
        self.hover_sound = pygame.mixer.Sound(os.path.join(sounds_path, "Select.mp3"))
        self.characterselect_sound = pygame.mixer.Sound(os.path.join(ost_path, "Character Select.mp3"))
        pygame.mixer.music.load(os.path.join(ost_path, "Title screen.mp3"))
        pygame.mixer.music.play(-1)

    def load_background_gif(self):
        try:
            gif = Image.open(os.path.join("assets", "GIFS", "Bg3.gif"))
            frames = []
            for i in range(gif.n_frames):
                gif.seek(i)
                surf = pygame.image.fromstring(gif.convert("RGBA").tobytes(), gif.size, "RGBA")
                frames.append(pygame.transform.scale(surf, (800, 600)))
            return frames
        except Exception as e:
            print("Fallo GIF:", e)
            return [pygame.Surface((800, 600))]

    def draw_button(self, text, center):
        rect = pygame.Rect(0, 0, 280, 60)
        rect.center = center
        mpos = pygame.mouse.get_pos()
        over = rect.collidepoint(mpos)
        color = (70,70,70) if over else (30,30,30)
        pygame.draw.rect(self.screen, (200,200,200), rect, border_radius=12)
        pygame.draw.rect(self.screen, color, rect.inflate(-4,-4), border_radius=10)
        lbl = self.font.render(text, True, (255,255,255))
        self.screen.blit(lbl, lbl.get_rect(center=center))
        if over and getattr(self, "last_hover", None) != text:
            self.hover_sound.play()
            self.last_hover = text
        elif not over and getattr(self, "last_hover", None) == text:
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
        self.screen.blit(frame, (-self.bg_scroll_x,0))
        self.screen.blit(frame, (800-self.bg_scroll_x,0))

    def show_final_victory_screen(self):
        font_big = pygame.font.SysFont("Arial", 60)
        font_small = pygame.font.SysFont("Arial", 36)
        msg = font_big.render("¡Has completado todos los niveles!", True, (0, 255, 0))
        menu_msg = font_small.render("Presiona M para volver al menú", True, (200, 200, 200))

        while True:
            self.screen.fill((0, 0, 0))
            self.screen.blit(msg, msg.get_rect(center=(400, 200)))
            self.screen.blit(menu_msg, menu_msg.get_rect(center=(400, 400)))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        return

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if self.start_button.collidepoint(e.pos):
                    self.click_sound.play()
                    while True:
                        pygame.mixer.music.stop()
                        pygame.mixer.music.load(os.path.join("assets", "OST", "Character Select.mp3"))
                        pygame.mixer.music.play(-1)

                        select = CharacterSelectWindow(self.screen, self.clock, [
                            {"name": "Bomberman", "gif_path": os.path.join("assets", "GIFS", "player1.gif"), "lives": 3, "speed": 2},
                            {"name": "Black Bomberman", "gif_path": os.path.join("assets", "GIFS", "player3.gif"), "lives": 5, "speed": 1},
                            {"name": "Blue Bomberman", "gif_path": os.path.join("assets", "GIFS", "player2.gif"), "lives": 2, "speed": 3}
                        ])
                        selected_character = select.run()
                        if not selected_character:
                            pygame.mixer.music.stop()
                            loader = LoadingScreen(self.screen)
                            loader.run(duration=2000)
                            pygame.mixer.music.load(os.path.join("assets", "OST", "Title screen.mp3"))
                            pygame.mixer.music.play(-1)
                            return

                        # --- Silencio en la pantalla de carga tras selección de personaje ---
                        pygame.mixer.music.stop()
                        loader = LoadingScreen(self.screen)
                        loader.run(duration=3000)

                        while True:
                            pygame.mixer.music.load(os.path.join("assets", "OST", "Map.mp3"))
                            pygame.mixer.music.play(-1)
                            mapa = LevelMap(self.screen)
                            mapa_result = mapa.run()
                            if mapa_result == "continue":
                                # --- Pantalla de carga antes de entrar al primer nivel ---
                                pygame.mixer.music.stop()
                                loader = LoadingScreen(self.screen)
                                loader.run(duration=3000)
                                # Nivel 1
                                while True:
                                    level1 = LevelWindow1(self.screen, self.clock, os.path.join("assets", "GIFS", "Bg2.gif"), selected_character)
                                    level1_result = level1.run()
                                    if level1_result == "reload":
                                        loader = LoadingScreen(self.screen)
                                        loader.run(duration=3000)
                                        continue
                                    elif not level1_result:
                                        pygame.mixer.music.stop()
                                        loader = LoadingScreen(self.screen)
                                        loader.run(duration=2000)
                                        pygame.mixer.music.load(os.path.join("assets", "OST", "Title screen.mp3"))
                                        pygame.mixer.music.play(-1)
                                        break
                                    else:
                                        break

                                if level1_result:
                                    loader = LoadingScreen(self.screen)
                                    loader.run(duration=3000)

                                    # Nivel 2
                                    while True:
                                        level2 = LevelWindow2(self.screen, self.clock, os.path.join("assets", "GIFS", "Bg3.gif"), selected_character)
                                        level2_result = level2.run()
                                        if level2_result == "reload":
                                            loader = LoadingScreen(self.screen)
                                            loader.run(duration=3000)
                                            continue
                                        elif not level2_result:
                                            pygame.mixer.music.stop()
                                            loader = LoadingScreen(self.screen)
                                            loader.run(duration=2000)
                                            pygame.mixer.music.load(os.path.join("assets", "OST", "Title screen.mp3"))
                                            pygame.mixer.music.play(-1)
                                            break
                                        else:
                                            break

                                    if level2_result:
                                        loader = LoadingScreen(self.screen)
                                        loader.run(duration=3000)

                                        # Nivel 3
                                        while True:
                                            level3 = LevelWindow3(self.screen, self.clock, os.path.join("assets", "GIFS", "Bg5.gif"), selected_character)
                                            level3_result = level3.run()
                                            if level3_result == "reload":
                                                loader = LoadingScreen(self.screen)
                                                loader.run(duration=3000)
                                                continue
                                            else:
                                                break

                                        # Victoria final
                                        pygame.mixer.music.stop()
                                        pygame.mixer.music.load(os.path.join("assets", "OST", "Victory.mp3"))
                                        pygame.mixer.music.play(-1)
                                        self.show_final_victory_screen()
                                        pygame.mixer.music.stop()
                                        loader = LoadingScreen(self.screen)
                                        loader.run(duration=2000)
                                        pygame.mixer.music.load(os.path.join("assets", "OST", "Title screen.mp3"))
                                        pygame.mixer.music.play(-1)
                                        return
                            elif mapa_result == "back":
                                pygame.mixer.music.stop()
                                loader = LoadingScreen(self.screen)
                                loader.run(duration=2000)
                                pygame.mixer.music.load(os.path.join("assets", "OST", "Character Select.mp3"))
                                pygame.mixer.music.play(-1)
                                break  # <-- Esto regresa a la selección de personaje

                        # Si el jugador vuelve a la selección, el bucle while True vuelve a mostrar selección

                elif self.options_button.collidepoint(e.pos):
                    self.click_sound.play()
                    self.volume_window.run()
                elif self.about_button.collidepoint(e.pos):
                    self.click_sound.play()
                    self.about_window.run()
                elif self.exit_button.collidepoint(e.pos):
                    self.click_sound.play()
                    self.running = False

    def run(self):
        while self.running:
            self.clock.tick(60)
            self.update_background()
            self.draw_buttons()
            self.handle_events()
            pygame.display.flip()

if __name__ == "__main__":
    BombermanGame().run()
    pygame.quit()