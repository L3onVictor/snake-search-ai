from src.utils.manhattan_distance import manhattan_distance


class GreedySearch:
    """
    Busca Gulosa pura para o Snake.
    """

    def __init__(self, board, snake, food):
        self.board = board
        self.snake = snake
        self.food = food

    def _free_neighbors(self, pos, body_set):
        return sum(
            1 for n in self.board.get_neighbors(pos)
            if n not in body_set and n not in self.board.obstacles
        )

    def _mobility(self, pos, body_set):
        score = 0
        for n in self.board.get_neighbors(pos):
            if n in body_set or n in self.board.obstacles:
                continue
            score += self._free_neighbors(n, body_set)
        return score

    def get_move(self):
        head = self.snake.body[0]
        body_set = set(self.snake.body)

        neighbors = self.board.get_neighbors(head)

        valid = [
            n for n in neighbors
            if n not in body_set and n not in self.board.obstacles
        ]

        if not valid:
            return None

        best = min(
            valid,
            key=lambda pos: (
                manhattan_distance(pos, self.food.position),
                -self._mobility(pos, body_set)
            )
        )

        return best