from enum import Enum



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
