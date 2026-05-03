# Name: Sumaiyah Rahman
# UNI: sr3986

import time
import math
from BaseAI import BaseAI


class IntelligentAgent(BaseAI):

    def getMove(self, grid):
        self.start_time = time.time()
        self.time_limit = 0.18

        best_move = None
        best_score = -math.inf

        moves = grid.getAvailableMoves()
        if not moves:
            return None

    
        moves = sorted(moves, key=lambda x: self.fast_evaluate(x[1]), reverse=True)

        for move, new_grid in moves:

            empty = len(new_grid.getAvailableCells())
            max_tile = new_grid.getMaxTile()

            
            if empty >= 10:
                depth = 3
            elif max_tile >= 512:
                depth = 4
            else:
                depth = 4

            score = self.minimize(new_grid, -math.inf, math.inf, depth)

            if score > best_score:
                best_score = score
                best_move = move

            if time.time() - self.start_time > self.time_limit:
                break

        return best_move
    
    def fast_evaluate(self, grid):
        empty = len(grid.getAvailableCells())
        max_tile = grid.getMaxTile()

        # bias toward corner 
        corner = self.corner_bonus(grid)
        smooth = self.smoothness(grid)

        return (
            empty * 30 +
            math.log2(max_tile) * 5 +
            corner * 2 +
            smooth * 1.5
        )

    
    # MAX NODE (PLAYER)
    def maximize(self, grid, alpha, beta, depth):

        if self.cutoff(depth):
            return self.evaluate(grid)

        moves = grid.getAvailableMoves()
        if not moves:
            return self.evaluate(grid)

        if time.time() - self.start_time > self.time_limit:
            return self.evaluate(grid)

        max_utility = float('-inf')

        
        moves = sorted(moves, key=lambda x: self.fast_evaluate(x[1]), reverse=True)

        for move, new_grid in moves:

            utility = self.minimize(new_grid, alpha, beta, depth - 1)

            max_utility = max(max_utility, utility)
            alpha = max(alpha, max_utility)

            if alpha >= beta:
                break

        return max_utility
   
    # MIN NODE (COMPUTER)
  
    def minimize(self, grid, alpha, beta, depth):

        if self.cutoff(depth):
            return self.evaluate(grid)

        cells = grid.getAvailableCells()

        if not cells:
            return self.evaluate(grid)

        if time.time() - self.start_time > self.time_limit:
            return self.evaluate(grid)

        total_utility = 0
        total_prob = 0

        cells = sorted(cells, key=lambda c: -(
            abs(c[0]-1.5) + abs(c[1]-1.5)
        ))
        for cell in cells[:4]:
            for value, prob in [(2, 0.9), (4, 0.1)]:

                new_grid = grid.clone()
                new_grid.setCellValue(cell, value)

                utility = self.maximize(new_grid, alpha, beta, depth - 1)

                total_utility += prob * utility
                total_prob += prob

        if total_prob == 0:
            return self.evaluate(grid)

        return total_utility / total_prob
    
    def light_eval(self, grid):
        return len(grid.getAvailableCells()) * 10 + grid.getMaxTile()
    
    def quick_features(self, grid):
        return len(grid.getAvailableCells()), grid.getMaxTile()

    def evaluate(self, grid):

        empty = len(grid.getAvailableCells())
        max_tile = grid.getMaxTile()
        max_score = math.log2(max_tile) if max_tile > 0 else 0

        smooth = self.smoothness(grid)
        mono = self.monotonicity(grid)
        corner = self.corner_bonus(grid)
        merge = self.merge_potential(grid)

        
        clustering_penalty = 0
        for i in range(4):
            for j in range(4):
                if grid.map[i][j] != 0:
                    for dx, dy in [(1,0),(0,1)]:
                        x, y = i+dx, j+dy
                        if 0 <= x < 4 and 0 <= y < 4:
                            if grid.map[x][y] != 0:
                                if abs(math.log2(grid.map[i][j]) - math.log2(grid.map[x][y])) > 2:
                                    clustering_penalty -= 5

        return (
            5.0 * empty +
            3.0 * mono +
            2.5 * smooth +
            4.0 * corner +
            2.0 * merge +
            1.0 * max_score +
            clustering_penalty
        )
        
    
    # CUTOFF CONDITION
    
    def cutoff(self, depth):
        if depth <= 0:
            return True
        if time.time() - self.start_time > self.time_limit:
            return True
        return False

   
    # HEURISTIC FUNCTION
    
    def heuristic(self, grid):
        empty = len(grid.getAvailableCells())
        max_tile = grid.getMaxTile()

        smooth = self.smoothness(grid)
        mono = self.monotonicity(grid)
        snake = self.snake_score(grid)

        corner = self.corner_bonus(grid)
        merge = self.merge_potential(grid)

        return (
            4.0 * empty +
            1.5 * smooth +
            2.5 * mono +
            0.00005 * snake +
            1.0 * max_tile +
            3.0 * corner +
            3.0 * merge   
        )
    
    def snake_score(self, grid):
        weights = [
            [65536, 32768, 16384, 8192],
            [512,   1024,  2048,  4096],
            [256,   128,   64,    32],
            [2,     4,     8,     16]
        ]

        score = 0

        for i in range(4):
            for j in range(4):
                score += grid.map[i][j] * weights[i][j]

        return score

    
    # SMOOTHNESS 
    
    def smoothness(self, grid):
        smooth = 0

        for i in range(4):
            for j in range(4):
                if grid.map[i][j] != 0:
                    val = grid.map[i][j].bit_length() - 1

                    for dx, dy in [(1, 0), (0, 1)]:
                        x, y = i + dx, j + dy
                        if 0 <= x < 4 and 0 <= y < 4 and grid.map[x][y] != 0:
                            neighbor = grid.map[x][y].bit_length() - 1
                            smooth -= abs(val - neighbor)

        return smooth

    
    # MONOTONICITY 
    
    def monotonicity(self, grid):
        totals = [0, 0, 0, 0]

        # Rows
        for i in range(4):
            for j in range(3):
                current = grid.map[i][j]
                next_val = grid.map[i][j + 1]

                if current and next_val:
                    current = current.bit_length() - 1
                    next_val = next_val.bit_length() - 1

                    if current > next_val:
                        totals[0] += next_val - current
                    else:
                        totals[1] += current - next_val

        # Columns
        for j in range(4):
            for i in range(3):
                current = grid.map[i][j]
                next_val = grid.map[i + 1][j]

                if current and next_val:
                    current = current.bit_length() - 1
                    next_val = next_val.bit_length() - 1

                    if current > next_val:
                        totals[2] += next_val - current
                    else:
                        totals[3] += current - next_val

        return max(totals[0], totals[1]) + max(totals[2], totals[3])

    
    # CORNER HEURISTIC
    
    def corner_bonus(self, grid):
        max_tile = grid.getMaxTile()

        corners = [
            grid.map[0][0],
            grid.map[0][3],
            grid.map[3][0],
            grid.map[3][3]
        ]

        if max_tile in corners:
            return math.log2(max_tile) * 20   
        return -20
    
    def merge_potential(self, grid):
        score = 0

        for i in range(4):
            for j in range(4):
                if grid.map[i][j] != 0:
                    for dx, dy in [(1, 0), (0, 1)]:
                        x, y = i + dx, j + dy
                        if 0 <= x < 4 and 0 <= y < 4:
                            if grid.map[i][j] == grid.map[x][y]:
                                score += math.log2(grid.map[i][j])

        return score