from heapq import heappush, heappop
import manhattan_distance

class AStarSearch:

    def __init__(self, board, snake, food):
        self.board = board
        self.snake = snake
        self.food = food

    def find_path(self):
        start = self.snake.body[0]
        goal = self.food.position