import pygame
from ai_pong import PongGame
from agent import Agent
from app_types import PlayerType, AppConfig, GameResult, GameState, PlotInfo
from plot_graph import generate_and_save_plots
import sys

WIDTH = 1280
HEIGHT = 720

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.paused = False
        self.config = AppConfig()
        self.state = self.config.mode
        self.games = None
        self.agents = None
        self.delta = None

    def setup_session(self):
        left_paddle = False
        if self.config.left_player != PlayerType.NONE: left_paddle = True

        right_paddle = False
        if self.config.right_player != PlayerType.NONE: right_paddle = True

        self.plot_data = [PlotInfo() for _ in range(self.config.instances)]
        self.global_epsilons = []

        self.games = []
        for i in range(self.config.instances):
            is_main = (i == 0)
            g = PongGame(self.screen, left_paddle, right_paddle,
                         alpha = 255 if is_main else 50,
                         draw_ui = is_main,
                         clear_bg = is_main,
                         mode = self.config.mode)
            self.games.append(g)

        self.state = self.config.mode
        
        self.agents = []
        self.game_controllers = []

        if self.config.mode == GameState.PLAY:
            self.delta = 1/60
            controllers = {'left': None, 'right': None}
            
            if self.config.right_player == PlayerType.AI:
                agent_r = Agent()
                agent_r.model.load(self.config.load_path)
                agent_r.epsilon = 0 
                self.agents.append(agent_r)
                controllers['right'] = agent_r
                
            if self.config.left_player == PlayerType.AI:
                agent_l = Agent(is_left=True) #reverse perspective
                agent_l.model.load(self.config.load_path)
                agent_l.epsilon = 0
                self.agents.append(agent_l)
                controllers['left'] = agent_l
                
            self.game_controllers.append(controllers)
        
        if self.config.mode == GameState.TRAIN: # Only right paddle + agent(for now same)
            self.delta = 1/120
            
            
            main_agent = Agent(self.config.e_decay, self.config.e_min, self.config.e_threshold, self.config.e_increase)
            main_agent.model.load(self.config.load_path)
            self.agents.append(main_agent)
            
            for _ in range(self.config.instances):
                controllers = {
                    'left': None, 
                    'right': self.agents[0]
                }
                self.game_controllers.append(controllers)
    
    
    def handle_train(self,events,frame_count): #in training mode only right paddle
        frame_count+=1
        for i,game in enumerate(self.games):
            controllers = self.game_controllers

            states = {}
            actions = {'left': None, 'right':None}

            for side, agent in controllers.items():
                if agent is not None:
                    paddle = game.paddle_l if side == 'left' else game.paddle_r
                    state = agent.get_state(game, paddle)
                    states[side] = state
                    actions[side] = agent.get_action(state)



            # reward_l,reward_r, done, score_l, score_r, points_l, points_r
            results: GameResult = game.play_step(self.delta, actions)

            for side, agent in controllers.items():
                if agent is not None:
                    paddle = game.paddle_l if side == 'left' else game.paddle_r
                    next_state = agent.get_state(game, paddle)
                    reward = results.reward_l if side == 'left' else results.reward_r
                    
                    agent.remember(states[side], actions[side], reward, next_state, results.done)
            
            if results.done:

                if controllers['right'] is not None:
                    controllers['right'].update_epsilon(self.config.instances, results.points_r)
                    
                    info = self.plot_data[i]
                    info.scores.append(results.points_r)
                    info.total_score += results.points_r
                    info.mean_scores.append(info.total_score / len(info.scores))

                if len(self.agents) > 0 and i == 0: 
                    self.global_epsilons.append(self.agents[0].epsilon)

        if frame_count > 12:
            for agent in self.agents:
                agent.train_memory()
                agent.soft_update()
            frame_count = 0

        return frame_count
            

    def handle_play(self,events):
        game = self.games[0]
        controllers = self.game_controllers[0]
        actios={}
        if self.agent is not None:
            state = self.agent.get_state(game,game.paddle_r)
            action = self.agent.get_action(state)
        game.game_loop(self.delta,events,None,action)
    
    def handle_menu(self, events):
        if len(self.games) > 0:
            self.games[0]._draw() 
        else:
            self.screen.fill((20, 20, 20))

        font = pygame.font.SysFont("arial", 40)
        txt = font.render("PAUSED - PRESS 'S' TO SAVE OR 'P' TO RESUME OR K TO PLOT", True, (255, 255, 255))
        self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                if self.agent is not None:
                    self.agent.model.save(self.config.save_path)
                    self.agent.model.save_onnx(self.config.save_onnx_path)
                    print(f"--- MODEL SAVED ---")
            if event.type == pygame.KEYDOWN and event.key == pygame.K_k:
                generate_and_save_plots(self.plot_data, self.global_epsilons)

    def main_loop(self):
        frame_count = 0
        self.setup_session()
        while True:
            events = pygame.event.get() 
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                    if self.state in [GameState.TRAIN,GameState.PLAY]:
                        self.previous_state = self.state
                        self.state = GameState.MENU
                    elif self.state == GameState.MENU and hasattr(self, 'previous_state'):
                        self.state = self.previous_state

            if self.state == GameState.MENU:
                self.handle_menu(events)
            elif self.state == GameState.TRAIN:
                frame_count = self.handle_train(events,frame_count)
            elif self.state == GameState.PLAY:
                self.handle_play(events)
            
            pygame.display.flip()


            if self.state == GameState.PLAY:
                self.games[0].clock.tick(60)
            else:
                self.games[0].clock.tick(500)


if __name__=="__main__":
    app = App()
    app.config.load_from_json("config.json")
    app.main_loop()
