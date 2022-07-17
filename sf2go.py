#!/usr/bin/python

# Imports
import os
import chess
from time import sleep
from threading import Thread
from rpi_lcd import LCD
from gpiozero import Button
from stockfish import Stockfish
from signal import signal, SIGTERM, SIGHUP, pause

# Components
lcd = LCD()
btn01 = Button(5)  # P, a, 1
btn02 = Button(6)  # R, b, 2
btn03 = Button(13) # N, c, 3
btn04 = Button(19) # B, d, 4
btn05 = Button(26) # Enter
btn06 = Button(25) # Q, e, 5
btn07 = Button(12) # K, f, 6
btn08 = Button(16) # O-O, g, 7
btn09 = Button(20) # O-O-O, h, 8
btn10 = Button(21) # Modifier

# Global Variables
board = chess.Board()
started = False
analyze = True
depth = 10
move = ""
state = 0

# Stockfish
sfpath = os.path.join(os.path.dirname(__file__), "stockfish_15")
stockfish = Stockfish(path = sfpath)

# Button Functions
def btn01Press():
    global move
    global state
    if state == 0:
        move += "P"
        state += 1
    elif state == 1:
        if btn10.is_pressed == True:
            move += "1"
        else:
            move += "a"
            state += 1
    elif state == 2:
        if btn10.is_pressed == True:
            move += "a"
        else:
            move += "1"
            state += 1

# Best Move Loop
def best_move():
    global analyze
    global depth

    while analyze or depth < 50:
        stockfish.set_depth(depth)
        moves = stockfish.get_top_moves(1) # can change if more lines
        for i, m in enumerate(moves):
            # print lines
            # print("move:", board.san(chess.Move.from_uci(m["Move"])), "cp:", m["Centipawn"] / 100, "depth:", d)
        depth += 1

# User Input Loop
def user_input():
    move = ""
    while True:


# Safe Exit
def safe_exit(signum, frame):
    lcd.clear()
    exit(1)

# Main Function
def main():
    global analyze
    global board
    global started

    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    while True:
        if started == False:
            board = chess.Board()
            stockfish.set_fen_position(board.fen())
            started = True
        analyze = True
        find_best_move = Thread(target = best_move, daemon = True).start()
        read_user_input = Thread(target = user_input, daemon = True).start()
        
        read_user_input.join()
        # check to see if ending

if __name__ == '__main__': main()