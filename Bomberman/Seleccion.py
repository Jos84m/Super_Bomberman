import pygame
from PIL import Image, ImageSequence
import os

class CharacterSelectWindow:
    def __init__(self, screen, clock, characters):
        self.screen = screen
        self.clock = clock
        self.running = True
        self.characters = characters
        self.selected_index = 0
        self.frames_list = []
        self.current_frame = 0
        self.frame_delay = 5
        self.frame_counter = 0

        # Cargar frames de GIF
        for char in self.characters:
            gif = Image.open(char["gif_path"])
            frames = []
            for frame in ImageSequence.Iterator(gif):
                frame = frame.convert("RGBA")
                surf = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode).convert_alpha()
                surf = pygame.transform.scale(surf, (128, 128))
                frames.append(surf)
            self.frames_list.append(frames)

        self.title_font = pygame.font.SysFont("Arial", 32, bold=True)
        self.info_font = pygame.font.SysFont("Arial", 24)

    def draw_background(self):
        self.screen.fill((20, 20, 20))
        
    def draw_arrows(self):
        arrow_font = pygame.font.SysFont("Arial", 60, bold=True)
        left_arrow = arrow_font.render("<", True, (255, 255, 255))
        right_arrow = arrow_font.render(">", True, (255, 255, 255))

        self.screen.blit(left_arrow, (100, self.screen.get_height() // 2 - 30))
        self.screen.blit(right_arrow, (self.screen.get_width() - 140, self.screen.get_height() // 2 - 30))

    def draw_character_card(self):
        frames = self.frames_list[self.selected_index]
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % len(frames)

        character_image = frames[self.current_frame]
        center_x = self.screen.get_width() // 2

        # Fondo del personaje (más grande)
        pygame.draw.rect(self.screen, (50, 50, 50), (center_x - 120, 110, 240, 300), border_radius=15)
        pygame.draw.rect(self.screen, (200, 200, 200), (center_x - 120, 110, 240, 300), 2, border_radius=15)

        # Imagen
        self.screen.blit(character_image, (center_x - 64, 130))

        # Nombre
        name = self.characters[self.selected_index]["name"]
        name_surface = self.title_font.render(name, True, (255, 255, 255))
        self.screen.blit(name_surface, (center_x - name_surface.get_width() // 2, 270))

        # Info adicional
        lives = self.characters[self.selected_index]["lives"]
        speed = self.characters[self.selected_index]["speed"]
        info_text = f"Vidas: {lives}   Velocidad: {speed}"
        info_surface = self.info_font.render(info_text, True, (200, 200, 200))
        self.screen.blit(info_surface, (center_x - info_surface.get_width() // 2, 330))

    def run(self):
        while self.running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.selected_index = (self.selected_index + 1) % len(self.characters)
                        self.current_frame = 0
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.selected_index = (self.selected_index - 1) % len(self.characters)
                        self.current_frame = 0
                    elif event.key == pygame.K_RETURN:
                        self.running = False
                        return self.characters[self.selected_index]
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                        return None

            self.draw_background()
            text = self.title_font.render("Selecciona tu personaje", True, (255, 255, 255))
            self.screen.blit(text, (self.screen.get_width() // 2 - text.get_width() // 2, 40))
            self.draw_arrows()
            self.draw_character_card()
            pygame.display.flip()