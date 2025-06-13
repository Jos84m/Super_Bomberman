import enum
from enum import Enum



class GameState(Enum):
    MENU = 1
    CHARACTER_SELECT = 3
    GAME = 4
    SETTINGS = 4
    SCORES = 5
    INFO = 6
    GAME_OVER = 7
    LEVEL_COMPLETE = 8