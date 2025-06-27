import pygame
import sys

class VolumeSettings:
    def __init__(self):
        self.music_volume = 0.5
        self.effects_volume = 0.5
        self.music_enabled = True

    def toggle_music(self):
        self.music_enabled = not self.music_enabled

    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))

    def set_effects_volume(self, volume):
        self.effects_volume = max(0.0, min(1.0, volume))

    def get_music_volume(self):
        return self.music_volume if self.music_enabled else 0.0