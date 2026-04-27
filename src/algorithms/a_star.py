from heapq import heappush, heappop
from src.utils.manhattan_distance import manhattan_distance

class AStarSearch:

    def __init__(self, board, snake, food):
        self.board = board
        self.snake = snake
        self.food = food

    def find_path(self):
        start = self.snake.body[0]
        goal = self.food.position

        open_set = []
        heappush(open_set, (0, start))

        came_from = {}
        g_score = {start: 0}

        while open_set:
            _, current = heappop(open_set)

            if current == goal:
                return self.reconstruct_path(came_from, current)
           

            for neighbor in self.board.get_neighbors(current):

                if neighbor in self.snake.body:
                    continue

                tentative_g = g_score[current] + 1

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g

                    f_score = tentative_g + manhattan_distance(neighbor, goal)
                    heappush(open_set, (f_score, neighbor))

        return None
    
    def reconstruct_path(self, came_from, current):
        total_path = [current]

        while current in came_from:
            current = came_from[current]
            total_path.append(current)
            
        total_path.reverse()
        return total_path

    def get_move(self):
        path = self.find_path()

        if path and len(path) > 1:
            return path[1]
        else:
            return None