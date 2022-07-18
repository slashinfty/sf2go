#!/usr/bin/python

# Imports
import os
import chess
from time import sleep
from threading import Thread
from rpi_lcd import LCD
from gpiozero import Button
from stockfish import Stockfish
from signal import signal, SIGTERM, SIGHUP, SIGINT, pause

# Components
lcd = LCD()
btn01 = Button(5, bounce_time = 0.3)  # P, a, 1
btn02 = Button(6, bounce_time = 0.3)  # R, b, 2
btn03 = Button(13, bounce_time = 0.3) # N, c, 3
btn04 = Button(19, bounce_time = 0.3) # B, d, 4
btn05 = Button(26, bounce_time = 0.3) # Enter
btn06 = Button(25, bounce_time = 0.3) # Q, e, 5
btn07 = Button(12, bounce_time = 0.3) # K, f, 6
btn08 = Button(16, bounce_time = 0.3) # O-O, g, 7
btn09 = Button(20, bounce_time = 0.3) # O-O-O, h, 8
btn10 = Button(21, bounce_time = 0.3, hold_time = 2) # Modifier

# Global Variables
characters = 16
rows = 2
board = chess.Board()
started = False
analyze = False
typing = False
depth = 10
move = ""
state = -1

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
    lcd.text("Input: {}".format(move), rows)

def btn02Press():
    global move
    global state
    if state == 0:
        move += "R"
        state += 1
    elif state == 1:
        if btn10.is_pressed == True:
            move += "2"
        else:
            move += "b"
            state += 1
    elif state == 2:
        if btn10.is_pressed == True:
            move += "b"
        else:
            move += "2"
            state += 1
    elif state == 3:
        move += "=R"
    lcd.text("Input: {}".format(move), rows)

def btn03Press():
    global move
    global state
    if state == 0:
        move += "N"
        state += 1
    elif state == 1:
        if btn10.is_pressed == True:
            move += "3"
        else:
            move += "c"
            state += 1
    elif state == 2:
        if btn10.is_pressed == True:
            move += "c"
        else:
            move += "3"
            state += 1
    elif state == 3:
        move += "=N"
    lcd.text("Input: {}".format(move), rows)

def btn04Press():
    global move
    global state
    if state == 0:
        move += "B"
        state += 1
    elif state == 1:
        if btn10.is_pressed == True:
            move += "4"
        else:
            move += "d"
            state += 1
    elif state == 2:
        if btn10.is_pressed == True:
            move += "d"
        else:
            move += "4"
            state += 1
    elif state == 3:
        move += "=B"
    lcd.text("Input: {}".format(move), rows)

def btn05Press():
    global analyze
    global move
    global state
    global typing
    if btn10.is_pressed == True:
        move = ""
        state = 0
    elif state == 3:
        if move.startswith("P"):
            move = move.lstrip("P")
        if board.parse_san(move) in board.legal_moves == True:
            board.push_san(move)
            analyze = False
            typing = False
        move = ""
        state = 0
    lcd.text("Input: {}".format(move), rows)

def btn06Press():
    global move
    global state
    if state == 0:
        move += "Q"
        state += 1
    elif state == 1:
        if btn10.is_pressed == True:
            move += "5"
        else:
            move += "e"
            state += 1
    elif state == 2:
        if btn10.is_pressed == True:
            move += "e"
        else:
            move += "5"
            state += 1
    elif state == 3:
        move += "=Q"
    lcd.text("Input: {}".format(move), rows)

def btn07Press():
    global move
    global state
    if state == 0:
        move += "K"
        state += 1
    elif state == 1:
        if btn10.is_pressed == True:
            move += "6"
        else:
            move += "f"
            state += 1
    elif state == 2:
        if btn10.is_pressed == True:
            move += "f"
        else:
            move += "6"
            state += 1
    lcd.text("Input: {}".format(move), rows)

def btn08Press():
    global move
    global state
    if state == 0:
        move += "O-O"
        state += 3
    elif state == 1:
        if btn10.is_pressed == True:
            move += "7"
        else:
            move += "g"
            state += 1
    elif state == 2:
        if btn10.is_pressed == True:
            move += "g"
        else:
            move += "7"
            state += 1
    lcd.text("Input: {}".format(move), rows)

def btn09Press():
    global move
    global state
    if state == 0:
        move += "O-O-O"
        state += 3
    elif state == 1:
        if btn10.is_pressed == True:
            move += "8"
        else:
            move += "h"
            state += 1
    elif state == 2:
        if btn10.is_pressed == True:
            move += "h"
        else:
            move += "8"
            state += 1
    lcd.text("Input: {}".format(move), rows)

def btn10Held():
    global analyze
    global move
    global started
    global state
    global typing
    move = ""
    lcd.text("Input: {}".format(move), rows)
    state = -1
    started = False
    analyze = False
    typing = False

# Best Move Loop
def best_move():
    global depth

    while analyze or depth < 50:
        stockfish.set_depth(depth)
        moves = stockfish.get_top_moves(rows - 1)
        for i, m in enumerate(moves):
            move = board.san(chess.Move.from_uci(m["Move"]))
            evaluation = ""
            if m["Mate"] is None:
                if (m["Centipawn"] > 0):
                    evaluation += "+"
                evaluation += str(m["Centipawn"] / 100)
            else:
                evaluation += "#" + m["Mate"]
            line = move + " " * (16 - len(move) - len(evaluation)) + evaluation
            lcd.text(line, i + 1)
        depth += 1

# User Input Loop
def user_input():
    lcd.text("Input: {}".format(move), rows)
    while typing:
        sleep(0.1)

# Safe Exit
def safe_exit(signum, frame):
    lcd.clear()
    exit(1)

# Main Function
def main():
    global analyze
    global board
    global started
    global state
    global typing

    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)
    signal(SIGINT, safe_exit)

    btn01.when_pressed = btn01Press
    btn02.when_pressed = btn02Press
    btn03.when_pressed = btn03Press
    btn04.when_pressed = btn04Press
    btn05.when_pressed = btn05Press
    btn06.when_pressed = btn06Press
    btn07.when_pressed = btn07Press
    btn08.when_pressed = btn08Press
    btn09.when_pressed = btn09Press
    btn10.when_held = btn10Held

    while True:
        if started == False:
            board = chess.Board()
            started = True
            state = 0
        stockfish.set_fen_position(board.fen())
        analyze = True
        find_best_move = Thread(target = best_move, daemon = True)
        find_best_move.start()
        typing = True
        read_user_input = Thread(target = user_input, daemon = True)
        read_user_input.start()
        
        read_user_input.join()
        if board.is_checkmate() or board.is_stalemate() or board.is_insufficient_material() or board.is_repetition():
            if board.is_checkmate():
                lcd.text("Checkmate", rows)
            else:
                lcd.text("Draw", rows)
            state = -1
            started = False
            analyze = False
            typing = False
            btn05.wait_for_press()

if __name__ == '__main__': main()
