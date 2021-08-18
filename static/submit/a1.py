import sys
sys.path.append('../')
from codeparty_simulator.square_drop import Helper,Player,Tile,Tiles

import  random as rd

name = "Sample2" #名前を書く
def action(helper):
    stack = []
    if helper.get_up_tile(name).is_alive :
        stack.append(0)
    if helper.get_down_tile(name).is_alive:
        stack.append(1)
    if helper.get_left_tile(name).is_alive:
        stack.append(2)
    if helper.get_right_tile(name).is_alive:
        stack.append(3)
    if len(stack) == 0:
        return 4
    else:
        return stack[rd.randrange(len(stack))]