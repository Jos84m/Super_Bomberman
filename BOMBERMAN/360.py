import time
import random

def movimento_personaje360():
    """
    Simula el movimiento de un personaje en un entorno 360 grados.
    El personaje se mueve en una dirección aleatoria y espera un tiempo aleatorio entre movimientos.
    """
    directions = ['Norte', 'Sur', 'Este', 'Oeste', 'Noreste', 'Noroeste', 'Sureste', 'Suroeste']
    
    while True:
        direction = random.choice(directions)
        print(f"El personaje se mueve hacia: {direction}")
        time.sleep(random.uniform(0.5, 2.0))  # Espera entre 0.5 y 2 segundos antes del siguiente movimiento
