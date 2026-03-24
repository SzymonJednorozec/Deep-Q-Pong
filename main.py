import pygame
from ai_pong import PongGame
from agent import Agent
from app_types import PlayerType, AppConfig, GameResult
import sys
# TODO it strongly depends on w and h set up in ai_pong.py
# TODO zapisywanie podczas treningu, plotting
# TODO setup musi robic wiecej
# TODO ai dla lewej paletki
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

        self.games = [PongGame(self.screen,left_paddle,right_paddle) for i in range(self.config.instances)]
        self.state = self.config.mode

        if self.config.mode == "PLAY":
            if self.config.right_player == "AI":
                self.agent = Agent()
                self.agent.model.load(self.config.load_path)
                self.agent.epsilon = 0 
            self.delta=1/60
        
        if self.config.mode == "TRAIN":
            self.agent = Agent()
            self.agent.model.load(self.config.load_path)
            self.delta=1/180
    
    
    def handle_train(self,events,frame_count): #in training mode only right paddle
        frame_count+=1
        for i,game in enumerate(self.games):
            state = self.agent.get_state(game,game.paddle_r)
            action = self.agent.get_action(state)

            if i == 0:
                alpha_val = 255
                draw_ui_val = True
                clear_bg_val = True  
            else:
                alpha_val = 50       
                draw_ui_val = False
                clear_bg_val = False

            # reward_l,reward_r, done, score_l, score_r, points_l, points_r
            results: GameResult = game.play_step(self.delta,events, None, action,alpha=alpha_val, draw_ui=draw_ui_val, clear_bg=clear_bg_val)
            next_state = self.agent.get_state(game, game.paddle_r)
        
            self.agent.remember(state, action, results.reward_r, next_state, results.done)
            
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
    
    def handle_menu(self,events):
        pass

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
                    self.paused = not self.paused

            if self.state == "MENU":
                self.handle_menu(events)
            elif self.state == "TRAIN":
                frame_count = self.handle_train(events,frame_count)
            elif self.state == "PLAY":
                self.handle_play(events)
            
            pygame.display.flip()


            if self.state == "PLAY":
                self.games[0].clock.tick(60)
            else:
                self.games[0].clock.tick(500)


if __name__=="__main__":
    app = App()
    app.config.load_from_json("config.json")
    app.main_loop()
