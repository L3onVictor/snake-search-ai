import random
import time
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import Counter

# Imports do projeto
from src.core.board import Board
from src.core.snake import Snake
from src.core.food import Food

from src.algorithms.a_star import AStarSearch
from src.algorithms.a_star_path import AStarSmartSearch
from src.algorithms.greedy import GreedySearch
from src.algorithms.greedy_path import GreedySmartSearch

# Configurações do Benchmark
BOARD_SIZE = 20
N_GAMES = 100  # Reduzido para 100 conforme sugestão do usuário (8 configs x 100 = 800 partidas)
MAX_STEPS = 2000
OBSTACLE_INTERVAL = 25
SEED = 42

ALGORITHMS = {
    "A* Puro": AStarSearch,
    "A* Smart": AStarSmartSearch,
    "Greedy Puro": GreedySearch,
    "Greedy Smart": GreedySmartSearch,
}

MODES = [True, False]  # True = Crescimento, False = Obstáculos

def run_simulation(AlgoClass, grow_mode, seed):
    random.seed(seed)
    board = Board(BOARD_SIZE, BOARD_SIZE)
    start_pos = (BOARD_SIZE // 2, BOARD_SIZE // 2)
    snake = Snake(start_pos)
    food = Food(BOARD_SIZE, BOARD_SIZE)
    food.spawn(snake.body, board.obstacles)
    
    # Inicializa o agente
    agent = AlgoClass(board, snake, food)
    
    score = 0
    steps = 0
    decision_times = []
    reason = "Success" # Default
    
    while steps < MAX_STEPS:
        # Medir tempo de decisão
        start_time = time.perf_counter()
        move = agent.get_move()
        end_time = time.perf_counter()
        decision_times.append((end_time - start_time) * 1000) # ms
        
        if move is None:
            reason = "Trapped/No Path"
            break
            
        hx, hy = snake.body[0]
        nx, ny = move
        
        # Verificar colisões
        if not board.in_bounds((nx, ny)):
            reason = "Wall Collision"
            break
        if (nx, ny) in snake.body:
            reason = "Body Collision"
            break
        if (nx, ny) in board.obstacles:
            reason = "Obstacle Collision"
            break
            
        will_eat = (nx, ny) == food.position
        snake.set_direction((nx - hx, ny - hy))
        snake.move(grow=will_eat and grow_mode)
        steps += 1
        
        # Gerar obstáculos se não estiver crescendo
        if not grow_mode and steps % OBSTACLE_INTERVAL == 0:
            free_cells = [
                (x, y) for x in range(BOARD_SIZE) for y in range(BOARD_SIZE)
                if (x, y) not in snake.body and (x, y) != food.position and (x, y) not in board.obstacles
            ]
            if free_cells:
                board.obstacles.add(random.choice(free_cells))
        
        if will_eat:
            score += 1
            # spawn retorna None se houver sucesso, então precisamos checar se ele falhou
            # mas o spawn atual não retorna False explicitamente exceto se free_cells for vazio.
            # No entanto, a lógica 'if not food.spawn' disparava porque spawn() retorna None.
            if food.spawn(snake.body, board.obstacles) == False:
                reason = "Victory (Full Board)"
                break
            # Atualizar comida no agente
            agent.food = food
            
        if steps >= MAX_STEPS:
            reason = "Max Steps Reached"
            
    return {
        "score": score,
        "steps": steps,
        "avg_time": np.mean(decision_times) if decision_times else 0,
        "reason": reason,
        "steps_per_food": steps / score if score > 0 else steps
    }

def generate_charts(results):
    print("\nGerando gráficos...")
    
    # Estilo "Acadêmico"
    plt.rcParams.update({'font.size': 12, 'font.family': 'serif'})
    
    # 1. Boxplot de Pontuação (Crescimento vs Obstáculos)
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), sharey=True)
    for i, mode in enumerate(MODES):
        mode_label = "Crescimento" if mode else "Obstáculos"
        data = []
        labels = []
        for algo_name in ALGORITHMS:
            scores = [r["score"] for r in results[(algo_name, mode)]]
            data.append(scores)
            labels.append(algo_name)
        
        axes[i].boxplot(data, tick_labels=labels)
        axes[i].set_title(f"Pontuação: Modo {mode_label}")
        axes[i].set_ylabel("Comidas Coletadas")
        axes[i].grid(axis='y', linestyle='--', alpha=0.7)
        plt.setp(axes[i].get_xticklabels(), rotation=30, ha="right")

    plt.tight_layout()
    plt.savefig("benchmark_pontuacao.png", dpi=300)
    plt.close()

    # 2. Eficiência de Caminho (Passos por Comida)
    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(ALGORITHMS))
    width = 0.35
    
    grow_means = [np.mean([r["steps_per_food"] for r in results[(name, True)]]) for name in ALGORITHMS]
    obs_means = [np.mean([r["steps_per_food"] for r in results[(name, False)]]) for name in ALGORITHMS]
    
    ax.bar(x - width/2, grow_means, width, label='Modo Crescimento')
    ax.bar(x + width/2, obs_means, width, label='Modo Obstáculos')
    
    ax.set_ylabel('Passos por Comida (Menor é Melhor)')
    ax.set_title('Eficiência de Trajeto por Algoritmo')
    ax.set_xticks(x)
    ax.set_xticklabels(ALGORITHMS.keys())
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig("benchmark_eficiencia.png", dpi=300)
    plt.close()

    # 3. Tempo Computacional (ms por decisão)
    fig, ax = plt.subplots(figsize=(10, 6))
    times = [np.mean([r["avg_time"] for r in results[(name, True)] + results[(name, False)]]) for name in ALGORITHMS]
    
    bars = ax.bar(ALGORITHMS.keys(), times, color='skyblue', edgecolor='navy')
    ax.set_ylabel('Tempo de Decisão (ms)')
    ax.set_title('Complexidade Computacional Média')
    
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 0.01, f'{yval:.2f}ms', ha='center', va='bottom')

    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig("benchmark_tempo.png", dpi=300)
    plt.close()

    # 4. Causas de Morte (Crescimento)
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    axes = axes.flatten()
    for i, algo_name in enumerate(ALGORITHMS):
        reasons = [r["reason"] for r in results[(algo_name, True)]]
        counts = Counter(reasons)
        axes[i].pie(counts.values(), labels=counts.keys(), autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
        axes[i].set_title(f"Falhas: {algo_name} (Crescimento)")

    plt.tight_layout()
    plt.savefig("benchmark_falhas.png", dpi=300)
    plt.close()

    print("Gráficos salvos com sucesso!")

def main():
    print(f"Iniciando Benchmark: {BOARD_SIZE}x{BOARD_SIZE}, {N_GAMES} partidas por configuração.")
    results = {}
    
    start_total = time.time()
    
    for algo_name, AlgoClass in ALGORITHMS.items():
        for mode in MODES:
            mode_label = "Crescimento" if mode else "Obstáculos"
            print(f"Testando {algo_name} em modo {mode_label}...")
            config_results = []
            for i in range(N_GAMES):
                res = run_simulation(AlgoClass, mode, SEED + i)
                config_results.append(res)
            results[(algo_name, mode)] = config_results
            
            # Print summary for this config
            avg_score = np.mean([r["score"] for r in config_results])
            avg_steps = np.mean([r["steps"] for r in config_results])
            print(f"  -> Score Médio: {avg_score:.2f} | Passos Médios: {avg_steps:.2f}")
            
    end_total = time.time()
    print(f"\nTempo total de benchmark: {end_total - start_total:.2f} segundos.")
    
    generate_charts(results)

if __name__ == "__main__":
    main()
