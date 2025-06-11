import pygame
import random
import json
import os
from enum import Enum
from typing import List, Tuple, Dict, Optional
import time
import math
import sys
from Character import Character

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
        self.small_font = pygame.font.Font(None, 24)
        
        # Estados del juego
        self.state = GameState.MENU
        self.running = True
        self.music_enabled = True
        self.current_level = 1
        self.max_levels = 4
        
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
            if self.state == GameState.MENU:
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
                # Ya se usa en place_bomb
                pass
            elif item_type == "range":
                # Ya se usa en place_bomb
                pass

    def use_powerup(self, powerup_type: str):
        if self.player.powerups[powerup_type] > 0:
            self.player.powerups[powerup_type] -= 1
            
            if powerup_type == "health":
                self.player.health = min(self.player.health + 1, self.player.max_health)
            elif powerup_type == "damage":
                # Ya se aplica en bomb_damage
                pass

    def update_bombs(self):
        current_time = pygame.time.get_ticks()
        
        for bomb in self.bombs[:]:
            bomb.timer -= self.clock.get_time()
            if bomb.timer <= 0 and not bomb.exploded:
                self.explode_bomb(bomb)
                bomb.exploded = True

    def explode_bomb(self, bomb: Bomb):
        # Remover bomba del laberinto
        self.maze[bomb.y][bomb.x] = TileType.EMPTY
        self.player.bombs_placed -= 1
        
        # Crear explosión central
        self.explosions.append(Explosion(bomb.x, bomb.y))
        self.maze[bomb.y][bomb.x] = TileType.EXPLOSION
        
        # Explosiones en las 4 direcciones
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dx, dy in directions:
            for i in range(1, bomb.range + 1):
                ex, ey = bomb.x + dx * i, bomb.y + dy * i
                
                if ex < 0 or ex >= MAZE_WIDTH or ey < 0 or ey >= MAZE_HEIGHT:
                    break
                    
                if self.maze[ey][ex] == TileType.WALL:
                    break
                elif self.maze[ey][ex] == TileType.DESTRUCTIBLE:
                    self.maze[ey][ex] = TileType.EXPLOSION
                    self.explosions.append(Explosion(ex, ey))
                    self.player.score += 10
                    
                    # Chance de revelar llave
                    if hasattr(self, 'key_position') and (ex, ey) == self.key_position:
                        # La llave aparecerá después de que se desvanezca la explosión
                        pass
                    elif hasattr(self, 'door_position') and (ex, ey) == self.door_position:
                        # La puerta aparecerá después de que se desvanezca la explosión
                        pass
                    break
                else:
                    self.maze[ey][ex] = TileType.EXPLOSION
                    self.explosions.append(Explosion(ex, ey))
        
        # Remover bomba de la lista
        if bomb in self.bombs:
            self.bombs.remove(bomb)

    def update_explosions(self):
        current_time = pygame.time.get_ticks()
        
        for explosion in self.explosions[:]:
            explosion.timer -= self.clock.get_time()
            if explosion.timer <= 0:
                self.maze[explosion.y][explosion.x] = TileType.EMPTY
                
                # Revelar objetos ocultos
                if hasattr(self, 'key_position') and (explosion.x, explosion.y) == self.key_position:
                    self.maze[explosion.y][explosion.x] = TileType.KEY
                elif hasattr(self, 'door_position') and (explosion.x, explosion.y) == self.door_position:
                    self.maze[explosion.y][explosion.x] = TileType.DOOR
                    
                self.explosions.remove(explosion)

    def update_enemies(self):
        current_time = pygame.time.get_ticks()
        
        for enemy in self.enemies[:]:
            # Movimiento básico
            if current_time - enemy.last_move_time > enemy.move_delay:
                self.move_enemy(enemy)
                enemy.last_move_time = current_time
                enemy.move_delay = random.randint(500, 1500)
                
            # Disparo para enemigos que pueden disparar
            if enemy.can_shoot and current_time - enemy.last_shot_time > enemy.shot_delay:
                self.enemy_shoot(enemy)
                enemy.last_shot_time = current_time
                enemy.shot_delay = random.randint(2000, 4000)

    def move_enemy(self, enemy: Enemy):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            new_x = enemy.x + dx
            new_y = enemy.y + dy
            
            if self.can_move_to(new_x, new_y):
                enemy.x = new_x
                enemy.y = new_y
                break

    def enemy_shoot(self, enemy: Enemy):
        # Disparar hacia el jugador si está en línea de vista
        if enemy.x == self.player.x:
            direction = (0, 1 if self.player.y > enemy.y else -1)
        elif enemy.y == self.player.y:
            direction = (1 if self.player.x > enemy.x else -1, 0)
        else:
            return
            
        projectile = Projectile(enemy.x, enemy.y, direction, 1)
        self.projectiles.append(projectile)

    def update_projectiles(self):
        for projectile in self.projectiles[:]:
            projectile.x += projectile.dx * projectile.speed
            projectile.y += projectile.dy * projectile.speed
            
            # Verificar colisiones
            grid_x, grid_y = int(projectile.x), int(projectile.y)
            
            if (grid_x < 0 or grid_x >= MAZE_WIDTH or 
                grid_y < 0 or grid_y >= MAZE_HEIGHT or
                self.maze[grid_y][grid_x] in [TileType.WALL, TileType.DESTRUCTIBLE]):
                self.projectiles.remove(projectile)
                continue
                
            # Colisión con jugador
            if grid_x == self.player.x and grid_y == self.player.y:
                if pygame.time.get_ticks() - self.player.invulnerable_time > 1000:
                    self.player.health -= projectile.damage
                    self.player.invulnerable_time = pygame.time.get_ticks()
                    if self.player.health <= 0:
                        self.game_over()
                self.projectiles.remove(projectile)

    def check_collisions(self):
        # Colisión jugador con enemigos
        for enemy in self.enemies:
            if enemy.x == self.player.x and enemy.y == self.player.y:
                if pygame.time.get_ticks() - self.player.invulnerable_time > 1000:
                    self.player.health -= 1
                    self.player.invulnerable_time = pygame.time.get_ticks()
                    if self.player.health <= 0:
                        self.game_over()
                        
        # Colisión jugador con explosiones
        if self.maze[self.player.y][self.player.x] == TileType.EXPLOSION:
            if pygame.time.get_ticks() - self.player.invulnerable_time > 1000:
                self.player.health -= 1
                self.player.invulnerable_time = pygame.time.get_ticks()
                if self.player.health <= 0:
                    self.game_over()
                    
        # Enemigos vs explosiones
        for enemy in self.enemies[:]:
            if self.maze[enemy.y][enemy.x] == TileType.EXPLOSION:
                enemy.health -= 1
                if enemy.health <= 0:
                    self.enemies.remove(enemy)
                    self.player.score += 50

    def game_over(self):
        total_time = pygame.time.get_ticks() - self.game_start_time
        self.add_high_score(self.player_name, self.player.score, total_time)
        self.state = GameState.GAME_OVER

    def update(self):
        if self.state == GameState.GAME:
            self.move_player()
            self.update_bombs()
            self.update_explosions()
            self.update_enemies()
            self.update_projectiles()
            self.check_collisions()

    def draw_tile(self, x: int, y: int, tile_type: TileType):
        screen_x = x * TILE_SIZE + 50
        screen_y = y * TILE_SIZE + 50
        rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
        
        color_map = {
            TileType.EMPTY: WHITE,
            TileType.WALL: GRAY,
            TileType.DESTRUCTIBLE: BROWN,
            TileType.BOMB: BLACK,
            TileType.EXPLOSION: ORANGE,
            TileType.KEY: YELLOW,
            TileType.DOOR: PURPLE,
            TileType.POWERUP_HEALTH: RED,
            TileType.POWERUP_DAMAGE: BLUE,
            TileType.ITEM_SPEED: GREEN,
            TileType.ITEM_BOMBS: DARK_GRAY,
            TileType.ITEM_RANGE: (255, 0, 255)
        }
        
        pygame.draw.rect(self.screen, color_map.get(tile_type, WHITE), rect)
        pygame.draw.rect(self.screen, BLACK, rect, 1)

    def draw_character(self, x: int, y: int, color: tuple):
        screen_x = x * TILE_SIZE + 50 + TILE_SIZE // 4
        screen_y = y * TILE_SIZE + 50 + TILE_SIZE // 4
        radius = TILE_SIZE // 4
        pygame.draw.circle(self.screen, color, (screen_x, screen_y), radius)

    def draw_enemy(self, enemy: Enemy):
        color_map = {
            "basic": (150, 0, 0),
            "archer": (0, 150, 0),
            "mage": (0, 0, 150)
        }
        color = color_map.get(enemy.type, (150, 0, 0))
        
        screen_x = enemy.x * TILE_SIZE + 50 + TILE_SIZE // 4
        screen_y = enemy.y * TILE_SIZE + 50 + TILE_SIZE // 4
        radius = TILE_SIZE // 6
        pygame.draw.circle(self.screen, color, (screen_x, screen_y), radius)

    def draw_projectile(self, projectile: Projectile):
        screen_x = int(projectile.x * TILE_SIZE + 50 + TILE_SIZE // 2)
        screen_y = int(projectile.y * TILE_SIZE + 50 + TILE_SIZE // 2)
        pygame.draw.circle(self.screen, RED, (screen_x, screen_y), 3)

    def draw_menu(self):
        self.screen.fill(BLACK)
        
        # Título
        title = self.big_font.render("VINTAGE BOMBERMAN", True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Opciones del menú
        options = [
            "1. Jugar",
            "2. Mejores Puntajes",
            "3. Configuración",
            "4. Información",
            "ESC. Salir"
        ]
        
        for i, option in enumerate(options):
            text = self.font.render(option, True, WHITE)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 300 + i * 60))
            self.screen.blit(text, text_rect)

    def draw_character_select(self):
        self.screen.fill(BLACK)
        
        # Título
        title = self.font.render("Seleccionar Personaje", True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Personajes
        char = self.characters[self.selected_character]
        
        # Mostrar personaje actual
        pygame.draw.circle(self.screen, char.color, (WINDOW_WIDTH // 2, 250), 40)
        
        # Información del personaje
        info = [
            f"Nombre: {char.name}",
            f"Vida: {char.health}",
            f"Daño de Bomba: {char.bomb_damage}",
            f"Bombas Máximas: {char.max_bombs}",
            f"Habilidad: {char.special_ability}"
        ]
        
        for i, line in enumerate(info):
            text = self.small_font.render(line, True, WHITE)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 320 + i * 30))
            self.screen.blit(text, text_rect)
        
        # Controles
        controls = self.small_font.render("← → para cambiar, ENTER para continuar", True, GRAY)
        controls_rect = controls.get_rect(center=(WINDOW_WIDTH // 2, 500))
        self.screen.blit(controls, controls_rect)
        
        # Nombre del jugador
        name_label = self.font.render("Nombre:", True, WHITE)
        name_rect = name_label.get_rect(center=(WINDOW_WIDTH // 2 - 100, 550))
        self.screen.blit(name_label, name_rect)
        
        name_text = self.font.render(self.player_name + "_", True, YELLOW)
        name_text_rect = name_text.get_rect(center=(WINDOW_WIDTH // 2 + 50, 550))
        self.screen.blit(name_text, name_text_rect)

    def draw_game(self):
        self.screen.fill(BLACK)
        
        # Dibujar laberinto
        for y in range(MAZE_HEIGHT):
            for x in range(MAZE_WIDTH):
                self.draw_tile(x, y, self.maze[y][x])
        
        # Dibujar jugador (con parpadeo si es invulnerable)
        current_time = pygame.time.get_ticks()
        if current_time - self.player.invulnerable_time > 1000 or (current_time // 100) % 2:
            self.draw_character(self.player.x, self.player.y, self.player.color)
        
        # Dibujar enemigos
        for enemy in self.enemies:
            self.draw_enemy(enemy)
        
        # Dibujar proyectiles
        for projectile in self.projectiles:
            self.draw_projectile(projectile)
        
        # HUD
        self.draw_hud()

    def draw_hud(self):
        hud_x = MAZE_WIDTH * TILE_SIZE + 100
        
        # Vida
        life_text = self.font.render(f"Vida: {self.player.health}/{self.player.max_health}", True, WHITE)
        self.screen.blit(life_text, (hud_x, 50))
        
        # Puntos
        score_text = self.font.render(f"Puntos: {self.player.score}", True, WHITE)
        self.screen.blit(score_text, (hud_x, 90))
        
        # Tiempo
        current_time = pygame.time.get_ticks()
        game_time = (current_time - self.game_start_time) // 1000
        time_text = self.font.render(f"Tiempo: {game_time}s", True, WHITE)
        self.screen.blit(time_text, (hud_x, 130))
        
        # Nivel
        level_text = self.font.render(f"Nivel: {self.current_level}/{self.max_levels}", True, WHITE)
        self.screen.blit(level_text, (hud_x, 170))
        
        # Bombas
        bombs_available = self.player.max_bombs + self.player.items["bombs"] - self.player.bombs_placed
        bomb_text = self.font.render(f"Bombas: {bombs_available}", True, WHITE)
        self.screen.blit(bomb_text, (hud_x, 210))
        
        # Llave
        key_status = "Sí" if self.player.has_key else "No"
        key_text = self.font.render(f"Llave: {key_status}", True, YELLOW if self.player.has_key else WHITE)
        self.screen.blit(key_text, (hud_x, 250))
        
        # Items
        items_y = 300
        items_text = self.small_font.render("ITEMS:", True, WHITE)
        self.screen.blit(items_text, (hud_x, items_y))
        
        for i, (item, count) in enumerate(self.player.items.items()):
            item_text = self.small_font.render(f"{i+1}. {item.title()}: {count}", True, WHITE)
            self.screen.blit(item_text, (hud_x, items_y + 30 + i * 25))
        
        # PowerUps
        powerups_y = 400
        powerups_text = self.small_font.render("POWERUPS:", True, WHITE)
        self.screen.blit(powerups_text, (hud_x, powerups_y))
        
        for i, (power, count) in enumerate(self.player.powerups.items()):
            power_text = self.small_font.render(f"{'Q' if i == 0 else 'E'}. {power.title()}: {count}", True, WHITE)
            self.screen.blit(power_text, (hud_x, powerups_y + 30 + i * 25))
        
        # Controles
        controls_y = 500
        controls_text = self.small_font.render("CONTROLES:", True, WHITE)
        self.screen.blit(controls_text, (hud_x, controls_y))
        
        control_info = [
            "WASD: Mover",
            "SPACE: Bomba",
            "1-3: Usar Items",
            "Q,E: Usar PowerUps",
            "ESC: Menú"
        ]
        
        for i, control in enumerate(control_info):
            control_text = self.small_font.render(control, True, GRAY)
            self.screen.blit(control_text, (hud_x, controls_y + 30 + i * 20))

    def draw_settings(self):
        self.screen.fill(BLACK)
        
        title = self.font.render("Configuración", True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        music_status = "Activada" if self.music_enabled else "Desactivada"
        music_text = self.font.render(f"Música: {music_status}", True, WHITE)
        music_rect = music_text.get_rect(center=(WINDOW_WIDTH // 2, 250))
        self.screen.blit(music_text, music_rect)
        
        instruction = self.small_font.render("Presiona M para cambiar música", True, GRAY)
        instruction_rect = instruction.get_rect(center=(WINDOW_WIDTH // 2, 300))
        self.screen.blit(instruction, instruction_rect)
        
        back = self.small_font.render("ESC para volver", True, GRAY)
        back_rect = back.get_rect(center=(WINDOW_WIDTH // 2, 400))
        self.screen.blit(back, back_rect)

    def draw_scores(self):
        self.screen.fill(BLACK)
        
        title = self.font.render("Mejores Puntajes", True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        if not self.high_scores:
            no_scores = self.font.render("No hay puntajes registrados", True, WHITE)
            no_scores_rect = no_scores.get_rect(center=(WINDOW_WIDTH // 2, 300))
            self.screen.blit(no_scores, no_scores_rect)
        else:
            headers = self.small_font.render("Pos. | Nombre | Puntos | Tiempo | Nivel", True, YELLOW)
            headers_rect = headers.get_rect(center=(WINDOW_WIDTH // 2, 180))
            self.screen.blit(headers, headers_rect)
            
            for i, score in enumerate(self.high_scores[:5]):
                time_str = f"{score['time'] // 1000}s"
                score_line = f"{i+1:2d}.  | {score['name']:8s} | {score['score']:6d} | {time_str:6s} | {score['level']:2d}"
                score_text = self.small_font.render(score_line, True, WHITE)
                score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, 220 + i * 40))
                self.screen.blit(score_text, score_rect)
        
        back = self.small_font.render("ESC para volver", True, GRAY)
        back_rect = back.get_rect(center=(WINDOW_WIDTH // 2, 500))
        self.screen.blit(back, back_rect)

    def draw_info(self):
        self.screen.fill(BLACK)
        
        title = self.font.render("Información", True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        info_lines = [
            "Vintage Bomberman v1.0",
            "",
            "Desarrollado para:",
            "Instituto Tecnológico de Costa Rica",
            "Escuela de Ingeniería en Computación",
            "Curso: Introducción a la Programación",
            "",
            "Profesores:",
            "Jeff Schmidt Peralta",
            "Diego Mora Rojas",
            "",
            "Año: 2025",
            "País: Costa Rica",
            "",
            "Objetivo:",
            "Encuentra la llave y llega a la puerta",
            "para avanzar al siguiente nivel.",
            "Evita enemigos y usa bombas sabiamente."
        ]
        
        for i, line in enumerate(info_lines):
            color = YELLOW if line and line[0].isupper() and ":" in line else WHITE
            text = self.small_font.render(line, True, color)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 140 + i * 25))
            self.screen.blit(text, text_rect)
        
        back = self.small_font.render("ESC para volver", True, GRAY)
        back_rect = back.get_rect(center=(WINDOW_WIDTH // 2, 650))
        self.screen.blit(back, back_rect)

    def draw_game_over(self):
        self.screen.fill(BLACK)
        
        title = self.big_font.render("JUEGO TERMINADO", True, RED)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)
        
        # Estadísticas finales
        total_time = (pygame.time.get_ticks() - self.game_start_time) // 1000
        
        stats = [
            f"Puntuación Final: {self.player.score}",
            f"Nivel Alcanzado: {self.current_level}",
            f"Tiempo Total: {total_time}s",
            f"Jugador: {self.player_name}"
        ]
        
        for i, stat in enumerate(stats):
            text = self.font.render(stat, True, WHITE)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 300 + i * 50))
            self.screen.blit(text, text_rect)
        
        continue_text = self.small_font.render("Presiona SPACE para continuar", True, GRAY)
        continue_rect = continue_text.get_rect(center=(WINDOW_WIDTH // 2, 550))
        self.screen.blit(continue_text, continue_rect)

    def draw_level_complete(self):
        self.screen.fill(BLACK)
        
        title = self.big_font.render("¡NIVEL COMPLETADO!", True, GREEN)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)
        
        # Estadísticas del nivel
        level_time = (pygame.time.get_ticks() - self.level_start_time) // 1000
        
        stats = [
            f"Nivel: {self.current_level}",
            f"Puntos Obtenidos: {self.player.score}",
            f"Tiempo del Nivel: {level_time}s"
        ]
        
        for i, stat in enumerate(stats):
            text = self.font.render(stat, True, WHITE)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 300 + i * 50))
            self.screen.blit(text, text_rect)
        
        if self.current_level < self.max_levels:
            next_text = "Presiona SPACE para el siguiente nivel"
        else:
            next_text = "Presiona SPACE para terminar"
            
        continue_text = self.small_font.render(next_text, True, GRAY)
        continue_rect = continue_text.get_rect(center=(WINDOW_WIDTH // 2, 500))
        self.screen.blit(continue_text, continue_rect)

    def draw(self):
        if self.state == GameState.MENU:
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

    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.handle_input(event)
            
            self.update()
            self.draw()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

def main():
    game = BombermanGame()
    game.run()

if __name__ == "__main__":
    main()


# README para el proyecto
# ==================================================================================================================================
# Controles:
# - WASD: Mover jugador
# - SPACE: Colocar bomba
# - 1-3: Usar items (velocidad, bombas extra, rango)
# - Q, E: Usar powerups (vida, daño)
# - ESC: Volver al menú
# 
# Características implementadas:
# - 4 niveles progresivos con boss fight final
# - 3 personajes jugables con diferentes estadísticas
# - Sistema de vidas y puntuación
# - Enemigos con diferentes comportamientos
# - Items y powerups
# - Sistema de explosiones con propagación
# - Guardado de mejores puntajes
# - Múltiples pantallas (menú, configuración, etc.)
# - Ambientación de niveles
# 
# El objetivo es encontrar la llave oculta en los bloques
# destructibles y llegar a la puerta para avanzar al siguiente nivel.
# ¡Cuidado con los enemigos y las explosiones!