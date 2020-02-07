# pygameUCI, an UCI chess frontend for use with USB joysticks or gamepads

![screenshot](https://github.com/mdoege/pygameUCI/raw/master/pygameuci.png "pygameUCI screenshot")

The default engine is ``/usr/bin/stockfish``, but other UCI engine binaries can also be used.

## Prerequisites

Needs [python-chess](https://github.com/niklasf/python-chess), [Pillow](https://github.com/python-pillow/Pillow), [pygame](https://www.pygame.org/), and a USB joystick or gamepad to play

## Usage

Move the blue cursor to the piece you want to move and press any joystick button to pick it up. The cursor turns red. Move it to a valid target square (the cursor will turn green over it) and press a joystick button again to complete the move. Computer moves are highlighted in purple on the board.

You will play as White by default; to play as Black just add ``black`` as a commandline parameter.

After every move the game is exported to ``game.pgn`` in the working directory.

## License

GPL

Board and piece images are from [Lichess](https://github.com/ornicar/lila).

