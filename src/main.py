from core.board import Board
from core.snake import Snake
from core.food import Food
from core import Snake


from core.game_stats import GameStats

game = GameStats(10, 10)

for step in range(50):
    game.update()

    print("Step:", step)
    print("Snake:", game.snake.body)
    print("Food:", game.food.position)
    print("Score:", game.score)
    print("Game Over:", game.game_over)
    print("------")

    if game.game_over:
        break
    
# food = Food(10,10)
# snake_body = [(2, 2), (2, 3), (2, 4)]
# food.spawn(snake_body)
# print(food.position)
# snake = Snake((2, 2))

# if snake.body[0] == food.position:
#     snake.move(grow=True)
#     food.spawn(snake.body)
# else:
#     snake.move()

# board = Board(5, 5)
# print(board.get_neighbors((0, 0)))

# snake = Snake((2, 2))
# print(snake.body) # (2, 2)
# snake.move()
# print(snake.body) # (2, 3)
# snake.set_direction((0, 1)) # baixo
# snake.move()
# print(snake.body) # (2, 4)
# snake.move()
# print(snake.body) # (2, 5)