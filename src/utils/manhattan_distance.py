def manhattan_distance(pos, food):
        fx, fy = food
        x, y = pos
        return abs(x - fx) + abs(y - fy)