import pygame
import math
import random
import time
from PIL import Image, ImageSequence
import os


# Inicializar Pygame
pygame.init()

# Configuración de la pantalla
ANCHO = 800
ALTO = 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Final Boss - Boss Intro")

# Colores oscuros inspirados en Bomberman
NEGRO = (0, 0, 0)
GRIS_OSCURO = (20, 20, 20)
BLANCO = (255, 255, 255)
NARANJA_FUEGO = (255, 100, 0)
ROJO_EXPLOSION = (255, 50, 50)
AMARILLO_BOMBA = (255, 200, 0)
VERDE_TOXICO = (100, 255, 50)
PURPURA_SOMBRA = (80, 0, 120)
AZUL_ELECTRICO = (0, 150, 255)

# Fuentes pixeladas
try:
    fuente_titulo = pygame.font.Font(None, 84)
    fuente_nombre = pygame.font.Font(None, 56)
    fuente_dialogo = pygame.font.Font(None, 32)
    fuente_boton = pygame.font.Font(None, 48)
except:
    fuente_titulo = pygame.font.SysFont('courier', 84, bold=True)
    fuente_nombre = pygame.font.SysFont('courier', 56, bold=True)
    fuente_dialogo = pygame.font.SysFont('courier', 32)
    fuente_boton = pygame.font.SysFont('courier', 48, bold=True)
    
