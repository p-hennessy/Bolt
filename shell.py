#!/usr/bin/env python

from string import printable
from curses import erasechar, wrapper

PRINTABLE = map(ord, printable)

def input(stdscr):
    ERASE = input.ERASE = getattr(input, "ERASE", ord(erasechar()))
    Y, X = stdscr.getyx()
    s = []

    while True:
        c = stdscr.getch()

        if c in (13, 10):
            break
        elif c == ERASE:
            y, x = stdscr.getyx()
            if x > X:
                del s[-1]
                stdscr.move(y, (x - 1))
                stdscr.clrtoeol()
                stdscr.refresh()
        elif c in PRINTABLE:
            s.append(chr(c))
            stdscr.addch(c)

    return "".join(s)

def prompt(stdscr, y, x, prompt=">>> "):
    stdscr.move(y, x)
    stdscr.clrtoeol()
    stdscr.addstr(y, x, prompt)
    return input(stdscr)

def main(stdscr):
    Y, X = stdscr.getmaxyx()

    print Y, X

    lines = []
    max_lines = (Y - 3)

    stdscr.clear()

    while True:
        s = prompt(stdscr, (Y - 1), 0)  # noqa
        if s == ":q":
            break

        # scroll
        if len(lines) > max_lines:
            lines = lines[1:]
            stdscr.clear()
            for i, line in enumerate(lines):
                stdscr.addstr(i, 0, line)

        stdscr.addstr(len(lines), 0, s)
        lines.append(s)

        stdscr.refresh()

wrapper(main)
