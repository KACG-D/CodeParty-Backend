import sys
sys.path.append('../')
from square_drop import Helper,Player,Tile,Tiles
###ここよりうえは変更しない

import  random as rd
#実名を下に書いてください
#氏名: 98
name = "Curryu" #アバター名に書き換えてください


def action(helper):
    #以下にロジックを書いてください
    a=helper.get_my_point(name)
    print(a)
    if a[2]==0:
        return 4
    elif a[2]==1:
        return 4
    elif a[2]==2:
        return 4
    else:
        ok_tile=[]
        if helper.get_up_tile(name).is_alive:
            ok_tile.append(0)
        if helper.get_down_tile(name).is_alive:
            ok_tile.append(1)
        if helper.get_left_tile(name).is_alive:
            ok_tile.append(2)
        if helper.get_right_tile(name).is_alive:
            ok_tile.append(3)
        size=len(ok_tile)
        if size==0:
            return 4
        else:
            print(ok_tile)
            x = rd.randint(0,size-1)
            print(x)
            if ok_tile[x]==0:
                return 0
            elif ok_tile[x]==1:
                return 1
            elif ok_tile[x]==2:
                return 2
            else:
                return 3

    #人の下をくりぬく
    #helper.get_enemy_players(name):