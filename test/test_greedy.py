from src.core import Board, Snake, Food
from src.algorithms.greedy import GreedySearch
import random

board = Board(10, 10)
snake = Snake((5, 5))

food = Food(10, 10)
food.spawn(snake.body)

agent = GreedySearch(board, snake, food)

def print_board():
    grid = [["." for _ in range(10)] for _ in range(10)]

    fx, fy = food.position
    grid[fy][fx] = "F"

    for i, (x, y) in enumerate(snake.body):
        grid[y][x] = "H" if i == 0 else "o"

    for row in grid:
        print(" ".join(row))
    print("\n")

for step in range(30):
    print(f"STEP {step}")
    print_board()

    move = agent.get_move()

    if move is None:
        print("Sem movimentos possíveis")
        break

    hx, hy = snake.body[0]
    nx, ny = move

    snake.set_direction((nx - hx, ny - hy))
    will_eat = (nx, ny) == food.position
    snake.move(grow=will_eat)

    # 🍎 comida
    if snake.body[0] == food.position:
        print("COMEU!\n")
        food.spawn(snake.body)

        # atualiza agente (IMPORTANTE)
        agent.food = food