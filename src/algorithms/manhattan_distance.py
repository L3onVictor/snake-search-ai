def manhattan_distance(self, pos):
        fx, fy = self.food.position
        x, y = pos
        return abs(x - fx) + abs(y - fy)