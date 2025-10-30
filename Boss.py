import pygame
import os
import random
import math
from Enemy import Enemy
from Flying_Enemy import FlyingEnemy
from Item import Item

class Boss:
    def __init__(self, x, y, sprite_folder, tile_size, level):
        self.x = x
        self.y = y
        self.tile_size = tile_size
        self.sprite_folder = sprite_folder
        self.level = level

        self.max_health = 10
        self.health = self.max_health
        self.speed = 0.7
        self.phase = 1
        self.alive = True

        self.load_sprites()
        self.current_frame = 0
        self.frame_delay = 8
        self.frame_counter = 0

        scale_factor = 1.2
        self.width = int(self.tile_size * scale_factor)
        self.height = int(self.tile_size * scale_factor)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.state = "moving"
        self.attack_frames = [self.frames[1], self.frames[2], self.frames[3]]
        self.attack_frame_index = 0
        self.attack_frame_delay = 6
        self.attack_frame_counter = 0

        self.hit_duration = 120
        self.hit_timer = 0

        self.ground_enemies = []
        self.flying_enemies = []

        self.invocation_cooldown = 500
        self.invocation_timer = 0
        self.damage_cooldown = 60  # frames (~1 segundo)
        self.damage_timer = 0

    def load_sprites(self):
        self.frames = []
        scale_factor = 1.2
        new_size = (int(self.tile_size * scale_factor), int(self.tile_size * scale_factor))

        for i in range(1, 5):
            path = os.path.join(self.sprite_folder, f"Boss {i}.png")
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(image, new_size)
            self.frames.append(image)

        hit_path = os.path.join(self.sprite_folder, "Boss Hit.png")
        self.hit_frame = pygame.image.load(hit_path).convert_alpha()
        self.hit_frame = pygame.transform.scale(self.hit_frame, new_size)

    def move_towards_player(self, player):
        if self.state != "moving":
            return
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.hypot(dx, dy)
        if distance > 0:
            dx, dy = dx / distance, dy / distance
            current_speed = self.speed if self.phase == 1 else 1.2
            self.x += dx * current_speed
            self.y += dy * current_speed
            self.rect.topleft = (self.x, self.y)

    def update(self, player):
        if not self.alive:
            return

        if self.health <= 3 and self.phase == 1:
            self.phase = 2

        if self.state == "hit":
            self.hit_timer -= 1
            if self.hit_timer <= 0:
                self.state = "moving"
            return

        if self.state == "attacking":
            self.attack_frame_counter += 1
            if self.attack_frame_counter >= self.attack_frame_delay:
                self.attack_frame_counter = 0
                self.attack_frame_index += 1
                if self.attack_frame_index >= len(self.attack_frames):
                    self.attack_frame_index = 0
                    self.state = "moving"
            return

        self.move_towards_player(player)

        # Reducir cooldown de daño
        if self.damage_timer > 0:
            self.damage_timer -= 1

        # Verificar colisión con jugador y aplicar daño solo si no está en cooldown
        if self.state != "hit" and self.rect.colliderect(player.get_rect()):
            if self.damage_timer == 0 and player.can_take_damage:
                self.state = "attacking"
                self.attack_frame_index = 0
                self.attack_frame_counter = 0
                player.lose_life()
                self.damage_timer = self.damage_cooldown
            

        self.invocation_timer += 1
        if self.invocation_timer >= self.invocation_cooldown or not self.ground_enemies or not self.flying_enemies:
            self.invocation_timer = 0
            self.spawn_enemies()

        # Actualizar listas eliminando enemigos muertos
        self.ground_enemies = [e for e in self.ground_enemies if e.alive]
        self.flying_enemies = [f for f in self.flying_enemies if f.alive]

        # Actualizar enemigos invocados para que se muevan y disparen
        for f_enemy in self.flying_enemies:
            if f_enemy.alive:
                f_enemy.update(self.level.level_map, player, self.tile_size, self.level.start_x, self.level.start_y)
        for g_enemy in self.ground_enemies:
            if g_enemy.alive:
                g_enemy.move(self.level.level_map, self.level.start_x, self.level.start_y)

    def spawn_enemies(self):
        base_x = self.x
        base_y = self.y

        while len(self.ground_enemies) < 2:
            offset_x = random.choice([-1, 1]) * self.tile_size * random.randint(1, 2)
            offset_y = random.choice([-1, 1]) * self.tile_size * random.randint(1, 2)
            spawn_x = base_x + offset_x
            spawn_y = base_y + offset_y
            enemy = Enemy(spawn_x, spawn_y, os.path.join("assets", "SPRITES", "Enemies", "Basic enemies"), self.tile_size)
            enemy.speed = 1.2
            enemy.active = True
            self.ground_enemies.append(enemy)
            self.level.enemies.append(enemy)

        if len(self.flying_enemies) < 1:
            offset_x = random.choice([-1, 1]) * self.tile_size * random.randint(1, 2)
            offset_y = random.choice([-1, 1]) * self.tile_size * random.randint(1, 2)
            spawn_x = base_x + offset_x
            spawn_y = base_y + offset_y
            flying_enemy = FlyingEnemy(spawn_x, spawn_y, os.path.join("assets", "SPRITES", "Enemies", "FlyingEnemy"), self.tile_size)
            flying_enemy.speed = 1.2
            flying_enemy.active = True
            self.flying_enemies.append(flying_enemy)
            self.level.flying_enemies.append(flying_enemy)

    def take_damage(self, amount=1):
        if self.state == "hit":
            return
        self.health -= amount
        if self.health <= 0:
            self.alive = False
            key_item = Item(self.x, self.y, self.tile_size, "key")
            self.level.items.append(key_item)
        else:
            self.state = "hit"
            self.hit_timer = self.hit_duration

    def draw(self, screen):
        offset_x = (self.width - self.tile_size) // 2
        offset_y = (self.height - self.tile_size) // 2

        draw_x = self.x - offset_x
        draw_y = self.y - offset_y
        
        if self.state == "hit":
            screen.blit(self.hit_frame, (draw_x, draw_y))
        elif self.state == "attacking":
            screen.blit(self.attack_frames[self.attack_frame_index], (draw_x, draw_y))
        else:
            screen.blit(self.frames[0], (draw_x, draw_y))
            
        bar_width = self.width
        bar_height = 6
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, (255, 0, 0), (draw_x, draw_y - 10, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (draw_x, draw_y - 10, bar_width * health_ratio, bar_height))
