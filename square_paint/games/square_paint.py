
    
class Game():
    start_point = [[2,2],[2,9],[9,2],[9,9]]
    def __init__(self,names):
        self.p_num = 4
        self.max_x = 10
        self.max_y = 10
        self.players = [Player(i,name,Game.start_point[i]) for i,name in enumerate(names)]
        self.tiles = Tiles(self.max_x,self.max_y,self.p_num)
        self.turn_num = 0

        #初期位置のちぇっく
        for i,player in enumerate(self.players):
            self.tiles.change_color(self.players) #タイルの色を変える

    def get_helper(self):
        return Helper(self.tiles,self.players,self)

    #actionを受け取る
    def do_action(self,p_idx,action):
        player = self.players[p_idx]
        player.move(action)#移動さきの座標を取得するだけ

    #tile playerを更新する
    def next_turn(self):
        self.turn_num += 1

        for p in self.players:
            p.update()#スタンのカウントをへらす、wall=falseにする

        for p in self.players:
            p.check_stun(self.players) #同じマスにいる人はスタンさせてキックバックする。
            p.check_wall(self.tiles) #壁にぶつかってる人はスタンさせてキックバックする

        
        self.tiles.change_color(self.players) #タイルの色を変える
        scores = self.tiles.get_scores()
        for i,p in enumerate(self.players):
            p.score = scores[i]

    #200 ターン後true
    def is_end(self):
        if self.turn_num == 100:
            return True
        else:
            return False

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
        orders = []
        score_order = set(self.tiles.get_scores())
        order= 1
        for s in list(score_order):
            count = 0
            for p in self.players:
                if s == p.score:
                    orders.append({"name":p.name,"order":order})
                    count += 1
            order += count
        return orders

class Tiles():
    def __init__(self,x_max,y_max, p_num):
        self.x_max = x_max
        self.y_max = y_max
        self.p_num = p_num
        self.tiles = []
        for _ in range(x_max+2):
            self.tiles.append([ Tile(p_num) for _ in range(y_max+2) ])
        self._create_dead_area()#周りのマスを空にしておく
        self.to_log()
        
    #周りに空のエリアを作る
    def _create_dead_area(self): 
        for x in range(self.x_max+2):
            for y in range(self.y_max+2):
                    if x == 0 or x == self.x_max+1 or y == 0 or y == self.y_max+1 :
                        self.tiles[x][y].is_alive = False

    #タイルの色を更新する
    def change_color(self,players):
        for p in players:
            if not p.is_stun:#タイルをその人の色に
                self.get_tile(p.get_point()).status = p.id+1


    # 配列にする
    def to_log(self):
        tiles_arr = []
        for y in range(1,self.y_max+1):
            for x in range(1,self.x_max+1):
                tiles_arr.append(self.tiles[x][y].status)
        return tiles_arr
    
    def get_tile(self,point):
        return self.tiles[point[0]][point[1]]
    #score配列を返す
    def get_scores(self):
        counter = [0]*self.p_num
        for x in range(1,self.x_max+1):
            for y in range(1,self.y_max+1):
                if self.tiles[x][y].status != 0:
                    counter[self.tiles[x][y].status-1] += 1
        return counter
    
    def get_status(self):
        tiles = []
        temp = list()
        for i, status in enumerate(self.to_log()):
            temp.append(status)
            if i % self.x_max == self.x_max-1:
                tiles.append(temp)
                temp = list()
        return tiles

class Tile():
    dead_count = 1 # タイルが消えるまでの時間
    def __init__(self,p_num):
        self.is_alive = True #場内かどうか
        self.status = 0 # 0:未着色, 1:p0, 2:p1, 3,p2, 4:p3,
        
    #countを小さくする 0になったら消える
    def pressed(self,p_idx):
        self.status = p_idx
    
    #利用可能ならtrue 利用不可能ならfalse
    def get_is_alive(self):
        return self.is_alive

class Player():
    def __init__(self,id,name,start_point):
        self.id = id
        self.name = name+" #"+str(id)
        self.point = start_point
        self.before_action = 0
        self.before_point = start_point
        self.is_stun = False
        self.count_stun = 0
        self.score = 1
        self.is_hit_wall = False

    #移動する
    def move(self,action):
        self.before_action = action
        self.before_point = self.point
        if not self.is_stun:
            if action == 0:
                self.point =  [self.point[0], self.point[1]-1]
            elif action == 1:
                self.point =  [self.point[0], self.point[1]+1]
            elif action == 2:
                self.point =  [self.point[0]-1, self.point[1]]
            elif action == 3:
                self.point =  [self.point[0]+1, self.point[1]]
            elif action == 4:
                self.point =  [self.point[0], self.point[1]]

    #スタンさせる
    def stun(self):
        self.is_stun = True
        self.count_stun = 3

    #フラグの更新
    def update(self):
        self.is_hit_wall = False
        if self.is_stun == True:
            self.count_stun -=1
            if self.count_stun == 0:
                self.is_stun = False
    #スタンチェック
    def check_stun(self,players):
        for p in players:#スタン判定
            if p.id != self.id and p.get_point() == self.get_point(): #座標が同じプレイヤーがいたら
                p.stun()# 両者スタン
                self.stun()#両者stun
                p.point = p.before_point
                self.point = self.before_point

    #壁チェック
    def check_wall(self,tiles):
        if tiles.get_tile(self.point).is_alive == False:# 壁にあたってたら
            self.is_hit_wall = True #壁ヒット= true
            self.point = self.before_point #プレイヤー座標を移動前に



    def to_log(self):
        return {
            "name": self.name,
            "point": self.point,
            "is_stun": self.is_stun,
            "count_stun": self.count_stun,
            "is_hit_wall": self.is_hit_wall,
            "score": self.score,

        }
        
    def get_point(self):
        return self.point




class Helper():
    def __init__(self,tiles,players,game):
        self.tiles_ori = tiles
        self.tiles = tiles.get_status()
        self.player_list = players
        self.game = game
        self.turn = self.get_turn_num()
        self.players = [ player.point for player in self.player_list]
        self.index = None
        self.scores = tiles.get_scores()

    def set_player_index(self,i):
        self.index = i


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
        return [point[0],point[1]-1]
    def get_down_point(self,point):
        return [point[0],point[1]+1]
    def get_left_point(self,point):
        return [point[0]-1,point[1]]
    def get_right_point(self,point):
        return [point[0]+1,point[1]]

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

    
    #特定プレイヤーの前回の行動を取る
    def get_before_action(self,name):
        p = self.get_my_player(name)
        return p.before_action
    
    #周囲のtile一覧を取得 上下左右の順
    def get_around_tiles(self,name):
        return [self.get_up_tile(name),self.get_down_tile(name),self.get_left_tile(name),self.get_right_tile(name)]


