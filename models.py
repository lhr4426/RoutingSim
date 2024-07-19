from pyevsim import BehaviorModelExecutor, Infinite, SysMessage
import json
import heapq
from copy import deepcopy
import os, sys
import socket

def key_to_position(input_key, prev_pos) :
    if input_key in ['f', 'b', 'l', 'r'] :
        x, y = prev_pos
        if input_key == 'f' : 
            y -= 1
        elif input_key == 'b' :
            y += 1
        elif input_key == 'l' :
            x -= 1
        elif input_key == 'r' :
            x += 1
        cur_pos = (x, y)
        return cur_pos 
    
    else : return None

def position_to_key(prev_pos, cur_pos) :
    dx = cur_pos[0] - prev_pos[0]
    dy = cur_pos[1] - prev_pos[1]
    abs_dx = abs(dx)
    abs_dy = abs(dy)

    if abs_dx + abs_dy != 1 :
        return None
    else :
        if dx == 0 and dy == -1 :
            return 'f'
        elif dx == 0 and dy == 1 :
            return 'b'
        elif dx == 1 and dy == 0 :
            return 'r'
        elif dx == -1 and dy == 0 :
            return 'l'


class initializer(BehaviorModelExecutor) :
    def __init__(self, instantiate_time, destruct_time, name, engine_name, config_file, host='localhost', port='12345'):
        BehaviorModelExecutor.__init__(self, instantiate_time, destruct_time, name, engine_name)
        self.init_state("Wait")
        self.insert_state("Wait", Infinite)
        self.insert_state("Init", 1)

        self.insert_input_port("start")
        self.insert_output_port("init_done")

        self.grid_scale = 3 # 사용자 입력 받도록 변경 가능함
        self.start_point = 0
        self.end_point = 0
        self.key_dict = {}
        self.config_file = config_file
        self.host = host
        self.port = port

    def ext_trans(self, port, msg) :
        if port == "start" :
            print("Simulator Start")
            self._cur_state = "Init"
    
    def output(self) :
        # TODO : tcp 서버 하나 만들어서 다른 애들한테도 소켓 주기
        if self._cur_state == "Init" :

            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((self.host, self.port))
            

            with open(self.config_file, 'r', encoding='utf-8') as f :
                self.key_dict = json.load(f)
            print(f"moving keywords : {self.key_dict}")

            
            
            #while self.grid_scale == 0 :
             #   try :
              #      self.grid_scale = int(input("Grid Scale (ex. 3): "))
               # except TypeError :
                #    print("Please enter the correct format.")
                 #   continue
            while self.start_point == 0 :                
                input_data = input("Input Start Point x, y. (ex : 0, 0) : ")
                try : 
                    x_str, y_str = input_data.split(',')
                    x = int(x_str.strip())
                    y = int(y_str.strip())

                    self.start_point = (x, y)
                except ValueError :
                    print("Please enter the correct format.")
                    continue
            while self.end_point == 0 :
                input_data = input("Input End Point x, y. (ex : 2, 2) : ")
                try : 
                    x_str, y_str = input_data.split(',')
                    x = int(x_str.strip())
                    y = int(y_str.strip())

                    self.end_point = (x, y)
                except ValueError :
                    print("Please enter the correct format.")
                    continue
                
            msg = SysMessage(self.get_name(), "init_done")
            msg.insert(self.grid_scale)
            msg.insert(self.start_point)
            msg.insert(self.end_point)
            msg.insert(self.key_dict)
            return msg

    def int_trans(self):
        if self._cur_state == "Wait" :
            self._cur_state = "Wait"
        elif self._cur_state == "Init" :
            self._cur_state = "Wait"
        

