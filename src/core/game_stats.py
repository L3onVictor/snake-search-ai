from core import Snake, Food, Board

class GameStats:
    def __init__(self, board_width: int, board_height: int):
        self.board = Board(board_width, board_height)
        self.snake = Snake((board_width // 2, board_height // 2))
        self.food = Food(board_width, board_height)

        self.food.spawn(self.snake.body)

        self.score = 0
        self.game_over = False


    def get_next_head(self):
        head_x, head_y = self.snake.body[0]
        dx, dy = self.snake.direction
        return (head_x + dx, head_y + dy)
    
    
    def update(self):
        if self.game_over:
            return
        
        next_head = self.get_next_head()

        # Colisão com as paredes
        if not self.board.in_bounds(next_head):
            self.game_over = True
            return
        
        # Colisão com o próprio corpo
        if next_head in self.snake.body:
            self.game_over = True
            return
        
        # Verificar se comeu a comida
        if next_head == self.food.position:
            self.snake.move(grow=True)
            self.score += 1
            self.food.spawn(self.snake.body)
        else:
            self.snake.move()
