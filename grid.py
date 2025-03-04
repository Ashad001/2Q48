import random
import copy
import pygame as pg
import numpy as np
from numpy import ndindex

class Grid:
    def __init__(self, size):
        self.size = size
        self.grid = [[0 for _ in range(size)] for _ in range(size)]
        self.grid[random.randint(0, size - 1)][random.randint(0, size - 1)] = 2

        self.score = 0
        self.flag = 0

        pg.init()
        self.myfont = pg.font.SysFont('Arial', 30)
        self.screen_width = 400
        self.screen_height = 450  # Added height for score display
        self.cell_size = self.screen_width // self.size
        self.padding = 10
        self.colors = {
            0: (205, 193, 180),
            2: (238, 228, 218),
            4: (237, 224, 200),
            8: (242, 177, 121),
            16: (245, 149, 99),
            32: (246, 124, 95),
            64: (246, 94, 59),
            128: (237, 207, 114),
            256: (237, 204, 97),
            512: (237, 200, 80),
            1024: (237, 197, 63),
            2048: (237, 194, 46),
        }
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height))
        pg.display.set_caption("2048")

    def render(self):
        self.screen.fill((187, 173, 160))  # Background color
        self.handle_events()
        for i in range(self.size):
            for j in range(self.size):
                value = self.grid[i][j]
                color = self.colors.get(value, (100, 105, 100))  #
                pg.draw.rect(self.screen, color, (j * self.cell_size + self.padding,
                                                  i * self.cell_size + 50 + self.padding,
                                                  self.cell_size - 2 * self.padding, self.cell_size - 2 * self.padding))
                if value != 0:
                    text = self.myfont.render(str(value), True, (0, 0, 0))  # Black text
                    text_rect = text.get_rect(center=(j * self.cell_size + self.cell_size / 2,
                                                       i * self.cell_size + 50 + self.cell_size / 2))
                    self.screen.blit(text, text_rect)
        pg.display.flip()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()

    def is_safe(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size and self.grid[x][y] == 0

    def is_full(self):
        if (
            self.move_up(copy.deepcopy(self.grid))
            or self.move_down(copy.deepcopy(self.grid))
            or self.move_left(copy.deepcopy(self.grid))
            or self.move_right(copy.deepcopy(self.grid))
        ):
            return False
        return True

    def reset(self):
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.grid[random.randint(0, self.size - 1)][random.randint(0, self.size - 1)] = 2
        self.score = 0
        return copy.deepcopy(self.grid)

    def generate_new_cell(self):
        empty_cells = [(i, j) for i in range(self.size) for j in range(self.size) if self.grid[i][j] == 0]
        if empty_cells:
            x, y = random.choice(empty_cells)
            self.grid[x][y] = 2 if random.random() < 0.9 else 4

    def move_up(self, grid=None):
        if grid is None:
            grid = self.grid
        moved = False
        for j in range(self.size):
            for i in range(1, self.size):
                if grid[i][j] == 0:
                    continue
                x = i
                while x > 0 and grid[x - 1][j] == 0:
                    x -= 1
                if x == 0 or (grid[x - 1][j] != grid[i][j]):
                    grid[x][j] = grid[i][j]
                    if x != i:
                        grid[i][j] = 0
                        moved = True
                else:
                    grid[x - 1][j] *= 2
                    self.score += grid[x - 1][j]  # adding to total score
                    grid[i][j] = 0
                    moved = True
        return moved

    def move_down(self, grid=None):
        if grid is None:
            grid = self.grid
        moved = False
        for j in range(self.size):
            for i in range(self.size - 2, -1, -1):
                if grid[i][j] == 0:
                    continue
                x = i
                while x < self.size - 1 and grid[x + 1][j] == 0:
                    x += 1
                if x == self.size - 1 or (grid[x + 1][j] != grid[i][j]):
                    grid[x][j] = grid[i][j]
                    if x != i:
                        grid[i][j] = 0
                        moved = True
                else:
                    grid[x + 1][j] *= 2
                    self.score += grid[x + 1][j]  # adding to total score
                    grid[i][j] = 0
                    moved = True

        return moved

    def move_left(self, grid=None):
        if grid is None:
            grid = self.grid
        moved = False
        for j in range(self.size):
            for i in range(self.size):
                if grid[i][j] == 0:
                    continue
                x = j
                while x > 0 and grid[i][x - 1] == 0:
                    x -= 1
                if x == 0 or (grid[i][x - 1] != grid[i][j]):
                    grid[i][x] = grid[i][j]
                    if x != j:
                        grid[i][j] = 0
                        moved = True
                else:
                    grid[i][x - 1] *= 2
                    self.score += grid[i][x - 1]  # adding to total score
                    grid[i][j] = 0
                    moved = True
        return moved

    def move_right(self, grid=None):
        if grid is None:
            grid = self.grid
        moved = False
        for j in range(self.size):
            for i in range(self.size - 1, -1, -1):
                if grid[i][j] == 0:
                    continue
                x = j
                while x < self.size - 1 and grid[i][x + 1] == 0:
                    x += 1
                if x == self.size - 1 or (grid[i][x + 1] != grid[i][j]):
                    grid[i][x] = grid[i][j]
                    if x != j:
                        grid[i][j] = 0
                        moved = True
                else:
                    grid[i][x + 1] *= 2
                    self.score += grid[i][x + 1]  # adding to total score
                    grid[i][j] = 0
                    moved = True
        return moved

    def step(self, action):
        # Store the current state before taking the action
        current_state = copy.deepcopy(self.grid)
        current_score = self.score

        # Perform the action
        if action == "w" or action == 0:
            moved = self.move_up()
        elif action == "s" or action == 1:
            moved = self.move_down()
        elif action == "a" or action == 2:
            moved = self.move_left()
        elif action == "d" or action == 3:
            moved = self.move_right()
        else:
            raise ValueError("Invalid action")

        if moved:
            self.generate_new_cell()

            reward = self.score - current_score + self.get_score(self.grid) * 0.1
            done = self.is_full()
        else:
            reward = -0.1
            done = False

        next_state = copy.deepcopy(self.grid)
        return next_state, reward, done
    
    
    def score_mean_neighbor(self, newgrid):
        """
        Calculate the mean(average) of  tiles with the same values that are adjacent in a row/column.
        """
        horizontal_sum, count_horizontal = self.check_adjacent(newgrid)
        vertical_sum, count_vertical = self.check_adjacent(newgrid.T)
        if count_horizontal == 0 or count_vertical == 0:
            return 0
        return (horizontal_sum + vertical_sum) / (count_horizontal + count_vertical)


    def check_adjacent(self, grid):
        """
        Returns the sum and total number (count) of tiles with the same values that are adjacent in a row/column.
        """
        count = 0
        total_sum = 0
        for row in grid:
            previous = -1
            for tile in row:
                if previous == tile:
                    total_sum += tile
                    count += 1
                previous = tile
        return total_sum, count


    def score_count_neighbor(self, grid):
        _, horizontal_count = self.check_adjacent(grid)
        _, vertical_count = self.check_adjacent(grid.T)
        return horizontal_count + vertical_count



    def get_empty_cells(self, grid):
        return [(i, j) for i in range(self.size) for j in range(self.size) if grid[i][j] == 0]


    def score_adjacent_tiles(self, grid):
        """
        The function `score_adjacent_tiles` calculates the average of the scores obtained from counting and
        finding the mean of neighboring tiles on a grid.
        
        """
        return (self.score_count_neighbor(grid) + self.score_mean_neighbor(grid)) / 2

    def score_snake(self, grid, base_value=0.25):
        """
        The function `score_snake` calculates the score of a game grid in a snake-like game by combining
        values from different directions.
        """
        size = len(grid)
        rewardArray = np.array([base_value ** i for i in range(size ** 2)])

        score = 0
        for i in range(2):
            gridArray_horizontal = np.hstack(tuple(grid[j] if i % 2 == 0 else grid[j][::-1] for j in range(size)))
            score = max(score, np.sum(rewardArray * gridArray_horizontal))
            score = max(score, np.sum(rewardArray[::-1] * gridArray_horizontal))
            gridArray_vertical = np.hstack(tuple(grid[j][::-1] if i % 2 == 0 else grid[j] for j in range(size)))
            score = max(score, np.sum(rewardArray * gridArray_vertical))
            score = max(score, np.sum(rewardArray[::-1] * gridArray_vertical))

            # grid = np.rot90(grid)
            grid = grid.T

        return score


    def calculate_empty_tiles(self, grid):
        empty_tiles = 0
        for x, y in ndindex(grid.shape):
            if grid[x, y] == 0:
                empty_tiles += 1
        return empty_tiles


    def get_score(self, grid):
        grid = np.array(grid)
        adjacent_tiles_score = self.score_adjacent_tiles(grid)
        snake_score = self.score_snake(grid)
        empty_tiles = self.calculate_empty_tiles(grid)
        total_score = (adjacent_tiles_score + 3 * snake_score + empty_tiles) / 6
        # print("Total Score: ", total_score)
        return total_score
