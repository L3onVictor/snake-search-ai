import pygame
import sys
import random

from src.core import Board, Snake, Food
from src.algorithms.greedy import GreedySearch
from src.algorithms.greedy_path import GreedySmartSearch
from src.algorithms.a_star import AStarSearch
from src.algorithms.a_star_path import AStarSmartSearch

# CONFIG
BOARD_WIDTH = 600
HEIGHT = 610
SIDEBAR_WIDTH = 280
WIDTH = BOARD_WIDTH + SIDEBAR_WIDTH

GRID_SIZE = 15
CELL_SIZE = BOARD_WIDTH // GRID_SIZE

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake AI")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 22)
title_font = pygame.font.SysFont(None, 30)

# ===== GLOBAL STATE =====
ALGORITHM_OPTIONS = ["A*", "A* Smart", "Greedy", "Greedy Smart"]
BOARD_SIZES = [10, 15, 20, 40]
agent_name = "A*"
game_speed = 10
game_state = "MENU"
score = 0
total_steps_since_start = 0
grow_enabled = True

board = None
snake = None
food = None
agent = None


# ===== HELPERS =====

def set_agent(name):
    global agent, agent_name

    agent_name = name

    if board is None or snake is None or food is None:
        return

    if name == "A*":
        agent = AStarSearch(board, snake, food)
    elif name == "A* Smart":
        agent = AStarSmartSearch(board, snake, food)
    elif name == "Greedy":
        agent = GreedySearch(board, snake, food)
    elif name == "Greedy Smart":
        agent = GreedySmartSearch(board, snake, food)


