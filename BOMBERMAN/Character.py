import pygame
import random
import time
import math


class Character:
    def __init__(self, name, health, bomb_damage, max_bombs, special_ability, color, image_path=None):
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
        
        # Configuración de imagen
        self.image = None
        self.image_path = image_path
        self.rect = None
        self.load_image()
    
    def load_image(self):
        """Carga la imagen del personaje"""
        if self.image_path:
            try:
                # Cargar la imagen
                self.image = pygame.image.load(self.image_path)
                # Crear rectángulo para posicionamiento
                self.rect = self.image.get_rect()
                print(f"Imagen cargada exitosamente para {self.name}")
            except pygame.error as e:
                print(f"No se pudo cargar la imagen {self.image_path}: {e}")
                self.create_default_image()
        else:
            self.create_default_image()
    
    def create_default_image(self):
        """Crea una imagen por defecto si no se puede cargar la imagen personalizada"""
        # Crear una superficie de 32x32 píxeles
        self.image = pygame.Surface((32, 32))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        print(f"Usando imagen por defecto para {self.name}")
    
    def scale_image(self, width, height):
        """Redimensiona la imagen del personaje"""
        if self.image:
            self.image = pygame.transform.scale(self.image, (width, height))
            self.rect = self.image.get_rect()
    
    def update_position(self, grid_x, grid_y, cell_size):
        """Actualiza la posición del personaje en la pantalla"""
        self.x = grid_x
        self.y = grid_y
        if self.rect:
            self.rect.x = grid_x * cell_size
            self.rect.y = grid_y * cell_size
    
    def draw(self, screen, cell_size):
        """Dibuja el personaje en la pantalla"""
        if self.image and self.rect:
            # Actualizar posición del rectángulo
            self.rect.x = self.x * cell_size
            self.rect.y = self.y * cell_size
            
            # Dibujar la imagen
            screen.blit(self.image, self.rect)
            
            # Dibujar barra de vida si no está a máxima salud
            if self.health < self.max_health:
                self.draw_health_bar(screen, cell_size)
    
    def draw_health_bar(self, screen, cell_size):
        """Dibuja una barra de vida encima del personaje"""
        bar_width = cell_size - 4
        bar_height = 6
        bar_x = self.rect.x + 2
        bar_y = self.rect.y - 10
        
        # Fondo de la barra (rojo)
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        # Barra de vida actual (verde)
        health_percentage = self.health / self.max_health
        current_width = int(bar_width * health_percentage)
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, current_width, bar_height))
        
        # Borde de la barra
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)
    
    def rotate_image(self, angle):
        """Rota la imagen del personaje"""
        if self.image:
            original_center = self.rect.center
            self.image = pygame.transform.rotate(self.image, angle)
            self.rect = self.image.get_rect(center=original_center)
    
    def flip_image(self, flip_x=False, flip_y=False):
        """Voltea la imagen del personaje"""
        if self.image:
            self.image = pygame.transform.flip(self.image, flip_x, flip_y)
    
    def set_alpha(self, alpha):
        """Establece la transparencia del personaje (0-255)"""
        if self.image:
            self.image.set_alpha(alpha)
    
    def is_invulnerable(self):
        """Verifica si el personaje está en período de invulnerabilidad"""
        current_time = pygame.time.get_ticks()
        return current_time < self.invulnerable_time
    
    def take_damage(self, damage):
        """El personaje recibe daño"""
        if not self.is_invulnerable():
            self.health -= damage
            # Período de invulnerabilidad de 1 segundo
            self.invulnerable_time = pygame.time.get_ticks() + 1000
            
            if self.health <= 0:
                self.health = 0
                return True  # Personaje murió
        return False  # Personaje sigue vivo
















# Ejemplo de uso:
# character = Character("Jugador", 100, 50, 3, "Super Bomba", (0, 255, 0), "imagenes/jugador.png")
# 
# En tu loop principal del juego:
# character.draw(screen, 32)  # 32 es el tamaño de cada celda del grid

# to do ------------------------------------------------------------------------
# ✓ El dibujo del personaje con imagen
# Sonido de pasos = (dependiendo el material que pise)
# Animaciones de movimiento
# Sprites para diferentes direcciones