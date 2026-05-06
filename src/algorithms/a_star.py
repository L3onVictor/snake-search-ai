from heapq import heappush, heappop
from src.utils.manhattan_distance import manhattan_distance


class AStarSearch:
    """
    A* puro para o Snake.
    """

    def __init__(self, board, snake, food):
        self.board = board
        self.snake = snake
        self.food = food
        self.current_path = []

    def find_path(self):
        start = self.snake.body[0]
        goal = self.food.position
        body_set = set(self.snake.body)

        open_set = []
        heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}

        while open_set:
            _, current = heappop(open_set)

            if current == goal:
                return self._reconstruct(came_from, current)

            for nb in self.board.get_neighbors(current):
                if nb in body_set or nb in self.board.obstacles:
                    continue

                tg = g_score[current] + 1
                if nb not in g_score or tg < g_score[nb]:
                    came_from[nb] = current
                    g_score[nb] = tg
                    heappush(open_set, (tg + manhattan_distance(nb, goal), nb))

        return None

    def _reconstruct(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def _free_neighbors(self, pos):
        body_set = set(self.snake.body)
        return sum(1 for nb in self.board.get_neighbors(pos)
                   if nb not in body_set and nb not in self.board.obstacles)

    def get_move(self):
        head = self.snake.body[0]
        body_set = set(self.snake.body)

        path = self.find_path()

        if path and len(path) > 1:
            self.current_path = path
            return path[1]

        # Fallback: vizinho com mais espaço livre
        neighbors = self.board.get_neighbors(head)
        valid = [n for n in neighbors
                 if n not in body_set and n not in self.board.obstacles]

        if valid:
            best = max(valid, key=self._free_neighbors)
            self.current_path = [head, best]
            return best

        self.current_path = []
        return None