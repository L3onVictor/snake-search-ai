from typing import List, Tuple, Set

Position = Tuple[int, int]

class Board:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.obstacles: Set[Position] = set()

    def in_bounds(self, pos:Position) -> bool:
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height
    
    def get_neighbors(self, pos:Position) -> List[Position]:
        x, y = pos
        neighbors = [
            (x, y + 1), # baixo
            (x + 1, y), # direita
            (x, y - 1), # cima
            (x - 1, y) # esquerda
            ]
        return [n for n in neighbors if self.in_bounds(n) and n not in self.obstacles]