# Clase para manejar GIF animado como fondo
class FondoGIF:
    def __init__(self, ruta_gif=None):
        self.frames = []
        self.frame_actual = 0
        self.tiempo_frame = 0
        self.duracion_frame = 100  # milisegundos por frame
        self.usando_gif = False
        
        if ruta_gif and os.path.exists(ruta_gif):
            self.cargar_gif(ruta_gif)
        else:
            self.crear_fondo_procedural()
    
    def cargar_gif(self, ruta_gif):
        try:
            gif = Image.open(ruta_gif)
            for frame in ImageSequence.Iterator(gif):
                if frame.mode != 'RGB':
                    frame = frame.convert('RGB')
                frame = frame.resize((ANCHO, ALTO), Image.Resampling.LANCZOS)
                frame_string = frame.tobytes()
                pygame_frame = pygame.image.fromstring(frame_string, (ANCHO, ALTO), 'RGB')
                self.frames.append(pygame_frame)
            self.usando_gif = True
        except Exception:
            self.crear_fondo_procedural()
    
    def crear_fondo_procedural(self):
        for i in range(30):
            frame_surface = pygame.Surface((ANCHO, ALTO))
            frame_surface.fill((5, 5, 10))
            for x in range(0, ANCHO, 40):
                for y in range(0, ALTO, 40):
                    variacion = math.sin((x + y + i * 10) * 0.01) * 0.3
                    if (x + y) % 80 == 0:
                        r = max(10, min(80, int(25 + variacion * 30)))
                        g = max(5, min(40, int(15 + variacion * 20)))
                        b = max(5, min(30, int(10 + variacion * 15)))
                        color_ladrillo = (r, g, b)
                        pygame.draw.rect(frame_surface, color_ladrillo, (x, y, 35, 35))
                        if random.randint(1, 100) < 20:
                            pygame.draw.line(frame_surface, (r//2, g//2, b//2), 
                                           (x + 5, y + 5), (x + 30, y + 30), 2)
            for _ in range(15):
                humo_x = random.randint(0, ANCHO)
                humo_y = random.randint(0, ALTO)
                humo_radio = random.randint(20, 60)
                alpha = int(30 + 20 * math.sin((i + humo_x + humo_y) * 0.02))
                humo_surf = pygame.Surface((humo_radio * 2, humo_radio * 2), pygame.SRCALPHA)
                color_humo = (40, 60, 40, alpha)
                pygame.draw.circle(humo_surf, color_humo, (humo_radio, humo_radio), humo_radio)
                frame_surface.blit(humo_surf, (humo_x - humo_radio, humo_y - humo_radio))
            if i % 5 == 0:
                for _ in range(8):
                    chispa_x = random.randint(0, ANCHO)
                    chispa_y = random.randint(0, ALTO)
                    chispa_color = random.choice([NARANJA_FUEGO, AMARILLO_BOMBA, ROJO_EXPLOSION])
                    pygame.draw.circle(frame_surface, chispa_color, (chispa_x, chispa_y), 2)
            self.frames.append(frame_surface)
    
    def actualizar(self, tiempo_actual):
        if len(self.frames) == 0:
            return
        if tiempo_actual - self.tiempo_frame > self.duracion_frame:
            self.frame_actual = (self.frame_actual + 1) % len(self.frames)
            self.tiempo_frame = tiempo_actual
    
    def dibujar(self, superficie, alpha=255, offset_x=0, offset_y=0):
        if len(self.frames) == 0:
            superficie.fill(NEGRO)
            return
        frame_actual_surface = self.frames[self.frame_actual].copy()
        if alpha < 255:
            frame_actual_surface.set_alpha(alpha)
        if offset_x != 0 or offset_y != 0:
            superficie.fill(NEGRO)
            superficie.blit(frame_actual_surface, (offset_x, offset_y))
        else:
            superficie.blit(frame_actual_surface, (0, 0))

# Clase para humo tóxico (sin cambios)
class HumoToxico:
    def __init__(self):
        self.x = random.randint(0, ANCHO)
        self.y = ALTO + random.randint(0, 50)
        self.velocidad_y = random.uniform(0.5, 1.5)
        self.velocidad_x = random.uniform(-0.3, 0.3)
        self.tamaño = random.randint(15, 30)
        self.alpha = random.randint(50, 120)
        self.color = VERDE_TOXICO
        
    def actualizar(self):
        self.y -= self.velocidad_y
        self.x += self.velocidad_x
        self.tamaño += 0.1
        if self.y < -50:
            self.y = ALTO + random.randint(0, 50)
            self.x = random.randint(0, ANCHO)
            self.tamaño = random.randint(15, 30)
    
    def dibujar(self, superficie):
        humo_surf = pygame.Surface((self.tamaño * 2, self.tamaño * 2), pygame.SRCALPHA)
        color_con_alpha = (*self.color, self.alpha)
        pygame.draw.circle(humo_surf, color_con_alpha, (self.tamaño, self.tamaño), self.tamaño)
        superficie.blit(humo_surf, (self.x - self.tamaño, self.y - self.tamaño))

# Clase para el Boss BIGARON
class BossBomberman:
    def __init__(self):
        self.x = ANCHO // 2
        self.y = ALTO // 2 - 50
        self.escala = 0
        self.rotacion = 0
        self.alpha = 0
        self.ojos_brillo = 0
        self.ojos_direccion = 1
        self.tiempo_bomba = 0
        self.bombas_activas = []
        # Cargar imagen del boss
        try:
            self.imagen = pygame.image.load("boss 1.png").convert_alpha()
        except Exception:
            self.imagen = pygame.Surface((200, 200), pygame.SRCALPHA)
            pygame.draw.circle(self.imagen, ROJO_EXPLOSION, (100, 100), 100)
        self.imagen_original = self.imagen.copy()

    def actualizar(self, tiempo_transcurrido):
        # Animación de aparición más dramática
        if tiempo_transcurrido > 1500:
            target_escala = 1.0
            target_alpha = 255
            self.escala += (target_escala - self.escala) * 0.04
            self.alpha += (target_alpha - self.alpha) * 0.03
        # Efecto de temblor cuando aparece
        if 1500 < tiempo_transcurrido < 3000:
            self.x = ANCHO // 2 + random.randint(-3, 3)
            self.y = ALTO // 2 - 50 + random.randint(-2, 2)
        else:
            self.x = ANCHO // 2
            self.y = ALTO // 2 - 50
        # Animación de ojos malvados (no usada en imagen)
        self.ojos_brillo += self.ojos_direccion * 8
        if self.ojos_brillo >= 255:
            self.ojos_brillo = 255
            self.ojos_direccion = -1
        elif self.ojos_brillo <= 80:
            self.ojos_brillo = 80
            self.ojos_direccion = 1
        # Crear bombas amenazantes ocasionalmente
        self.tiempo_bomba += 1
        if self.tiempo_bomba > 180 and random.randint(1, 100) < 3:
            self.bombas_activas.append({
                'x': random.randint(100, ANCHO - 100),
                'y': random.randint(100, ALTO - 200),
                'tiempo': 0,
                'parpadeo': False
            })
            self.tiempo_bomba = 0
        # Actualizar bombas
        for bomba in self.bombas_activas[:]:
            bomba['tiempo'] += 1
            if bomba['tiempo'] > 120:
                bomba['parpadeo'] = True
            if bomba['tiempo'] > 180:
                # Crear explosión
                pass
        # Limpiar bombas explotadas
        self.bombas_activas = [b for b in self.bombas_activas if b['tiempo'] <= 180]
        return None

    def dibujar(self, superficie):
        if self.escala <= 0:
            return
        ancho = int(self.imagen_original.get_width() * self.escala)
        alto = int(self.imagen_original.get_height() * self.escala)
        imagen_escalada = pygame.transform.smoothscale(self.imagen_original, (ancho, alto))
        imagen_escalada.set_alpha(int(self.alpha))
        rect = imagen_escalada.get_rect(center=(self.x, self.y))
        superficie.blit(imagen_escalada, rect)
        # Bombas animadas
        for bomba in self.bombas_activas:
            color_bomba = AMARILLO_BOMBA
            if bomba['parpadeo'] and int(time.time() * 10) % 2:
                color_bomba = ROJO_EXPLOSION
            pygame.draw.circle(superficie, color_bomba, (bomba['x'], bomba['y']), 15)
            pygame.draw.circle(superficie, NEGRO, (bomba['x'], bomba['y']), 15, 2)
            if bomba['tiempo'] > 60:
                mecha_color = NARANJA_FUEGO if int(time.time() * 20) % 2 else AMARILLO_BOMBA
                pygame.draw.line(superficie, mecha_color,
                                 (bomba['x'], bomba['y'] - 15),
                                 (bomba['x'] - 5, bomba['y'] - 25), 3)

# Sistema de diálogos temático de BIGARON
class SistemaDialogoOscuro:
    def __init__(self):
        self.dialogos = [
            "¡Ja, ja, ja! ¡Otro insignificante guerrero!",
            "Soy BIGARON, señor de la destrucción...",
            "Mi martillo ha destruido miles de mundos.",
            "¿Crees que puedes detener mi reinado del caos?",
            "¡Entonces prepárate para una EXPLOSIÓN DE DOLOR!",
            "¡Que comience la ANIQUILACIÓN TOTAL!"
        ]
        self.dialogo_actual = 0
        self.texto_mostrado = ""
        self.indice_caracter = 0
        self.tiempo_ultimo_caracter = 0
        self.velocidad_texto = 70
        self.dialogo_completo = False
        self.mostrar_dialogo = False
        
    def iniciar_dialogo(self):
        self.mostrar_dialogo = True
        self.dialogo_completo = False
        self.texto_mostrado = ""
        self.indice_caracter = 0
        
    def actualizar(self, tiempo_actual):
        if not self.mostrar_dialogo:
            return
        if not self.dialogo_completo:
            if tiempo_actual - self.tiempo_ultimo_caracter > self.velocidad_texto:
                if self.indice_caracter < len(self.dialogos[self.dialogo_actual]):
                    self.texto_mostrado += self.dialogos[self.dialogo_actual][self.indice_caracter]
                    self.indice_caracter += 1
                    self.tiempo_ultimo_caracter = tiempo_actual
                else:
                    self.dialogo_completo = True
    
    def siguiente_dialogo(self):
        if self.dialogo_actual < len(self.dialogos) - 1:
            self.dialogo_actual += 1
            self.dialogo_completo = False
            self.texto_mostrado = ""
            self.indice_caracter = 0
            return True
        return False
    
    def dibujar(self, superficie):
        if not self.mostrar_dialogo:
            return
        dialogo_rect = pygame.Rect(80, ALTO - 220, ANCHO - 160, 180)
        pygame.draw.rect(superficie, (10, 5, 5), dialogo_rect)
        pygame.draw.rect(superficie, NARANJA_FUEGO, dialogo_rect, 4)
        for i in range(0, dialogo_rect.width, 20):
            flame_height = random.randint(5, 15)
            pygame.draw.polygon(superficie, ROJO_EXPLOSION, [
                (dialogo_rect.x + i, dialogo_rect.y),
                (dialogo_rect.x + i + 10, dialogo_rect.y - flame_height),
                (dialogo_rect.x + i + 20, dialogo_rect.y)
            ])
        nombre_texto = fuente_nombre.render("💣BIGARON💣", True, AMARILLO_BOMBA)
        nombre_rect = nombre_texto.get_rect()
        nombre_rect.centerx = dialogo_rect.centerx
        nombre_rect.y = dialogo_rect.y + 15
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            nombre_sombra = fuente_nombre.render("💣BIGARON💣", True, ROJO_EXPLOSION)
            superficie.blit(nombre_sombra, (nombre_rect.x + offset[0], nombre_rect.y + offset[1]))
        superficie.blit(nombre_texto, nombre_rect)
        lineas = self.texto_mostrado.split('\n') if '\n' in self.texto_mostrado else [self.texto_mostrado]
        for i, linea in enumerate(lineas):
            texto_surface = fuente_dialogo.render(linea, True, BLANCO)
            texto_rect = texto_surface.get_rect()
            texto_rect.x = dialogo_rect.x + 25
            texto_rect.y = dialogo_rect.y + 80 + (i * 35)
            superficie.blit(texto_surface, texto_rect)
        if self.dialogo_completo:
            cursor_tiempo = int(time.time() * 3) % 2
            if cursor_tiempo:
                cursor_text = fuente_dialogo.render("💣", True, AMARILLO_BOMBA)
                cursor_x = dialogo_rect.x + 25 + len(self.texto_mostrado) * 12
                cursor_y = dialogo_rect.y + 80
                superficie.blit(cursor_text, (cursor_x, cursor_y))


# Clase para la ventana de introducción del jefe (nuevo)
class IntroBossWindow:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock

    def run(self):
        # --- Copia de la lógica de main(), adaptada para usar self.screen y self.clock ---
        ANCHO, ALTO = self.screen.get_size()
        ruta_gif = "112.gif"
        fondo_gif = FondoGIF(ruta_gif)
        humo_toxico = [HumoToxico() for _ in range(15)]
        boss = BossBomberman()
        sistema_dialogo = SistemaDialogoOscuro()
        explosiones = []
        tiempo_inicio = pygame.time.get_ticks()
        fase_actual = "intro"
        mostrar_titulo = True
        alpha_titulo = 255
        temblor_pantalla = 0

        running = True
        while running:
            tiempo_actual = pygame.time.get_ticks()
            tiempo_transcurrido = tiempo_actual - tiempo_inicio
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    running = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        if fase_actual == "dialogo":
                            if sistema_dialogo.dialogo_completo:
                                if not sistema_dialogo.siguiente_dialogo():
                                    fase_actual = "batalla"
                            else:
                                sistema_dialogo.texto_mostrado = sistema_dialogo.dialogos[sistema_dialogo.dialogo_actual]
                                sistema_dialogo.dialogo_completo = True
                    elif evento.key == pygame.K_RETURN:
                        if fase_actual == "batalla":
                            running = False
            if fase_actual == "intro":
                if tiempo_transcurrido > 3000:
                    alpha_titulo = max(0, alpha_titulo - 8)
                    if alpha_titulo == 0:
                        mostrar_titulo = False
                if tiempo_transcurrido > 5000:
                    fase_actual = "dialogo"
                    sistema_dialogo.iniciar_dialogo()
            fondo_gif.actualizar(tiempo_actual)
            for humo in humo_toxico:
                humo.actualizar()
            boss.actualizar(tiempo_transcurrido)
            sistema_dialogo.actualizar(tiempo_actual)
            if temblor_pantalla > 0:
                temblor_pantalla -= 1
            offset_x = random.randint(-temblor_pantalla, temblor_pantalla) if temblor_pantalla > 0 else 0
            offset_y = random.randint(-temblor_pantalla, temblor_pantalla) if temblor_pantalla > 0 else 0
            fondo_gif.dibujar(self.screen, offset_x=offset_x, offset_y=offset_y)
            for humo in humo_toxico:
                humo.dibujar(self.screen)
            for explosion in explosiones:
                explosion.dibujar(self.screen)
            if mostrar_titulo:
                titulo_texto = fuente_titulo.render("💣 Final Boss 💣", True, AMARILLO_BOMBA)
                titulo_surface = pygame.Surface(titulo_texto.get_size(), pygame.SRCALPHA)
                for offset in [(3, 3), (-3, -3), (3, -3), (-3, 3)]:
                    titulo_sombra = fuente_titulo.render("💣 Final Boss  💣", True, ROJO_EXPLOSION)
                    titulo_surface.blit(titulo_sombra, offset)
                titulo_surface.blit(titulo_texto, (0, 0))
                titulo_surface.set_alpha(alpha_titulo)
                titulo_rect = titulo_surface.get_rect()
                titulo_rect.centerx = ANCHO // 2 + offset_x
                titulo_rect.y = 80 + offset_y
                self.screen.blit(titulo_surface, titulo_rect)
            boss.dibujar(self.screen)
            sistema_dialogo.dibujar(self.screen)
            if fase_actual == "dialogo":
                instruccion = "ESPACIO - Continuar diálogo"
                texto_instruccion = fuente_dialogo.render(instruccion, True, VERDE_TOXICO)
                rect_instruccion = texto_instruccion.get_rect()
                rect_instruccion.centerx = ANCHO // 2
                rect_instruccion.y = ALTO - 30
                self.screen.blit(texto_instruccion, rect_instruccion)
            elif fase_actual == "batalla":
                instruccion = "💥 ENTER - ¡INICIAR BATALLA ! 💥"
                escala = 1 + 0.2 * math.sin(tiempo_actual * 0.008)
                color_pulso = ROJO_EXPLOSION if int(tiempo_actual * 0.01) % 2 else AMARILLO_BOMBA
                texto_instruccion = fuente_boton.render(instruccion, True, color_pulso)
                texto_escalado = pygame.transform.scale(texto_instruccion, 
                                                      (int(texto_instruccion.get_width() * escala), 
                                                       int(texto_instruccion.get_height() * escala)))
                rect_escalado = texto_escalado.get_rect()
                rect_escalado.centerx = ANCHO // 2
                rect_escalado.y = ALTO - 120
                self.screen.blit(texto_escalado, rect_escalado)
            pygame.display.flip()
            self.clock.tick(60)


# Función principal
def main():
    reloj = pygame.time.Clock()
    corriendo = True
    ruta_gif = "112.gif"
    fondo_gif = FondoGIF(ruta_gif)
    humo_toxico = [HumoToxico() for _ in range(15)]
    boss = BossBomberman()
    sistema_dialogo = SistemaDialogoOscuro()
    explosiones = []
    tiempo_inicio = pygame.time.get_ticks()
    fase_actual = "intro"
    mostrar_titulo = True
    alpha_titulo = 255
    temblor_pantalla = 0
    while corriendo:
        tiempo_actual = pygame.time.get_ticks()
        tiempo_transcurrido = tiempo_actual - tiempo_inicio
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    if fase_actual == "dialogo":
                        if sistema_dialogo.dialogo_completo:
                            if not sistema_dialogo.siguiente_dialogo():
                                fase_actual = "batalla"
                        else:
                            sistema_dialogo.texto_mostrado = sistema_dialogo.dialogos[sistema_dialogo.dialogo_actual]
                            sistema_dialogo.dialogo_completo = True
                elif evento.key == pygame.K_RETURN:
                    if fase_actual == "batalla":
                        corriendo = False
        if fase_actual == "intro":
            if tiempo_transcurrido > 3000:
                alpha_titulo = max(0, alpha_titulo - 8)
                if alpha_titulo == 0:
                    mostrar_titulo = False
            if tiempo_transcurrido > 5000:
                fase_actual = "dialogo"
                sistema_dialogo.iniciar_dialogo()
        fondo_gif.actualizar(tiempo_actual)
        for humo in humo_toxico:
            humo.actualizar()
        boss.actualizar(tiempo_transcurrido)
        sistema_dialogo.actualizar(tiempo_actual)
        if temblor_pantalla > 0:
            temblor_pantalla -= 1
        offset_x = random.randint(-temblor_pantalla, temblor_pantalla) if temblor_pantalla > 0 else 0
        offset_y = random.randint(-temblor_pantalla, temblor_pantalla) if temblor_pantalla > 0 else 0
        fondo_gif.dibujar(pantalla, offset_x=offset_x, offset_y=offset_y)
        for humo in humo_toxico:
            humo.dibujar(pantalla)
        for explosion in explosiones:
            explosion.dibujar(pantalla)
        if mostrar_titulo:
            titulo_texto = fuente_titulo.render("💣 Final Boss  💣", True, AMARILLO_BOMBA)
            titulo_surface = pygame.Surface(titulo_texto.get_size(), pygame.SRCALPHA)
            for offset in [(3, 3), (-3, -3), (3, -3), (-3, 3)]:
                titulo_sombra = fuente_titulo.render("💣 Final Boss 💣", True, ROJO_EXPLOSION)
                titulo_surface.blit(titulo_sombra, offset)
            titulo_surface.blit(titulo_texto, (0, 0))
            titulo_surface.set_alpha(alpha_titulo)
            titulo_rect = titulo_surface.get_rect()
            titulo_rect.centerx = ANCHO // 2 + offset_x
            titulo_rect.y = 80 + offset_y
            pantalla.blit(titulo_surface, titulo_rect)
        boss.dibujar(pantalla)
        sistema_dialogo.dibujar(pantalla)
        if fase_actual == "dialogo":
            instruccion = "ESPACIO - Continuar diálogo explosivo"
            texto_instruccion = fuente_dialogo.render(instruccion, True, VERDE_TOXICO)
            rect_instruccion = texto_instruccion.get_rect()
            rect_instruccion.centerx = ANCHO // 2
            rect_instruccion.y = ALTO - 30
            pantalla.blit(texto_instruccion, rect_instruccion)
        elif fase_actual == "batalla":
            instruccion = "💥 ENTER - ¡BATALLA DE FINAL BOSS INICIADA ! 💥"
            escala = 1 + 0.2 * math.sin(tiempo_actual * 0.008)
            color_pulso = ROJO_EXPLOSION if int(tiempo_actual * 0.01) % 2 else AMARILLO_BOMBA
            texto_instruccion = fuente_boton.render(instruccion, True, color_pulso)
            texto_escalado = pygame.transform.scale(texto_instruccion, 
                                                  (int(texto_instruccion.get_width() * escala), 
                                                   int(texto_instruccion.get_height() * escala)))
            rect_escalado = texto_escalado.get_rect()
            rect_escalado.centerx = ANCHO // 2
            rect_escalado.y = ALTO - 120
            pantalla.blit(texto_escalado, rect_escalado)
        pygame.display.flip()
        reloj.tick(60)