import sys
sys.path.append('../')
from square_drop import Helper,Player,Tile,Tiles

import  random as rd

name = "Sample3"

act_li = [0,3,1,2]
idx = 0
def action(helper):
    global idx
    my_point = helper.get_my_point(name)
    around_tiles = helper.get_around_tiles(name)
    is_alive_count = sum([ 1 if tile.is_alive else 0 for tile in around_tiles])

    if my_point[0] == 5 and my_point[1] == 5 and my_point[2] !=4:
        return 4
    elif my_point[2] != 4:
        toward = helper.get_toward_distination(my_point,[5,5])
        return toward
    else:
        if is_alive_count >= 3:
            idx = (idx+1 )% 4
        print(act_li) 
        return act_li[idx]

    