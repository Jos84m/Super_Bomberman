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

        self.bomb_icon = pygame.image.load(os.path.join("Assets", "Sprites", "Bomb", "Bomb 1.png"))
        self.bomb_icon = pygame.transform.scale(self.bomb_icon, (24, 24))
        
        # Sistema de nombre del jugador
        self.player_name = ""
        self.name_active = True
        self.cursor_visible = True
        self.cursor_timer = 0
        self.max_name_length = 15

        # Habilidades especiales
        self.special_abilities = {
            "Bomberman": "Bola de fuego",
            "Black Bomberman": "Invulnerabilidad",
            "Blue Bomberman": "Aumento de velocidad"
        }

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
        self.name_font = pygame.font.SysFont("Arial", 28)
        self.instruction_font = pygame.font.SysFont("Arial", 20)

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

        # Fondo del personaje
        pygame.draw.rect(self.screen, (50, 50, 50), (center_x - 200, 110, 390, 330), border_radius=15)
        pygame.draw.rect(self.screen, (200, 200, 200), (center_x - 200, 110, 390, 330), 2, border_radius=15)

        # Imagen
        self.screen.blit(character_image, (center_x - 64, 130))

        # Nombre del personaje
        name = self.characters[self.selected_index]["name"]
        name_surface = self.title_font.render(name, True, (255, 255, 255))
        self.screen.blit(name_surface, (center_x - name_surface.get_width() // 2, 270))

        # Info adicional
        char = self.characters[self.selected_index]
        lives = char["lives"]
        speed = char["speed"]
        bombs = char.get("bombs", 15)
        
        info_text = f"Vidas: {lives}   Velocidad: {speed}"
        info_surface = self.info_font.render(info_text, True, (200, 200, 200))
        self.screen.blit(info_surface, (center_x - info_surface.get_width() // 2, 330))

    # Bombas iniciales con ícono
        bomb_count = self.characters[self.selected_index].get("bombs", 0)
        bomb_surface = self.info_font.render(f"{bomb_count}", True, (255, 255, 255))
        x_surface = self.info_font.render("x", True, (255, 255, 255))
        
        bomb_x = center_x - bomb_surface.get_width() // 2 + 20
        bomb_y = 370
        
        self.screen.blit(self.bomb_icon, (bomb_x - 40, bomb_y + 2))
        self.screen.blit(x_surface, (bomb_x - 10, bomb_y))
        self.screen.blit(bomb_surface, (bomb_x, bomb_y))

        # Habilidad especial
        special_name = self.special_abilities.get(self.characters[self.selected_index]["name"], "Desconocida")
        special_text = f"Habilidad Especial: {special_name}"
        special_surface = self.info_font.render(special_text, True, (180, 180, 250))
        self.screen.blit(special_surface, (center_x - special_surface.get_width() // 2, 410))

    def draw_name_input(self):
        center_x = self.screen.get_width() // 2
        
        # Título para el nombre
        name_title = self.info_font.render("Ingresa tu nombre:", True, (255, 255, 255))
        self.screen.blit(name_title, (center_x - name_title.get_width() // 2, 470))
        
        # Caja de texto para el nombre
        name_box_rect = pygame.Rect(center_x - 150, 500, 300, 40)
        pygame.draw.rect(self.screen, (40, 40, 40), name_box_rect)
        pygame.draw.rect(self.screen, (100, 100, 255) if self.name_active else (100, 100, 100), name_box_rect, 2)
        
        # Texto del nombre
        display_name = self.player_name
        if self.name_active and self.cursor_visible:
            display_name += "|"
        
        name_surface = self.name_font.render(display_name, True, (255, 255, 255))
        text_x = name_box_rect.x + 10
        text_y = name_box_rect.y + (name_box_rect.height - name_surface.get_height()) // 2
        self.screen.blit(name_surface, (text_x, text_y))
        
        # Instrucciones
        if not self.player_name:
            instruction = "Escribe tu nombre y presiona ENTER para continuar"
        else:
            instruction = "Presiona ENTER para jugar o ESC para salir"
        
        instruction_surface = self.instruction_font.render(instruction, True, (150, 150, 150))
        self.screen.blit(instruction_surface, (center_x - instruction_surface.get_width() // 2, 550))

    def update_cursor(self):
        self.cursor_timer += 1
        if self.cursor_timer >= 30:  # Parpadeo cada medio segundo (30 frames a 60 FPS)
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def handle_name_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif event.key == pygame.K_RETURN:
                if self.player_name.strip():  # Solo continuar si hay un nombre
                    return True
            elif event.unicode.isprintable() and len(self.player_name) < self.max_name_length:
                self.player_name += event.unicode
        return False

    def run(self):
        while self.running:
            self.clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None, None
                
                # Manejar entrada de nombre
                if self.handle_name_input(event):
                    self.running = False
                    return self.characters[self.selected_index], self.player_name.strip()
                
                elif event.type == pygame.KEYDOWN:
                    # Solo usar flechas para cambiar personaje
                    if event.key == pygame.K_RIGHT:
                        self.selected_index = (self.selected_index + 1) % len(self.characters)
                        self.current_frame = 0
                    elif event.key == pygame.K_LEFT:
                        self.selected_index = (self.selected_index - 1) % len(self.characters)
                        self.current_frame = 0
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                        return None, None

            self.update_cursor()
            self.draw_background()
            
            # Título principal
            text = self.title_font.render("Selecciona tu personaje", True, (255, 255, 255))
            self.screen.blit(text, (self.screen.get_width() // 2 - text.get_width() // 2, 40))
            
            self.draw_arrows()
            self.draw_character_card()
            self.draw_name_input()
            
            pygame.display.flip()
