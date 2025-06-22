import pygame
import os

class Player:
    def __init__(self, x, y, sprite_folder, sprite_prefix, speed=2):
        self.x = x
        self.y = y
        self.speed = speed
        self.sprite_folder = sprite_folder
        self.sprite_prefix = sprite_prefix
        self.direction = "Down"
        self.walk_cycle = [1, 2, 3, 2]
        self.walk_index = 1  # Empieza en 2 (índice 1)
        self.last_direction = "Down"
        self.image = self.load_sprite("Walking", self.direction, self.walk_cycle[self.walk_index])
        self.rect = pygame.Rect(self.x, self.y, 48, 48)
        self.pet = None
        self.moving = False

        # Control de velocidad de animación
        self.anim_counter = 0
        self.anim_speed = 6  # Más alto = más lento

        # --- QUITADO: Cargar sonido de paso ---
        # self.walk_sound = pygame.mixer.Sound(os.path.join("assets", "SOUNDS", "Walking.wav"))

    def load_sprite(self, action, direction, frame):
        filename = f"{self.sprite_prefix} {action} {direction} {frame}.png"
        path = os.path.join(self.sprite_folder, filename)
        return pygame.transform.scale(pygame.image.load(path).convert_alpha(), (48, 48))

    def move(self, dx, dy, level_map, tile_size, start_x, start_y, bombs):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed
        new_rect = pygame.Rect(new_x, new_y, tile_size, tile_size)

        # Verificar colisiones con paredes y cajas
        collided = False
        for row_idx, row in enumerate(level_map):
            for col_idx, tile in enumerate(row):
                if tile in ['#', '?']:
                    tile_rect = pygame.Rect(start_x + col_idx * tile_size,
                                            start_y + row_idx * tile_size,
                                            tile_size, tile_size)
                    if new_rect.colliderect(tile_rect):
                        collided = True
                        break
            if collided:
                break

        # Verificar colisiones con bombas
        if not collided:
            for bomb in bombs:
                if bomb.rect.colliderect(new_rect):
                    collided = True
                    break

        # Si no hay colisión, actualizar posición y sprite
        if not collided:
            self.x = new_x
            self.y = new_y
            self.rect.topleft = (self.x, self.y)
            # Cambia dirección según movimiento
            if dx > 0:
                self.direction = "Right"
            elif dx < 0:
                self.direction = "Left"
            elif dy > 0:
                self.direction = "Down"
            elif dy < 0:
                self.direction = "Up"
            self.moving = True

            # Solo avanza el frame cada X llamadas
            self.anim_counter += 1
            if self.anim_counter >= self.anim_speed:
                self.walk_index = (self.walk_index + 1) % len(self.walk_cycle)
                self.anim_counter = 0
                # --- QUITADO: Reproducir sonido de paso ---
                # self.walk_sound.play()
            frame = self.walk_cycle[self.walk_index]
            self.image = self.load_sprite("Walking", self.direction, frame)
            self.last_direction = self.direction
        else:
            self.moving = False
            self.anim_counter = 0
            self.image = self.load_sprite("Walking", self.direction, 2)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, 48, 48)

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        if self.pet:
            self.pet.draw(screen)

    def hurt(self):
        pass