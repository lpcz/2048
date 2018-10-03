#2048 clone with the novelty of arbitrary board size (original game was 4x4)
#(c) 2017 Erik Szigeti, Márton Lipécz

import math
import random
import signal
from sys import exit
from os import name, system
import curses
import time

logo = \
' 222222      00000        44         88888  '+ \
'2     22   00     00     44        88     88' + \
'      22   00     00    44         88     88' + \
'  2222     00     00   44   44       88888  ' + \
'22         00     00   444444444   88     88' + \
'22         00     00        44     88     88' + \
'22222222     00000          44       88888  '
# 44x7

gameover ='''
█████ █████ █   █ ███   ████ █   █ ███ ████ 
██    █   █ ██ ██ █▃    █  █ █  █  █▃  █  █
██  █ █████ █ █ █ █     █  █  █ █  █   ███
█████ █   █ █   █ ███   ████   █   ███ █  █
'''
won ='''
    █         █  █████████   ██     ██
    ██   █   ██  █       █   ████   ██
     ██ ███ ██   █       █   ██  ██ ██
      ██   ██    █████████   ██    ███
'''
points = 0
sym = 0
win = None
logowin = None

def display_logo(s, color):
    logowin.clear()
    logowin.addstr(0, 0, s, color)
    logowin.refresh()

def display_points(points):
    y, x = win.getbegyx()
    height, width = win.getmaxyx()
    stdscr.addstr(y+height, x, "Points: "+str(points)) 

def display(field):
    """Prints out the playfield. It takes one argument which is a list."""
    side = int(math.sqrt(len(field))) # in number of elements (tiles)
        
    def pos():
        cy, cx = win.getyx()
        stdscr.addstr(0, 0, "cy: "+str(cy)+", cx: "+str(cx))

    def br():
        while True:
            c = stdscr.getch()
            if c == curses.KEY_RIGHT:
                break
        win.refresh()

    win.addstr(0, 0, '┏')
    for _ in range(side-1):
        win.addstr('━━━━━━')
        win.addstr('┳')
    win.addstr('━━━━━━')
    win.addstr('┓ ')

    for y in range(side):
        
        win.addstr('┃')
        for x in range(side):
            #stdscr.addstr(0, 0, "side: " + str(x))
            idx = y * side + x
            if field[idx] == 0:
                win.addstr(' '.center(6))
            else:
                n = field[idx]
                color = curses.color_pair(0)
                if n < 0:
                    field[idx] *= -1
                    n = field[idx]
                    color = curses.A_BOLD | curses.A_STANDOUT
                elif n == 4:
                    color = curses.color_pair(3)
                elif n == 8:
                    color = curses.color_pair(4)
                elif n >= 16:
                    color = curses.color_pair(1)
                
                #win.addstr(str(n).center(6), color)
                
                n = str(n)
                left = (6-len(n)) // 2
                right = 6 - (left + len(n))
                win.addstr(left*' ')
                win.addstr(n, color)
                win.addstr(right*' ')

            
            win.addstr('┃')
        win.addstr(' ')
        if y == side-1:
            break
        else: 
            win.addstr('┣')
            for _ in range(side-1):
                win.addstr('━━━━━━')
                win.addstr('╋')
            win.addstr('━━━━━━')
            win.addstr('┫ ')
    
    win.addstr('┗')
    for _ in range(side-1):
        win.addstr('━━━━━━')
        win.addstr('┻')
    win.addstr('━━━━━━')
    #pos()
    #br()
    win.addstr('┛')

    #win.border()
    win.refresh()


def GenerateField(N):
    """Generates the array of the field . Takes one argument (int) which is the row/column size of the field"""
    field = list(range(N * N))
    for i in range(N * N):
        field[i] = 0

    return field


def NewTile(field):
    """Generates a 2 or a 4 in a random place to the field . Takes a field (list) as an argument"""
    var = False
    while not var:
        temp = random.randrange(0, len(field), 1)
        if field[temp] == 0:
            r = random.randrange(0, 100, 1)
            if r > 80:
                field[temp] = -4
            else:
                field[temp] = -2
            
            var = True
    return field


def move(line):
    """Moves the numbers in one line according to the rules of 2048. Takes a line (list) as an argument"""
    length = len(line)
    pos = 0
    global points
    global sym
    while pos < len(
            line):  
        if (line[pos] == 0):
            del line[pos]
        else:
            pos = pos + 1
    if len(line) == 0:
        return [0] * length
    pos = 0
    while line[pos] != 0 and pos + 1 < len(line):
        if (abs(line[pos]) == abs(line[pos + 1])):
            line[pos] = line[pos] * 2
            if sym == 0:
                points = points + line[pos]
            del line[pos + 1]
        else:
            pos = pos + 1
    if len(line) < length:
        for _ in range(length - len(line)):
            line.append(0)
    return line


def Transform(field, dir):
    """Decides which direction the numbers should move and which function to use.
        Takes a field (list) and a direction (string) as arguments"""
    if dir == "w":
        field = TransformUpMovement(field)
    elif dir == "s":
        field = TransformDownMovement(field)
    elif dir == "a":
        field = TransformLeftMovement(field)
    elif dir == "d":
        field = TransformRightMovement(field)
    return field


def TransformRightMovement(field):
    """Gives the needed rows/columns to the move funcion and injects them back to the field afterwards.
     Takes a list as an argument"""
    i = 0
    side = int(math.sqrt(len(field)))
    while i < len(field):
        j = (i + side) - 1
        line = []
        for x in range(j, i - 1, -1):
            line.append(field[x])
        line = move(line)
        k = 0
        for x in range(j, i - 1, -1):
            field[x] = line[k]
            k = k + 1
        i = i + side
    return field


