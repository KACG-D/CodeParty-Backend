import sys
sys.path.append('../')
from square_drop import Helper,Player,Tile,Tiles
###ここよりうえは変更しない

import  random as rd
#実名を下に書いてください
#氏名: 
name = "Avoter Name" #アバター名に書き換えてください


def action(helper):
    #以下にロジックを書いてください
    if helper.get_up_tile(name).is_alive:
        return 0
    elif helper.get_down_tile(name).is_alive:
        return 1
    elif helper.get_left_tile(name).is_alive:
        return 2
    elif helper.get_right_tile(name).is_alive:
        return 3
    return 4
