from src.utils.manhattan_distance import manhattan_distance
class GreedySearch:
    def __init__(self, board, snake, food):
        self.board = board
        self.snake = snake
        self.food = food
    
    def get_move(self):
        head = self.snake.body[0]

        neighbors = self.board.get_neighbors(head)

        valid = [n for n in neighbors if n not in self.snake.body]
       
        if not valid:
           return None
       
        best = min(valid, key=lambda pos: manhattan_distance(pos, self.food.position))
        return best
       