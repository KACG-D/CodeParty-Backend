# coding: UTF-8
from importlib import import_module
import json
import os
from codeparty_simulator.game_controller import GameController

player_paths= ["players.yourcode","players.sample2","players.sample3","players.sample4"]
player_num = 4


if __name__ == '__main__':
    players = [import_module(path) for path in player_paths ]
    
    g_con = GameController(players)
    log = g_con.start()
    with open('./log/input.json', 'w') as f:
        json.dump({"game_info":log}, f, indent=4)

def execute(modules,room_id):
    player_paths = modules
    players = [import_module(path) for path in player_paths ]
    
    g_con = GameController(players)
    log = g_con.start()
    print(os.listdir(path='/'))
    filename = '/static/json/'+str(room_id)+'.json'
    with open("."+filename, 'w') as f:
        json.dump({"game_info":log}, f, indent=4)
    return filename