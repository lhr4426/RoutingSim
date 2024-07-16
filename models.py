from pyevsim import BehaviorModelExecutor, SystemSimulator, Infinite, SysMessage
import datetime
import json
import heapq
from copy import deepcopy

class initializer(BehaviorModelExecutor) :
    def __init__(self, instantiate_time, destruct_time, name, engine_name, config_file):
        BehaviorModelExecutor.__init__(self, instantiate_time, destruct_time, name, engine_name)
        self.init_state("Wait")
        self.insert_state("Wait", Infinite)
        self.insert_state("Init", 1)

        self.insert_input_port("start")
        self.insert_output_port("init_done")

        self.grid_scale = 0 
        self.start_point = 0
        self.end_point = 0
        self.move_dict = {}
        self.config_file = config_file

    def ext_trans(self, port, msg) :
        if port == "start" :
            print("Simulator Start")
            self._cur_state = "Init"
    
    def output(self) :
        if self._cur_state == "Init" :
            with open(self.config_file, 'r', encoding='utf-8') as f :
                self.move_dict = json.load(f)
            print(f"moving keywords : {self.move_dict}")

            while self.grid_scale == 0 :
                try :
                    self.grid_scale = int(input("Grid Scale : "))
                except TypeError :
                    print("Please enter the correct format.")
                    continue
            while self.start_point == 0 :                
                input_data = input("Input Start Point. (ex : 0, 0) : ")
                try : 
                    x_str, y_str = input_data.split(',')
                    x = int(x_str.strip())
                    y = int(y_str.strip())

                    self.start_point = (x, y)
                except ValueError :
                    print("Please enter the correct format.")
                    continue
            while self.end_point == 0 :
                input_data = input("Input End Point. (ex : 3, 3) : ")
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
            msg.insert(self.move_dict)
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
        self.insert_state("Init", 1)
        self.insert_state("Predict", 1)

        self.insert_input_port("init_done")
        self.insert_input_port("move_done")
        self.insert_output_port("pred_done")

        self.grid_scale = 0 
        self.start_point = 0
        self.end_point = 0
        self.move_dict = {}


    def ext_trans(self, port, msg):
        # initializer -> predictor
        if port == "init_done" :
            self.grid_scale = msg.retrieve()[0]
            self.start_point = msg.retrieve()[1]
            self.end_point = msg.retrieve()[2]
            self.move_dict = msg.retrieve()[3]
            self._cur_state = "Init"

        # mover -> predictor
        elif port == "move_done" :
            # TODO : 마지막 이동이 어디서 온건지 알아야함. 거기 제외하고 이동
            self._cur_state = "Predict"
        

    
    def output(self):
        if self._cur_state == "Init" :

        elif self._cur_state == "Predict" :
            
    
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

        self.recommended_route = []
        self.current_position = ()
        self.moving_log = []
        
        self.grid_scale = 0 
        self.start_point = 0
        self.end_point = 0
        self.move_dict = {}

    def ext_trans(self, port, msg):
        # initializer -> mover
        if port == "init_done" :
            self.grid_scale = msg.retrieve()[0]
            self.start_point = msg.retrieve()[1]
            self.end_point = msg.retrieve()[2]
            self.move_dict = msg.retrieve()[3]
            self.current_position = deepcopy(self.start_point)
            

            self._cur_state = "Wait"

        elif port == "pred_done" :
            self.recommended_route = msg.retrieve()[0]
            

    
    def output(self):
        return super().output()
    
    def int_trans(self):
        return super().int_trans()
    