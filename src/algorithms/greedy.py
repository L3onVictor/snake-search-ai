from src.utils.manhattan_distance import manhattan_distance


class GreedySearch:
    """
    Busca Gulosa pura para o Snake.

    Melhorias em relação à versão original:
    - Ignora obstáculos do tabuleiro além do corpo.
    - Fallback vai para o vizinho com mais vizinhos livres (evita becos),
      em vez de escolher aleatoriamente.
    """

    def __init__(self, board, snake, food):
        self.board = board
        self.snake = snake
        self.food = food

    def _free_neighbors(self, pos):
        body_set = set(self.snake.body)
        return sum(1 for nb in self.board.get_neighbors(pos)
                   if nb not in body_set and nb not in self.board.obstacles)

    def get_move(self):
        head = self.snake.body[0]
        body_set = set(self.snake.body)

        neighbors = self.board.get_neighbors(head)
        valid = [n for n in neighbors
                 if n not in body_set and n not in self.board.obstacles]

        if not valid:
            return None

        # Escolhe o vizinho mais próximo da comida
        best = min(valid, key=lambda pos: manhattan_distance(pos, self.food.position))
        return best