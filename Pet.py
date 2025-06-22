import pygame

class Pet:
    def __init__(self, x, y, image_path):
        self.x = x
        self.y = y
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (32, 32))

    def follow(self, target_x, target_y, level_map, start_x, start_y, tile_size):
        # Movimiento simple hacia el jugador
        if self.x < target_x: self.x += 2
        elif self.x > target_x: self.x -= 2
        if self.y < target_y: self.y += 2
        elif self.y > target_y: self.y -= 2

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
