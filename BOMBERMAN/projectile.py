import math
from typing import Tuple


class Projectile:
    def __init__(self, x: int, y: int, direction: Tuple[int, int], damage: int):
        self.x = float(x)
        self.y = float(y)
        self.dx, self.dy = direction
        self.damage = damage
        self.speed = 3
