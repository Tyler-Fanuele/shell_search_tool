#!/usr/bin/env python3
from audioop import add
from importlib.metadata import files
import os
import re
import curses
from curses import wrapper
import sys

G = 32
R = 31
B = 34
# format
BLD = 1
UND = 4
REG = 0

def add_color(wString, color, form):
    temp1 = "\033[" + str(form) + ";" + str(color) + "m" + wString + "\033[0m" # add color to the given string
    return temp1

class Screen(object):
    UP = -1
    DOWN = 1

    def __init__(self, display, input, items, title, edge):
        """ Initialize the screen window
        This Class was taken and modified from 
        https://github.com/mingrammer/python-curses-scroll-example/blob/master/tui.py
        """
        self.window = None # window object for the screen

        self.width = 0 # screen width
        self.height = 0 # screen height

        self.title_offset = len(title) + 1 # Added by me, The title offset is the amount of space the title list
                                           # will take up
        self.title = title # Added by me, the list of strings that will be sequencially printed to the screen

        self.option = "get" # Added by me, the current option for the program. Init at "get"

        self.edge = edge # Added by me, the edge string to be printed at the edge of each list item

        self.init_curses() # Inits the curses objects

        self.display = display

        self.input = input

        self.items = items # the list of items, in this case our snips

        self.max_lines = curses.LINES - self.title_offset # This stores the max lines printable, goten when visual starts
        self.top = 0 # Keeps the top item index
        self.bottom = len(self.items) # keeps the last item index
        self.current = 0 # keeps the current item index
        self.page = self.bottom // self.max_lines # figures our how to allocate pages

    def init_curses(self):
        """Setup the curses"""
        self.window = curses.initscr() # inits the curses object
        self.window.keypad(True) # allows for keypad reading

        curses.noecho() 
        curses.cbreak()

        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)

        self.current = curses.color_pair(2) # sets color pair

        self.height, self.width = self.window.getmaxyx() # sets max width

    def run(self):
        """Continue running the TUI until get interrupted"""
        try:
            self.input(self) # gets input strings
        except KeyboardInterrupt:
            pass
        finally:
            curses.endwin() # ends program


    #scrole in the given direction
    def scroll(self, direction):
        """Scrolling the window when pressing up/down arrow keys"""
        # next cursor position after scrolling
        next_line = self.current + direction

        # Up direction scroll overflow
        # current cursor position is 0, but top position is greater than 0
        if (direction == self.UP) and (self.top > 0 and self.current == 0):
            self.top += direction
            return
        # Down direction scroll overflow
        # next cursor position touch the max lines, but absolute position of max lines could not touch the bottom
        if (direction == self.DOWN) and (next_line == self.max_lines) and (self.top + self.max_lines < self.bottom):
            self.top += direction
            return
        # Scroll up
        # current cursor position or top position is greater than 0
        if (direction == self.UP) and (self.top > 0 or self.current > 0):
            self.current = next_line
            return
        # Scroll down
        # next cursor position is above max lines, and absolute position of next cursor could not touch the bottom
        if (direction == self.DOWN) and (next_line < self.max_lines) and (self.top + next_line < self.bottom):
            self.current = next_line
            return

    def paging(self, direction):
        """Paging the window when pressing left/right arrow keys"""
        current_page = (self.top + self.current) // self.max_lines
        next_page = current_page + direction
        # The last page may have fewer items than max lines,
        # so we should adjust the current cursor position as maximum item count on last page
        if next_page == self.page:
            self.current = min(self.current, self.bottom % self.max_lines - 1)

        # Page up
        # if current page is not a first page, page up is possible
        # top position can not be negative, so if top position is going to be negative, we should set it as 0
        if (direction == self.UP) and (current_page > 0):
            self.top = max(0, self.top - self.max_lines)
            return
        # Page down
        # if current page is not a last page, page down is possible
        if (direction == self.DOWN) and (current_page < self.page):
            self.top += self.max_lines
            return
def input_stream(Screen):
    """Waiting an input and run a proper method according to type of input"""
    while True: # runs until input is recieved
        Screen.display(Screen)

        ch = Screen.window.getch() # gets the key pressed as a char
        if ch == curses.KEY_UP: # looks for up keypress, will call scroll function with up
            Screen.scroll(Screen.UP)
        elif ch == curses.KEY_DOWN: # looks for down keypress, will call scroll function with down
            Screen.scroll(Screen.DOWN)
        elif ch == curses.KEY_LEFT: # looks for left keypress, will call page function with up
            Screen.paging(Screen.UP)
        elif ch == curses.KEY_RIGHT: # looks for right keypress, will call page function with down
            Screen.paging(Screen.DOWN)
        elif ch == ord('q'): # if q then quit the program
            break
        elif ch == curses.KEY_ENTER or ch == 10 or ch == 13: # if the enter key is pressed
            os.system("code " + Screen.items[Screen.current])


def snip_display(Screen):
    """Display the items on window"""
    Screen.window.erase() # erase the window for future writing
    for title_index, string in enumerate(Screen.title): # print the contents of the title strings given, in order
        Screen.window.addstr(title_index, 0, Screen.edge + string, curses.color_pair(1))
    #for x, s in enumerate(Screen.items[Screen.current][1]): 
    #    Screen.window.addstr(x + 5 + Screen.title_offset, 50, s, curses.color_pair(1))# print the contents of the snip strings given, in order
    for idx, item in enumerate(Screen.items[Screen.top:Screen.top + Screen.max_lines]): # start loop on the list of snips
        # Highlight the current cursor line
        if idx == Screen.current: 
            Screen.window.addstr(idx + Screen.title_offset, 0,
                               Screen.edge + item.ljust(42), curses.color_pair(2)) # print the current index item in
        else:                                                                               # different color
            Screen.window.addstr(idx + Screen.title_offset,
                               0, Screen.edge + item.ljust(42), curses.color_pair(1))      # print the rest
    Screen.window.refresh()  # refresh the page

def snip_visual(wanted, dict):
    print(add_color("===\n=== Entering visual mode.", G, REG))
    wrapper(visual, wanted, dict)
    print(add_color("===\n=== Exiting visual mode.", G, REG))

# internal visual function
def visual(stdscr, wanted, l):

    # turn the dictionary into a list so we can access by iterator
    # init a screen object with our list of snips, our list of strings for the title and the edge string
    screen = Screen(snip_display, input_stream, l, ["Title", "Wanted word: " + wanted], "=== ")
    screen.run()

def return_like_items(dict, string):
    return_dict = []
    for key in dict:
        if re.search(r"\W*(" + string + ")\W*", key, re.IGNORECASE):
            return_dict.append(key)
    return return_dict


def main():
    path = os.getcwd()
    fname = []
    wanted = sys.argv[1]
    string = ""
    if not len(sys.argv) <= 2:
        string = sys.argv[2]
    print(string)

    for root,d_names,f_names in os.walk(path):
        if wanted == "dir":
            for d in d_names: # gets directorty names
                fname.append(os.path.join(root, d))
        elif wanted == "file":
            for f in f_names: # gets file names
                fname.append(os.path.join(root, f))
        elif wanted == "all":
            for f in f_names: # gets file names
                fname.append(os.path.join(root, f)) 
            for d in d_names: # gets directorty names
                fname.append(os.path.join(root, d))     
        else:
            print(add_color("=== That option is not supported", R, BLD))
            return

    retlist = return_like_items(fname, string)
    
    print(add_color("=== Shell Search Tool\n=== Copyright 2022, Tyler Fanuele", G, REG))
    snip_visual(string, retlist)
main()