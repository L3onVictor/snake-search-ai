import pygame
import sys

from src.core import Board, Snake, Food
from src.algorithms.greedy import GreedySearch
from src.algorithms.a_star import AStarSearch

# CONFIG
CELL_SIZE = 30
GRID_SIZE = 15
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake AI")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)


# ===== GAME SETUP =====
board = Board(GRID_SIZE, GRID_SIZE)
snake = Snake((GRID_SIZE // 2, GRID_SIZE // 2))
food = Food(GRID_SIZE, GRID_SIZE)
food.spawn(snake.body)

agent = AStarSearch(board, snake, food)
agent_name = "A*"


def draw():
    screen.fill((0, 0, 0))

    # snake
    for i, (x, y) in enumerate(snake.body):
        color = (0, 255, 0) if i == 0 else (0, 180, 0)
        pygame.draw.rect(screen, color, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # food
    fx, fy = food.position
    pygame.draw.rect(screen, (255, 0, 0), (fx*CELL_SIZE, fy*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # texto
    text = font.render(f"Algoritmo: {agent_name}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

    pygame.display.flip()


running = True

while running:
    clock.tick(10)  # velocidade

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    move = agent.get_move()

    if move is None:
        print("Game Over")
        break

    hx, hy = snake.body[0]
    nx, ny = move

    # colisões
    if not board.in_bounds((nx, ny)) or (nx, ny) in snake.body:
        print("Game Over")
        break

    will_eat = (nx, ny) == food.position

    snake.set_direction((nx - hx, ny - hy))
    snake.move(grow=will_eat)

    if will_eat:
        food.spawn(snake.body)
        agent.food = food

    draw()

pygame.quit()
sys.exit()