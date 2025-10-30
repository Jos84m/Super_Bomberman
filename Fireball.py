import pygame

class Fireball:
    def __init__(self, x, y, direction, speed=8, damage=5):
        self.radius = 12
        self.color_fill = (255, 50, 0)      
        self.color_border = (255, 165, 0)   
        self.rect = pygame.Rect(x, y, self.radius * 2, self.radius * 2)
        self.rect.center = (x, y)
        # direction ahora debe ser una tupla (dx, dy) con valores -1, 0 o 1
        self.dx, self.dy = direction
        self.speed = speed
        self.damage = damage
        self.active = True

    def update(self, enemies, flying_enemies, boss, screen_width, screen_height):
        if not self.active:
             return None

        # Movimiento en ambas direcciones
        self.rect.x += self.speed * self.dx
        self.rect.y += self.speed * self.dy

        # Fuera de pantalla
        if (self.rect.right < 0 or self.rect.left > screen_width or
            self.rect.bottom < 0 or self.rect.top > screen_height):
             self.active = False
             return None

        # Colisión con enemigos normales
        if enemies is not None:
             for enemy in enemies[:]:
                  if self.rect.colliderect(enemy.rect):
                       enemies.remove(enemy)
                       self.active = False
                       return "ground"
             
        # Colisión con enemigos voladores
        if flying_enemies is not None:
             for enemy in flying_enemies[:]:
                  if self.rect.colliderect(enemy.rect):
                       flying_enemies.remove(enemy)
                       self.active = False
                       return "flying"

        # Colisión con jefe
        if boss and self.rect.colliderect(boss.rect):
           boss.take_damage(self.damage)
           self.active = False
           if boss.health <= 0:
               return "boss_killed"
           return None

        return None

    def draw(self, screen):
        if self.active:
            pygame.draw.circle(screen, self.color_border, self.rect.center, self.radius)
            pygame.draw.circle(screen, self.color_fill, self.rect.center, self.radius - 3)
