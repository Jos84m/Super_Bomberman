import pygame
import random
import time
import sys



class Explosion:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.timer = 500  # 0.5 segundos
        