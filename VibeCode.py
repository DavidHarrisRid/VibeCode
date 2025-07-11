"""Console Tetris game using curses.

If you run this on Windows, install the optional ``windows-curses``
package so that ``import curses`` succeeds:

    pip install windows-curses
"""

try:
    import curses
except ImportError as e:
    import sys
    if sys.platform.startswith("win"):
        print(
            "curses is missing. Install it with 'pip install windows-curses'",
            file=sys.stderr,
        )
        raise SystemExit(1) from e
    raise
import random
import time

# Constants for the game
# Dimensions of the playing field
BOARD_WIDTH = 12
BOARD_HEIGHT = 22
TICK_RATE = 0.5  # seconds between automatic piece drops

# Snake constants
SNAKE_WIDTH = 40
SNAKE_HEIGHT = 25
# Horizontal movement tick. Vertical movement is twice as fast.
SNAKE_TICK_HOR = 0.1
# Vertical movement felt faster than horizontal, so make it slower
# by using a longer tick duration for up/down moves.
SNAKE_TICK_VER = SNAKE_TICK_HOR * 2

# Space Invaders constants - wide play area similar to the arcade game
INV_WIDTH = 60
INV_HEIGHT = 20
INV_TICK = 0.2
ALIEN_WIDTH = 3  # aliens are drawn wider than one cell

# Ice Climber constants
CLIMB_WIDTH = 30
CLIMB_VISIBLE = 20
CLIMB_JUMP = 3
CLIMB_TICK = 0.05