def TransformLeftMovement(field):
    """Gives the needed rows/columns to the move funcion and injects them back to the field afterwards.
     Takes a list as an argument"""
    i = 0
    side = int(math.sqrt(len(field)))
    while i < len(field):
        j = (i + side)
        line = []
        for x in range(i, j):
            line.append(field[x])

        line = move(line)
        k = 0
        for x in range(i, j):
            field[x] = line[k]
            k = k + 1
        i = i + side
    return field


def TransformUpMovement(field):
    """Gives the needed rows/columns to the move funcion and injects them back to the field afterwards.
     Takes a list as an argument"""
    i = 0
    side = int(math.sqrt(len(field)))
    while i < side:
        j = len(field) - side + i
        line = []
        l = i
        while l <= j:
            line.append(field[l])
            l = l + side

        line = move(line)
        j = len(field) - side + i
        l = i
        k = 0
        while l <= j:
            field[l] = line[k]
            l = l + side
            k = k + 1
        i = i + 1
    return field


def TransformDownMovement(field):
    """Gives the needed rows/columns to the move funcion and injects them back to the field afterwards.
     Takes a field (list) as an argument"""
    i = 0
    side = int(math.sqrt(len(field)))
    while i < side:
        j = len(field) - side + i
        line = []
        l = j
        while l >= i:
            line.append(field[l])
            l = l - side

        line = move(line)
        j = len(field) - side + i
        l = j
        k = 0
        while l >= i:
            field[l] = line[k]
            l = l - side
            k = k + 1
        i = i + 1
    return field


def WinCheck(field):
    """Check the field if the player has won. Takes a field (list) as argument"""
    for i in range(len(field)):
        if field[i] == 2048:
            return True
    return False


def FullCheck(field):
    """Checks the field if it is full. Takes a field (list) as argument"""
    temp_list = field[:]
    field_copy = field[:]
    if temp_list == Transform(field_copy, "w"):
        if temp_list == Transform(field_copy, "a"):
            if temp_list == Transform(field_copy, "s"):
                if temp_list == Transform(field_copy, "d"):
                    return True
    return False


def Turn(field):
    """Constantly asks for a direction until it is in a valid format. Takes a field (list) as argument"""
    dir = ''
    while True:
        c = stdscr.getch()
        if c == ord('q'):
            close_curses()
            exit(0)
        elif c == curses.KEY_UP:
            dir = "w" 
        elif c == curses.KEY_LEFT:
            dir = "a"
        elif c == curses.KEY_RIGHT:
            dir = "d"
        elif c == curses.KEY_DOWN:
            dir = "s"
        
        if TurnCheck(field, dir):
            return dir


def TurnCheck(field, dir):
    """Checks the given direction. Takes a field (list) and a direction (string) as arguments"""
    global sym
    sym = 1
    temp_list = field[:]
    field_copy = field[:]
    if temp_list == Transform(field_copy, dir):
        sym = 0
        return False
    else:
        sym = 0
        return True


def signal_handler(signal, frame):
    """Handles all signals with escaping. Takes a signal and a frames as arguments"""
    Clear()
    exit(0)


def SizeCheck():
    """Ask for a row/column size constatly until it is not a valid choice (choice >= 2)"""
    while True:
        try:
            curses.echo()            # Enable echoing of characters
            stdscr.addstr(0, 0, "Give a table square row/column size : ")
            stdscr.move(0, 38)
            size = stdscr.getstr(0, 38, 2)
            size = int(size)
            curses.noecho()
            if size < 2:
                raise ValueError
            return size
        except ValueError:
            stdscr.addstr(1, 0, "That is not a valid choice")


def Clear():
    """Clears the terminal."""
    stdscr.clear()

def Init_curses():
    """Main drawing function that initializes curses"""
    curses.noecho()
    curses.cbreak()
    curses.curs_set(False)
    stdscr.keypad(True)
    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)

    

def close_curses():
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

def Main(stdscr):
    signal.signal(signal.SIGINT, signal_handler)
    global sym
    global points
    Init_curses()
    size = SizeCheck()
    stdscr.erase()
    stdscr.refresh()
         
    
    field = GenerateField(size)
    field = NewTile(field)
    field = NewTile(field)

    side = int(math.sqrt(len(field))) # in number of elements (tiles)
    width = 7*side+2 #in character-cells
    height = 2*side+1
    # x and y coord of upper-left corner of win in order to be in the center:
    winy = math.floor((curses.LINES - height) / 2) + 5
    winx = math.floor((curses.COLS - width) / 2)
    
    global win
    global logowin
    win = curses.newwin(height, width, winy, winx)
    logowin = curses.newwin(8, 44, winy-9, math.floor((curses.COLS - 44) / 2))
    

    display_logo(logo, curses.color_pair(0))
    display(field)
    display_points(points)
    while True:
        dir = Turn(field)
        field = Transform(field, dir)
        field = NewTile(field)
        sym = 1
        if WinCheck(field):
            display(field)
            display_points(points)
            display_logo(won, curses.color_pair(3))
            break
        if FullCheck(field):
            display(field)
            display_points(points)
            display_logo(gameover, curses.color_pair(2))
            break
        sym = 0
        display(field)
        display_points(points)
    
    stdscr.getch()
    close_curses()

stdscr = curses.initscr()
curses.wrapper(Main)

