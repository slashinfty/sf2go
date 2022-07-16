#!/usr/bin/python

import os
from time import sleep
from threading import Thread
from rpi_lcd import LCD
import chess
from stockfish import Stockfish

lcd = LCD()
sfpath = os.path.join(os.path.dirname(__file__), "stockfish_15")
stockfish = Stockfish(path = sfpath)

board = chess.Board()
stockfish.set_fen_position(board.fen())

d = 10
while d < 31:
    stockfish.set_depth(d)
    moves = stockfish.get_top_moves(1)
    for m in moves:
        print("move:", board.san(chess.Move.from_uci(m["Move"])), "cp:", m["Centipawn"] / 100, "depth:", d)
    d += 1