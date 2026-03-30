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
        self.agent = None
        self.games = []
        self.paused = False
        self.config = AppConfig()
        self.state = self.config.mode
        self.delta = 1/60

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

        if self.config.mode == GameState.PLAY:
            if self.config.right_player == PlayerType.AI:
                self.agent = Agent()
                self.agent.model.load(self.config.load_path)
                self.agent.epsilon = 0 
            self.delta=1/60
        
        if self.config.mode == GameState.TRAIN:
            self.agent = Agent(self.config.e_decay,self.config.e_min,self.config.e_threshold,self.config.e_increase,self.config.e)
            self.agent.model.load(self.config.load_path)
            self.delta=1/120
    
    
    def handle_train(self,events,frame_count): #in training mode only right paddle
        frame_count+=1
        for i,game in enumerate(self.games):
            state = self.agent.get_state(game,game.paddle_r)
            action = self.agent.get_action(state)


            # reward_l,reward_r, done, score_l, score_r, points_l, points_r
            results: GameResult = game.play_step(self.delta, None, action)
            next_state = self.agent.get_state(game, game.paddle_r)
        
            self.agent.remember(state, action, results.reward_r, next_state, results.done)
            
            if results.done:
                self.agent.update_epsilon(self.config.instances,results.points_r)

                info = self.plot_data[i]
                info.scores.append(results.points_r)
                info.total_score += results.points_r
                info.mean_scores.append(info.total_score / len(info.scores))
                self.global_epsilons.append(self.agent.epsilon)

        if frame_count > 12:
            self.agent.train_memory()
            self.agent.soft_update()
            frame_count=0

        return frame_count
            

    def handle_play(self,events):
        game = self.games[0]
        action=None
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
