class Constances:
    # Window dimensions
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    
    # Tamaño de los tiles
    TILE_SIZE = 32
    
    # Dimensiones del laberinto
    MAZE_WIDTH = (WINDOW_WIDTH - 100) // TILE_SIZE
    MAZE_HEIGHT = (WINDOW_HEIGHT - 100) // TILE_SIZE

    # Game grid
    TILE_SIZE = 32
    GRID_WIDTH = WINDOW_WIDTH // TILE_SIZE
    GRID_HEIGHT = WINDOW_HEIGHT // TILE_SIZE
    
    # Game speeds
    PLAYER_SPEED = 5
    ENEMY_SPEED = 3
    BOMB_TIMER = 3
    
    # Scoring
    POINTS_ENEMY = 100
    POINTS_ITEM = 50
    POINTS_LEVEL = 1000

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


