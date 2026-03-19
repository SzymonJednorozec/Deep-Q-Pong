import torch
import random
import numpy as np
from collections import deque
from ai_pong import PongGame
from model import   Qtrainer, Linear_Qnet
from plot_graph import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 128
LR = 0.001

class Agent:
    def __init__(self):
        # self.n_games = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_Qnet(5,128,3)
        self.trainer = Qtrainer(self.model,LR,self.gamma)
        #epsilon decay 
        self.epsilon = 1
        self.min_epsilon = 0.1
        self.epsilon_decay = 0.995
        
        self.games_from_last_record = 0
        self.record = 0
    
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
    
    def soft_update(self):
        self.trainer.soft_update_target_model()
    
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
    
    def save_model(self):
        self.model.save()
        self.model.save_onnx()

    def load_model(self):
        self.model.load()
    
def train(agent_l:Agent=None,agent_r:Agent=None):
    
    if agent_l is not None: agent_l.load_model() 
    if agent_r is not None: agent_r.load_model()

    watch=True
    game_cnt = 0
    game_frame_cnt = 0
    game = PongGame(False,True)
    dt = 1/180
    

    plot_scores = []
    plot_mean_scores = []
    plot_epsilons = []
    total_score=0

    while True:
        game.clock.tick(0)

        game_frame_cnt+=1
        state_l,action_l = get_state_action_pair(agent_l,game,game.paddle_l)
        state_r,action_r = get_state_action_pair(agent_r,game,game.paddle_r)

        # return reward_l,reward_r, game_over, self.score_l, self.score_r
        reward_l,reward_r, done, score_l, score_r, points_l, points_r = game.play_step(dt,action_l,action_r)

        next_state_l,_ = get_state_action_pair(agent_l,game,game.paddle_l)
        next_state_r,_ = get_state_action_pair(agent_r,game,game.paddle_r)

        if state_l is not None: agent_l.remember(state_l,action_l,reward_l,next_state_l,done)
        if state_r is not None: agent_r.remember(state_r,action_r,reward_r,next_state_r,done)

        if game_frame_cnt%12 == 0:
            train_agent(agent_l)
            train_agent(agent_r)


        if done:
            game_cnt+=1
            copy_network_change_epsilon(agent_l,points_l,game_cnt)
            copy_network_change_epsilon(agent_r,points_r,game_cnt)

            plot_scores.append(points_r)
            total_score+=points_r
            plot_mean_scores.append(total_score/game_cnt)
            plot_epsilons.append(agent_r.epsilon)
            plot(plot_scores,plot_mean_scores,plot_epsilons)

                



def get_state_action_pair(agent,game,paddle):
    if agent is not None and paddle is not None:
        state = agent.get_state(game,paddle)
        action = agent.get_action(state)
    else: state,action = None,None
    return  state,action

def copy_network_change_epsilon(agent: Agent,points,game_cnt):
    if agent is not None:
        if agent.epsilon > agent.min_epsilon:
            agent.epsilon *= agent.epsilon_decay

        if points>agent.record:
            agent.save_model()
            agent.record=points
            agent.games_from_last_record=0
        elif game_cnt%100 == 0:
            agent.save_model()

        if agent.games_from_last_record>200:
            agent.games_from_last_record=0
            agent.epsilon+=0.2
        else:
            agent.games_from_last_record+=1
        print(agent.epsilon)

def train_agent(agent):
    if agent is not None:
        agent.train_memory()
        agent.soft_update()

if __name__ == '__main__':
    # agent_l = Agent()
    agent_r = Agent()
    train(None,agent_r)
    

         