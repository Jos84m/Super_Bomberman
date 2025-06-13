import pygame
import random
import time
import math


class Character:
    def __init__(self, name, health, bomb_damage, max_bombs, special_ability, color):
        self.name = name
        self.health = health
        self.max_health = health
        self.bomb_damage = bomb_damage
        self.max_bombs = max_bombs
        self.special_ability = special_ability
        self.color = color
        self.x = 1
        self.y = 1
        self.score = 0
        self.bombs_placed = 0
        self.has_key = False
        self.invulnerable_time = 0
        self.items = {"speed": 0, "bombs": 0, "range": 0}
        self.powerups = {"health": 0, "damage": 0}
        self.last_move_time = 0

# to do ------------------------------------------------------------------------
# El dibujo del personaje
# Sonido de pasos = (dependiendo el material que pise)
# 
