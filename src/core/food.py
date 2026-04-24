import random
from typing import Tuple, List

Position = Tuple[int, int]

class Food:
    def __init__(self, board_width: int, board_height: int):
        self.board_width = board_width
        self.board_height = board_height
        self.position: Position = (0, 0)

    def spawn(self, snake_body: List[Position]):
        free_cells = [
            (x, y) for x in range(self.board_width)
            for y in range(self.board_height)

            if (x, y) not in snake_body
        ]
        if not free_cells:
            return #TODO: lidar com caso onde não há mais espaço para a comida
        
        self.position = random.choice(free_cells)
                