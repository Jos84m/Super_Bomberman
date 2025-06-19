import pygame

class Pet:
    def __init__(self, x, y, image_path):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.x = x
        self.y = y
        self.speed = 2
        self.rect = self.image.get_rect(topleft=(x, y))

    def follow(self, target_x, target_y):
        if self.x < target_x: self.x += self.speed
        if self.x > target_x: self.x -= self.speed
        if self.y < target_y: self.y += self.speed
        if self.y > target_y: self.y -= self.speed
        self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
