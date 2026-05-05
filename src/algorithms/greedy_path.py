from collections import deque
from src.utils.manhattan_distance import manhattan_distance


class GreedySmartSearch:
    """
    Busca Gulosa modificada com detecção de regiões fechadas.

    Lógica (espelho do AStarSmartSearch, mas usando busca gulosa):
    1. Calcula o menor caminho até a comida via busca gulosa
       (sempre avança para o vizinho mais próximo da meta).
    2. Antes de confirmar o próximo passo, verifica se ele cria
       uma região fechada (flood fill < tamanho da cobra).
    3. Se cria região fechada mas há alternativa, usa a alternativa.
    4. Se não há caminho até a comida, busca caminho guloso até a cauda.
    5. Fallback: vizinho com mais espaço livre.
    """

    def __init__(self, board, snake, food):
        self.board = board
        self.snake = snake
        self.food = food
        self.current_path = []

    # ------------------------------------------------------------------
    # Busca gulosa pura: avança sempre para o vizinho mais próximo da meta
    # Não garante caminho ótimo, mas é leve e suficiente para o Snake.
    # ------------------------------------------------------------------
    def _greedy_path(self, start, goal, body_set):
        """Retorna lista de posições [start, ..., goal] ou None."""
        path = [start]
        visited = set(body_set) | {start}
        current = start

        while current != goal:
            neighbors = self.board.get_neighbors(current)
            candidates = [n for n in neighbors
                          if n not in visited and n not in self.board.obstacles]

            if not candidates:
                return None

            best = min(candidates, key=lambda n: manhattan_distance(n, goal))
            path.append(best)
            visited.add(best)
            current = best

            if len(path) > self.board.width * self.board.height:
                return None  # loop guard

        return path

    # ------------------------------------------------------------------
    # Flood fill — conta células acessíveis a partir de 'start'
    # ------------------------------------------------------------------
    def _flood_fill(self, start, body_set):
        visited = {start}
        queue = deque([start])
        while queue:
            pos = queue.popleft()
            for nb in self.board.get_neighbors(pos):
                if nb not in visited and nb not in body_set and nb not in self.board.obstacles:
                    visited.add(nb)
                    queue.append(nb)
        return len(visited)

    # ------------------------------------------------------------------
    # Simula o corpo da cobra após um passo
    # ------------------------------------------------------------------
    def _simulate(self, move):
        body = list(self.snake.body)
        body.insert(0, move)
        if move != self.food.position:
            body.pop()
        return body

    # ------------------------------------------------------------------
    # Verifica se um movimento cria região fechada
    # ------------------------------------------------------------------
    def _creates_closed_region(self, move):
        sim_body = self._simulate(move)
        sim_set = set(sim_body)
        free = self._flood_fill(move, sim_set)
        return free < len(sim_body)

    # ------------------------------------------------------------------
    # Decisão principal
    # ------------------------------------------------------------------
    def get_move(self):
        head = self.snake.body[0]
        body_set = set(self.snake.body)

        neighbors = self.board.get_neighbors(head)
        valid = [n for n in neighbors
                 if n not in body_set and n not in self.board.obstacles]

        if not valid:
            self.current_path = []
            return None

        # --- 1. Caminho guloso até a comida ---
        path_to_food = self._greedy_path(head, self.food.position, body_set)

        if path_to_food and len(path_to_food) > 1:
            next_step = path_to_food[1]

            # --- 2. Esse passo cria região fechada? ---
            if not self._creates_closed_region(next_step):
                self.current_path = path_to_food
                return next_step

            # Procura alternativa entre os vizinhos válidos
            alternatives = [n for n in valid
                            if n != next_step and not self._creates_closed_region(n)]

            if alternatives:
                best = max(alternatives,
                           key=lambda n: self._flood_fill(n, set(self._simulate(n))))
                self.current_path = [head, best]
                return best

            # Nenhuma alternativa: segue o caminho guloso mesmo assim
            self.current_path = path_to_food
            return next_step

        # --- 3. Sem caminho até a comida → tenta chegar à cauda ---
        tail = list(self.snake.body)[-1]
        path_to_tail = self._greedy_path(head, tail, body_set)

        if path_to_tail and len(path_to_tail) > 1:
            next_step = path_to_tail[1]
            self.current_path = path_to_tail
            return next_step

        # --- 4. Fallback: vizinho com mais espaço livre ---
        best = max(valid,
                   key=lambda n: self._flood_fill(n, set(self._simulate(n))))
        self.current_path = [head, best]
        return best