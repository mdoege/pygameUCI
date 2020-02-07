#!/usr/bin/env python3

# pygameUCI, an UCI chess frontend for use with USB joysticks or gamepads

import pygame
from PIL import Image, ImageDraw
import chess, chess.engine, chess.pgn
import sys

# Open an UCI chess engine
if "ntc" in sys.argv:
        engine = chess.engine.SimpleEngine.popen_uci("../nimTUROCHAMP/ntc")
        limit = chess.engine.Limit()
else:
        engine = chess.engine.SimpleEngine.popen_uci("/usr/bin/stockfish")
        limit = chess.engine.Limit(time = 1)    # calculate for one second

hicolor = (100, 0, 100, 100)       # highlight color (RGBA)
curx, cury = 4, 1       # cursor initial position

# Do not change these
w, h = 100, 100         # tile dimensions
rotate = False          # Black plays from bottom?

pygame.init()
screen = pygame.display.set_mode((1000, 1000))
pygame.display.set_caption("pygameUCI")

joystick_count = pygame.joystick.get_count()
if joystick_count < 1:
        print("*** No supported joysticks or gamepads found! ***")

clock = pygame.time.Clock()
pygame.joystick.init()

ib = Image.open("img/maple.png").convert("RGBA")

b = chess.Board()
res = b.result()
oldmove = ()
result = None

# human plays Black?
if "black" in sys.argv:
        player = False
        rotate = True
        curx, cury = 4, 6
else: player = True

done = False
lim = .8        # minimum joystick movement needed to register
selected = -1   # selected "from" square
target = []     # possible "to" squares for move
cmove = []      # computer move highlights

def getpos(x, y):
        "Board coordinates to screen coordinates"
        if rotate:
                return (700 - 100 * x, 100 * y)
        else:
                return (100 * x, 700 - 100 * y)

def blit(im, pos):
        "Copy image im to position pos"

        data = im.tobytes()
        mode = im.mode
        size = im.size
        image = pygame.image.fromstring(data, size, mode)
        screen.blit(image, (pos[0] + 100, pos[1] + 100))

def put(fn, pos, highlight = False, cursor = False):
        "Display piece image with file name fn at position pos with offset xoff/yoff"
        if fn:
                im = Image.open(fn).convert("RGBA")
                if highlight:
                        ib_crop = Image.new('RGBA', (w, h), hicolor)
                else:
                        ib_crop = ib.crop((pos[0], pos[1], pos[0] + w, pos[1] + h))
                im = Image.alpha_composite(ib_crop, im)
        else:
                if highlight:
                        im = Image.new('RGBA', (w, h), hicolor)
                else:
                        im = ib.crop((pos[0], pos[1], pos[0] + w, pos[1] + h))

        if cursor:
                draw = ImageDraw.Draw(im)
                ccol = (0, 0, 255, 200)
                if selected > -1:
                        index = 8 * cury + curx
                        if index in target: ccol = (0, 255, 0, 200)
                        else: ccol = (255, 0, 0, 200)
                if res == "*":
                        draw.ellipse((0, 0, 99, 99), outline = ccol, width = 7)
        blit(im, pos)

def draw_square(b, i, highlight = False):
        "Draw a square on the board"
        x = chess.square_file(i)
        y = chess.square_rank(i)
        p = b.piece_at(8 * y + x)
        if curx == x and cury == y: cursor = True
        else: cursor = False
        if i in cmove: highlight = True
        if p:
                if p.color: col = "w"
                else: col = "b"
                fn = "img/" + col + p.symbol().upper() + ".png"
                put(fn, getpos(x, y), highlight = highlight, cursor = cursor)
        else:
                put("", getpos(x, y), highlight = highlight, cursor = cursor)

def draw_board(b):
        "Draw complete chessboard on screen"
        for i in range(64):
                draw_square(b, i)

def draw_labels():
        "Draw board labels"
        for x in range(8):
                im = Image.open("img/%s.png" % chr(97 + x)).convert("RGBA")

                pos = getpos(x, -1)
                blit(im, pos)

                pos = getpos(x, 8)
                blit(im, pos)

        for y in range(8):
                im = Image.open("img/%s.png" % chr(49 + y)).convert("RGBA")

                pos = getpos(-1, y)
                blit(im, pos)

                pos = getpos(8, y)
                blit(im, pos)

def rot():
        "Determine cursor movement direction"
        if rotate: return -1
        else: return 1

def write_pgn():
        "Export current game to PGN file"
        game = chess.pgn.Game.from_board(b)
        with open("game.pgn", 'w') as pgnfile:
                pgnfile.write(str(game) + '\n\n\n')

while not done:
        for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        done = True
        
                if event.type == pygame.JOYBUTTONDOWN:
                        index = 8 * cury + curx
                        p = b.piece_at(index)

                        # pick up piece
                        if p and p.color == player and selected < 0:
                                selected = index
                                target = []
                                moves = b.legal_moves
                                for m in moves:
                                        if m.from_square == selected:
                                                target.append(m.to_square)
                                if len(target) == 0:
                                        selected = -1
                        # set down piece
                        if selected >= 0 and index in target:
                                moves = b.legal_moves
                                for m in moves:
                                        if m.from_square == selected and m.to_square == index:
                                                b.push(m)
                                                selected = -1
                                                target = []
                                                write_pgn()
                                                break

        for i in range(joystick_count):
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                name = joystick.get_name()

                axis = joystick.get_axis(0)     # left-right
                if axis > lim:
                        curx += 1 * rot()
                if axis < -lim:
                        curx -= 1 * rot()
                axis = joystick.get_axis(1)     # up-down
                if axis > lim :
                        cury -= 1 * rot()
                if axis < -lim:
                        cury += 1 * rot()
                curx = min(max(0, curx), 7)
                cury = min(max(0, cury), 7)

        draw_board(b)
        draw_labels()
        pygame.display.flip()

        # computer move
        if b.turn != player and len(list(b.legal_moves)):
                result = engine.play(b, limit)
                mm = result.move
                cmove = (mm.from_square, mm.to_square)
                b.push(mm)
                write_pgn()
        draw_board(b)
        draw_labels()
        pygame.display.flip()

        res = b.result()
        if res != "*":
                if res == "1-0":
                        pygame.display.set_caption("pygameUCI -- White wins")
                if res == "0-1":
                        pygame.display.set_caption("pygameUCI -- Black wins")
                if res == "1/2-1/2":
                        pygame.display.set_caption("pygameUCI -- Draw")
        clock.tick(5)   # limit frame rate to 5 FPS


engine.quit()

pygame.quit()


