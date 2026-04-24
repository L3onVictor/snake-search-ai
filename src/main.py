from core.board import Board
from core.snake import Snake

# board = Board(5, 5)
# print(board.get_neighbors((0, 0)))

snake = Snake((2, 2))
print(snake.body) # (2, 2)
snake.move()
print(snake.body) # (2, 3)
snake.set_direction((0, 1)) # baixo
snake.move()
print(snake.body) # (2, 4)
snake.move()
print(snake.body) # (2, 5)