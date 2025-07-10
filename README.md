# VibeCode Tetris

This repository contains a simple console-based Tetris game written in Python.
When you run the program you first see a small menu where you can choose to
start Tetris or quit. After a game ends you are returned to this menu.

The game relies on the `curses` module for drawing. On Windows systems the
standard Python distribution does not ship with curses. To run the game
install the [windows-curses](https://pypi.org/project/windows-curses/) package
first:

```bash
pip install windows-curses
```

Then launch the game with:

```bash
python VibeCode.py
```

If you see an error about `curses` being missing, make sure you've installed the
`windows-curses` package in the same Python environment.