def reset_game():
    global board, snake, food, agent, score, game_state, total_steps_since_start

    board = Board(GRID_SIZE, GRID_SIZE)
    snake = Snake((GRID_SIZE // 2, GRID_SIZE // 2))
    food = Food(GRID_SIZE, GRID_SIZE)

    food.spawn(snake.body, board.obstacles)

    set_agent(agent_name)

    score = 0
    total_steps_since_start = 0
    game_state = "PLAYING"


def set_grid_size(size):
    global GRID_SIZE, CELL_SIZE
    GRID_SIZE = size
    CELL_SIZE = BOARD_WIDTH // GRID_SIZE
    reset_game()


def spawn_obstacle():
    max_obstacles = (GRID_SIZE * GRID_SIZE) // 5

    free_cells = [
        (x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)
        if (x, y) not in snake.body
        and (x, y) != food.position
        and (x, y) not in board.obstacles
    ]

    if free_cells and len(board.obstacles) < max_obstacles:
        board.obstacles.add(random.choice(free_cells))


def draw_button(text, rect, color, hover_color, is_hover):
    pygame.draw.rect(screen, hover_color if is_hover else color, rect)
    pygame.draw.rect(screen, (255, 255, 255), rect, 2)

    txt = font.render(text, True, (255, 255, 255))
    screen.blit(txt, txt.get_rect(center=rect.center))


# ===== DRAW =====

def draw():
    screen.fill((18, 18, 18))

    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            pygame.draw.rect(
                screen,
                (45, 45, 45),
                (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                1
            )

    if board:
        for ox, oy in board.obstacles:
            pygame.draw.rect(screen, (90, 90, 90),
                             (ox * CELL_SIZE, oy * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    if agent and hasattr(agent, 'current_path') and agent.current_path:
        path_points = [
            (x * CELL_SIZE + CELL_SIZE // 2,
             y * CELL_SIZE + CELL_SIZE // 2)
            for x, y in agent.current_path
        ]
        if len(path_points) > 1:
            pygame.draw.lines(screen, (80, 150, 240), False, path_points, 3)
            pygame.draw.circle(screen, (255, 215, 100), path_points[-1], 6)

    if food:
        fx, fy = food.position
        pygame.draw.rect(screen, (220, 70, 70),
                         (fx * CELL_SIZE, fy * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    if snake:
        for i, (x, y) in enumerate(snake.body):
            color = (140, 255, 130) if i == 0 else (40, 180, 40)
            pygame.draw.rect(screen, color,
                             (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    panel_x = BOARD_WIDTH + 12
    panel_y = 20

    screen.blit(title_font.render("Snake Search AI", True, (230, 230, 255)), (panel_x, panel_y))
    panel_y += 36

    status = {
        "MENU": "Menu",
        "PLAYING": "Running",
        "PAUSED": "Paused",
        "GAME_OVER": "Game Over"
    }.get(game_state, game_state)

    info = [
        f"Status: {status}",
        f"Board: {GRID_SIZE} x {GRID_SIZE}",
        f"Score: {score}",
        f"Steps: {total_steps_since_start}",
        f"Snake len: {len(snake.body) if snake else 0}",
        f"Path len: {len(agent.current_path) - 1 if agent and getattr(agent, 'current_path', None) else 0}",
        f"Speed: {game_speed}",
        f"Alg: {agent_name}",
        f"Grow: {'ON' if grow_enabled else 'OFF'}"
    ]

    if snake and food:
        dist = abs(snake.body[0][0] - food.position[0]) + abs(snake.body[0][1] - food.position[1])
        info.insert(5, f"Food dist: {dist}")

    col_a = panel_x
    col_b = panel_x + 140
    row_a = panel_y
    row_b = panel_y

    for idx, line in enumerate(info):
        target_x = col_a if idx % 2 == 0 else col_b
        target_y = row_a if idx % 2 == 0 else row_b
        screen.blit(font.render(line, True, (220, 220, 220)), (target_x, target_y))
        if idx % 2 == 0:
            row_a += 24
        else:
            row_b += 24

    panel_y = max(row_a, row_b) + 18
    screen.blit(font.render("Controles", True, (180, 180, 255)), (panel_x, panel_y))
    panel_y += 28

    buttons = {}
    mouse = pygame.mouse.get_pos()

    play_rect = pygame.Rect(panel_x, panel_y, 128, 42)
    pause_text = "Iniciar" if game_state != "PLAYING" else "Pausar"
    if game_state == "GAME_OVER":
        pause_text = "Reiniciar"
    draw_button(pause_text, play_rect, (80, 80, 80), (120, 120, 120), play_rect.collidepoint(mouse))
    buttons["play"] = play_rect

    reset_rect = pygame.Rect(panel_x + 138, panel_y, 128, 42)
    draw_button("Resetar", reset_rect, (80, 55, 55), (125, 80, 80), reset_rect.collidepoint(mouse))
    buttons["reset"] = reset_rect
    panel_y += 52

    screen.blit(font.render("Algoritmos", True, (180, 180, 255)), (panel_x, panel_y))
    panel_y += 28
    for idx, name in enumerate(ALGORITHM_OPTIONS):
        col = panel_x if idx % 2 == 0 else panel_x + 138
        row = panel_y + (idx // 2) * 44
        rect = pygame.Rect(col, row, 128, 36)
        color = (10, 120, 90) if agent_name == name else (60, 60, 60)
        draw_button(name, rect, color, (110, 110, 110), rect.collidepoint(mouse))
        buttons[f"algo_{name}"] = rect
    panel_y += 96

    screen.blit(font.render("Tamanho do tabuleiro", True, (180, 180, 255)), (panel_x, panel_y))
    panel_y += 28
    size_x = panel_x
    for size in BOARD_SIZES:
        rect = pygame.Rect(size_x, panel_y, 56, 36)
        color = (10, 120, 90) if GRID_SIZE == size else (60, 60, 60)
        draw_button(str(size), rect, color, (110, 110, 110), rect.collidepoint(mouse))
        buttons[f"size_{size}"] = rect
        size_x += 64
    panel_y += 50

    screen.blit(font.render("Velocidade", True, (180, 180, 255)), (panel_x, panel_y))
    panel_y += 28
    vel_down = pygame.Rect(panel_x, panel_y, 120, 36)
    vel_up = pygame.Rect(panel_x + 136, panel_y, 120, 36)
    draw_button("Vel -", vel_down, (60, 60, 60), (110, 110, 110), vel_down.collidepoint(mouse))
    draw_button("Vel +", vel_up, (60, 60, 60), (110, 110, 110), vel_up.collidepoint(mouse))
    buttons["speed_down"] = vel_down
    buttons["speed_up"] = vel_up
    panel_y += 54

    grow_rect = pygame.Rect(panel_x, panel_y, 256, 42)
    draw_button(f"Crescimento: {'ON' if grow_enabled else 'OFF'}", grow_rect,
                (0, 120, 0) if grow_enabled else (120, 0, 0),
                (110, 110, 110), grow_rect.collidepoint(mouse))
    buttons["grow"] = grow_rect
    panel_y += 52

    pygame.display.flip()
    return buttons


# ===== LOOP =====

reset_game()

running = True
buttons = draw()

while running:
    clock.tick(game_speed)
    buttons = draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            if buttons.get("play") and buttons["play"].collidepoint(pos):
                if game_state == "GAME_OVER":
                    reset_game()
                elif game_state == "PLAYING":
                    game_state = "PAUSED"
                else:
                    game_state = "PLAYING"

            elif buttons.get("reset") and buttons["reset"].collidepoint(pos):
                reset_game()

            for name in ALGORITHM_OPTIONS:
                key = f"algo_{name}"
                if buttons.get(key) and buttons[key].collidepoint(pos):
                    set_agent(name)

            for size in BOARD_SIZES:
                key = f"size_{size}"
                if buttons.get(key) and buttons[key].collidepoint(pos):
                    set_grid_size(size)

            if buttons.get("speed_down") and buttons["speed_down"].collidepoint(pos):
                game_speed = max(1, game_speed - 2)

            if buttons.get("speed_up") and buttons["speed_up"].collidepoint(pos):
                game_speed = min(30, game_speed + 2)

            if buttons.get("grow") and buttons["grow"].collidepoint(pos):
                grow_enabled = not grow_enabled

    if game_state == "PLAYING" and agent and snake and food and board:
        move = agent.get_move()

        if move:
            hx, hy = snake.body[0]
            nx, ny = move
            if not board.in_bounds((nx, ny)) or (nx, ny) in snake.body or (nx, ny) in board.obstacles:
                game_state = "GAME_OVER"
            else:
                will_eat = (nx, ny) == food.position
                snake.set_direction((nx - hx, ny - hy))
                snake.move(grow=will_eat and grow_enabled)
                total_steps_since_start += 1
                if will_eat:
                    score += 1
                    food.spawn(snake.body, board.obstacles)
                if not grow_enabled and total_steps_since_start % 30 == 0:
                    spawn_obstacle()
        else:
            game_state = "GAME_OVER"

pygame.quit()
sys.exit()