# Define the seven standard Tetris pieces using coordinate sets
PIECES = {
    'I': [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    'O': [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    'T': [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    'S': [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    'Z': [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
    'J': [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    'L': [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}

class Piece:
    """Represents a falling Tetris piece."""

    def __init__(self, name):
        self.name = name
        self.rotation = 0
        self.coords = PIECES[name]
        # Start near the top center
        self.x = BOARD_WIDTH // 2 - 2
        self.y = 0

    def get_cells(self, rot=None, off_x=0, off_y=0):
        rot = self.rotation if rot is None else rot
        cells = []
        for x, y in self.coords[rot % 4]:
            cells.append((x + self.x + off_x, y + self.y + off_y))
        return cells

class Tetris:
    """Main game class handling board state and logic."""

    def __init__(self):
        self.board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.current = self.new_piece()
        self.game_over = False
        self.last_drop_time = time.time()

    def new_piece(self):
        piece_type = random.choice(list(PIECES.keys()))
        return Piece(piece_type)

    def check_collision(self, cells):
        for x, y in cells:
            if x < 0 or x >= BOARD_WIDTH or y >= BOARD_HEIGHT:
                return True
            if y >= 0 and self.board[y][x]:
                return True
        return False

    def lock_piece(self):
        for x, y in self.current.get_cells():
            if 0 <= y < BOARD_HEIGHT and 0 <= x < BOARD_WIDTH:
                self.board[y][x] = self.current.name
        self.clear_lines()
        self.current = self.new_piece()
        if self.check_collision(self.current.get_cells()):
            self.game_over = True

    def clear_lines(self):
        new_board = []
        lines_cleared = 0
        for row in self.board:
            if all(row):
                lines_cleared += 1
            else:
                new_board.append(row)
        for _ in range(lines_cleared):
            new_board.insert(0, [0] * BOARD_WIDTH)
        self.board = new_board
        self.score += lines_cleared * 100

    def move(self, dx, dy):
        if not self.check_collision(self.current.get_cells(off_x=dx, off_y=dy)):
            self.current.x += dx
            self.current.y += dy
            return True
        return False

    def rotate(self):
        new_rot = (self.current.rotation + 1) % 4
        if not self.check_collision(self.current.get_cells(rot=new_rot)):
            self.current.rotation = new_rot

    def step(self):
        now = time.time()
        if now - self.last_drop_time > TICK_RATE:
            if not self.move(0, 1):
                self.lock_piece()
            self.last_drop_time = now

    def draw(self, stdscr):
        """Render the board, current piece and UI."""
        stdscr.clear()
        # Draw borders
        horizontal = "-" * (BOARD_WIDTH * 2)
        stdscr.addstr(0, 1, horizontal)
        stdscr.addstr(BOARD_HEIGHT + 1, 1, horizontal)
        for y in range(1, BOARD_HEIGHT + 1):
            stdscr.addstr(y, 0, "|")
            stdscr.addstr(y, BOARD_WIDTH * 2 + 1, "|")

        # Draw locked cells
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.board[y][x]:
                    stdscr.addstr(y + 1, x * 2 + 1, "[]")
                else:
                    stdscr.addstr(y + 1, x * 2 + 1, "  ")

        # Draw the active piece
        for x, y in self.current.get_cells():
            if y >= 0:
                stdscr.addstr(y + 1, x * 2 + 1, "[]")

        # Score and game over message
        stdscr.addstr(1, BOARD_WIDTH * 2 + 4, f"Score: {self.score}")
        if self.game_over:
            stdscr.addstr(BOARD_HEIGHT // 2, BOARD_WIDTH, "GAME OVER")
        stdscr.refresh()

    def run(self, stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        while not self.game_over:
            key = stdscr.getch()
            if key == curses.KEY_LEFT:
                self.move(-1, 0)
            elif key == curses.KEY_RIGHT:
                self.move(1, 0)
            elif key == curses.KEY_DOWN:
                if not self.move(0, 1):
                    self.lock_piece()
            elif key == curses.KEY_UP:
                self.rotate()
            elif key == ord('q'):
                break
            self.step()
            self.draw(stdscr)
        stdscr.nodelay(False)
        stdscr.addstr(BOARD_HEIGHT + 2, 0, "Press any key to return")
        stdscr.refresh()
        stdscr.getch()


class Snake:
    """Simple Snake game."""

    def __init__(self):
        mid_x = SNAKE_WIDTH // 2
        mid_y = SNAKE_HEIGHT // 2
        self.snake = [(mid_x, mid_y)]
        self.direction = (1, 0)
        self.food = self.new_food()
        self.score = 0
        self.game_over = False
        self.last_move = time.time()

    def new_food(self):
        while True:
            fx = random.randint(1, SNAKE_WIDTH - 2)
            fy = random.randint(1, SNAKE_HEIGHT - 2)
            if (fx, fy) not in self.snake:
                return (fx, fy)

    def move_snake(self):
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        if (
            new_head in self.snake
            or new_head[0] <= 0
            or new_head[0] >= SNAKE_WIDTH - 1
            or new_head[1] <= 0
            or new_head[1] >= SNAKE_HEIGHT - 1
        ):
            self.game_over = True
            return
        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 1
            self.food = self.new_food()
        else:
            self.snake.pop()

    def change_dir(self, key):
        if key == curses.KEY_UP and self.direction != (0, 1):
            self.direction = (0, -1)
        elif key == curses.KEY_DOWN and self.direction != (0, -1):
            self.direction = (0, 1)
        elif key == curses.KEY_LEFT and self.direction != (1, 0):
            self.direction = (-1, 0)
        elif key == curses.KEY_RIGHT and self.direction != (-1, 0):
            self.direction = (1, 0)

    def step(self):
        now = time.time()
        tick = (
            SNAKE_TICK_VER
            if self.direction in ((0, 1), (0, -1))
            else SNAKE_TICK_HOR
        )
        if now - self.last_move > tick:
            self.move_snake()
            self.last_move = now

    def draw(self, stdscr):
        stdscr.clear()
        horizontal = "-" * SNAKE_WIDTH
        stdscr.addstr(0, 1, horizontal)
        stdscr.addstr(SNAKE_HEIGHT, 1, horizontal)
        for y in range(1, SNAKE_HEIGHT):
            stdscr.addstr(y, 0, "|")
            stdscr.addstr(y, SNAKE_WIDTH + 1, "|")
        for i, (x, y) in enumerate(self.snake):
            char = "@" if i == 0 else "o"
            stdscr.addstr(y, x + 1, char)
        fx, fy = self.food
        stdscr.addstr(fy, fx + 1, "*")
        stdscr.addstr(SNAKE_HEIGHT + 1, 0, f"Score: {self.score}")
        if self.game_over:
            stdscr.addstr(SNAKE_HEIGHT // 2, SNAKE_WIDTH // 2 - 4, "GAME OVER")
        stdscr.refresh()

    def run(self, stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        while not self.game_over:
            key = stdscr.getch()
            if key in (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT):
                self.change_dir(key)
            elif key == ord("q"):
                break
            self.step()
            self.draw(stdscr)
        stdscr.nodelay(False)
        stdscr.addstr(SNAKE_HEIGHT + 2, 0, "Press any key to return")
        stdscr.refresh()
        stdscr.getch()


class SpaceInvaders:
    """Very small Space Invaders clone."""

    def __init__(self):
        self.player_x = INV_WIDTH // 2
        # Allow up to two bullets on screen
        self.bullets = []  # list of (x, y) positions for active bullets
        self.aliens = []
        self.direction = 1
        self.last_move = time.time()
        # start with the standard tick duration and speed up with each drop
        self.move_interval = INV_TICK
        self.game_over = False
        self.score = 0
        self.setup_aliens()

    def setup_aliens(self):
        # Fewer aliens for a more compact formation
        for row in range(3):
            for col in range(5):
                x = 6 + col * 8
                y = 2 + row * 2
                self.aliens.append([x, y])

    def move_aliens(self):
        need_down = False
        for alien in self.aliens:
            alien[0] += self.direction
            if alien[0] <= 1 or alien[0] + ALIEN_WIDTH - 1 >= INV_WIDTH - 2:
                need_down = True
        if need_down:
            self.direction *= -1
            for alien in self.aliens:
                alien[1] += 1
                if alien[1] >= INV_HEIGHT - 1:
                    self.game_over = True
            # Invaders get slightly faster each time they descend
            self.move_interval = max(self.move_interval * 0.9, 0.05)

    def step_bullets(self):
        new_bullets = []
        for x, y in self.bullets:
            y -= 1
            if y <= 0:
                continue
            hit = False
            for alien in list(self.aliens):
                if alien[1] == y and alien[0] <= x < alien[0] + ALIEN_WIDTH:
                    self.aliens.remove(alien)
                    self.score += 10
                    hit = True
                    break
            if not hit:
                new_bullets.append((x, y))
        self.bullets = new_bullets

    def draw(self, stdscr):
        stdscr.clear()
        horiz = "-" * INV_WIDTH
        stdscr.addstr(0, 1, horiz)
        stdscr.addstr(INV_HEIGHT, 1, horiz)
        for y in range(1, INV_HEIGHT):
            stdscr.addstr(y, 0, "|")
            stdscr.addstr(y, INV_WIDTH + 1, "|")
        stdscr.addstr(INV_HEIGHT + 1, 0, f"Score: {self.score}")
        if self.game_over:
            stdscr.addstr(INV_HEIGHT // 2, INV_WIDTH // 2 - 5, "GAME OVER")
        for alien in self.aliens:
            stdscr.addstr(alien[1], alien[0] + 1, "M" * ALIEN_WIDTH)
        for x, y in self.bullets:
            stdscr.addstr(y, x + 1, "|")
        stdscr.addstr(INV_HEIGHT - 1, self.player_x + 1, "A")
        stdscr.refresh()

    def run(self, stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        while not self.game_over and self.aliens:
            key = stdscr.getch()
            if key == curses.KEY_LEFT and self.player_x > 1:
                self.player_x -= 1
            elif key == curses.KEY_RIGHT and self.player_x < INV_WIDTH - 2:
                self.player_x += 1
            elif key in (ord(" "), curses.KEY_UP):
                if len(self.bullets) < 2:
                    self.bullets.append((self.player_x, INV_HEIGHT - 2))
            elif key == ord("q"):
                break

            now = time.time()
            if now - self.last_move > self.move_interval:
                self.move_aliens()
                self.step_bullets()
                self.last_move = now
            self.draw(stdscr)

        stdscr.nodelay(False)
        msg = "YOU WIN" if not self.aliens else "Press any key to return"
        stdscr.addstr(INV_HEIGHT + 2, 0, msg)
        stdscr.refresh()
        stdscr.getch()


class IceClimber:
    """Simple vertical climbing game."""

    def __init__(self):
        self.world = []  # bottom-up rows stored as lists of chars
        self.player_x = CLIMB_WIDTH // 2
        self.player_y = 1
        self.scroll = 0
        self.jump_remaining = 0
        # number of blank rows until the next platform is added
        self.next_platform = random.randint(1, 2)
        self.generate_rows(CLIMB_VISIBLE + 5)

    def generate_row(self):
        """Create a new row at the top of the world list."""
        if not self.world:
            row = ['|'] + ['='] * CLIMB_WIDTH + ['|']
        elif self.next_platform > 0:
            row = ['|'] + [' '] * CLIMB_WIDTH + ['|']
            self.next_platform -= 1
        else:
            parts = ['='] * CLIMB_WIDTH
            gap = random.randint(1, CLIMB_WIDTH - 4)
            for i in range(3):
                parts[gap + i] = ' '
            row = ['|'] + parts + ['|']
            # after placing a platform, wait 1-2 rows before the next
            self.next_platform = random.randint(1, 2)
        self.world.append(row)

    def generate_rows(self, count):
        for _ in range(count):
            self.generate_row()

    def cell(self, x, y):
        while y >= len(self.world):
            self.generate_row()
        return self.world[y][x]

    def set_cell(self, x, y, ch):
        while y >= len(self.world):
            self.generate_row()
        self.world[y][x] = ch

    def on_ground(self):
        if self.player_y == 0:
            return True
        return self.cell(self.player_x, self.player_y - 1) == "="

    def move_horiz(self, dx):
        nx = self.player_x + dx
        if 0 < nx < CLIMB_WIDTH + 1 and self.cell(nx, self.player_y) == ' ':
            self.player_x = nx

    def jump(self):
        if self.on_ground():
            self.jump_remaining = CLIMB_JUMP

    def apply_gravity(self):
        if self.jump_remaining > 0:
            ny = self.player_y + 1
            above = self.cell(self.player_x, ny)
            if above == ' ':
                self.player_y = ny
            elif above == '=':
                self.set_cell(self.player_x, ny, ' ')
                self.player_y = ny
            else:
                self.jump_remaining = 0
            self.jump_remaining -= 1
        elif not self.on_ground():
            self.player_y -= 1

    def update_scroll(self):
        target = self.player_y - CLIMB_VISIBLE // 2
        if target > self.scroll:
            self.scroll = target

    def draw(self, stdscr):
        stdscr.clear()
        horiz = '+' + '-' * CLIMB_WIDTH + '+'
        stdscr.addstr(0, 0, horiz)
        for i in range(CLIMB_VISIBLE):
            idx = self.scroll + CLIMB_VISIBLE - 1 - i
            row = ''.join(self.world[idx])
            stdscr.addstr(i + 1, 0, row)
        stdscr.addstr(CLIMB_VISIBLE + 1, 0, horiz)
        sy = self.scroll + CLIMB_VISIBLE - self.player_y
        if 1 <= sy <= CLIMB_VISIBLE:
            stdscr.addstr(sy, self.player_x, '@')
        stdscr.refresh()

    def run(self, stdscr):
        curses.curs_set(0)
        stdscr.nodelay(True)
        while self.player_y >= 0:
            key = stdscr.getch()
            while key != -1:
                if key == curses.KEY_LEFT:
                    self.move_horiz(-1)
                if key == curses.KEY_RIGHT:
                    self.move_horiz(1)
                if key == curses.KEY_UP:
                    self.jump()
                if key == ord("q"):
                    return
                key = stdscr.getch()
            self.apply_gravity()
            self.update_scroll()
            self.draw(stdscr)
            time.sleep(CLIMB_TICK)
        stdscr.nodelay(False)
        stdscr.addstr(CLIMB_VISIBLE + 2, 0, "Game Over - press any key")
        stdscr.refresh()
        stdscr.getch()



def start_menu(stdscr):
    """Display the startup menu and return the selected option index."""
    curses.curs_set(0)
    options = [
        "Play Tetris",
        "Play Snake",
        "Play Space Invaders",
        "Play Ice Climber",
        "Quit",
    ]
    current = 0
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Select a game:")
        for i, option in enumerate(options):
            marker = "-> " if i == current else "   "
            stdscr.addstr(2 + i, 0, marker + option)
        stdscr.refresh()
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord("k")):
            current = (current - 1) % len(options)
        elif key in (curses.KEY_DOWN, ord("j")):
            current = (current + 1) % len(options)
        elif key in (curses.KEY_ENTER, 10, 13):
            return current
        elif key == ord("q"):
            # Treat 'q' as selecting "Quit"
            return len(options) - 1


def main(stdscr):
    while True:
        choice = start_menu(stdscr)
        if choice == 0:
            game = Tetris()
            game.run(stdscr)
        elif choice == 1:
            game = Snake()
            game.run(stdscr)
        elif choice == 2:
            game = SpaceInvaders()
            game.run(stdscr)
        elif choice == 3:
            game = IceClimber()
            game.run(stdscr)
        elif choice == 4:
            break
        

if __name__ == "__main__":
    curses.wrapper(main)
