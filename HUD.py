import pygame
import os
import math

class HUD:
    def __init__(self, screen, start_time, lives=3, score=0, level=1):
        self.screen = screen
        self.start_time = start_time
        self.lives = lives
        self.score = score
        self.level = level
        self.timer_active = True
        self.has_key = False
        self.bombs_left = 0
        self.special_ability_cooldown = 0
        
        # Dimensiones escalables basadas en resolución
        self.screen_width, self.screen_height = screen.get_size()
        self.scale_factor = min(self.screen_width / 1920, self.screen_height / 1080)  # Factor de escala
        
        # HUD adaptativo - porcentaje de la pantalla
        self.hud_height_percent = 0.18  # 18% de la altura de pantalla
        self.hud_height = int(self.screen_height * self.hud_height_percent)
        
        # Tamaños escalados
        self.heart_size = int(100 * self.scale_factor)
        self.item_size = int(40 * self.scale_factor)
        self.padding = int(20 * self.scale_factor)

        # Fuentes escaladas - se crean una sola vez aquí
        self.font_bomb = pygame.font.SysFont("Arial", int(36 * self.scale_factor), bold=True)
        self.font_level = pygame.font.SysFont("Arial", int(60 * self.scale_factor), bold=True)
        self.font_time = pygame.font.SysFont("Arial", int(40 * self.scale_factor), bold=True)
        self.font_key = pygame.font.SysFont("Arial", int(32 * self.scale_factor), bold=True)
        self.font_score = pygame.font.SysFont("Arial", int(50 * self.scale_factor), bold=True)
        self.font_item_number = pygame.font.SysFont("Arial", int(30 * self.scale_factor), bold=True)
        self.font_item_text = pygame.font.SysFont("Arial", int(20 * self.scale_factor), bold=True)
        
        # Cargar imagen de corazón con escala
        try:
            self.heart_img = pygame.image.load(os.path.join("assets", "SPRITES", "Heart.png")).convert_alpha()
            self.heart_img = pygame.transform.scale(self.heart_img, (self.heart_size, self.heart_size))
        except:
            # Si no encuentra la imagen, crear un corazón básico
            self.heart_img = self.create_heart_surface()

        # Cargar imagen de bomba con escala
        try:
            bomb_path = os.path.join("Assets", "Sprites", "Bomb", "Bomb 1.png")
            self.bomb_img = pygame.image.load(bomb_path).convert_alpha()
            bomb_size = int(48 * self.scale_factor)
            self.bomb_img = pygame.transform.scale(self.bomb_img, (bomb_size, bomb_size))
        except pygame.error:
            bomb_size = int(48 * self.scale_factor)
            self.bomb_img = pygame.Surface((bomb_size, bomb_size))
            self.bomb_img.fill((200, 0, 0))
        self.bomb_size = bomb_size
        
        self.permanent_powerups = {"heart", "damage_increase"}
        self.elapsed_time = 0
        self.animation_timer = 0
        
        # Optimización: superficie pre-renderizada para el fondo
        self.hud_bg_surface = None
        self.create_hud_background()

    def create_heart_surface(self):
        """Crea un corazón básico si no se encuentra la imagen"""
        surface = pygame.Surface((self.heart_size, self.heart_size), pygame.SRCALPHA)
        pygame.draw.circle(surface, (255, 0, 0), (self.heart_size//3, self.heart_size//3), self.heart_size//4)
        pygame.draw.circle(surface, (255, 0, 0), (2*self.heart_size//3, self.heart_size//3), self.heart_size//4)
        points = [(self.heart_size//2, 2*self.heart_size//3), 
                 (self.heart_size//6, self.heart_size//2),
                 (5*self.heart_size//6, self.heart_size//2)]
        pygame.draw.polygon(surface, (255, 0, 0), points)
        return surface

    def create_hud_background(self):
        """Pre-renderiza el fondo del HUD para optimizar rendimiento"""
        self.hud_bg_surface = pygame.Surface((self.screen_width, self.hud_height), pygame.SRCALPHA)
        panel_color = (30, 30, 30, 230)
        border_color = (255, 215, 0)
        
        # Fondo con gradiente sutil
        for y in range(self.hud_height):
            alpha = int(230 * (y / self.hud_height))
            color = (30 + alpha//10, 30 + alpha//10, 30 + alpha//10, 230)
            pygame.draw.line(self.hud_bg_surface, color[:3], (0, y), (self.screen_width, y))
        
        # Borde dorado
        pygame.draw.rect(self.hud_bg_surface, border_color, 
                        (0, 0, self.screen_width, self.hud_height), 4)

    def update(self, elapsed_time):
        if self.timer_active:
            self.elapsed_time = int(elapsed_time)
        self.animation_timer += 1
        
        # Recrear fondo si cambió el tamaño de pantalla
        current_size = self.screen.get_size()
        if current_size != (self.screen_width, self.screen_height):
            self.screen_width, self.screen_height = current_size
            self.scale_factor = min(self.screen_width / 1920, self.screen_height / 1080)
            self.hud_height = int(self.screen_height * self.hud_height_percent)
            self.create_hud_background()

        if self.special_ability_cooldown > 0:
            self.special_ability_cooldown = max(0, self.special_ability_cooldown - 1 / 60)  # se asume 60 FPS

    def draw_optimized_particles(self):
        """Partículas optimizadas - menos cálculos por frame"""
        if self.animation_timer % 3 == 0:  # Solo actualizar cada 3 frames
            particle_surface = pygame.Surface((self.screen_width, 100), pygame.SRCALPHA)
            for i in range(0, 8, 2):  # Menos partículas
                particle_x = (self.animation_timer * 2 + i * 60) % self.screen_width
                particle_y = 50 + 25 * math.sin(self.animation_timer * 0.05 + i)
                particle_alpha = int(80 + 40 * math.sin(self.animation_timer * 0.1 + i))
                particle_color = (100, 150, 255, particle_alpha)
                
                pygame.draw.circle(particle_surface, particle_color, 
                                 (int(particle_x), int(particle_y)), 3)
            
            self.screen.blit(particle_surface, (0, 0))

    def draw(self, collected_items=None):
        width, height = self.screen.get_size()
        
        # Dibujar fondo pre-renderizado
        hud_y = height - self.hud_height
        self.screen.blit(self.hud_bg_surface, (0, hud_y))

        # VIDAS (izquierda, optimizado)
        heart_spacing = self.heart_size + int(12 * self.scale_factor)
        for i in range(self.lives):
            # Animación más suave y menos costosa
            if self.animation_timer % 20 < 10:  # Animación cada 20 frames
                scale_offset = 0.05 * math.sin(self.animation_timer * 0.1 + i)
                heart_size = int(self.heart_size * (1.0 + scale_offset))
                scaled_heart = pygame.transform.scale(self.heart_img, (heart_size, heart_size))
            else:
                scaled_heart = self.heart_img
            
            heart_x = self.padding * 2 + i * heart_spacing
            heart_y = hud_y + self.padding
            self.screen.blit(scaled_heart, (heart_x, heart_y))

        # BOMBAS (debajo de corazones)
        bomb_x = self.padding * 2
        bomb_y = hud_y + self.padding + self.heart_size + int(10 * self.scale_factor)
        self.screen.blit(self.bomb_img, (bomb_x, bomb_y))

        bomb_text = self.font_bomb.render(f"x {self.bombs_left}", True, (255, 255, 255))
        self.screen.blit(bomb_text, (bomb_x + self.bomb_img.get_width() + int(10 * self.scale_factor), bomb_y + self.bomb_img.get_height() // 4))

        # NIVEL (centro arriba)
        level_text = self.font_level.render(f"NIVEL {self.level}", True, (255, 255, 100))
        level_rect = level_text.get_rect(center=(width // 2, hud_y + self.hud_height // 4))
        self.screen.blit(level_text, level_rect)

        # TIEMPO (centro abajo)
        time_text = self.font_time.render(f"TIEMPO: {self.elapsed_time}s", True, (255, 255, 255))
        time_rect = time_text.get_rect(center=(width // 2, hud_y + 3 * self.hud_height // 4))
        self.screen.blit(time_text, time_rect)

        # MOSTRAR LLAVE OBTENIDA
        if self.has_key:
            key_text = self.font_key.render("Llave obtenida", True, (255, 255, 0))
            key_rect = key_text.get_rect(center=(width // 2, hud_y + self.hud_height // 2))
            self.screen.blit(key_text, key_rect)

        # PUNTUACIÓN (derecha, arriba)
        score_color = (255, 215, 0)
        score_text = self.font_score.render(f"PUNTOS: {self.score:,}", True, score_color)
        self.screen.blit(score_text, (width - score_text.get_width() - self.padding * 2, 
                                     hud_y + self.padding))

        # ITEMS (derecha, abajo, optimizado)
        if collected_items:
            self.draw_items_optimized(collected_items, width, hud_y)

        font = pygame.font.SysFont("Arial", 20)
        screen_height = self.screen.get_height()

        # Posición para el texto del cooldown justo debajo de las vidas
        cooldown_x = 15  # igual que el primer corazón (ajústalo si quieres)
        cooldown_y = self.screen.get_height() - 34 + 32 + 5  # 32 es la altura del corazón, +5 de margen

        if self.special_ability_cooldown <= 0:
             ability_text = "E. Habilidad Especial (Lista)"
        else:
             ability_text = f"E. Habilidad Especial ({int(self.special_ability_cooldown)}s)"
             
        ability_surface = font.render(ability_text, True, (173, 216, 230))  # celeste claro
        self.screen.blit(ability_surface, (cooldown_x, cooldown_y))

        # Partículas optimizadas
        self.draw_optimized_particles()

    def draw_items_optimized(self, collected_items, width, hud_y):
        """Dibuja items de manera optimizada"""
        tecla_items = [item for item in collected_items if item[0] not in self.permanent_powerups]
        max_items = min(6, (width - 300) // (self.item_size + 20))  # Adaptativo al ancho
        
        if not tecla_items:
            return
            
        item_spacing = self.item_size + int(180 * self.scale_factor)
        base_y = hud_y + self.hud_height // 2 + self.padding
        base_x = width - (item_spacing * min(len(tecla_items), max_items)) - self.padding * 2
        
        colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), 
                 (255, 255, 100), (255, 100, 255), (100, 255, 255)]
        
        for idx, (item_name, count) in enumerate(tecla_items[:max_items]):
            color = colors[idx % len(colors)]
            circle_x = base_x + idx * item_spacing + self.item_size // 2
            circle_y = base_y + self.item_size // 2
            
            #Número del item
            number_text = self.font_item_number.render(str(idx + 1), True, (255, 255, 255))
            number_rect = number_text.get_rect(center=(circle_x, circle_y))
            self.screen.blit(number_text, number_rect)

            # Texto del item
            nombre = item_name.replace('_', ' ').title()
            estado = f"x{count}" if count > 0 else "Usado"
            item_text = self.font_item_text.render(f"{nombre} {estado}", True, (255, 255, 255))
            text_rect = item_text.get_rect(center=(circle_x, base_y + self.item_size + 15))
            self.screen.blit(item_text, text_rect)
        
        # Indicador de más items
        if len(tecla_items) > max_items:
            puntos = self.font_item_text.render("...", True, (255, 255, 255))
            self.screen.blit(puntos, (base_x + max_items * item_spacing, base_y + self.item_size // 2))

    def set_bombs(self, bombs_left):
        self.bombs_left = bombs_left

    def set_special_ability_cooldown(self, cooldown):
        self.special_ability_cooldown = cooldown

