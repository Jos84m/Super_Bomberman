import pygame
import sys

# Inicializar Pygame
pygame.init()

# Configuración de la ventana
ANCHO, ALTO = 400, 200
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Control de Música y Volumen")

# Colores
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AZUL = (0, 120, 255)
GRIS = (200, 200, 200)

# Fuente
fuente = pygame.font.SysFont(None, 30)

# Música
pygame.mixer.music.load("Music.mp3")  # <-- Reemplaza por tu archivo
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# Estado
volumen = 0.5
musica_activada = True

# Función para mostrar los controles
def mostrar_control_volumen(pantalla):
    global volumen, musica_activada

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    # Dibujar barra de volumen
    pygame.draw.rect(pantalla, GRIS, (50, 100, 300, 10))
    pygame.draw.circle(pantalla, AZUL, (50 + int(volumen * 300), 105), 10)

    # Mostrar porcentaje
    texto_vol = fuente.render(f"Volumen: {int(volumen * 100)}%", True, NEGRO)
    pantalla.blit(texto_vol, (140, 30))

    # Mostrar estado ON/OFF
    estado = "ON" if musica_activada else "OFF"
    texto_estado = fuente.render(f"[Espacio] Música: {estado}", True, NEGRO)
    pantalla.blit(texto_estado, (90, 150))

    # Control por clic
    if click[0] == 1 and 100 <= mouse[1] <= 120 and 50 <= mouse[0] <= 350:
        volumen = (mouse[0] - 50) / 300
        if musica_activada:
            pygame.mixer.music.set_volume(volumen)

# Bucle principal
corriendo = True
while corriendo:
    ventana.fill(BLANCO)

    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            corriendo = False

        if evento.type == pygame.KEYDOWN:
            # Encender/Apagar música
            if evento.key == pygame.K_SPACE:
                if musica_activada:
                    pygame.mixer.music.stop()
                else:
                    pygame.mixer.music.play(-1)
                    pygame.mixer.music.set_volume(volumen)
                musica_activada = not musica_activada

            # Subir volumen
            elif evento.key == pygame.K_UP:
                volumen = min(1.0, volumen + 0.1)
                if musica_activada:
                    pygame.mixer.music.set_volume(volumen)

            # Bajar volumen
            elif evento.key == pygame.K_DOWN:
                volumen = max(0.0, volumen - 0.1)
                if musica_activada:
                    pygame.mixer.music.set_volume(volumen)

    # Mostrar controles en pantalla
    mostrar_control_volumen(ventana)

    # Actualizar pantalla
    pygame.display.flip()

pygame.quit()
sys.exit()
