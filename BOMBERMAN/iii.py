import pygame
import random
import json
import os
from enum import Enum
from typing import List, Tuple, Dict, Optional
import math


# Inicializar Pygame
pygame.init()

# Dimensiones de la ventana
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
# Tamaño de los tiles
TILE_SIZE = 32
# Dimensiones del laberinto
MAZE_WIDTH = (WINDOW_WIDTH - 100) // TILE_SIZE
MAZE_HEIGHT = (WINDOW_HEIGHT - 100) // TILE_SIZE
# Velocidades
PLAYER_SPEED = 5
ENEMY_SPEED = 3
BOMB_TIMER = 3000  # 3 segundos
# Puntajes
POINTS_ENEMY = 100
POINTS_ITEM = 50
POINTS_LEVEL = 1000
FPS = 60  # Frames por segundo


# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

class GameState(Enum):
    INTRO = 0
    MENU = 1
    CHARACTER_SELECT = 2
    GAME = 3
    SETTINGS = 4
    SCORES = 5
    INFO = 6
    GAME_OVER = 7
    LEVEL_COMPLETE = 8

class TileType(Enum):
    EMPTY = 0
    WALL = 1
    DESTRUCTIBLE = 2
    BOMB = 3
    EXPLOSION = 4
    KEY = 5
    DOOR = 6
    POWERUP_HEALTH = 7
    POWERUP_DAMAGE = 8
    ITEM_SPEED = 9
    ITEM_BOMBS = 10
    ITEM_RANGE = 11

class Particle:
    def __init__(self, x: float, y: float, color: tuple, velocity: Tuple[float, float], lifetime: int):
        self.x = x
        self.y = y
        self.color = color
        self.vel_x, self.vel_y = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.lifetime -= 1
        
    def draw(self, screen):
        alpha = self.lifetime / self.max_lifetime
        size = int(3 * alpha) + 1
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

class Character:
    def __init__(self, name: str, health: int, bomb_damage: int, max_bombs: int, special_ability: str, color: tuple):
        self.name = name
        self.health = health
        self.max_health = health
        self.bomb_damage = bomb_damage
        self.max_bombs = max_bombs
        self.special_ability = special_ability
        self.color = color
        self.x = 1
        self.y = 1
        self.speed = 2
        self.bombs_placed = 0
        self.has_key = False
        self.score = 0
        self.items = {"speed": 0, "bombs": 0, "range": 0}
        self.powerups = {"health": 0, "damage": 0}
        self.last_move_time = 0
        self.invulnerable_time = 0

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

class Bomb:
    def __init__(self, x: int, y: int, damage: int, range_size: int = 2):
        self.x = x
        self.y = y
        self.damage = damage
        self.range = range_size
        self.timer = 3000  # 3 segundos
        self.exploded = False

class Explosion:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.timer = 500  # 0.5 segundos

class Projectile:
    def __init__(self, x: int, y: int, direction: Tuple[int, int], damage: int):
        self.x = float(x)
        self.y = float(y)
        self.dx, self.dy = direction
        self.damage = damage
        self.speed = 3

class BombermanGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Vintage Bomberman")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.huge_font = pygame.font.Font(None, 96)
        self.small_font = pygame.font.Font(None, 24)
        
        # Estados del juego
        self.state = GameState.INTRO
        self.running = True
        self.music_enabled = True
        self.current_level = 1
        self.max_levels = 4
        
        # Variables de animación de intro
        self.intro_start_time = pygame.time.get_ticks()
        self.intro_duration = 5000  # 5 segundos
        self.particles = []
        self.logo_scale = 0.0
        self.logo_rotation = 0.0
        self.text_alpha = 0
        self.background_stars = []
        
        # Inicializar estrellas de fondo
        for _ in range(100):
            star = {
                'x': random.randint(0, WINDOW_WIDTH),
                'y': random.randint(0, WINDOW_HEIGHT),
                'speed': random.uniform(0.5, 2.0),
                'brightness': random.randint(100, 255)
            }
            self.background_stars.append(star)
        
        # Personajes disponibles
        self.characters = [
            Character("Bomber", 3, 1, 1, "Extra Bomb", RED),
            Character("Speedy", 2, 1, 1, "Speed Boost", BLUE),
            Character("Tank", 4, 2, 1, "Shield", GREEN)
        ]
        self.selected_character = 0
        self.player_name = ""
        
        # Datos del juego
        self.player = None
        self.maze = []
        self.enemies = []
        self.bombs = []
        self.explosions = []
        self.projectiles = []
        self.game_start_time = 0
        self.level_start_time = 0
        
        # Puntajes
        self.high_scores = self.load_high_scores()
        
        # Controles
        self.controls = {
            'up': pygame.K_w,
            'down': pygame.K_s, 
            'left': pygame.K_a,
            'right': pygame.K_d,
            'bomb': pygame.K_SPACE,
            'item1': pygame.K_1,
            'item2': pygame.K_2,
            'item3': pygame.K_3,
            'power1': pygame.K_q,
            'power2': pygame.K_e
        }

    def update_intro_animation(self):
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.intro_start_time
        progress = min(elapsed / self.intro_duration, 1.0)
        
        # Actualizar animaciones basadas en el progreso
        if progress < 0.3:
            # Fase 1: Aparecer estrellas y logo
            self.logo_scale = min(progress * 3.33, 1.0)
            self.logo_rotation += 2
        elif progress < 0.7:
            # Fase 2: Estabilizar logo y aparecer texto
            self.logo_scale = 1.0
            self.logo_rotation += 1
            self.text_alpha = min((progress - 0.3) * 2.5 * 255, 255)
        else:
            # Fase 3: Efectos finales
            self.text_alpha = 255
            self.logo_rotation += 0.5
        
        # Actualizar partículas
        self.update_particles()
        
        # Generar nuevas partículas
        if random.random() < 0.3:
            self.spawn_particle()
        
        # Actualizar estrellas de fondo
        for star in self.background_stars:
            star['y'] += star['speed']
            if star['y'] > WINDOW_HEIGHT:
                star['y'] = 0
                star['x'] = random.randint(0, WINDOW_WIDTH)
        
        # Finalizar intro
        if elapsed >= self.intro_duration:
            self.state = GameState.MENU

    def spawn_particle(self):
        # Generar partículas desde diferentes puntos
        if random.random() < 0.5:
            # Partículas desde los bordes
            if random.random() < 0.5:
                x = random.choice([0, WINDOW_WIDTH])
                y = random.randint(0, WINDOW_HEIGHT)
                vel_x = random.uniform(-2, 2) if x == 0 else random.uniform(-2, 2)
                vel_y = random.uniform(-2, 2)
            else:
                x = random.randint(0, WINDOW_WIDTH)
                y = random.choice([0, WINDOW_HEIGHT])
                vel_x = random.uniform(-2, 2)
                vel_y = random.uniform(-2, 2) if y == 0 else random.uniform(-2, 2)
        else:
            # Partículas desde el centro (explosión)
            center_x, center_y = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            x = center_x + random.uniform(-50, 50)
            y = center_y + random.uniform(-50, 50)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
        
        color = random.choice([RED, ORANGE, YELLOW, WHITE])
        lifetime = random.randint(60, 180)
        
        particle = Particle(x, y, color, (vel_x, vel_y), lifetime)
        self.particles.append(particle)

    def update_particles(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)

    def draw_intro(self):
        # Fondo negro con gradiente
        self.screen.fill(BLACK)
        
        # Dibujar estrellas de fondo
        for star in self.background_stars:
            brightness = star['brightness']
            color = (brightness, brightness, brightness)
            pygame.draw.circle(self.screen, color, (int(star['x']), int(star['y'])), 1)
        
        # Dibujar partículas
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Logo principal (bomba animada)
        center_x, center_y = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50
        
        if self.logo_scale > 0:
            # Crear superficie para rotación
            logo_size = int(80 * self.logo_scale)
            logo_surface = pygame.Surface((logo_size * 2, logo_size * 2), pygame.SRCALPHA)
            
            # Dibujar bomba
            bomb_center = (logo_size, logo_size)
            pygame.draw.circle(logo_surface, BLACK, bomb_center, logo_size)
            pygame.draw.circle(logo_surface, WHITE, bomb_center, logo_size, 3)
            
            # Mecha
            mecha_end_x = bomb_center[0] + int(logo_size * 0.7 * math.cos(math.radians(self.logo_rotation)))
            mecha_end_y = bomb_center[1] - int(logo_size * 0.7 * math.sin(math.radians(self.logo_rotation)))
            pygame.draw.line(logo_surface, ORANGE, bomb_center, (mecha_end_x, mecha_end_y), 5)
            
            # Chispa en la punta de la mecha
            spark_colors = [RED, ORANGE, YELLOW]
            spark_color = spark_colors[int(self.logo_rotation / 10) % len(spark_colors)]
            pygame.draw.circle(logo_surface, spark_color, (mecha_end_x, mecha_end_y), 8)
            
            # Rotar y dibujar
            rotated_logo = pygame.transform.rotate(logo_surface, self.logo_rotation)
            logo_rect = rotated_logo.get_rect(center=(center_x, center_y))
            self.screen.blit(rotated_logo, logo_rect)
        
        # Título principal
        if self.text_alpha > 0:
            title_color = (*YELLOW[:3], int(self.text_alpha))
            title_text = self.huge_font.render("VINTAGE", True, YELLOW)
            title_rect = title_text.get_rect(center=(center_x, center_y + 100))
            self.screen.blit(title_text, title_rect)
            
            subtitle_text = self.big_font.render("BOMBERMAN", True, ORANGE)
            subtitle_rect = subtitle_text.get_rect(center=(center_x, center_y + 150))
            self.screen.blit(subtitle_text, subtitle_rect)
            
            # Efectos de texto brillante
            for i in range(3):
                glow_color = (255, 255, 0, max(0, int(self.text_alpha - i * 50)))
                glow_title = self.huge_font.render("VINTAGE", True, (255, 255, 100))
                glow_rect = glow_title.get_rect(center=(center_x + i, center_y + 100 + i))
                self.screen.blit(glow_title, glow_rect)
        
        # Texto de carga y skip
        current_time = pygame.time.get_ticks()
        if (current_time // 500) % 2:  # Parpadeo
            loading_text = self.small_font.render("Presiona cualquier tecla para continuar...", True, WHITE)
            loading_rect = loading_text.get_rect(center=(center_x, WINDOW_HEIGHT - 100))
            self.screen.blit(loading_text, loading_rect)
        
        # Información adicional
        info_text = self.small_font.render("Instituto Tecnológico de Costa Rica", True, GRAY)
        info_rect = info_text.get_rect(center=(center_x, WINDOW_HEIGHT - 50))
        self.screen.blit(info_text, info_rect)
        
        year_text = self.small_font.render("2025", True, GRAY)
        year_rect = year_text.get_rect(center=(center_x, WINDOW_HEIGHT - 30))
        self.screen.blit(year_text, year_rect)

    def load_high_scores(self) -> List[Dict]:
        if os.path.exists('high_scores.json'):
            try:
                with open('high_scores.json', 'r') as f:
                    return json.load(f)
            except:
                pass
        return []

    def save_high_scores(self):
        try:
            with open('high_scores.json', 'w') as f:
                json.dump(self.high_scores, f)
        except:
            pass

    def add_high_score(self, name: str, score: int, time_played: int):
        self.high_scores.append({
            'name': name,
            'score': score,
            'time': time_played,
            'level': self.current_level
        })
        self.high_scores.sort(key=lambda x: x['score'], reverse=True)
        self.high_scores = self.high_scores[:5]
        self.save_high_scores()

    def generate_maze(self):
        # Crear laberinto base
        self.maze = [[TileType.EMPTY for _ in range(MAZE_WIDTH)] for _ in range(MAZE_HEIGHT)]
        
        # Paredes exteriores
        for x in range(MAZE_WIDTH):
            self.maze[0][x] = TileType.WALL
            self.maze[MAZE_HEIGHT-1][x] = TileType.WALL
        for y in range(MAZE_HEIGHT):
            self.maze[y][0] = TileType.WALL
            self.maze[y][MAZE_WIDTH-1] = TileType.WALL
            
        # Patrón de paredes internas
        for y in range(2, MAZE_HEIGHT-2, 2):
            for x in range(2, MAZE_WIDTH-2, 2):
                self.maze[y][x] = TileType.WALL
                
        # Bloques destructibles aleatorios
        destructible_count = 30 + self.current_level * 10
        for _ in range(destructible_count):
            x = random.randint(1, MAZE_WIDTH-2)
            y = random.randint(1, MAZE_HEIGHT-2)
            if self.maze[y][x] == TileType.EMPTY and not (x <= 2 and y <= 2):
                self.maze[y][x] = TileType.DESTRUCTIBLE
                
        # Colocar llave en bloque destructible
        destructible_blocks = []
        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                if self.maze[y][x] == TileType.DESTRUCTIBLE:
                    destructible_blocks.append((x, y))
        
        if destructible_blocks:
            key_x, key_y = random.choice(destructible_blocks)
            self.key_position = (key_x, key_y)
            
        # Colocar puerta
        while True:
            door_x = random.randint(1, MAZE_WIDTH-2)
            door_y = random.randint(1, MAZE_HEIGHT-2)
            if self.maze[door_y][door_x] == TileType.DESTRUCTIBLE:
                self.door_position = (door_x, door_y)
                break

    def spawn_enemies(self):
        self.enemies = []
        enemy_count = min(2 + self.current_level, 8)
        
        for _ in range(enemy_count):
            while True:
                x = random.randint(3, MAZE_WIDTH-4)
                y = random.randint(3, MAZE_HEIGHT-4)
                if self.maze[y][x] == TileType.EMPTY and (abs(x - self.player.x) > 3 or abs(y - self.player.y) > 3):
                    if self.current_level <= 2:
                        enemy_type = "basic"
                    elif self.current_level == 3:
                        enemy_type = random.choice(["basic", "archer"])
                    else:
                        enemy_type = random.choice(["basic", "archer", "mage"])
                    
                    health = 1 if enemy_type == "basic" else 2
                    self.enemies.append(Enemy(x, y, enemy_type, health))
                    break

    def spawn_items(self):
        # Spawnar powerups (solo para el nivel actual)
        for _ in range(2):
            while True:
                x = random.randint(1, MAZE_WIDTH-2)
                y = random.randint(1, MAZE_HEIGHT-2)
                if self.maze[y][x] == TileType.EMPTY:
                    powerup_type = random.choice([TileType.POWERUP_HEALTH, TileType.POWERUP_DAMAGE])
                    self.maze[y][x] = powerup_type
                    break
                    
        # Spawnar items (permanentes)
        for _ in range(3):
            while True:
                x = random.randint(1, MAZE_WIDTH-2)
                y = random.randint(1, MAZE_HEIGHT-2)
                if self.maze[y][x] == TileType.EMPTY:
                    item_type = random.choice([TileType.ITEM_SPEED, TileType.ITEM_BOMBS, TileType.ITEM_RANGE])
                    self.maze[y][x] = item_type
                    break

    def start_new_game(self):
        self.player = Character(
            self.characters[self.selected_character].name,
            self.characters[self.selected_character].health,
            self.characters[self.selected_character].bomb_damage,
            self.characters[self.selected_character].max_bombs,
            self.characters[self.selected_character].special_ability,
            self.characters[self.selected_character].color
        )
        self.player.x = 1
        self.player.y = 1
        self.current_level = 1
        self.game_start_time = pygame.time.get_ticks()
        self.start_level()

    def start_level(self):
        self.level_start_time = pygame.time.get_ticks()
        self.generate_maze()
        self.spawn_enemies()
        self.spawn_items()
        self.bombs = []
        self.explosions = []
        self.projectiles = []
        self.player.bombs_placed = 0
        self.player.has_key = False
        # Resetear powerups del nivel anterior
        self.player.powerups = {"health": 0, "damage": 0}

    def handle_input(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            
        if event.type == pygame.KEYDOWN:
            if self.state == GameState.INTRO:
                # Cualquier tecla salta la intro
                self.state = GameState.MENU
            elif self.state == GameState.MENU:
                self.handle_menu_input(event)
            elif self.state == GameState.CHARACTER_SELECT:
                self.handle_character_select_input(event)
            elif self.state == GameState.GAME:
                self.handle_game_input(event)
            elif self.state == GameState.SETTINGS:
                self.handle_settings_input(event)
            elif self.state == GameState.SCORES:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU
            elif self.state == GameState.INFO:
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU
            elif self.state == GameState.GAME_OVER:
                if event.key == pygame.K_SPACE:
                    self.state = GameState.MENU
            elif self.state == GameState.LEVEL_COMPLETE:
                if event.key == pygame.K_SPACE:
                    if self.current_level < self.max_levels:
                        self.current_level += 1
                        self.start_level()
                        self.state = GameState.GAME
                    else:
                        # Juego completado
                        self.add_high_score(self.player_name, self.player.score, 
                                          pygame.time.get_ticks() - self.game_start_time)
                        self.state = GameState.GAME_OVER

    def handle_menu_input(self, event):
        if event.key == pygame.K_1:
            self.state = GameState.CHARACTER_SELECT
        elif event.key == pygame.K_2:
            self.state = GameState.SCORES
        elif event.key == pygame.K_3:
            self.state = GameState.SETTINGS
        elif event.key == pygame.K_4:
            self.state = GameState.INFO
        elif event.key == pygame.K_ESCAPE:
            self.running = False

    def handle_character_select_input(self, event):
        if event.key == pygame.K_LEFT:
            self.selected_character = (self.selected_character - 1) % len(self.characters)
        elif event.key == pygame.K_RIGHT:
            self.selected_character = (self.selected_character + 1) % len(self.characters)
        elif event.key == pygame.K_RETURN:
            if self.player_name:
                self.start_new_game()
                self.state = GameState.GAME
        elif event.key == pygame.K_ESCAPE:
            self.state = GameState.MENU
        elif event.key == pygame.K_BACKSPACE:
            self.player_name = self.player_name[:-1]
        else:
            if len(self.player_name) < 15 and event.unicode.isalnum():
                self.player_name += event.unicode

    def handle_game_input(self, event):
        if event.key == pygame.K_ESCAPE:
            self.state = GameState.MENU
        elif event.key == self.controls['bomb']:
            self.place_bomb()
        elif event.key == self.controls['item1']:
            self.use_item("speed")
        elif event.key == self.controls['item2']:
            self.use_item("bombs") 
        elif event.key == self.controls['item3']:
            self.use_item("range")
        elif event.key == self.controls['power1']:
            self.use_powerup("health")
        elif event.key == self.controls['power2']:
            self.use_powerup("damage")

    def handle_settings_input(self, event):
        if event.key == pygame.K_m:
            self.music_enabled = not self.music_enabled
        elif event.key == pygame.K_ESCAPE:
            self.state = GameState.MENU

    def move_player(self):
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()
        
        # Control de velocidad de movimiento
        if current_time - self.player.last_move_time < 100:
            return
            
        new_x, new_y = self.player.x, self.player.y
        
        if keys[self.controls['up']]:
            new_y -= 1
        elif keys[self.controls['down']]:
            new_y += 1
        elif keys[self.controls['left']]:
            new_x -= 1
        elif keys[self.controls['right']]:
            new_x += 1
        else:
            return
            
        # Verificar colisiones
        if self.can_move_to(new_x, new_y):
            self.player.x = new_x
            self.player.y = new_y
            self.player.last_move_time = current_time
            
            # Verificar pickup de items
            self.check_pickups()

    def can_move_to(self, x: int, y: int) -> bool:
        if x < 0 or x >= MAZE_WIDTH or y < 0 or y >= MAZE_HEIGHT:
            return False
            
        tile = self.maze[y][x]
        if tile in [TileType.WALL, TileType.DESTRUCTIBLE, TileType.BOMB]:
            return False
            
        # Verificar colisión con enemigos
        for enemy in self.enemies:
            if enemy.x == x and enemy.y == y:
                return False
                
        return True

    def check_pickups(self):
        tile = self.maze[self.player.y][self.player.x]
        
        if tile == TileType.KEY:
            self.player.has_key = True
            self.player.score += 100
            self.maze[self.player.y][self.player.x] = TileType.EMPTY
            
        elif tile == TileType.DOOR and self.player.has_key:
            self.player.score += 200
            self.state = GameState.LEVEL_COMPLETE
            
        elif tile == TileType.POWERUP_HEALTH:
            self.player.powerups["health"] += 1
            self.maze[self.player.y][self.player.x] = TileType.EMPTY
            
        elif tile == TileType.POWERUP_DAMAGE:
            self.player.powerups["damage"] += 1
            self.maze[self.player.y][self.player.x] = TileType.EMPTY
            
        elif tile in [TileType.ITEM_SPEED, TileType.ITEM_BOMBS, TileType.ITEM_RANGE]:
            item_name = {
                TileType.ITEM_SPEED: "speed",
                TileType.ITEM_BOMBS: "bombs", 
                TileType.ITEM_RANGE: "range"
            }[tile]
            self.player.items[item_name] += 1
            self.maze[self.player.y][self.player.x] = TileType.EMPTY

    def place_bomb(self):
        if self.player.bombs_placed >= self.player.max_bombs + self.player.items["bombs"]:
            return
            
        if self.maze[self.player.y][self.player.x] != TileType.EMPTY:
            return
            
        bomb_range = 2 + self.player.items["range"]
        bomb_damage = self.player.bomb_damage + self.player.powerups["damage"]
        
        bomb = Bomb(self.player.x, self.player.y, bomb_damage, bomb_range)
        self.bombs.append(bomb)
        self.maze[self.player.y][self.player.x] = TileType.BOMB
        self.player.bombs_placed += 1

    def use_item(self, item_type: str):
        if self.player.items[item_type] > 0:
            self.player.items[item_type] -= 1
            
            if item_type == "speed":
                # Implementar efecto de velocidad temporal
                pass
            elif item_type == "bombs":
                # Efecto ya aplicado en place_bomb()
                pass
            elif item_type == "range":
                # Efecto ya aplicado en place_bomb()
                pass

    def use_powerup(self, powerup_type: str):
        if self.player.powerups[powerup_type] > 0:
            self.player.powerups[powerup_type] -= 1
            
            if powerup_type == "health":
                if self.player.health < self.player.max_health:
                    self.player.health += 1
            elif powerup_type == "damage":
                # Efecto ya aplicado en place_bomb()
                pass

    def update_bombs(self):
        current_time = pygame.time.get_ticks()
        
        for bomb in self.bombs[:]:
            bomb.timer -= self.clock.get_time()
            
            if bomb.timer <= 0 and not bomb.exploded:
                self.explode_bomb(bomb)
                bomb.exploded = True
                self.bombs.remove(bomb)
                # Reducir contador de bombas colocadas
                if self.player.bombs_placed > 0:
                    self.player.bombs_placed -= 1

    def explode_bomb(self, bomb: Bomb):
        # Crear explosión en la posición de la bomba
        self.explosions.append(Explosion(bomb.x, bomb.y))
        self.maze[bomb.y][bomb.x] = TileType.EXPLOSION
        
        # Explosión en las 4 direcciones
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dx, dy in directions:
            for distance in range(1, bomb.range + 1):
                exp_x = bomb.x + dx * distance
                exp_y = bomb.y + dy * distance
                
                # Verificar límites
                if exp_x < 0 or exp_x >= MAZE_WIDTH or exp_y < 0 or exp_y >= MAZE_HEIGHT:
                    break
                    
                tile = self.maze[exp_y][exp_x]
                
                # Pared indestructible detiene la explosión
                if tile == TileType.WALL:
                    break
                    
                # Crear explosión
                self.explosions.append(Explosion(exp_x, exp_y))
                
                # Destruir bloque destructible
                if tile == TileType.DESTRUCTIBLE:
                    self.maze[exp_y][exp_x] = TileType.EXPLOSION
                    
                    # Posibilidad de revelar llave o puerta
                    if (exp_x, exp_y) == self.key_position:
                        # La llave aparecerá cuando la explosión termine
                        pass
                    elif (exp_x, exp_y) == self.door_position:
                        # La puerta aparecerá cuando la explosión termine
                        pass
                    break
                elif tile == TileType.EMPTY:
                    self.maze[exp_y][exp_x] = TileType.EXPLOSION
                else:
                    # Otros tiles detienen la explosión
                    break
        
        # Dañar enemigos en el área de explosión
        for explosion in self.explosions:
            for enemy in self.enemies[:]:
                if enemy.x == explosion.x and enemy.y == explosion.y:
                    enemy.health -= bomb.damage
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.player.score += POINTS_ENEMY
        
        # Dañar jugador si está en el área de explosión
        for explosion in self.explosions:
            if (self.player.x == explosion.x and self.player.y == explosion.y and 
                self.player.invulnerable_time <= 0):
                self.player.health -= 1
                self.player.invulnerable_time = 2000  # 2 segundos de invulnerabilidad
                if self.player.health <= 0:
                    self.state = GameState.GAME_OVER

    def update_explosions(self):
        current_time = pygame.time.get_ticks()
        
        for explosion in self.explosions[:]:
            explosion.timer -= self.clock.get_time()
            
            if explosion.timer <= 0:
                self.explosions.remove(explosion)
                
                # Limpiar tile de explosión
                if self.maze[explosion.y][explosion.x] == TileType.EXPLOSION:
                    # Verificar si debe aparecer llave o puerta
                    if (explosion.x, explosion.y) == self.key_position:
                        self.maze[explosion.y][explosion.x] = TileType.KEY
                    elif (explosion.x, explosion.y) == self.door_position:
                        self.maze[explosion.y][explosion.x] = TileType.DOOR
                    else:
                        self.maze[explosion.y][explosion.x] = TileType.EMPTY

    def update_enemies(self):
        current_time = pygame.time.get_ticks()
        
        for enemy in self.enemies[:]:
            # Movimiento
            if current_time - enemy.last_move_time > enemy.move_delay:
                self.move_enemy(enemy)
                enemy.last_move_time = current_time
                enemy.move_delay = random.randint(500, 1500)
            
            # Disparar proyectiles (para arqueros y magos)
            if (enemy.can_shoot and current_time - enemy.last_shot_time > enemy.shot_delay):
                self.enemy_shoot(enemy)
                enemy.last_shot_time = current_time
                enemy.shot_delay = random.randint(2000, 4000)
            
            # Verificar colisión con jugador
            if (enemy.x == self.player.x and enemy.y == self.player.y and 
                self.player.invulnerable_time <= 0):
                self.player.health -= 1
                self.player.invulnerable_time = 2000
                if self.player.health <= 0:
                    self.state = GameState.GAME_OVER

    def move_enemy(self, enemy: Enemy):
        # IA simple: moverse hacia el jugador o aleatoriamente
        possible_moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dx, dy in directions:
            new_x = enemy.x + dx
            new_y = enemy.y + dy
            
            if self.can_enemy_move_to(new_x, new_y):
                # Calcular distancia al jugador
                dist_to_player = abs(new_x - self.player.x) + abs(new_y - self.player.y)
                possible_moves.append((new_x, new_y, dist_to_player))
        
        if possible_moves:
            # 70% probabilidad de moverse hacia el jugador, 30% aleatorio
            if random.random() < 0.7:
                # Moverse hacia el jugador
                possible_moves.sort(key=lambda x: x[2])
                enemy.x, enemy.y = possible_moves[0][:2]
            else:
                # Movimiento aleatorio
                move = random.choice(possible_moves)
                enemy.x, enemy.y = move[:2]

    def can_enemy_move_to(self, x: int, y: int) -> bool:
        if x < 0 or x >= MAZE_WIDTH or y < 0 or y >= MAZE_HEIGHT:
            return False
            
        tile = self.maze[y][x]
        if tile in [TileType.WALL, TileType.DESTRUCTIBLE, TileType.BOMB]:
            return False
            
        # Verificar colisión con otros enemigos
        for enemy in self.enemies:
            if enemy.x == x and enemy.y == y:
                return False
                
        return True

    def enemy_shoot(self, enemy: Enemy):
        # Calcular dirección hacia el jugador
        dx = self.player.x - enemy.x
        dy = self.player.y - enemy.y
        
        # Normalizar dirección
        if abs(dx) > abs(dy):
            direction = (1 if dx > 0 else -1, 0)
        else:
            direction = (0, 1 if dy > 0 else -1)
        
        # Crear proyectil
        damage = 1 if enemy.type == "archer" else 2
        projectile = Projectile(enemy.x, enemy.y, direction, damage)
        self.projectiles.append(projectile)

    def update_projectiles(self):
        for projectile in self.projectiles[:]:
            # Mover proyectil
            projectile.x += projectile.dx * projectile.speed
            projectile.y += projectile.dy * projectile.speed
            
            # Convertir a coordenadas de tile
            tile_x = int(projectile.x)
            tile_y = int(projectile.y)
            
            # Verificar límites y colisiones
            if (tile_x < 0 or tile_x >= MAZE_WIDTH or tile_y < 0 or tile_y >= MAZE_HEIGHT or
                self.maze[tile_y][tile_x] in [TileType.WALL, TileType.DESTRUCTIBLE]):
                self.projectiles.remove(projectile)
                continue
            
            # Verificar colisión con jugador
            if (tile_x == self.player.x and tile_y == self.player.y and 
                self.player.invulnerable_time <= 0):
                self.player.health -= projectile.damage
                self.player.invulnerable_time = 2000
                self.projectiles.remove(projectile)
                if self.player.health <= 0:
                    self.state = GameState.GAME_OVER

    def update_game(self):
        if self.player.invulnerable_time > 0:
            self.player.invulnerable_time -= self.clock.get_time()
            
        self.move_player()
        self.update_bombs()
        self.update_explosions()
        self.update_enemies()
        self.update_projectiles()
        
        # Verificar condición de victoria (todos los enemigos eliminados)
        if not self.enemies:
            # Hacer aparecer la puerta si no está visible
            door_x, door_y = self.door_position
            if self.maze[door_y][door_x] == TileType.DESTRUCTIBLE:
                self.maze[door_y][door_x] = TileType.DOOR

    def draw_game(self):
        self.screen.fill(BLACK)
        
        # Dibujar laberinto
        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                rect = pygame.Rect(x * TILE_SIZE + 50, y * TILE_SIZE + 50, TILE_SIZE, TILE_SIZE)
                tile = self.maze[y][x]
                
                if tile == TileType.WALL:
                    pygame.draw.rect(self.screen, GRAY, rect)
                elif tile == TileType.DESTRUCTIBLE:
                    pygame.draw.rect(self.screen, BROWN, rect)
                elif tile == TileType.BOMB:
                    pygame.draw.rect(self.screen, BLACK, rect)
                    pygame.draw.circle(self.screen, WHITE, rect.center, TILE_SIZE//3)
                elif tile == TileType.EXPLOSION:
                    pygame.draw.rect(self.screen, YELLOW, rect)
                elif tile == TileType.KEY:
                    pygame.draw.rect(self.screen, YELLOW, rect)
                    pygame.draw.circle(self.screen, WHITE, rect.center, TILE_SIZE//4)
                elif tile == TileType.DOOR:
                    pygame.draw.rect(self.screen, GREEN, rect)
                elif tile == TileType.POWERUP_HEALTH:
                    pygame.draw.rect(self.screen, RED, rect)
                    pygame.draw.circle(self.screen, WHITE, rect.center, TILE_SIZE//3)
                elif tile == TileType.POWERUP_DAMAGE:
                    pygame.draw.rect(self.screen, ORANGE, rect)
                    pygame.draw.circle(self.screen, WHITE, rect.center, TILE_SIZE//3)
                elif tile in [TileType.ITEM_SPEED, TileType.ITEM_BOMBS, TileType.ITEM_RANGE]:
                    color = {TileType.ITEM_SPEED: BLUE, TileType.ITEM_BOMBS: PURPLE, TileType.ITEM_RANGE: GREEN}[tile]
                    pygame.draw.rect(self.screen, color, rect)
        
        # Dibujar jugador (con efecto de parpadeo si es invulnerable)
        if self.player.invulnerable_time <= 0 or (pygame.time.get_ticks() // 100) % 2:
            player_rect = pygame.Rect(self.player.x * TILE_SIZE + 50, self.player.y * TILE_SIZE + 50, 
                                    TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(self.screen, self.player.color, player_rect)
        
        # Dibujar enemigos
        for enemy in self.enemies:
            enemy_rect = pygame.Rect(enemy.x * TILE_SIZE + 50, enemy.y * TILE_SIZE + 50, 
                                   TILE_SIZE, TILE_SIZE)
            if enemy.type == "basic":
                pygame.draw.rect(self.screen, RED, enemy_rect)
            elif enemy.type == "archer":
                pygame.draw.rect(self.screen, PURPLE, enemy_rect)
            elif enemy.type == "mage":
                pygame.draw.rect(self.screen, BLUE, enemy_rect)
        
        # Dibujar proyectiles
        for projectile in self.projectiles:
            proj_x = int(projectile.x * TILE_SIZE + 50 + TILE_SIZE//2)
            proj_y = int(projectile.y * TILE_SIZE + 50 + TILE_SIZE//2)
            pygame.draw.circle(self.screen, YELLOW, (proj_x, proj_y), 3)
        
        # Dibujar UI
        self.draw_ui()

    def draw_ui(self):
        # Panel de información
        ui_y = 10
        
        # Salud
        health_text = self.font.render(f"Salud: {self.player.health}/{self.player.max_health}", True, WHITE)
        self.screen.blit(health_text, (10, ui_y))
        ui_y += 30
        
        # Puntaje
        score_text = self.font.render(f"Puntaje: {self.player.score}", True, WHITE)
        self.screen.blit(score_text, (10, ui_y))
        ui_y += 30
        
        # Nivel
        level_text = self.font.render(f"Nivel: {self.current_level}", True, WHITE)
        self.screen.blit(level_text, (10, ui_y))
        ui_y += 30
        
        # Items
        items_text = self.font.render(f"Items - Velocidad: {self.player.items['speed']} " +
                                    f"Bombas: {self.player.items['bombs']} " +
                                    f"Rango: {self.player.items['range']}", True, WHITE)
        self.screen.blit(items_text, (10, ui_y))
        ui_y += 30
        
        # Powerups
        powerups_text = self.font.render(f"Powerups - Salud: {self.player.powerups['health']} " +
                                       f"Daño: {self.player.powerups['damage']}", True, WHITE)
        self.screen.blit(powerups_text, (10, ui_y))
        
        # Estado de llave
        if self.player.has_key:
            key_text = self.font.render("LLAVE OBTENIDA", True, YELLOW)
            self.screen.blit(key_text, (WINDOW_WIDTH - 200, 10))
        
        # Controles
        controls_y = WINDOW_HEIGHT - 100
        control_texts = [
            "WASD: Mover | ESPACIO: Bomba | ESC: Menú",
            "123: Usar Items | QE: Usar Powerups"
        ]
        for i, text in enumerate(control_texts):
            control_text = self.small_font.render(text, True, GRAY)
            self.screen.blit(control_text, (10, controls_y + i * 20))

    def draw_menu(self):
        self.screen.fill(BLACK)
        
        # Título
        title_text = self.big_font.render("VINTAGE BOMBERMAN", True, YELLOW)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Opciones del menú
        menu_options = [
            "1. Nueva Partida",
            "2. Puntajes Altos", 
            "3. Configuración",
            "4. Información",
            "ESC. Salir"
        ]
        
        for i, option in enumerate(menu_options):
            color = WHITE
            option_text = self.font.render(option, True, color)
            option_rect = option_text.get_rect(center=(WINDOW_WIDTH//2, 200 + i * 50))
            self.screen.blit(option_text, option_rect)

    def draw_character_select(self):
        self.screen.fill(BLACK)
        
        # Título
        title_text = self.big_font.render("SELECCIONAR PERSONAJE", True, YELLOW)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 50))
        self.screen.blit(title_text, title_rect)
        
        # Personajes
        char_y = 150
        char = self.characters[self.selected_character]
        
        # Mostrar personaje seleccionado
        char_rect = pygame.Rect(WINDOW_WIDTH//2 - 50, char_y, 100, 100)
        pygame.draw.rect(self.screen, char.color, char_rect)
        
        # Información del personaje
        info_y = char_y + 120
        info_texts = [
            f"Nombre: {char.name}",
            f"Salud: {char.health}",
            f"Daño de Bomba: {char.bomb_damage}",
            f"Bombas Máximas: {char.max_bombs}",
            f"Habilidad: {char.special_ability}"
        ]
        
        for i, text in enumerate(info_texts):
            info_text = self.font.render(text, True, WHITE)
            info_rect = info_text.get_rect(center=(WINDOW_WIDTH//2, info_y + i * 30))
            self.screen.blit(info_text, info_rect)
        
        # Campo de nombre
        name_y = info_y + len(info_texts) * 30 + 30
        name_label = self.font.render("Nombre del Jugador:", True, WHITE)
        name_rect = name_label.get_rect(center=(WINDOW_WIDTH//2, name_y))
        self.screen.blit(name_label, name_rect)
        
        name_input = self.font.render(self.player_name + "_", True, YELLOW)
        name_input_rect = name_input.get_rect(center=(WINDOW_WIDTH//2, name_y + 30))
        self.screen.blit(name_input, name_input_rect)
        
        # Controles
        controls_y = WINDOW_HEIGHT - 80
        control_texts = [
            "← → : Cambiar Personaje | ENTER: Comenzar",
            "ESC: Volver al Menú"
        ]
        for i, text in enumerate(control_texts):
            control_text = self.small_font.render(text, True, GRAY)
            control_rect = control_text.get_rect(center=(WINDOW_WIDTH//2, controls_y + i * 20))
            self.screen.blit(control_text, control_rect)

    def draw_scores(self):
        self.screen.fill(BLACK)
        
        # Título
        title_text = self.big_font.render("PUNTAJES ALTOS", True, YELLOW)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 50))
        self.screen.blit(title_text, title_rect)
        
        if not self.high_scores:
            no_scores_text = self.font.render("No hay puntajes registrados", True, WHITE)
            no_scores_rect = no_scores_text.get_rect(center=(WINDOW_WIDTH//2, 200))
            self.screen.blit(no_scores_text, no_scores_rect)
        else:
            for i, score in enumerate(self.high_scores):
                score_text = f"{i+1}. {score['name']} - {score['score']} pts (Nivel {score['level']})"
                score_surface = self.font.render(score_text, True, WHITE)
                score_rect = score_surface.get_rect(center=(WINDOW_WIDTH//2, 150 + i * 40))
                self.screen.blit(score_surface, score_rect)
        
        # Instrucciones
        back_text = self.small_font.render("ESC: Volver al Menú", True, GRAY)
        back_rect = back_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 50))
        self.screen.blit(back_text, back_rect)

    def draw_settings(self):
        self.screen.fill(BLACK)
        
        # Título
        title_text = self.big_font.render("CONFIGURACIÓN", True, YELLOW)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 50))
        self.screen.blit(title_text, title_rect)
        
        # Opciones
        music_status = "Activada" if self.music_enabled else "Desactivada"
        music_text = self.font.render(f"Música: {music_status} (M para cambiar)", True, WHITE)
        music_rect = music_text.get_rect(center=(WINDOW_WIDTH//2, 200))
        self.screen.blit(music_text, music_rect)
        
        # Controles
        controls_y = 300
        control_texts = [
            "Controles:",
            "WASD: Movimiento",
            "ESPACIO: Colocar Bomba",
            "1,2,3: Usar Items",
            "Q,E: Usar Powerups"
        ]
        
        for i, text in enumerate(control_texts):
            color = YELLOW if i == 0 else WHITE
            control_text = self.font.render(text, True, color)
            control_rect = control_text.get_rect(center=(WINDOW_WIDTH//2, controls_y + i * 30))
            self.screen.blit(control_text, control_rect)
        
        # Volver
        back_text = self.small_font.render("ESC: Volver al Menú", True, GRAY)
        back_rect = back_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 50))
        self.screen.blit(back_text, back_rect)

    def draw_info(self):
        self.screen.fill(BLACK)
        
        # Título
        title_text = self.big_font.render("INFORMACIÓN", True, YELLOW)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 50))
        self.screen.blit(title_text, title_rect)
        
        # Información del juego
        info_texts = [
            "Vintage Bomberman",
            "",
            "Objetivo: Elimina todos los enemigos y encuentra la puerta.",
            "Recoge la llave para abrir la puerta al siguiente nivel.",
            "",
            "Items:",
            "• Velocidad (Azul): Aumenta velocidad temporalmente",
            "• Bombas (Morado): Permite colocar más bombas",
            "• Rango (Verde): Aumenta el rango de explosión",
            "",
            "Powerups:",
            "• Salud (Rojo): Restaura puntos de vida",
            "• Daño (Naranja): Aumenta daño de bombas",
            "",
            "Enemigos:",
            "• Básico (Rojo): Movimiento simple",
            "• Arquero (Morado): Dispara proyectiles",
            "• Mago (Azul): Proyectiles más potentes"
        ]
        
        y_offset = 120
        for text in info_texts:
            if text == "":
                y_offset += 15
                continue
                
            color = YELLOW if text in ["Items:", "Powerups:", "Enemigos:"] else WHITE
            info_text = self.small_font.render(text, True, color)
            info_rect = info_text.get_rect(center=(WINDOW_WIDTH//2, y_offset))
            self.screen.blit(info_text, info_rect)
            y_offset += 25
        
        # Volver
        back_text = self.small_font.render("ESC: Volver al Menú", True, GRAY)
        back_rect = back_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT - 30))
        self.screen.blit(back_text, back_rect)

    def draw_game_over(self):
        self.screen.fill(BLACK)
        
        # Título
        title_text = self.big_font.render("JUEGO TERMINADO", True, RED)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 200))
        self.screen.blit(title_text, title_rect)
        
        # Puntaje final
        if self.player:
            final_score_text = self.font.render(f"Puntaje Final: {self.player.score}", True, WHITE)
            score_rect = final_score_text.get_rect(center=(WINDOW_WIDTH//2, 280))
            self.screen.blit(final_score_text, score_rect)
            
            level_text = self.font.render(f"Nivel Alcanzado: {self.current_level}", True, WHITE)
            level_rect = level_text.get_rect(center=(WINDOW_WIDTH//2, 320))
            self.screen.blit(level_text, level_rect)
        
        # Continuar
        continue_text = self.font.render("ESPACIO: Volver al Menú", True, YELLOW)
        continue_rect = continue_text.get_rect(center=(WINDOW_WIDTH//2, 400))
        self.screen.blit(continue_text, continue_rect)

    def draw_level_complete(self):
        self.screen.fill(BLACK)
        
        # Título
        title_text = self.big_font.render("¡NIVEL COMPLETADO!", True, GREEN)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, 200))
        self.screen.blit(title_text, title_rect)
        
        # Información del nivel
        level_text = self.font.render(f"Nivel {self.current_level} Completado", True, WHITE)
        level_rect = level_text.get_rect(center=(WINDOW_WIDTH//2, 280))
        self.screen.blit(level_text, level_rect)
        
        if self.player:
            score_text = self.font.render(f"Puntaje: {self.player.score}", True, WHITE)
            score_rect = score_text.get_rect(center=(WINDOW_WIDTH//2, 320))
            self.screen.blit(score_text, score_rect)
        
        # Continuar
        if self.current_level < self.max_levels:
            continue_text = self.font.render("ESPACIO: Siguiente Nivel", True, YELLOW)
        else:
            continue_text = self.font.render("ESPACIO: ¡Juego Completado!", True, YELLOW)
        
        continue_rect = continue_text.get_rect(center=(WINDOW_WIDTH//2, 400))
        self.screen.blit(continue_text, continue_rect)

    def draw(self):
        if self.state == GameState.INTRO:
            self.draw_intro()
        elif self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.CHARACTER_SELECT:
            self.draw_character_select()
        elif self.state == GameState.GAME:
            self.draw_game()
        elif self.state == GameState.SETTINGS:
            self.draw_settings()
        elif self.state == GameState.SCORES:
            self.draw_scores()
        elif self.state == GameState.INFO:
            self.draw_info()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        elif self.state == GameState.LEVEL_COMPLETE:
            self.draw_level_complete()
        
        pygame.display.flip()

    def run(self):
        while self.running:
            # Manejar eventos
            for event in pygame.event.get():
                self.handle_input(event)
            
            # Actualizar estado del juego
            if self.state == GameState.INTRO:
                self.update_intro_animation()
            elif self.state == GameState.GAME:
                self.update_game()
            
            # Dibujar
            self.draw()
            
            # Control de FPS
            self.clock.tick(FPS)
        
        pygame.quit()

# Función principal
def main():
    game = BombermanGame()
    game.run()

if __name__ == "__main__":
    main()
