import curses
import curses.textpad
import random
import signal
import sys
import time


win = curses.initscr()

curses.start_color()
curses.nonl()
curses.noecho()
curses.cbreak()
win.keypad(1)

curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_GREEN)
curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)
curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)
curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE)

def maketextbox(screen, h,w,y,x,value="",deco=None,underlineChr=curses.ACS_HLINE,textColorpair=0,decoColorpair=0):
    nw = curses.newwin(h,w,y,x)
    txtbox = curses.textpad.Textbox(nw)
    if deco=="frame":
        screen.attron(decoColorpair)
        curses.textpad.rectangle(screen,y-1,x-1,y+h,x+w)
        screen.attroff(decoColorpair)
    elif deco=="underline":
        screen.hline(y+1,x,underlineChr,w,decoColorpair)

    nw.addstr(0,0,value,textColorpair)
    nw.attron(textColorpair)
    screen.refresh()
    return txtbox

(win_height, win_width) = win.getmaxyx()

center = int(win_width/2)
middle = int(win_height/2)

debug_win = curses.newwin(1, win_width, win_height-1, 0)

def dlog(txt):
    debug_win.clear()
    debug_win.addstr(0, 0, txt)
    debug_win.refresh()

title_text = "SADARI"
title_size = len(title_text)
title_height = len(title_text.split('\n'))
margin = 2

dlog("size : %d, height : %d" % (title_size, title_height))

win.refresh()
title_win = curses.newwin(title_height, title_size+1, margin, center-title_size/2)
title_win.addstr(0, 0, "SADARI")
title_win.refresh()

player_width = 6
game_margin = 10
game_padding = 1
game_height = win_height - title_height - game_margin * 2
game_width = win_width - game_margin * 2
max_people = (game_width - game_padding*2) / (player_width + game_padding*2 + 2)

win.addstr(5, center - 37, "Insert Number of Peoples (2~%3d) : " % max_people)

txt_box = maketextbox(win, 1, 5, 5, center-2)

def onelinebox(ks):
    dlog(str(ks))
    if ks == 13:
        return 7
    return ks

people = []

count = 0
while True:
    txt = txt_box.edit(onelinebox)
    txt = txt.strip()
    if not txt.isdigit():
        dlog("It is not number.")
        continue
    count = int(txt)
    if count > max_people:
        dlog("It is must be 2 ~ %3d" % max_people)
        continue
    break
game_win = curses.newwin(game_height, game_width, title_height + game_margin, game_margin)
#game_win.bkgd(curses.color_pair(1))
game_win.refresh()


sadari_padding = 2
sadari_columns = count -1
sadari_max_rows = 12 if (game_height-sadari_padding*2) > 24 else (game_height-sadari_padding*2) / 2
sadari_row_height = (game_height - sadari_padding * 2) / sadari_max_rows

sadari = [[0 for x in range(sadari_max_rows)] for x in range(sadari_columns)]
old_v = []
for c in xrange(sadari_columns):
    v = [x for x in range(sadari_max_rows) if x not in old_v]
    vbars = random.sample(v, random.randint(3, 5))
    for b in vbars: sadari[c][b] = 1
    old_v = vbars
'''
sadari_columns = count-1
sadari_max_rows = (game_height-3) / 2

sadari = [[0 for x in range(sadari_max_rows)] for x in range(sadari_columns)]
vbars = []
max_vbar_count = (sadari_max_rows-2)/2
for c in xrange(sadari_columns):
    all_vbar = range(2, sadari_max_rows-2, 2)
    for i in vbars: all_vbar.remove(i)
    max_choose = len(all_vbar) - 3 if len(all_vbar)-3 > 2 else len(all_vbar)
    choose = random.randint(3, max_choose)
    vbars = random.sample(all_vbar, choose)
    for r in vbars:
        sadari[c][r] = 1
'''

odd_fix = count % 2 != 0 if player_width/2 else 0
player_start_y = game_height - game_padding - 3
player_start_x = win_width / 2 - count / 2 * (player_width + game_padding*2) - odd_fix

abcs = "abcdefghijklmnopqrstuvwxyz"
def n2abc(n):
    abc = ""
    while n > 0:
        nn = n % (len(abcs)+1)
        abc += abcs[nn-1]
        n -= nn+1
    return abc

