import random
import copy
import pygame as pg

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
        self.screen.fill((187, 173, 160))  
        self.handle_events()

        score_text = self.myfont.render(f'Score: {self.score}', True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

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
        if self.move_up(copy.deepcopy(self.grid))[0] or self.move_down(copy.deepcopy(self.grid))[0] or \
           self.move_left(copy.deepcopy(self.grid))[0] or self.move_right(copy.deepcopy(self.grid))[0]:
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
        move_score = 0
        merged = [[False for _ in range(self.size)] for _ in range(self.size)]

        for j in range(self.size):
            for i in range(1, self.size):
                if grid[i][j] == 0:
                    continue
                x = i
                while x > 0 and grid[x - 1][j] == 0:
                    grid[x - 1][j] = grid[x][j]
                    grid[x][j] = 0
                    x -= 1
                    moved = True
                if x > 0 and grid[x - 1][j] == grid[x][j] and not merged[x-1][j] and not merged[x][j]:
                    grid[x - 1][j] *= 2
                    move_score += grid[x - 1][j]
                    grid[x][j] = 0
                    merged[x-1][j] = True
                    moved = True

        if grid is self.grid and moved:
            self.score += move_score
        return moved, move_score

    def move_down(self, grid=None):
        if grid is None:
            grid = self.grid
        moved = False
        move_score = 0
        merged = [[False for _ in range(self.size)] for _ in range(self.size)]

        for j in range(self.size):
            for i in range(self.size - 2, -1, -1):
                if grid[i][j] == 0:
                    continue
                x = i
                while x < self.size - 1 and grid[x + 1][j] == 0:
                    grid[x + 1][j] = grid[x][j]
                    grid[x][j] = 0
                    x += 1
                    moved = True
                if x < self.size - 1 and grid[x + 1][j] == grid[x][j] and not merged[x+1][j] and not merged[x][j]:
                    grid[x + 1][j] *= 2
                    move_score += grid[x + 1][j]
                    grid[x][j] = 0
                    merged[x+1][j] = True
                    moved = True

        if grid is self.grid and moved:
            self.score += move_score
        return moved, move_score

    def move_left(self, grid=None):
        if grid is None:
            grid = self.grid
        moved = False
        move_score = 0
        merged = [[False for _ in range(self.size)] for _ in range(self.size)]

        for i in range(self.size):
            for j in range(1, self.size):
                if grid[i][j] == 0:
                    continue
                x = j
                while x > 0 and grid[i][x - 1] == 0:
                    grid[i][x - 1] = grid[i][x]
                    grid[i][x] = 0
                    x -= 1
                    moved = True
                if x > 0 and grid[i][x - 1] == grid[i][x] and not merged[i][x-1] and not merged[i][x]:
                    grid[i][x - 1] *= 2
                    move_score += grid[i][x - 1]
                    grid[i][x] = 0
                    merged[i][x-1] = True
                    moved = True

        if grid is self.grid and moved:
            self.score += move_score
        return moved, move_score

    def move_right(self, grid=None):
        if grid is None:
            grid = self.grid
        moved = False
        move_score = 0
        merged = [[False for _ in range(self.size)] for _ in range(self.size)]

        for i in range(self.size):
            for j in range(self.size - 2, -1, -1):
                if grid[i][j] == 0:
                    continue
                x = j
                while x < self.size - 1 and grid[i][x + 1] == 0:
                    grid[i][x + 1] = grid[i][x]
                    grid[i][x] = 0
                    x += 1
                    moved = True
                if x < self.size - 1 and grid[i][x + 1] == grid[i][x] and not merged[i][x+1] and not merged[i][x]:
                    grid[i][x + 1] *= 2
                    move_score += grid[i][x + 1]
                    grid[i][x] = 0
                    merged[i][x+1] = True
                    moved = True

        if grid is self.grid and moved:
            self.score += move_score
        return moved, move_score

    def step(self, action):
        current_score = self.score
        
        # Perform the action
        if action == 0:
            moved, points = self.move_up()
        elif action == 1:
            moved, points = self.move_down()
        elif action == 2:
            moved, points = self.move_left()
        elif action == 3:
            moved, points = self.move_right()
        else:
            raise ValueError("Invalid action")

        if moved:
            self.generate_new_cell()
            reward = points  # Reward is the points gained from merging tiles
            done = self.is_full()
        else:
            reward = -0.1  # Small negative reward to discourage invalid moves
            done = False

        return copy.deepcopy(self.grid), reward, done

if __name__ == "__main__":
    grid = Grid(4)
    running = True
    while running:
        grid.handle_events()
        grid.render()
        pg.time.delay(100)
        
        keys = pg.key.get_pressed()
        moved = False
        
        if keys[pg.K_w]:
            moved, _ = grid.move_up()
        elif keys[pg.K_s]:
            moved, _ = grid.move_down()
        elif keys[pg.K_a]:
            moved, _ = grid.move_left()
        elif keys[pg.K_d]:
            moved, _ = grid.move_right()

        if moved:
            grid.generate_new_cell()

        if grid.is_full():
            print("Game Over")
            running = False

        grid.render()

    pg.quit()