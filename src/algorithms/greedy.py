class GreedySearch:
    def __init__(self, board, snake, food):
        self.board = board
        self.snake = snake
        self.food = food

    def manhattan_distance(self, pos):
        fx, fy = self.food.position
        x, y = pos
        return abs(x - fx) + abs(y - fy)
    
    def get_best_move(self):
        head = self.snake.body[0]

        neighbors = self.board.get_neighbors(head)

        valid = [n for n in neighbors if n not in self.snake.body]
       
        if not valid:
           return None
       
        best = min(valid, key=self.manhattan_distance)
        return best
       