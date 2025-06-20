
import pygame

import pygame
import time
import pygame
from PIL import Image, ImageSequence

class Player:
    def __init__(self, x, y, gif_path, speed=2):
        self.x = x
        self.y = y
        self.speed = speed
        self.frames = []
        self.current_frame = 0
        self.frame_delay = 5
        self.frame_counter = 0
        self.load_gif_frames(gif_path)
        self.image = self.frames[0] if self.frames else None
        self.rect = pygame.Rect(self.x, self.y, 48, 48)
        self.pet = None

    def load_gif_frames(self, gif_path):
        gif = Image.open(gif_path)
        for frame in ImageSequence.Iterator(gif):
            frame = frame.convert("RGBA")
            surface = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode).convert_alpha()
            surface = pygame.transform.scale(surface, (48, 48))
            self.frames.append(surface)

    def update_animation(self):
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.image = self.frames[self.current_frame]

    def move(self, dx, dy, level_map, tile_size, start_x, start_y):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        new_rect = pygame.Rect(new_x, new_y, tile_size, tile_size)

        row = (new_y - start_y) // tile_size
        col = (new_x - start_x) // tile_size

        if 0 <= row < len(level_map) and 0 <= col < len(level_map[0]):
            if level_map[row][col] != '#' and level_map[row][col] != '?':
                self.x = new_x
                self.y = new_y
                self.rect.topleft = (self.x, self.y)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, 48, 48)

    def draw(self, screen):
        self.update_animation()
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        if self.pet:
            self.pet.draw(screen)