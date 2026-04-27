from src.core import Board, Snake, Food
from src.algorithms.a_star import AStarSearch

import time

BOARD_SIZE = 10
STEPS = 30


board = Board(BOARD_SIZE, BOARD_SIZE)
snake = Snake((5, 5))

food = Food(BOARD_SIZE, BOARD_SIZE)
food.spawn(snake.body)

agent = AStarSearch(board, snake, food)


def print_board(path=None):
    grid = [["." for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    # comida
    fx, fy = food.position
    grid[fy][fx] = "F"

    # caminho do A*
    if path:
        for (x, y) in path:
            if (x, y) != snake.body[0]:
                grid[y][x] = "*"

    # snake
    for i, (x, y) in enumerate(snake.body):
        grid[y][x] = "H" if i == 0 else "o"

    for row in grid:
        print(" ".join(row))
    print("\n")


for step in range(STEPS):
    print(f"STEP {step}")

    path = agent.find_path()  # 🔥 diferença importante

    print_board(path)

    if not path or len(path) < 2:
        print("Sem caminho possível")
        break

    next_move = path[1]

    hx, hy = snake.body[0]
    nx, ny = next_move

    snake.set_direction((nx - hx, ny - hy))

    will_eat = (nx, ny) == food.position
    snake.move(grow=will_eat)

    if will_eat:
        print("COMEU!\n")
        food.spawn(snake.body)
        agent.food = food

    time.sleep(0.3)  # só pra visualizar melhor