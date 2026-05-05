"""
benchmark.py — Snake AI Benchmark
Testa 4 algoritmos × 2 modos × N partidas e gera gráficos acadêmicos.
"""

import sys, os, random, time, copy
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from collections import deque

sys.path.insert(0, os.path.dirname(__file__))

from src.core.board import Board
from src.core.food import Food
from src.core.snake import Snake

# ── Imports dos algoritmos com fallback de importação relativa ───────
from src.algorithms.a_star       import AStarSearch
from src.algorithms.a_star_path  import AStarSmartSearch
from src.algorithms.greedy       import GreedySearch
from src.algorithms.greedy_path  import GreedySmartSearch

# ── Configurações ────────────────────────────────────────────────────
BOARD_W   = 20
BOARD_H   = 20
N_GAMES   = 40
MAX_STEPS = 2_500   # teto de segurança por partida
OBSTACLE_INTERVAL = 25
SEED      = 99

ALGO_NAMES = ["A* Puro", "A* Smart", "Gulosa Pura", "Gulosa Smart"]
ALGO_CLS   = [AStarSearch, AStarSmartSearch, GreedySearch, GreedySmartSearch]
COLORS     = ["#2E86AB", "#E84855", "#3BB273", "#F4A259"]
# ────────────────────────────────────────────────────────────────────

