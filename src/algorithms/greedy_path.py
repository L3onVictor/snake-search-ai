from collections import deque
from src.utils.manhattan_distance import manhattan_distance


class GreedySmartSearch:

    def __init__(self, board, snake, food):
        self.board = board
        self.snake = snake
        self.food = food
        self.current_path = []


    def _greedy_path(self, start, goal, body_set):
        path = [start]
        visited = set(body_set) | {start}
        current = start

        while current != goal:
            neighbors = self.board.get_neighbors(current)
            candidates = [
                n for n in neighbors
                if n not in visited and n not in self.board.obstacles
            ]

            if not candidates:
                return None

            best = min(candidates, key=lambda n: manhattan_distance(n, goal))

            path.append(best)
            visited.add(best)
            current = best

            if len(path) > self.board.width * self.board.height:
                return None

        return path

    # ------------------------------------------------------------------
    # Flood fill (espaço acessível)
    # ------------------------------------------------------------------
    def _flood_fill(self, start, body_set):
        visited = {start}
        queue = deque([start])

        while queue:
            pos = queue.popleft()
            for nb in self.board.get_neighbors(pos):
                if (
                    nb not in visited and
                    nb not in body_set and
                    nb not in self.board.obstacles
                ):
                    visited.add(nb)
                    queue.append(nb)

        return len(visited)

    # ------------------------------------------------------------------
    # Simula movimento da cobra
    # ------------------------------------------------------------------
    def _simulate(self, move):
        body = list(self.snake.body)
        body.insert(0, move)

        if move != self.food.position:
            body.pop()

        return body

    # ------------------------------------------------------------------
    # Decisão principal
    # ------------------------------------------------------------------
    def get_move(self):
        head = self.snake.body[0]
        body_set = set(self.snake.body)

        neighbors = self.board.get_neighbors(head)

        valid = [
            n for n in neighbors
            if n not in body_set and n not in self.board.obstacles
        ]

        if not valid:
            self.current_path = []
            return None

        # --- 1. tenta caminho guloso até comida ---
        path_to_food = self._greedy_path(
            head,
            self.food.position,
            body_set
        )

        if path_to_food and len(path_to_food) > 1:
            next_step = path_to_food[1]

            best = min(
                valid,
                key=lambda n: (
                    manhattan_distance(n, self.food.position),
                    -self._flood_fill(n, set(self._simulate(n)))
                )
            )

            if next_step in valid:
                ff_next = self._flood_fill(next_step, set(self._simulate(next_step)))
                ff_best = self._flood_fill(best, set(self._simulate(best)))

                if ff_next >= ff_best:
                    self.current_path = path_to_food
                    return next_step

            self.current_path = path_to_food
            return best

        # --- 2. sem caminho pra comida → tenta cauda ---
        tail = self.snake.body[-1]

        path_to_tail = self._greedy_path(head, tail, body_set)

        if path_to_tail and len(path_to_tail) > 1:
            next_step = path_to_tail[1]
            self.current_path = path_to_tail
            return next_step

        # --- 3. fallback seguro ---
        best = max(
            valid,
            key=lambda n: self._flood_fill(n, set(self._simulate(n)))
        )

        self.current_path = [head, best]
        return best