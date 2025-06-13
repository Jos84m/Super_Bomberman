import random
import time
import pygame
import sys
from pygame import Surface
from typing import Dict, Optional

# Diccionario con las rutas de las imágenes para cada tipo de enemigo
ENEMY_IMAGES = {
    "basic": "assets/enemy_basic.png",
    "archer": "assets/enemy_archer.png",
    "mage": "assets/enemy_mage.png",
    "boss": "assets/enemy_boss.png"
}

#==================================================================================================================================================================================================

# Class de Enemiigo 

class Enemy:
    def __init__(self, x: int, y: int, enemy_type: str, health: int = 1):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.health = health
        self.last_move_time = 0
        self.move_delay = random.randint(500, 1500)
        self.can_shoot = enemy_type in ["archer", "mage"]
        self.last_shot_time = 0
        self.shot_delay = random.randint(2000, 4000)
        
        # Cargar imagen del enemigo
        self.image = self.load_image()
        
# Carga de imagen 
    def load_image(self) -> Optional[Surface]:
        """Carga la imagen del enemigo según su tipo"""
        try:
            # Intentar cargar la imagen correspondiente al tipo de enemigo
            image_path = ENEMY_IMAGES.get(self.type)
            if image_path:
                image = pygame.image.load(image_path)
                return pygame.transform.scale(image, (32, 32))  # Ajustar tamaño
        except Exception as e:
            print(f"Error loading enemy image: {e}")
        
        # Si hay error o no hay imagen, crear un placeholder
        surface = pygame.Surface((32, 32))
        color = {
            "basic": (255, 0, 0),    # Rojo
            "archer": (0, 255, 0),    # Verde
            "mage": (0, 0, 255),      # Azul
            "boss": (255, 0, 255)     # Magenta
        }.get(self.type, (128, 128, 128))  # Gris por defecto
        surface.fill(color)
        return surface
    


    