def make_game(seed):
    random.seed(seed)
    board = Board(BOARD_W, BOARD_H)
    snake = Snake((BOARD_W // 2, BOARD_H // 2))
    food  = Food(BOARD_W, BOARD_H)
    food.spawn(snake.body, board.obstacles)
    return board, snake, food


def run_game(AlgoClass, seed, grow_mode: bool):
    """
    Roda uma partida completa.
    Retorna: (score, steps, steps_per_food, survived)
    """
    if SEED is not None:
        random.seed(seed)

    board = Board(BOARD_W, BOARD_H)
    snake = Snake((BOARD_W // 2, BOARD_H // 2))
    food  = Food(BOARD_W, BOARD_H)
    food.spawn(snake.body, board.obstacles)

    algo = AlgoClass(board, snake, food)

    score          = 0
    steps          = 0
    steps_per_food = []   # passo acumulado em que cada comida foi pega

    while steps < MAX_STEPS:
        # ── Pede movimento ao algoritmo ──────────────────────────────
        next_pos = algo.get_move()

        if next_pos is None:
            break   # sem saída → game over

        # ── Atualiza direção da cobra para o próximo passo ───────────
        head = snake.body[0]
        dx = next_pos[0] - head[0]
        dy = next_pos[1] - head[1]
        snake.set_direction((dx, dy))

        # ── Move a cobra ─────────────────────────────────────────────
        new_head = next_pos
        steps += 1

        # Colisão com paredes
        if not board.in_bounds(new_head):
            break

        # Colisão com obstáculos
        if new_head in board.obstacles:
            break

        # Colisão com corpo (exceto a cauda que sairá, a menos que cresça)
        body_except_tail = set(snake.body[:-1])
        if new_head in body_except_tail:
            break

        ate = (new_head == food.position)

        if grow_mode:
            snake.move(grow=ate)
        else:
            snake.move(grow=False)

        if ate:
            score += 1
            steps_per_food.append(steps)

            # Modo sem crescimento: obstáculo a cada 25 passos
            if not grow_mode and steps % OBSTACLE_INTERVAL == 0:
                occupied = set(snake.body) | board.obstacles | {food.position}
                free = [(x, y) for x in range(BOARD_W)
                        for y in range(BOARD_H) if (x, y) not in occupied]
                if free:
                    board.obstacles.add(random.choice(free))

            ok = food.spawn(snake.body, board.obstacles)
            if ok is False:
                # Tabuleiro cheio — vitória máxima
                break

        # Recria algoritmo com estado atualizado
        algo = AlgoClass(board, snake, food)

    return score, steps, steps_per_food


def run_benchmark(grow_mode: bool):
    label = "CRESCIMENTO" if grow_mode else "SEM CRESCIMENTO (obstáculos)"
    print(f"\n{'='*55}")
    print(f"  Modo: {label}")
    print(f"{'='*55}")

    results = {}
    for name, AlgoClass in zip(ALGO_NAMES, ALGO_CLS):
        print(f"\n[{name}]")
        games = []
        t0 = time.time()
        for i in range(N_GAMES):
            score, steps, spf = run_game(AlgoClass, SEED + i, grow_mode)
            games.append((score, steps, spf))
        elapsed = time.time() - t0
        scores = [g[0] for g in games]
        print(f"  Média={np.mean(scores):.1f}  Mediana={np.median(scores):.0f}"
              f"  Max={max(scores)}  Min={min(scores)}  Tempo={elapsed:.1f}s")
        results[name] = games

    return results


# ── Gráficos ─────────────────────────────────────────────────────────

def savefig(fig, name):
    # salva na pasta do projeto
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(base_dir, "outputs")

    os.makedirs(out_dir, exist_ok=True)  # cria pasta se não existir

    path = os.path.join(out_dir, name)

    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return path


def fig_score_boxplot(results_grow, results_nongrow, out_paths):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, results, title in [
        (axes[0], results_grow,    "Modo Crescimento"),
        (axes[1], results_nongrow, "Modo Sem Crescimento"),
    ]:
        data   = [[g[0] for g in v] for v in results.values()]
        bp = ax.boxplot(data, labels=ALGO_NAMES, patch_artist=True,
                        medianprops=dict(color="black", linewidth=2),
                        whiskerprops=dict(linewidth=1.5),
                        capprops=dict(linewidth=1.5))
        for patch, color in zip(bp["boxes"], COLORS):
            patch.set_facecolor(color); patch.set_alpha(0.75)
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.set_ylabel("Comidas coletadas (score)")
        ax.set_xlabel("Algoritmo")
        ax.tick_params(axis='x', labelsize=9)
        ax.grid(axis="y", linestyle="--", alpha=0.45)

    fig.suptitle(f"Distribuição de Pontuação — {N_GAMES} partidas, tabuleiro {BOARD_W}×{BOARD_H}",
                 fontsize=14, y=1.02)
    p = savefig(fig, "fig1_scores.png")
    out_paths.append(p)


def fig_efficiency(results_grow, results_nongrow, out_paths):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, results, title in [
        (axes[0], results_grow,    "Modo Crescimento"),
        (axes[1], results_nongrow, "Modo Sem Crescimento"),
    ]:
        means = [np.mean([g[0] for g in v]) for v in results.values()]
        stds  = [np.std([g[0]  for g in v]) for v in results.values()]
        bars  = ax.bar(ALGO_NAMES, means, yerr=stds, capsize=6,
                       color=COLORS, alpha=0.82, edgecolor="white", linewidth=1.2)
        for bar, m, s in zip(bars, means, stds):
            ax.text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + s + 0.4,
                    f"{m:.1f}", ha="center", va="bottom", fontsize=10, fontweight="bold")
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.set_ylabel("Score médio (±std)")
        ax.tick_params(axis='x', labelsize=9)
        ax.grid(axis="y", linestyle="--", alpha=0.45)

    fig.suptitle("Score Médio por Algoritmo", fontsize=14, y=1.02)
    p = savefig(fig, "fig2_efficiency.png")
    out_paths.append(p)


def fig_steps_per_food(results_grow, results_nongrow, out_paths):
    """Passos médios por comida (eficiência de rota)."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, results, title in [
        (axes[0], results_grow,    "Modo Crescimento"),
        (axes[1], results_nongrow, "Modo Sem Crescimento"),
    ]:
        eff = []
        errs = []
        for v in results.values():
            ratios = [g[1]/g[0] if g[0] > 0 else MAX_STEPS for g in v]
            eff.append(np.mean(ratios))
            errs.append(np.std(ratios))
        bars = ax.bar(ALGO_NAMES, eff, yerr=errs, capsize=6,
                      color=COLORS, alpha=0.82, edgecolor="white", linewidth=1.2)
        for bar, e in zip(bars, eff):
            ax.text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + 0.5,
                    f"{e:.1f}", ha="center", va="bottom", fontsize=10, fontweight="bold")
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.set_ylabel("Passos / comida  (menor = melhor)")
        ax.tick_params(axis='x', labelsize=9)
        ax.grid(axis="y", linestyle="--", alpha=0.45)

    fig.suptitle("Eficiência de Rota — Passos Médios por Comida", fontsize=14, y=1.02)
    p = savefig(fig, "fig3_steps_per_food.png")
    out_paths.append(p)


def fig_progress_curve(results_grow, results_nongrow, out_paths):
    """Curva de progresso: passo médio em que cada comida é coletada."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for ax, results, title in [
        (axes[0], results_grow,    "Modo Crescimento"),
        (axes[1], results_nongrow, "Modo Sem Crescimento"),
    ]:
        for (name, games), color in zip(results.items(), COLORS):
            max_food = max((len(g[2]) for g in games), default=1)
            if max_food == 0:
                continue
            matrix = np.full((len(games), max_food), np.nan)
            for i, (_, _, spf) in enumerate(games):
                for j, s in enumerate(spf):
                    matrix[i, j] = s

            mean_s = np.nanmean(matrix, axis=0)
            p25    = np.nanpercentile(matrix, 25, axis=0)
            p75    = np.nanpercentile(matrix, 75, axis=0)
            x = np.arange(1, len(mean_s)+1)
            ax.plot(x, mean_s, label=name, color=color, linewidth=2.2)
            ax.fill_between(x, p25, p75, alpha=0.15, color=color)

        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.set_xlabel("Nº da comida coletada")
        ax.set_ylabel("Passo médio acumulado")
        ax.legend(fontsize=9)
        ax.grid(linestyle="--", alpha=0.4)

    fig.suptitle("Curva de Progresso — Passo Médio por Comida", fontsize=14, y=1.02)
    p = savefig(fig, "fig4_progress.png")
    out_paths.append(p)


def fig_survival(results_grow, results_nongrow, out_paths):
    """Distribuição de passos totais por partida."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, results, title in [
        (axes[0], results_grow,    "Modo Crescimento"),
        (axes[1], results_nongrow, "Modo Sem Crescimento"),
    ]:
        data   = [[g[1] for g in v] for v in results.values()]
        bp = ax.boxplot(data, labels=ALGO_NAMES, patch_artist=True,
                        medianprops=dict(color="black", linewidth=2),
                        whiskerprops=dict(linewidth=1.5),
                        capprops=dict(linewidth=1.5))
        for patch, color in zip(bp["boxes"], COLORS):
            patch.set_facecolor(color); patch.set_alpha(0.75)
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.set_ylabel("Passos totais por partida")
        ax.set_xlabel("Algoritmo")
        ax.tick_params(axis='x', labelsize=9)
        ax.grid(axis="y", linestyle="--", alpha=0.45)

    fig.suptitle("Distribuição de Longevidade por Partida", fontsize=14, y=1.02)
    p = savefig(fig, "fig5_survival.png")
    out_paths.append(p)


def fig_score_distribution(results_grow, results_nongrow, out_paths):
    """Histograma de scores — permite ver bimodalidade / concentração."""
    fig, axes = plt.subplots(2, 4, figsize=(16, 7), sharey=False)
    for row, (results, mode_label) in enumerate([
        (results_grow, "Crescimento"),
        (results_nongrow, "Sem Crescimento"),
    ]):
        for col, (name, games, color) in enumerate(
                zip(ALGO_NAMES, results.values(), COLORS)):
            ax = axes[row][col]
            scores = [g[0] for g in games]
            ax.hist(scores, bins=15, color=color, alpha=0.8, edgecolor="white")
            ax.axvline(np.mean(scores), color="black", linestyle="--",
                       linewidth=1.5, label=f"μ={np.mean(scores):.1f}")
            ax.set_title(f"{name}\n({mode_label})", fontsize=10, fontweight="bold")
            ax.set_xlabel("Score")
            ax.set_ylabel("Frequência" if col == 0 else "")
            ax.legend(fontsize=8)
            ax.grid(axis="y", linestyle="--", alpha=0.4)

    fig.suptitle(f"Histograma de Scores — {N_GAMES} partidas", fontsize=14)
    plt.tight_layout()
    p = savefig(fig, "fig6_histograms.png")
    out_paths.append(p)


def print_academic_table(results_grow, results_nongrow):
    """Tabela de resultados no formato acadêmico."""
    print("\n" + "="*75)
    print("  TABELA DE RESULTADOS — RESUMO ACADÊMICO")
    print("="*75)
    header = f"{'Algoritmo':<17} {'Modo':<16} {'Média':>7} {'Mediana':>8} "
    header += f"{'Std':>7} {'Min':>5} {'Max':>5} {'Efic.':>8}"
    print(header)
    print("-"*75)

    for results, mode in [(results_grow, "Crescimento"), (results_nongrow, "Sem cresc.")]:
        for name, games in results.items():
            scores = [g[0] for g in games]
            spf    = [g[1]/g[0] if g[0]>0 else MAX_STEPS for g in games]
            print(f"  {name:<15} {mode:<16} "
                  f"{np.mean(scores):>7.2f} "
                  f"{np.median(scores):>8.1f} "
                  f"{np.std(scores):>7.2f} "
                  f"{min(scores):>5} "
                  f"{max(scores):>5} "
                  f"{np.mean(spf):>8.1f}")
        print("-"*75)

    print("\n  Efic. = passos médios por comida (menor é melhor)\n")


# ── Main ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\nSnake AI Benchmark")
    print(f"Tabuleiro: {BOARD_W}×{BOARD_H}  |  Partidas: {N_GAMES}  |  Seed: {SEED}")

    results_grow    = run_benchmark(grow_mode=True)
    results_nongrow = run_benchmark(grow_mode=False)

    print_academic_table(results_grow, results_nongrow)

    out_paths = []
    print("\nGerando gráficos...")
    fig_score_boxplot(results_grow, results_nongrow, out_paths)
    fig_efficiency(results_grow, results_nongrow, out_paths)
    fig_steps_per_food(results_grow, results_nongrow, out_paths)
    fig_progress_curve(results_grow, results_nongrow, out_paths)
    fig_survival(results_grow, results_nongrow, out_paths)
    fig_score_distribution(results_grow, results_nongrow, out_paths)

    for p in out_paths:
        print(f"  ✓ {p}")

    print("\nBenchmark concluído.\n")