class predictor(BehaviorModelExecutor) :
    def __init__(self, instantiate_time, destruct_time, name, engine_name):
        BehaviorModelExecutor.__init__(self, instantiate_time, destruct_time, name, engine_name)
        self.init_state("Wait")
        self.insert_state("Wait", Infinite)        
        self.insert_state("Predict", 1)

        self.insert_input_port("init_done")
        self.insert_input_port("move_done")
        self.insert_output_port("pred_done")

        self.grid_scale = 0 
        self.start_point = 0
        self.end_point = 0
        self.current_position = ()

        self.key_dict = {}
        self.distances = {}
        self.priority_queue = []
        self.recommand_path = []
        self.came_from = {}

        self.previous_position = ()



    def ext_trans(self, port, msg):
        # initializer -> predictor
        if port == "init_done" :
            self.grid_scale = msg.retrieve()[0] # int
            self.start_point = msg.retrieve()[1] # tuple (x, y)
            self.end_point = msg.retrieve()[2] # tuple (x, y)
            self.key_dict = msg.retrieve()[3] 
            self.distances = {(i, j) : float('inf') for i in range(self.grid_scale) for j in range(self.grid_scale)}
            self.distances[self.start_point] = 0
            self.current_position = deepcopy(self.start_point)
            self.priority_queue = [(0, self.start_point)]

            self._cur_state = "Predict"

        # mover -> predictor
        elif port == "move_done" :
            # 마지막 이동이 어디서 온건지 전달받음. 그걸 previous_position에 저장해야함
            # 마지막 갔던 위치로는 가지 않기 위함
            
            self.previous_position = deepcopy(self.current_position)
            self.current_position = msg.retrieve()[0]
            
            self._cur_state = "Predict"
        

    def output(self):
        if self._cur_state == "Predict" :
            # previos_position을 제외한 나머지 위치로의 이동을 해야함 (다익스트라)
            # 만약에, 마지막 이동이 recommand_path[0] 과 같을 경우 == 추천한 대로 움직였을 경우
            # 별다른 조치 없이 바로 다음 추천 위치를 mover에 전달함.
            # 마지막 이동이 recommand_path[0]과 다를 경우 == 추천한 대로 움직이지 않았을 경우
            # 새 루트를 짜줌
            msg = SysMessage(self.get_name(), "pred_done")
            print(f"previous_position : {self.previous_position}, current_position : {self.current_position}")
            print(f"recommand_path : {self.recommand_path}")
            

            if self.current_position == self.start_point or self.current_position != self.recommand_path[0] :
                print("dijkstra start")

                if self.current_position != self.start_point :
                    self.start_point = deepcopy(self.current_position)
                    self.distances = {(i, j) : float('inf') for i in range(self.grid_scale) for j in range(self.grid_scale)}
                    self.distances[self.current_position] = 0
                    self.priority_queue = [(0, self.current_position)]
                    self.came_from = {}

                while self.priority_queue:
                    current_distance, current_node = heapq.heappop(self.priority_queue)

                    if current_node == self.end_point : # end_point는 x, y로 구성
                        # 현재 노드가 도착 지점과 같으면
                        # 도착 지점까지 어떻게 이어졌는지 came_from 리스트에서 뽑으면서 저장함
                        self.recommand_path = []
                        while current_node in self.came_from :
                            self.recommand_path.append(current_node)
                            current_node = self.came_from[current_node]

                        # 마지막에 뒤집어서 경로를 표현함
                        self.recommand_path.reverse()
                        # 시작 위치를 제외한 경로가 나와있는 상태
                        # 따라서, recommand_path[0]은 현 위치에서 추천하는 이동 위치

                        msg = SysMessage(self.get_name(), "pred_done")
                        msg.insert(position_to_key(self.current_position, self.recommand_path[0]))
                        return msg

                    x, y = current_node
                    for dx, dy in [(0, 1), (0, -1), (-1, 0), (1, 0)] :
                        # 상, 하, 좌, 우
                        neighbor = (x + dx, y + dy)
                        if 0 <= neighbor[0] < self.grid_scale and 0 <= neighbor[1] < self.grid_scale:
                            if neighbor == self.previous_position:
                                continue
                            new_distance = current_distance + 1
                            if new_distance < self.distances[neighbor] :
                                self.distances[neighbor] = new_distance
                                self.came_from[neighbor] = current_node
                                heapq.heappush(self.priority_queue, (new_distance, neighbor))

                msg.insert("None")
                return msg 
            
            if self.current_position == self.recommand_path[0] :
                del(self.recommand_path[0])
                print(f"new recommand path : {self.recommand_path}")
                if len(self.recommand_path) > 0 :
                    msg.insert(position_to_key(self.current_position, self.recommand_path[0]))
                else :
                    msg.insert("Goal")

                return msg
            
    
    def int_trans(self):
        self._cur_state = "Wait"

class mover(BehaviorModelExecutor) :
    def __init__(self, instantiate_time, destruct_time, name, engine_name):
        BehaviorModelExecutor.__init__(self, instantiate_time, destruct_time, name, engine_name)
        self.init_state("Wait")
        self.insert_state("Wait", Infinite)
        self.insert_state("Move", 1)

        self.insert_input_port("init_done")
        self.insert_input_port("pred_done")
        self.insert_output_port("move_done")

        self.current_position = ()
        self.moving_log = []
        
        self.grid_scale = 0 
        self.start_point = 0
        self.end_point = 0
        self.key_dict = {}

    def ext_trans(self, port, msg):
        # initializer -> mover
        if port == "init_done" :
            self.grid_scale = msg.retrieve()[0]
            self.start_point = msg.retrieve()[1]
            self.end_point = msg.retrieve()[2]
            self.key_dict = msg.retrieve()[3]
            self.current_position = deepcopy(self.start_point)

            self._cur_state = "Wait"

        # predictor -> mover
        elif port == "pred_done" :
            recommended_key = msg.retrieve()[0]
            if recommended_key == "None" :
                print("No Recommanded Route. Exit RoutingSim.")
                sys.exit()
                

            # 맵 그려줘야함. 이동 할 수 있는 곳은 '.' 으로 표시, 추천 경로는 '+' 로 표시, 현위치는 P로 표시
            # 입력, 저장하는 좌표는 xy 좌표. 
            os.system('cls')
            map_grid = [['.'] * self.grid_scale for _ in range(self.grid_scale)]
            if recommended_key != "Goal" :
                recommended_position = key_to_position(recommended_key, self.current_position)
                map_grid[recommended_position[1]][recommended_position[0]] = '+'
            map_grid[self.current_position[1]][self.current_position[0]] = 'P'
            for row in map_grid :
                print(' '.join(row))

            if recommended_key == "Goal" :
                print("Goal! Exit RoutingSim.")
                print(f"Your Moving Log : {self.moving_log}")
                sys.exit()

            self._cur_state = "Move"

    
    def output(self):
        # if self._cur_state == "Move" :
        # 움직이는거 만들어야함. wasd 키 입력받게 하기
        # 움직인 위치를 moving_log에 넣고, predictor 모델에 전해주기

        if self._cur_state == "Move" :
            input_key = input("Enter Moving Direction (w, a, s, d) : ")
            changed_input_key = self.key_dict.get(input_key)
            next_position = key_to_position(changed_input_key, self.current_position)
            print(f"Current Position : {self.current_position}, Next Position : {next_position}")
            if next_position == None :
                print(f"Next Position == None.\ninput_key = {input_key}, cur_position = {self.current_position}")
                sys.exit()
            
            else :
                self.current_position = next_position
                self.moving_log.append(next_position)
                msg = SysMessage(self.get_name(), "move_done")
                msg.insert(next_position)
                return msg
                
    def int_trans(self):
        self._cur_state = "Wait"
    