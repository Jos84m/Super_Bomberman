import pygame
import sys

class AboutWindow:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 22)
        self.title_font = pygame.font.SysFont("Arial", 28, bold=True)
        self.running = True

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
            "Avanza por los niveles hasta encontrar la llave o ir a la puerta",
            "pero, ten cuidado si no es la puerta correcta puedes terminar en un lugar no deseado.",
            "Evita los enemigos y ten cuidado con tus propias bombas.",
        ]

    def run(self):
        while self.running:
            self.screen.fill((30, 30, 30))

            for i, line in enumerate(self.text_lines):
                font = self.title_font if i == 0 else self.font
                text_surface = font.render(line, True, (255, 255, 255))
                self.screen.blit(text_surface, (60, 40 + i * 30))

            # Botón de volver
            back_rect = pygame.Rect(300, 500, 200, 40)
            pygame.draw.rect(self.screen, (100, 100, 255), back_rect)
            back_text = self.font.render("← Volver", True, (255, 255, 255))
            self.screen.blit(back_text, (back_rect.x + 50, back_rect.y + 5))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if back_rect.collidepoint(event.pos):
                        self.running = False

            self.clock.tick(60)
