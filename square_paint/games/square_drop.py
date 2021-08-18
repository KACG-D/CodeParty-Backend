
    
class Game():
    start_point = [[2,2,0],[2,9,0],[9,2,0],[9,9,0]]
    def __init__(self,names):
        self.p_num = 4
        self.max_x = 10
        self.max_y = 10
        self.max_z = 5
        self.players = [Player(name,Game.start_point[i]) for i,name in enumerate(names)]
        self.tiles = Tiles(self.max_x,self.max_y,self.max_z)
        self.turn_num = 0
        self.helper = Helper(self.tiles,self.players,self)

        #初期位置のちぇっく
        for player in self.players:
            self.tiles.check_player_move(player,turn_num=0)



    def get_helper(self):
        return self.helper

    #actionを受け取る
    def do_action(self,p_num,action):
        player = self.players[p_num]
        player.move(action)#移動する
        self.tiles.check_player_move(player,self.turn_num)# 移動したときどうなるか
    
    #tileを更新する
    def next_turn(self):
        self.turn_num += 1
        self.tiles.update()

    #一人だけ生きてたらtrue
    def is_end(self):
        count = 0
        for player in self.players:
            if player.is_alive:
                count += 1
        return count <= 1

    # logを返す
    def get_log(self):
        log = {
            "turn_num":self.turn_num,
            "tiles": self.tiles.to_log(),
            "players": [player.to_log() for player in self.players] 
        }
        return log

    #最終結果のlog
    def get_result_log(self):
        ranking = []
        order_dead_turn_num = list()
        for p in self.players:
            print(p.dead_turn_num)
            if p.is_alive == True:
                ranking.append({"name":p.name,"order":1})
                order_dead_turn_num.append(99999)#ダミー
                continue
            order_dead_turn_num.append(p.dead_turn_num)
        order_dead_turn_num =list(reversed(list(sorted(order_dead_turn_num))))
        print(order_dead_turn_num)
        for p in self.players:
            print(p.name)
            print(p.dead_turn_num)
            if p.is_alive == False:
                rank = order_dead_turn_num.index(p.dead_turn_num)
                ranking.append({"name":p.name,"order":rank+1})
        print(ranking)
        return ranking

class Tiles():
    def __init__(self,x_max,y_max,z_max):
        self.x_max = x_max
        self.y_max = y_max
        self.z_max = z_max
        self.tiles = []
        for x in range(x_max+2):
            y_li = []
            for y in range(y_max+2):
                x_li = []
                for z in range(z_max+1):
                    x_li.append(Tile())
                y_li.append(x_li)
            self.tiles.append(y_li)
        self._create_dead_area()#周りのマスを空にしておく
        self.pressed_tiles = []#更新が必要なタイルたち
    
    #周りに空のエリアを作る
    def _create_dead_area(self): 
        for x in range(self.x_max+2):
            for y in range(self.y_max+2):
                for z in range(self.z_max+1):
                    if x == 0 or x == self.x_max+1 or y == 0 or y == self.y_max+1 or z == self.z_max:
                        self.tiles[x][y][z].is_alive = False

    #タイルを更新する 死んだらpressedtileから削除しておく
    def update(self):
        for i in reversed(range(len(self.pressed_tiles))):
            self.pressed_tiles[i].update()
            if self.pressed_tiles[i].is_alive == False:
                self.pressed_tiles.pop(i)

    #行動に応じてplayerを行動させる
    def check_player_move(self,player,turn_num):
        point = player.get_point()
        tile = self.tiles[point[0]][point[1]][point[2]]
        if point[2] == self.z_max: #最下層で生きているなら問答無用で殺す
            if player.is_alive == True:
                player.kill(turn_num)
        else:
            if tile.is_alive: # タイルがあればfalling = Falseなければfalling
                player.is_falling = False
                tile.is_pressed = True#タイルを踏んだのでtrueにする
                self.pressed_tiles.append(tile)
            else:
                player.is_falling = True

    # 配列にする
    def to_log(self):
        tiles_arr = []
        for x in range(self.x_max+2):
            li_y = []
            for y in range(self.y_max+2):
                li_z = []
                for z in range(self.z_max+1):
                    li_z.append(self.tiles[x][y][z].is_alive)
                li_y.append(li_z)
            tiles_arr.append(li_y) 
        return tiles_arr
    
    def get_tile(self,point):
        try :
            return self.tiles[point[0]][point[1]][point[2]]
        except :
            dummy =  Tile()
            dummy.is_alive = False
            return dummy

class Tile():
    dead_count = 1 # タイルが消えるまでの時間
    def __init__(self):
        self.is_alive = True
        self.is_pressed = False
        self.count = Tile.dead_count
        
    #countを小さくする　0になったら消える
    def update(self):
        self.count = self.count -1
        if self.count == 0:
            self.is_alive = False
    
    #利用可能ならtrue 利用不可能ならfalse
    def get_is_alive(self):
        return self.is_alive