def drawbox(win, h, w, y, x, txt, color=0):
    win.attron(color)
    curses.textpad.rectangle(win, y, x, y+h+1, x+w)
    win.addstr(y+1, x + w/2 - len(txt)/2, txt)
    win.attroff(color)

class Box:
    def __init__(self, index, win, h, w, y, x, txt, color=0):
        self.index = index
        self.win = win
        self.coord = [h+2,w+2,y,x]
        self.txt = txt
        self.color = color
        drawbox(win, h, w, y, x, txt, color)

    def set_color(self, color=0):
        self.color=color
        (h, w, y, x) = self.coord
        drawbox(self.win, h-2, w-2, y, x, self.txt, self.color) 

    def find_path(self, color=0):
        cindex = self.index

        (h, w, y, x) = columns[cindex][0].coord
        px = x + w / 2 -1
        py = y + h
        self.win.vline(py, px, curses.ACS_VLINE, sadari_padding, color)
        self.win.refresh()

        for i in range(sadari_max_rows):
            (h, w, y, x) = columns[cindex][0].coord
            px = x + w / 2 -1
            py = y + h + i * sadari_row_height + sadari_padding
            top = h + y
            curved = 0
            if cindex < len(sadari) and sadari[cindex][i] == 1:
                self.win.hline(py, px, curses.ACS_LLCORNER, 1, color)
                self.win.hline(py, px+1, curses.ACS_HLINE, player_width+1, color)
                self.win.hline(py, px+player_width+2, curses.ACS_URCORNER, 1, color)
                cindex+=1
                curved = 1
            elif cindex > 0 and sadari[cindex-1][i] == 1:
                self.win.hline(py, px, curses.ACS_LRCORNER, 1, color)
                self.win.hline(py, px-player_width-1, curses.ACS_HLINE, player_width+1, color)
                self.win.hline(py, px-player_width-2, curses.ACS_ULCORNER, 1, color)
                cindex-=1
                curved = 1

            self.win.refresh()
            time.sleep(0.1)

            (h, w, y, x) = columns[cindex][0].coord
            px = x + w / 2 -1
            py = y + h + i * sadari_row_height + sadari_padding + curved
            top = h + y
            self.win.vline(py, px, curses.ACS_VLINE, sadari_row_height, color)

            self.win.refresh()
            time.sleep(0.1)

        (h, w, y, x) = columns[cindex][0].coord
        px = x + w / 2 -1
        py = y + h + sadari_max_rows * sadari_row_height + sadari_padding
        self.win.vline(py, px, curses.ACS_VLINE, sadari_padding, color)
        self.win.refresh()

        columns[cindex][1].set_color(color)


def init_sadari(choose):
    columns = [[] for x in range(count)]
    for i in range(count):
        num_txt = str(i+1)
        player_box_start_x = player_start_x + (game_padding*2 + player_width)*i - player_width/2
        #print >> sys.stderr, "%d, %d, %d, %d" % (0, player_box_start_x, 2, player_box_start_x + player_width)

        columns[i] = [Box(i, game_win, 1, player_width, 0, player_box_start_x, num_txt),
                   Box(i, game_win, 1, player_width, player_start_y-1, player_box_start_x, num_txt)]
        game_win.vline(3, player_box_start_x + player_width/2, curses.ACS_VLINE, player_start_y-4)

        if i < count-1:
            for j in xrange(sadari_max_rows):
                if sadari[i][j] == 1:
                    top = columns[i][0].coord[0] + columns[i][0].coord[2]
                    game_win.hline(top + sadari_padding + j*sadari_row_height, player_box_start_x + player_width/2+1, curses.ACS_HLINE, player_width+1, curses.color_pair(4)) 

    columns[choose][0].set_color(curses.color_pair(4))
    return columns


try:
    position = 0
    columns = init_sadari(position)
    game_win.refresh()
    
    while True:
        c = win.getch()
        if c == 260 or c == 261:
            old_p = position
            if c == 260:
                position = position -1 if position > 0 else len(columns)-1
            elif c == 261:
                position = position +1 if position < len(columns)-1 else 0
            columns[old_p][0].set_color(curses.color_pair(0))
            columns[position][0].set_color(curses.color_pair(4))
        elif c == 13:
            game_win.clear()
            columns = init_sadari(position)
            columns[position][0].find_path(curses.color_pair(3))

                
        game_win.refresh()

finally:
    curses.nl()
    curses.nocbreak()
    win.keypad(0)
    curses.echo()
    curses.endwin()
