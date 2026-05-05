import random
import numpy as np
import matplotlib.pyplot as plt

from src.core.board import Board
from src.core.snake import Snake
from src.core.food import Food

from src.algorithms.a_star       import AStarSearch
from src.algorithms.a_star_path  import AStarSmartSearch
from src.algorithms.greedy       import GreedySearch
from src.algorithms.greedy_path  import GreedySmartSearch


# CONFIG
BOARD_WIDTH = 20
BOARD_HEIGHT = 20
N_GAMES = 30
MAX_STEPS = 3000
GROW_MODE = True
SEED = 42


ALGORITHMS = {
    "A* Puro": AStarSearch,
    "A* Smart": AStarSmartSearch,
    "Gulosa Pura": GreedySearch,
    "Gulosa Smart": GreedySmartSearch,
}


# =========================
# HELPERS
# =========================

def spawn_food(board, snake):
    food = Food(board.width, board.height)
    if not food.spawn(snake.body, board.obstacles):
        return None
    return food


def normalize_move(move, head):
    """
    Detecta automaticamente:
    - direção (dx, dy)
    - posição (nx, ny)
    """
    if move is None:
        return None

    x, y = move

    # Se parecer direção (valores pequenos)
    if abs(x) <= 1 and abs(y) <= 1:
        dx, dy = x, y
        nx, ny = head[0] + dx, head[1] + dy
    else:
        nx, ny = x, y
        dx, dy = nx - head[0], ny - head[1]

    return dx, dy, nx, ny


# =========================
# CORE GAME LOOP
# =========================

def run_game(AlgoClass, seed):
    random.seed(seed)

    board = Board(BOARD_WIDTH, BOARD_HEIGHT)
    snake = Snake((BOARD_WIDTH // 2, BOARD_HEIGHT // 2))
    food = spawn_food(board, snake)

    algo = AlgoClass(board, snake, food)

    score = 0
    steps = 0

    while steps < MAX_STEPS:

        if food is None:
            break

        move = algo.get_move()

        if move is None:
            break

        head = snake.body[0]

        result = normalize_move(move, head)
        if result is None:
            break

        dx, dy, nx, ny = result

        # VALIDAÇÃO ANTES DE MOVER
        if (
            nx < 0 or nx >= board.width or
            ny < 0 or ny >= board.height or
            (nx, ny) in snake.body or
            (nx, ny) in board.obstacles
        ):
            break

        will_eat = (nx, ny) == food.position

        snake.set_direction((dx, dy))
        snake.move(grow=will_eat and GROW_MODE)

        steps += 1

        if will_eat:
            score += 1
            food = spawn_food(board, snake)

            if food is None:
                break

            # Atualiza algoritmo com novo estado
            algo = AlgoClass(board, snake, food)

    return score, steps


# =========================
# BENCHMARK
# =========================

def run_benchmark():
    results = {}

    for name, AlgoClass in ALGORITHMS.items():
        print(f"\n=== {name} ===")
        scores = []
        steps_list = []

        for i in range(N_GAMES):
            score, steps = run_game(AlgoClass, SEED + i)

            print(f"Game {i+1:02d} | Score: {score} | Steps: {steps}")

            scores.append(score)
            steps_list.append(steps)

        results[name] = (scores, steps_list)

    return results


# =========================
# PLOTS
# =========================

def plot_results(results):
    labels = list(results.keys())
    scores = [results[k][0] for k in labels]

    plt.figure()
    plt.boxplot(scores)
    plt.xticks(range(1, len(labels)+1), labels)
    plt.title("Pontuação por algoritmo")
    plt.ylabel("Score")
    plt.show()


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    results = run_benchmark()
    plot_results(results)