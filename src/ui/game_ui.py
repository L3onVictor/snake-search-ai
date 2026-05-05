import pygame
import sys
import random

from src.core import Board, Snake, Food
from src.algorithms.greedy import GreedySearch
from src.algorithms.greedy_path import GreedyPathSearch
from src.algorithms.a_star import AStarSearch

# CONFIG
BOARD_WIDTH = 600
HEIGHT = 600
SIDEBAR_WIDTH = 250
WIDTH = BOARD_WIDTH + SIDEBAR_WIDTH

GRID_SIZE = 15
CELL_SIZE = BOARD_WIDTH // GRID_SIZE

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake AI")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
title_font = pygame.font.SysFont(None, 32)

def reset_game():
    global board, snake, food, agent, agent_name, steps_taken, score, game_state, total_steps_since_start
    board = Board(GRID_SIZE, GRID_SIZE)
    snake = Snake((GRID_SIZE // 2, GRID_SIZE // 2))
    food = Food(GRID_SIZE, GRID_SIZE)
    food.spawn(snake.body, board.obstacles)
    
    agent = AStarSearch(board, snake, food) if agent_name == "A*" else GreedyPathSearch(board, snake, food)
    steps_taken = 0
    score = 0
    total_steps_since_start = 0
    game_state = "PLAYING"

def set_grid_size(size):
    global GRID_SIZE, CELL_SIZE
    GRID_SIZE = size
    CELL_SIZE = BOARD_WIDTH // GRID_SIZE
    reset_game()

agent_name = "A*"
game_speed = 10
game_state = "MENU" # MENU, PLAYING, PAUSED, GAME_OVER
steps_taken = 0
score = 0
total_steps_since_start = 0
board = None
snake = None
food = None
agent = None
grow_enabled = True

reset_game()
game_state = "MENU"

def spawn_obstacle():
    free_cells = [
        (x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)
        if (x, y) not in snake.body 
        and (x, y) != food.position
        and (x, y) not in board.obstacles
    ]
    if free_cells:
        obs = random.choice(free_cells)
        board.obstacles.add(obs)

def draw_button(text, rect, color, hover_color, is_hover):
    pygame.draw.rect(screen, hover_color if is_hover else color, rect)
    pygame.draw.rect(screen, (255, 255, 255), rect, 2) # border
    txt_surf = font.render(text, True, (255, 255, 255))
    txt_rect = txt_surf.get_rect(center=rect.center)
    screen.blit(txt_surf, txt_rect)

def draw():
    screen.fill((0, 0, 0))

    # Desenhar grid (Opcional, mas ajuda a ver)
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, (30, 30, 30), rect, 1)

    # Desenhar cobra
    for i, (x, y) in enumerate(snake.body):
        color = (0, 255, 0) if i == 0 else (0, 180, 0)
        pygame.draw.rect(screen, color, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Desenhar comida
    fx, fy = food.position
    pygame.draw.rect(screen, (255, 0, 0), (fx*CELL_SIZE, fy*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Desenhar caminho planejado (AGORA POR CIMA DA COBRA)
    if hasattr(agent, 'current_path') and agent.current_path:
        points = []
        for p in agent.current_path:
            points.append((p[0] * CELL_SIZE + CELL_SIZE // 2, p[1] * CELL_SIZE + CELL_SIZE // 2))
        if len(points) > 1:
            pygame.draw.lines(screen, (100, 100, 255), False, points, 3)
            # Desenhar um pequeno círculo na ponta do caminho para destacar onde termina
            pygame.draw.circle(screen, (150, 150, 255), points[-1], 5)

    # Desenhar obstáculos
    for ox, oy in board.obstacles:
        pygame.draw.rect(screen, (128, 128, 128), (ox*CELL_SIZE, oy*CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Desenhar Divisória
    pygame.draw.line(screen, (255, 255, 255), (BOARD_WIDTH, 0), (BOARD_WIDTH, HEIGHT), 2)

    # Desenhar Painel Lateral
    panel_x = BOARD_WIDTH + 10
    
    # Textos
    title = title_font.render("Snake Search AI", True, (255, 255, 255))
    screen.blit(title, (panel_x, 20))
    
    screen.blit(font.render(f"Status: {game_state}", True, (200, 200, 200)), (panel_x, 70))
    screen.blit(font.render(f"Score (Tam): {score}", True, (200, 200, 200)), (panel_x, 100))
    screen.blit(font.render(f"Passos Totais: {total_steps_since_start}", True, (200, 200, 200)), (panel_x, 130))
    screen.blit(font.render(f"Velocidade: {game_speed} FPS", True, (200, 200, 200)), (panel_x, 160))
    screen.blit(font.render(f"Algoritmo: {agent_name}", True, (200, 200, 200)), (panel_x, 190))

    # Definir botões (retornaremos eles para verificação de clique no loop principal)
    buttons = {}
    
    mouse_pos = pygame.mouse.get_pos()

    # Botão Play/Pause/Restart
    play_rect = pygame.Rect(panel_x, 240, 220, 40)
    btn_text = "Iniciar / Pausar"
    if game_state == "GAME_OVER":
        btn_text = "Reiniciar"
    elif game_state == "MENU":
        btn_text = "Iniciar"
    draw_button(btn_text, play_rect, (50, 50, 50), (80, 80, 80), play_rect.collidepoint(mouse_pos))
    buttons["play"] = play_rect

    # Botões Algoritmo
    alg_a_rect = pygame.Rect(panel_x, 300, 105, 40)
    alg_g_rect = pygame.Rect(panel_x + 115, 300, 105, 40)
    draw_button("A*", alg_a_rect, (0, 100, 0) if agent_name == "A*" else (50, 50, 50), (80, 80, 80), alg_a_rect.collidepoint(mouse_pos))
    draw_button("Greedy", alg_g_rect, (0, 100, 0) if agent_name == "Greedy" else (50, 50, 50), (80, 80, 80), alg_g_rect.collidepoint(mouse_pos))
    buttons["alg_a"] = alg_a_rect
    buttons["alg_g"] = alg_g_rect

    # Botões Velocidade
    spd_down_rect = pygame.Rect(panel_x, 360, 105, 40)
    spd_up_rect = pygame.Rect(panel_x + 115, 360, 105, 40)
    draw_button("Vel -", spd_down_rect, (50, 50, 50), (80, 80, 80), spd_down_rect.collidepoint(mouse_pos))
    draw_button("Vel +", spd_up_rect, (50, 50, 50), (80, 80, 80), spd_up_rect.collidepoint(mouse_pos))
    buttons["spd_down"] = spd_down_rect
    buttons["spd_up"] = spd_up_rect

    # Botões Tamanho do Tabuleiro
    screen.blit(font.render("Tamanho:", True, (200, 200, 200)), (panel_x, 420))
    size_10_rect = pygame.Rect(panel_x, 450, 70, 40)
    size_15_rect = pygame.Rect(panel_x + 75, 450, 70, 40)
    size_20_rect = pygame.Rect(panel_x + 150, 450, 70, 40)
    draw_button("10", size_10_rect, (0, 100, 0) if GRID_SIZE == 10 else (50, 50, 50), (80, 80, 80), size_10_rect.collidepoint(mouse_pos))
    draw_button("15", size_15_rect, (0, 100, 0) if GRID_SIZE == 15 else (50, 50, 50), (80, 80, 80), size_15_rect.collidepoint(mouse_pos))
    draw_button("20", size_20_rect, (0, 100, 0) if GRID_SIZE == 20 else (50, 50, 50), (80, 80, 80), size_20_rect.collidepoint(mouse_pos))
    buttons["size_10"] = size_10_rect
    buttons["size_15"] = size_15_rect
    buttons["size_20"] = size_20_rect

    # Botão Crescimento
    grow_rect = pygame.Rect(panel_x, 510, 220, 40)
    draw_button(f"Crescimento: {'ON' if grow_enabled else 'OFF'}", grow_rect, (0, 100, 0) if grow_enabled else (100, 0, 0), (80, 80, 80), grow_rect.collidepoint(mouse_pos))
    buttons["grow_toggle"] = grow_rect

    pygame.display.flip()
    return buttons

running = True
buttons = {}

while running:
    clock.tick(game_speed)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if "play" in buttons and buttons["play"].collidepoint(pos):
                if game_state == "MENU" or game_state == "PAUSED":
                    game_state = "PLAYING"
                elif game_state == "PLAYING":
                    game_state = "PAUSED"
                elif game_state == "GAME_OVER":
                    reset_game()
            
            elif "alg_a" in buttons and buttons["alg_a"].collidepoint(pos):
                agent_name = "A*"
                agent = AStarSearch(board, snake, food)
            elif "alg_g" in buttons and buttons["alg_g"].collidepoint(pos):
                agent_name = "Greedy"
                agent = GreedySearch(board, snake, food)
                
            elif "spd_down" in buttons and buttons["spd_down"].collidepoint(pos):
                game_speed = max(1, game_speed - 2)
            elif "spd_up" in buttons and buttons["spd_up"].collidepoint(pos):
                game_speed = min(30, game_speed + 2)

            elif "size_10" in buttons and buttons["size_10"].collidepoint(pos):
                set_grid_size(10)
            elif "size_15" in buttons and buttons["size_15"].collidepoint(pos):
                set_grid_size(15)
            elif "size_20" in buttons and buttons["size_20"].collidepoint(pos):
                set_grid_size(20)

            elif "grow_toggle" in buttons and buttons["grow_toggle"].collidepoint(pos):
                grow_enabled = not grow_enabled

    if game_state == "PLAYING":
        move = agent.get_move()
        
        if move is not None:
            hx, hy = snake.body[0]
            nx, ny = move

            # colisões
            if not board.in_bounds((nx, ny)) or (nx, ny) in snake.body or (nx, ny) in board.obstacles:
                game_state = "GAME_OVER"
            else:
                will_eat = (nx, ny) == food.position

                snake.set_direction((nx - hx, ny - hy))
                snake.move(grow=will_eat and grow_enabled)
                total_steps_since_start += 1
                
                # Obstáculos apenas se o crescimento não estiver ativado
                if not grow_enabled and total_steps_since_start > 0 and total_steps_since_start % 25 == 0:
                    spawn_obstacle()

                if will_eat:
                    score += 1
                    food.spawn(snake.body, board.obstacles)
                    # Atualizar o objeto food no agente
                    agent.food = food
        else:
            game_state = "GAME_OVER"

    buttons = draw()

pygame.quit()
sys.exit()