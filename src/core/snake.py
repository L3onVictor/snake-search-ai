from typing import Tuple

Position = Tuple[int, int]

class Snake:
    def __init__(self, start_pos: Position):
        self.body: list[Position] = [start_pos]
        self.direction = (1, 0) # inicialmente se movendo para a direita

    def set_direction(self, new_direction: Position):
        self.direction = new_direction

    def move(self):
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        self.body.pop()