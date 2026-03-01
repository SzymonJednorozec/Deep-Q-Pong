import torch
import random
import numpy as np
from collections import deque
from ai_pong import PongGame

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 1
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        # model - brain
        # target_model - brain copied every 1000
        # trainer - optimizer(adam)
    
    def get_state(self,game,paddle):
        state = game.get_state(paddle)
        return np.array(state,dtype=float)
    
    def remember(self,state,action,reward,next_state,done):
        self.memory.append((state,action,reward,next_state,done))
    
    def train_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
    
    def copy_network(self):
        pass
    
    def get_action(self,state): # its not choosen randomly using policy propabilities,  we just pick the best (highest propability) or totally random option
        final_move = [0,0,0]
        if random.uniform(0,1) > self.epsilon:
           state0=torch.tensor(state,dtype=torch.float)
           prediction = self.model(state0)
           move = torch.argmax(prediction).item() 
           final_move[move]=1
        else:
            move = random.randint(0, 2)
            final_move[move] = 1
        
        return final_move
    
def train()
    pass


    

         