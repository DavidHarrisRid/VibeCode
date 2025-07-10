# VibeCode Games

This repository contains a simple console-based game collection written in
Python. When you run the program you first see a small menu where you can
choose to start Tetris, play Snake, play Space Invaders or quit. After a game
ends you are returned to this menu.

The Space Invaders screen is deliberately wider than the other games so the
action more closely resembles the classic arcade layout.

The game relies on the `curses` module for drawing. On Windows systems the
standard Python distribution does not ship with curses. To run the game
install the [windows-curses](https://pypi.org/project/windows-curses/) package
first:

```bash
pip install windows-curses
```

Then launch the collection with:

```bash
python VibeCode.py
```

If you see an error about `curses` being missing, make sure you've installed the
`windows-curses` package in the same Python environment.