class Player():
    def __init__(self,name,start_point):
        self.name = name
        self.point = start_point
        self.is_alive = True # 生きているか
        self.is_falling = False # 落ちているか
        self.before_action = 0
        self.dead_turn_num = 0
    #移動する
    def move(self,action):
        self.before_action = action
        if self.is_alive:
            if self.is_falling:#落ちている状況なら落ちる
                self.point = [self.point[0], self.point[1], self.point[2]+1]
            elif action == 0:
                self.point =  [self.point[0], self.point[1]-1, self.point[2]]
            elif action == 1:
                self.point =  [self.point[0], self.point[1]+1, self.point[2]]
            elif action == 2:
                self.point =  [self.point[0]-1, self.point[1], self.point[2]]
            elif action == 3:
                self.point =  [self.point[0]+1, self.point[1], self.point[2]]
            elif action == 4:
                self.point =  [self.point[0], self.point[1], self.point[2]]
            else:
                print(action)
                print(self.name)
                print("Action Error")
    
    def to_log(self):
        return {
            "name": self.name,
            "point": self.point,
            "is_alive": self.is_alive,
            "is_falling": self.is_falling
        }

    def get_point(self):
        return self.point

    def kill(self,turn_num):
        self.is_alive = False
        self.dead_turn_num = turn_num



class Helper():
    def __init__(self,tiles,players,game):
        self.tiles = tiles
        self.players = players
        self.game = game
    def labeling(self,level):
        #level層目をラベリングしてラベリング結果の２次元配列を返す
        x_max = self.tiles.x_max+2
        y_max = self.tiles.y_max+2

        labeled = [[(i*x_max+j if self.tiles.tiles[i][j][level].is_alive else -1)for j in range(y_max)] for i in range(x_max)]
        changed = True
        while changed:
            changed= False
            for i in range(x_max):
                for j in range(y_max):
                    candidate = []
                    if(labeled[i][j] == -1):
                        continue
                    if(i>=1 and self.tiles.tiles[i-1][j][level].is_alive):
                        candidate+=[labeled[i-1][j]]
                    if(j>=1 and self.tiles.tiles[i][j-1][level].is_alive):
                        candidate+=[labeled[i][j-1]]
                    if(i<=self.tiles.y_max-2 and self.tiles.tiles[i+1][j][level].is_alive):
                        candidate+=[labeled[i+1][j]]
                    if(j<=self.tiles.x_max-2 and self.tiles.tiles[i][j][level].is_alive):
                        candidate+=[labeled[i][j+1]]
                    mini = min(candidate)
                    if(mini < labeled[i][j]):
                        changed = True
                        labeled[i][j] = mini
        return labeled

    def get_tiles(self):
        return self.tiles
    
    
    def get_players(self):
        return self.players
    
    #敵の座標配列
    def get_enemy_players(self,name):
        stack = []
        for p in self.players:
            if p.name != name:
                stack.append(p)
        return stack

    #自分の座標
    def get_my_player(self,name):
        for p in self.players:
            if p.name == name:
                return p
    
    def get_my_point(self,name):
        for p in self.players:
            if p.name == name:
                return p.point


    #距離の差分* 敵３人
    def get_distance_points_from_me(self,name):
        stack = []
        you = self.get_your_player(name)
        yp = you.get_point()
        for p in self.get_enemy_players():
            pp = p.get_point()
            stack.append([yp[0]-pp[0],yp[1]-pp[1],yp[2]-pp[2]])
        return stack
    
    def get_distance_points_from_point(self,point):
        stack = []
        for p in self.get_enemy_players():
            pp = p.get_point()
            stack.append([point[0]-pp[0],point[1]-pp[1],point[2]-pp[2]])
        return stack

    def get_up_point(self,point):
        return [point[0],point[1]-1,point[2]]
    def get_down_point(self,point):
        return [point[0],point[1]+1,point[2]]
    def get_left_point(self,point):
        return [point[0]-1,point[1],point[2]]
    def get_right_point(self,point):
        return [point[0]+1,point[1],point[2]]

    def get_up_tile(self,name):
        point = self.get_my_point(name)
        return self.tiles.get_tile(self.get_up_point(point))
    def get_down_tile(self,name):
        point = self.get_my_point(name)
        return self.tiles.get_tile(self.get_down_point(point))
    def get_left_tile(self,name):
        point = self.get_my_point(name)
        return self.tiles.get_tile(self.get_left_point(point))
    def get_right_tile(self,name):
        point = self.get_my_point(name)
        return self.tiles.get_tile(self.get_right_point(point))
    
    def get_players_around_n_tiles(self,name,dis):
        stack = []
        me = self.get_my_player(name)
        for p in self.get_enemy_players(name):
            if p.point[2] == me.point[2] - (abs(p.point[0] - me.point[0]) > dis or abs(p.point[1]-me.point[1]) > dis ) :
                stack.append(p)
        return stack

    #ターン数を取得する
    def get_turn_num(self):
        return self.game.turn_num

    #dist_pointに最短距離で移動するときに向かうべき方向を返す
    def get_toward_distination(self,frompoint, dist_point):
        x = frompoint[0]-dist_point[0]
        y = frompoint[1]-dist_point[1]
        if x  == 0 and y == 0:
            return 5
        if abs(x) >= abs(y):
            if x >0:
                return 2
            if x < 0:
                return 3
        if abs(y) > abs(x):
            if y >0:
                return 0
            if y < 0:
                return 1
    
    #特定プレイヤーの前回の行動を取る
    def get_before_action(self,name):
        p = self.get_my_player(name)
        return p.before_action
    
    #周囲のtile一覧を取得 上下左右の順
    def get_around_tiles(self,name):
        return [self.get_up_tile(name),self.get_down_tile(name),self.get_left_tile(name),self.get_right_tile(name)]


