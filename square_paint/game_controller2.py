from importlib import import_module
from pprint import pprint
from importlib import import_module

class GameController():
    def __init__(self,players,gamename): # players:plyaerモジュール, gamename: game名
        self.players = players
        self.gameinfo = []
        self.game_module = import_module("square_paint.games."+gamename)

    def start(self):
        game = self.game_module.Game([player.name for player in self.players])
        while True:
            game.next_turn()# タイル更新が入る。前回のactionが反映される
            helper = game.get_helper() #ヘルパーインスタンスを受け取る
            actions = list()

            if game.is_end():
                self.gameinfo.append(game.get_log())
                for i in range(len(self.gameinfo)-1):
                    for j in range(len(self.gameinfo[i]["players"])):
                        self.gameinfo[i]["players"][j]["is_hit"] = self.gameinfo[i+1]["players"][j]["is_hit_wall"]
                        if self.gameinfo[i+1]["players"][j]["count_stun"] == 3:
                            self.gameinfo[i]["players"][j]["is_hit"] = True#次ぶつかりますよ
                        
                result = game.get_result_log()

                return {"gameinfo":self.gameinfo,"ranking":result}

            for i,player in enumerate(self.players):# playerが行動を決定する
                helper.set_player_index(i)
                actions.append(player.action(helper))
            
            new_log = game.get_log() #gameのログを追加する
            for i,action in enumerate(actions): # playerのログを追加する
                new_log["players"][i]["action"] = action


            self.gameinfo.append(new_log)# logにgameの情報とactionを書き込む

            pprint(new_log["turn_num"])
            for i,action in enumerate(actions):
                game.do_action(i,action)#ユーザが移動する。前回踏まれているところは消えているので落ちる
            
