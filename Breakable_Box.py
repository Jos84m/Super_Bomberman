import pygame
import os

class BreakableBox:
    def __init__(self, x, y, size, content):
        self.x = x
        self.y = y
        self.size = size
        self.content = content
        self.destroyed = False
        self.content_spawned = False  # Para que solo suelte ítem una vez

        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

        # Carga la imagen de caja rompible
        self.image = pygame.image.load(os.path.join("assets", "Box 2.png")).convert_alpha()

        # Imagen opcional para mostrar cuando está destruida
        self.destroyed_image = None

    def draw(self, screen):
        if not self.destroyed:
            screen.blit(self.image, (self.x, self.y))
        else:
            if self.destroyed_image:
                screen.blit(self.destroyed_image, (self.x, self.y))

    def get_rect(self):
        return self.rect

    def destroy(self):
        self.destroyed = True
        self.content_spawned = False
        # Aquí puedes agregar efectos de destrucción, sonido, animación, etc.

    def is_key(self):
        return self.content == "key"

    def get_content(self):
        return self.content
    
    def collides_with_rect(self, rect):
        return self.get_rect().colliderect(rect)
