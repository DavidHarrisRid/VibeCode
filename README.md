# VibeCode Games

This repository contains a simple console-based game collection written in
Python. When you run the program you first see a small menu where you can
choose to start Tetris, play Snake, play Space Invaders, try Ice Climber or quit. After a game
ends you are returned to this menu.

The Space Invaders screen is deliberately wider than the other games so the
action more closely resembles the classic arcade layout. The invader formation
is small and begins moving slowly, letting you fire up to two bullets at once
for a bit more firepower. The aliens themselves are drawn larger than a single
character so they are easier targets. Each time the invaders descend a row they
speed up slightly to keep the pressure on.

Ice Climber uses most of the screen for its climbing arena. If your terminal is
smaller than the default 60x30 field the game will shrink to fit so it starts
properly. Break the blocks above you with the jump key and work your way upward
through the gaps to reach the top.

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
