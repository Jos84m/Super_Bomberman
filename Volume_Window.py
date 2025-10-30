import pygame
from pygame.locals import *

class VolumeConfigWindow:
    def __init__(self, screen, settings, sounds):
        self.screen = screen
        self.settings = settings
        self.click_sound, self.hover_sound = sounds
        self.running = True
        self.font = pygame.font.SysFont("Arial", 28)
        self.clock = pygame.time.Clock()

    def draw_slider(self, value, y, label):
        x = 300
        width = 200
        height = 10
        pygame.draw.rect(self.screen, (180, 180, 180), (x, y, width, height))
        pygame.draw.rect(self.screen, (50, 200, 50), (x, y, width * value, height))
        text = self.font.render(f"{label}: {int(value * 100)}%", True, (255, 255, 255))
        self.screen.blit(text, (x, y - 30))
        return pygame.Rect(x, y, width, height)

    def draw_toggle_button(self, state, y):
        text = "Música: Activada" if state else "Música: Desactivada"
        color = (0, 200, 0) if state else (200, 0, 0)
        rect_width = 240
        rect_height = 40
        rect = pygame.Rect(300, y, rect_width, rect_height)
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        label = self.font.render(text, True, (255, 255, 255))
        label_pos = (rect.x + 15, rect.y + (rect.height - label.get_height()) // 2)
        self.screen.blit(label, label_pos)
        return rect

    def run(self):
        while self.running:
            self.screen.fill((30, 30, 30))
            music_rect = self.draw_slider(self.settings.music_volume, 150, "Volumen Música")
            fx_rect = self.draw_slider(self.settings.effects_volume, 250, "Volumen Efectos")
            toggle_rect = self.draw_toggle_button(self.settings.music_enabled, 350)
            back_rect = pygame.Rect(300, 450, 200, 40)
            pygame.draw.rect(self.screen, (100, 100, 255), back_rect)
            self.screen.blit(self.font.render("← Volver", True, (255, 255, 255)), (back_rect.x + 50, back_rect.y + 5))

            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == MOUSEBUTTONDOWN:
                    self.click_sound.play()
                    if music_rect.collidepoint(event.pos):
                        rel_x = event.pos[0] - music_rect.x
                        self.settings.set_music_volume(rel_x / music_rect.width)
                        pygame.mixer.music.set_volume(self.settings.music_volume)
                    elif fx_rect.collidepoint(event.pos):
                        rel_x = event.pos[0] - fx_rect.x
                        self.settings.set_effects_volume(rel_x / fx_rect.width)
                        self.click_sound.set_volume(self.settings.effects_volume)
                        self.hover_sound.set_volume(self.settings.effects_volume)
                    elif toggle_rect.collidepoint(event.pos):
                        self.settings.toggle_music()
                        if self.settings.music_enabled:
                            pygame.mixer.music.set_volume(self.settings.music_volume)
                            pygame.mixer.music.unpause()
                        else:
                            pygame.mixer.music.pause()
                    elif back_rect.collidepoint(event.pos):
                        self.running = False

            self.clock.tick(60)
