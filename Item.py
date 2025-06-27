import pygame
import os

class Item:
    def __init__(self, x, y, size, item_type):
        self.x = x
        self.y = y
        self.size = size
        self.item_type = item_type
        self.collected = False

        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

        # Carga la imagen según el tipo de ítem
        image_file = None
        if self.item_type == "key":
            image_file = os.path.join("assets", "SPRITES", "Key", "Key.png")
        elif self.item_type == "accelerator":
            image_file = os.path.join("assets", "SPRITES", "Items", "Accelerator.png")
        elif self.item_type == "extra_bombs":
            image_file = os.path.join("assets", "SPRITES", "Items", "Extra Bombs.png")
        elif self.item_type == "explosion_expander":
            image_file = os.path.join("assets", "SPRITES", "Items", "Explosion Expander.png")
        elif self.item_type == "heart":
            image_file = os.path.join("assets", "SPRITES", "Power Ups", "Heart.png")
        elif self.item_type == "damage_increase":
            image_file = os.path.join("assets", "SPRITES", "Power Ups", "Damage Increase.png")

        if image_file:
            self.image = pygame.image.load(image_file).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.size, self.size))
        else:
            self.image = None

    def draw(self, screen):
        if not self.collected and self.image:
            screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return self.rect

    def collect(self):
        self.collected = True

    def is_collected(self):
        return self.collected

    def update(self, player):
        if not self.collected and self.rect.colliderect(player.get_rect()):
            self.collect()
            self.apply_effect(player)
            return True
        return False

    def apply_effect(self, player):
        player.collect_item(self.item_type)
