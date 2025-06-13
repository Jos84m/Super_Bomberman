import pygame
import random
import time
import sys




class Bomb:
    def __init__(self, x: int, y: int, damage: int, range_size: int = 2):
        self.x = x
        self.y = y
        self.damage = damage
        self.range = range_size
        self.timer = 3000  # 3 segundos
        self.exploded = False


# to do 
# Agregar el efecto de explosion 
# Agregar el sonido de explosion 
# 