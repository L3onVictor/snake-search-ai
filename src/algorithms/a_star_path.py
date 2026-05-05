from heapq import heappush, heappop
from collections import deque
from src.utils.manhattan_distance import manhattan_distance


class AStarSmartSearch:
    """
    A* modificado com detecção de regiões fechadas.

    Lógica (fiel ao artigo):
    1. Calcula o menor caminho até a comida via A*.
    2. Antes de confirmar o próximo passo, verifica se ele cria
       uma região fechada no tabuleiro (flood fill < limiar).
    3. Se o passo cria região fechada mas existe alternativa que não cria,
       usa a alternativa.
    4. Se não há caminho até a comida (ou todos criam região fechada),
       busca o menor caminho até a cauda da cobra.
    5. Se nada funcionar, vai para o vizinho com mais espaço livre.
    """

    def __init__(self, board, snake, food):
        self.board = board
        self.snake = snake
        self.food = food
        self.current_path = []

    # ------------------------------------------------------------------
    # A* puro
    # ------------------------------------------------------------------
    def _astar(self, start, goal, body_set):
        """Retorna lista de posições [start, ..., goal] ou None."""
        open_set = []
        heappush(open_set, (0, start))
        came_from = {}
        g = {start: 0}

        while open_set:
            _, current = heappop(open_set)

            if current == goal:
                return self._reconstruct(came_from, current)

            for nb in self.board.get_neighbors(current):
                if nb in body_set:
                    continue
                tg = g[current] + 1
                if nb not in g or tg < g[nb]:
                    came_from[nb] = current
                    g[nb] = tg
                    heappush(open_set, (tg + manhattan_distance(nb, goal), nb))

        return None

    def _reconstruct(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
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
                if nb not in visited and nb not in body_set:
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
            body.pop()          # não cresceu
        return body

    # ------------------------------------------------------------------
    # Verifica se um movimento cria região fechada
    # Critério simples: espaço livre após o movimento < tamanho da cobra
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

        # --- 1. Caminho A* até a comida ---
        path_to_food = self._astar(head, self.food.position, body_set)

        if path_to_food and len(path_to_food) > 1:
            next_step = path_to_food[1]

            # --- 2. Esse passo cria região fechada? ---
            if not self._creates_closed_region(next_step):
                # Caminho limpo — segue direto
                self.current_path = path_to_food
                return next_step

            # Passo cria região fechada: procura alternativa entre os vizinhos válidos
            alternatives = [n for n in valid
                            if n != next_step and not self._creates_closed_region(n)]

            if alternatives:
                # Escolhe a alternativa com mais espaço livre
                best = max(alternatives,
                           key=lambda n: self._flood_fill(n, set(self._simulate(n))))
                self.current_path = [head, best]
                return best

            # Nenhuma alternativa evita região fechada: segue o caminho A* mesmo assim
            self.current_path = path_to_food
            return next_step

        # --- 3. Sem caminho até a comida → tenta chegar à cauda ---
        tail = list(self.snake.body)[-1]
        path_to_tail = self._astar(head, tail, body_set)

        if path_to_tail and len(path_to_tail) > 1:
            next_step = path_to_tail[1]
            self.current_path = path_to_tail
            return next_step

        # --- 4. Fallback: vizinho com mais espaço livre ---
        best = max(valid,
                   key=lambda n: self._flood_fill(n, set(self._simulate(n))))
        self.current_path = [head, best]
        return best