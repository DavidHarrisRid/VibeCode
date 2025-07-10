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
        raise ImportError(
            "curses is missing. Install it with 'pip install windows-curses'"
        ) from e
    raise
import random
import time

# Constants for the game
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
TICK_RATE = 0.5  # seconds between automatic piece drops

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
        stdscr.clear()
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.board[y][x]:
                    stdscr.addstr(y, x * 2, "[]")
                else:
                    stdscr.addstr(y, x * 2, "  ")
        for x, y in self.current.get_cells():
            if y >= 0:
                stdscr.addstr(y, x * 2, "[]")
        stdscr.addstr(0, BOARD_WIDTH * 2 + 2, f"Score: {self.score}")
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
        stdscr.getch()


def main():
    game = Tetris()
    curses.wrapper(game.run)


if __name__ == "__main__":
    main()
