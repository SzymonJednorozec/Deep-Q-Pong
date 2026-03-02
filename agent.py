import torch
import random
import numpy as np
from collections import deque
from ai_pong import PongGame
from model import   Qtrainer, Linear_Qnet

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 1
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_Qnet(5,128,3)
        self.trainer = Qtrainer(self.model,LR,self.gamma)

    
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
        self.trainer.update_target_model()
    
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
    
def train(agent_l:Agent=None,agent_r:Agent=None):
    game_cnt = 0
    game_frame_cnt = 0
    game = PongGame()
    dt = 1/60
    while True:
        game_frame_cnt+=1
        state_l,action_l = get_state_action_pair(agent_l,game,game.paddle_l)
        state_r,action_r = get_state_action_pair(agent_r,game,game.paddle_r)

        # return reward_l,reward_r, game_over, self.score_l, self.score_r
        reward_l,reward_r, done, score_l, score_r = game.play_step(dt,action_l,action_r)

        next_state_l,_ = get_state_action_pair(agent_l,game,game.paddle_l)
        next_state_r,_ = get_state_action_pair(agent_r,game,game.paddle_r)

        if state_l: agent_l.remember(state_l,action_l,reward_l,next_state_l,done)
        if state_r: agent_r.remember(state_r,action_r,reward_r,next_state_r,done)

        if game_frame_cnt%8:
            agent_l and agent_l.train_memory()
            agent_r and agent_r.train_memory()
        


        if done:
            game_cnt+=1
            agent_l and agent_l.copy_network()
            agent_r and agent_r.copy_network()
            # plotting



def get_state_action_pair(agent,game,paddle):
    if agent:
        state = agent.get_state(game,paddle)
        action = agent.get_action(state)
    else: state,action = None,None
    return  state,action

if __name__ == '__main__':
    agent_l = Agent()
    agent_r = Agent()
    train(agent_l,agent_r)
    

         