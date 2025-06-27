import pygame
import os

class AboutWindow:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 22)
        self.title_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.running = True
        self.show_authors = False

        self.scroll_offset_info = 0
        self.scroll_speed = 30

        self.scroll_offset_authors = 0

        # Cargar imágenes de autores (200x200)
        self.author1_img = self.load_author_image("autor1.png", (200, 200))
        self.author2_img = self.load_author_image("autor2.png", (200, 200))

        # Texto informativo
        self.text_lines = [
            "Vintage Bomberman v1.0",
            "",
            "Desarrollado para:",
            "Instituto Tecnológico de Costa Rica",
            "Escuela de Ingeniería en Computadores",
            "Curso: Introducción a la Programación",
            "",
            "Profesores:",
            "Jeff Schmidt Peralta",
            "Diego Mora Rojas",
            "",
            "Año: 2025",
            "País: Costa Rica",
            "",
            "Objetivo:",
            "Avanza por los niveles hasta encontrar la llave y luego ir a la puerta",
            "pero, ten cuidado si no es la puerta correcta puedes terminar en un lugar no deseado.",
            "Evita los enemigos y ten cuidado con tus propias bombas.",
            "",
            "",
            "",
        ]

    def load_author_image(self, filename, size):
        if os.path.exists(filename):
            img = pygame.image.load(filename).convert_alpha()
            return pygame.transform.scale(img, size)
        else:
            img = pygame.Surface(size)
            img.fill((100, 100, 100))
            font = pygame.font.SysFont("Arial", 16)
            text = font.render("Sin foto", True, (255, 255, 255))
            img.blit(text, (size[0] // 4, size[1] // 2 - 10))
            return img

    def run(self):
        screen_width, screen_height = self.screen.get_size()

        while self.running:
            self.screen.fill((30, 30, 30))

            if not self.show_authors:
                # Ventana info con scroll
                y_start = 40 - self.scroll_offset_info
                for i, line in enumerate(self.text_lines):
                    font = self.title_font if i == 0 else self.font
                    text_surface = font.render(line, True, (255, 255, 255))
                    self.screen.blit(text_surface, (60, y_start + i * 30))

                total_height = y_start + len(self.text_lines) * 30
                authors_rect = pygame.Rect(60, total_height, 180, 40)
                back_rect = pygame.Rect(300, total_height, 200, 40)

                pygame.draw.rect(self.screen, (0, 200, 100), authors_rect)
                authors_text = self.font.render("Autores", True, (255, 255, 255))
                self.screen.blit(authors_text, (authors_rect.x + 50, authors_rect.y + 5))

                pygame.draw.rect(self.screen, (100, 100, 255), back_rect)
                back_text = self.font.render("← Volver", True, (255, 255, 255))
                self.screen.blit(back_text, (back_rect.x + 50, back_rect.y + 5))

            else:
                # Ventana autores con scroll
                y_start = 30 - self.scroll_offset_authors
                img_x = (screen_width - 200) // 2

                # Autor 1
                border1 = pygame.Rect(img_x - 5, y_start - 5, 210, 210)
                pygame.draw.rect(self.screen, (255, 255, 255), border1, 2)
                self.screen.blit(self.author1_img, (img_x, y_start))

                y_start += 210
                name1 = self.font.render("Alessandro", True, (255, 255, 255))
                self.screen.blit(name1, ((screen_width - name1.get_width()) // 2, y_start))
                y_start += 40

                desc1 = [
                    "Estudiante de Ingeniería en Computadores.",
                    "Responsable de la música del juego.",
                    "Efectos de sonido del juego."
                ]
                for line in desc1:
                    rendered = self.font.render(line, True, (200, 200, 200))
                    self.screen.blit(rendered, ((screen_width - rendered.get_width()) // 2, y_start))
                    y_start += 30

                y_start += 60  # espacio entre autores

                # Autor 2
                border2 = pygame.Rect(img_x - 5, y_start - 5, 210, 210)
                pygame.draw.rect(self.screen, (255, 255, 255), border2, 2)
                self.screen.blit(self.author2_img, (img_x, y_start))

                y_start += 210
                name2 = self.font.render("Joshua Morales Guzmán", True, (255, 255, 255))
                self.screen.blit(name2, ((screen_width - name2.get_width()) // 2, y_start))
                y_start += 40

                desc2 = [
                    "Estudiante de Ingeniería en Computadores.",
                    "Responsable de los niveles y boss.",
                    "Responsable de la IA de los enemigos.",
                    "Responsable de configuraciones del juego.",
                ]
                for line in desc2:
                    rendered = self.font.render(line, True, (200, 200, 200))
                    self.screen.blit(rendered, ((screen_width - rendered.get_width()) // 2, y_start))
                    y_start += 30

                y_start += 40

                # Botón volver (se mueve con scroll)
                volver_info_rect = pygame.Rect((screen_width - 200) // 2, y_start, 200, 40)
                pygame.draw.rect(self.screen, (150, 0, 0), volver_info_rect)
                volver_text = self.font.render("← Información", True, (255, 255, 255))
                self.screen.blit(volver_text, (volver_info_rect.x + 20, volver_info_rect.y + 5))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if not self.show_authors:
                        total_height = 40 - self.scroll_offset_info + len(self.text_lines) * 30
                        authors_rect = pygame.Rect(60, total_height, 180, 40)
                        back_rect = pygame.Rect(300, total_height, 200, 40)

                        if authors_rect.collidepoint(mouse_pos):
                            self.show_authors = True
                        elif back_rect.collidepoint(mouse_pos):
                            self.running = False
                    else:
                        if volver_info_rect.collidepoint(mouse_pos):
                            self.show_authors = False

                elif event.type == pygame.MOUSEWHEEL:
                    if not self.show_authors:
                        self.scroll_offset_info -= event.y * self.scroll_speed
                        if self.scroll_offset_info < 0:
                            self.scroll_offset_info = 0
                    else:
                        self.scroll_offset_authors -= event.y * self.scroll_speed
                        if self.scroll_offset_authors < 0:
                            self.scroll_offset_authors = 0

                elif event.type == pygame.KEYDOWN:
                    if not self.show_authors:
                        if event.key == pygame.K_DOWN:
                            self.scroll_offset_info += self.scroll_speed
                        elif event.key == pygame.K_UP:
                            self.scroll_offset_info -= self.scroll_speed
                        if self.scroll_offset_info < 0:
                            self.scroll_offset_info = 0
                    else:
                        if event.key == pygame.K_DOWN:
                            self.scroll_offset_authors += self.scroll_speed
                        elif event.key == pygame.K_UP:
                            self.scroll_offset_authors -= self.scroll_speed
                        if self.scroll_offset_authors < 0:
                            self.scroll_offset_authors = 0

            self.clock.tick(60)
