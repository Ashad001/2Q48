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
        self.screen_height = 450  # Adjusted height for score and game over text
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

        # For animations
        self.tile_positions = {(i, j): (j * self.cell_size + self.padding, i * self.cell_size + 50 + self.padding)
                               for i in range(size) for j in range(size)}
        self.animating_tiles = []  # List to hold tiles in motion

    def render(self):
        self.screen.fill((187, 173, 160))  # Background color
        self.handle_events()

        # Score box styling
        score_box_width = 380
        score_box_height = 45
        score_box_x = 10
        score_box_y = 10
        score_box_color = (119, 110, 101)  # Dark background for the score box
        score_border_color = (255, 255, 255)  # White border for score box

        # Draw the score box with border
        pg.draw.rect(self.screen, score_border_color, 
                    (score_box_x - 2, score_box_y - 2, score_box_width + 4, score_box_height + 4), border_radius=10)
        pg.draw.rect(self.screen, score_box_color, 
                    (score_box_x, score_box_y, score_box_width, score_box_height), border_radius=10)

        # Render the score text
        score_text = self.myfont.render(f'Score:   {self.score}', True, (255, 255, 255))  # Title in white
        
        # Position text inside the score box
        self.screen.blit(score_text, (score_box_x + 10, score_box_y + 5))  # "Score" label

        # Draw the grid and cells
        for i in range(self.size):
            for j in range(self.size):
                value = self.grid[i][j]
                color = self.colors.get(value, (100, 105, 100))  # Default to gray for unknown values
                rect = pg.Rect(j * self.cell_size + self.padding,
                            i * self.cell_size + 50 + self.padding,
                            self.cell_size - 2 * self.padding,
                            self.cell_size - 2 * self.padding)
                pg.draw.rect(self.screen, color, rect, border_radius=10)

                if value != 0:
                    text = self.myfont.render(str(value), True, (0, 0, 0) if value < 8 else (255, 255, 255))  # Adjust text color
                    text_rect = text.get_rect(center=(rect.centerx, rect.centery))
                    self.screen.blit(text, text_rect)

        # Handle tile animations
        self.animate_tiles()

        pg.display.flip()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()

    def animate_tiles(self):
        for tile in self.animating_tiles:
            x, y, final_x, final_y, step = tile
            if step > 0:
                tile_rect = pg.Rect(x, y, self.cell_size - 2 * self.padding, self.cell_size - 2 * self.padding)
                pg.draw.rect(self.screen, (255, 0, 0), tile_rect)  # Draw moving tile
                new_x = x + (final_x - x) // step
                new_y = y + (final_y - y) // step
                tile[0], tile[1], tile[4] = new_x, new_y, step - 1
        # Remove tiles after they've finished animating
        self.animating_tiles = [tile for tile in self.animating_tiles if tile[4] > 0]

    def move_tile_animation(self, x1, y1, x2, y2):
        initial_pos = self.tile_positions[(x1, y1)]
        final_pos = self.tile_positions[(x2, y2)]
        self.animating_tiles.append([initial_pos[0], initial_pos[1], final_pos[0], final_pos[1], 10])  # 10 steps for animation


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

    def is_safe(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size and self.grid[x][y] == 0
    
    def is_full(self):
        if self.move_up(copy.deepcopy(self.grid))[0] or self.move_down(copy.deepcopy(self.grid))[0] or \
           self.move_left(copy.deepcopy(self.grid))[0] or self.move_right(copy.deepcopy(self.grid))[0]:
            return False
        self.flag = 0;
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
            # Display Game Over
            game_over_text = grid.myfont.render('Game Over!', True, (255, 0, 0))
            grid.screen.blit(game_over_text, (grid.screen_width // 2 - 100, grid.screen_height // 2 - 50))
            pg.display.flip()
            pg.time.delay(2000)
            grid.reset()
