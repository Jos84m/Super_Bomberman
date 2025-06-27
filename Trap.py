import pygame
import os

class Trap:
    def __init__(self, x, y, tile_size, trap_type, sprite_base_path):
        self.x = x
        self.y = y
        self.tile_size = tile_size
        self.trap_type = trap_type  # "spike" o "fire"
        self.state = "idle"
        self.trigger_time = 0
        self.cooldown = 1000  # 1 segundo de cooldown al volver a idle (ms)
        self.cooldown_start = 0
        self.last_damage_time = 0  
        self.damage_cooldown = 1000 

        self.rect = pygame.Rect(self.x, self.y, self.tile_size, self.tile_size)

        # Configurar tipo de trampa
        if trap_type == "spike":
            self.frame_count = 5
            self.danger_frames = [4]  # frame 5 en índice 4 es el daño
            self.ping_pong = True
            self.trigger_delay = 500  # ms antes de animar
            self.active_duration = 500  # tiempo en el último frame (no usado explícitamente aquí)
            self.folder = os.path.join(sprite_base_path, "Spike Trap")
            self.prefix = "ST"
        elif trap_type == "fire":
            self.frame_count = 14
            self.danger_frames = [8, 9]  # frames 9 y 10 (índices 8 y 9)
            self.ping_pong = False
            self.trigger_delay = 500
            self.active_duration = 0
            self.folder = os.path.join(sprite_base_path, "Fire Trap")
            self.prefix = "FT"
        else:
            raise ValueError(f"Tipo de trampa no reconocido: {trap_type}")

        self.frames = self.load_sprites()
        self.current_frame = 0
        self.animation_forward = True
        self.last_update = pygame.time.get_ticks()
        self.anim_speed = 100  # ms entre frames

        self.damage_cooldown = 500  # ms entre daños al jugador para no matar instantáneo
        self.last_damage_time = 0

    def load_sprites(self):
        frames = []
        for i in range(1, self.frame_count + 1):
            path = os.path.join(self.folder, f"{self.prefix} {i}.png")
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (self.tile_size, self.tile_size))
            frames.append(img)
        return frames

    def update(self, player):
        now = pygame.time.get_ticks()

        if self.state == "idle":
            # No puede activarse si está en cooldown
            if now - self.cooldown_start < self.cooldown:
                return  # aún en cooldown, no activar

            if self.rect.colliderect(player.get_rect()):
                self.state = "triggered"
                self.trigger_time = now

        elif self.state == "triggered":
            if now - self.trigger_time >= self.trigger_delay:
                self.state = "animating"
                self.last_update = now
                self.current_frame = 0
                self.animation_forward = True

        elif self.state == "animating":
            if now - self.last_update >= self.anim_speed:
                self.last_update = now

                # Daño solo si jugador colisiona y está en frame peligroso y cooldown de daño pasado
                if self.current_frame in self.danger_frames:
                    if self.rect.colliderect(player.get_rect()):
                        if now - self.last_damage_time > self.damage_cooldown:
                            player.lose_life()
                            self.last_damage_time = now

                # Avance de frame
                if self.ping_pong:
                    if self.animation_forward:
                        self.current_frame += 1
                        if self.current_frame >= self.frame_count - 1:
                            self.animation_forward = False
                            self.wait_after_peak = now
                    else:
                        self.current_frame -= 1
                        if self.current_frame <= 0:
                            self.state = "idle"
                            self.cooldown_start = now  # inicia cooldown al volver a idle
                else:
                    self.current_frame += 1
                    if self.current_frame >= self.frame_count:
                        self.current_frame = 0
                        self.state = "idle"
                        self.cooldown_start = now  # inicia cooldown al volver a idle

    def draw(self, screen):
        screen.blit(self.frames[self.current_frame], (self.x, self.y))

    def is_dangerous_frame(self):
        return self.current_frame in self.danger_frames
