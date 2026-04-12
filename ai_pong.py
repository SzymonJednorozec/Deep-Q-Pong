import pygame, random
from pygame import Vector2 as Vec2
import numpy as np
from app_types import GameResult, GameState

pygame.init()
font = pygame.font.Font('arial.ttf', 25)
large_font = pygame.font.SysFont('arial', 60)

WINNING_SCORE = 5
PADDLE_SPEED = 300
PADDLE_OFFSET = 40
START_BALL_SPEED = 500
SPEED_GROW_RATE = 1.005
WHITE, BLACK, GRAY, RED = (255, 255, 255), (0, 0, 0), (150, 150, 150), (255, 50, 50)

class PongGame:

    def __init__(self, screen, left=True, right=True, alpha=255, draw_ui=True, clear_bg=True, mode = GameState.PLAY):
        self.display = screen
        self.clock = pygame.time.Clock()
        
        # loading window size
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # visual config
        self.alpha = alpha
        self.draw_ui = draw_ui
        self.clear_bg = clear_bg

        self.winner = None
        self.game_active = True
        self.mode = mode

        self.score_l = 0
        self.score_r = 0
        self.points_l = 0
        self.points_r = 0

        self.paddle_l = Paddle(Vec2(0 + PADDLE_OFFSET, self.height/2), left, self.height)
        self.paddle_r = Paddle(Vec2(self.width - PADDLE_OFFSET, self.height/2), right, self.height)
        self.ball = Ball(Vec2(self.width/2, self.height/2), 7)

    def reset_game(self):
        self.score_l = 0
        self.score_r = 0
        self.full_reset()

    def full_reset(self):
        self.winner = None
        self.points_r = 0
        self.points_l = 0
        self.ball.reset(self.width, self.height)
        self.paddle_l.reset()
        self.paddle_r.reset()
        self.game_active = False
    
    def _draw(self):
        if self.clear_bg:
            self.display.fill(BLACK)

        temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        color = (255, 255, 255, self.alpha)

        self.paddle_l.draw(temp_surface, color)
        self.paddle_r.draw(temp_surface, color)
        self.ball.draw(temp_surface, color)

        self.display.blit(temp_surface, (0, 0))

        if self.draw_ui:
            self._draw_ui_elements()


    def play_step(self, dt, action_l=None, action_r=None): # TRAIN mode
        done = False
        reward_l, reward_r = 0, 0
        last_points_r, last_points_l = self.points_r, self.points_l

        if not self.winner:
            # evaluating reward 
            reward_l, reward_r = self._update_physics(dt, action_l, action_r)
            last_points_r, last_points_l = self.points_r, self.points_l
        else: 
            done = True
            self.full_reset()
            self.game_active = True

        self._draw()
        return GameResult(reward_l, reward_r, done, self.score_l, self.score_r, last_points_l, last_points_r)

    def game_loop(self, dt, events, action_l=None, action_r=None): # PLAY mode
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.full_reset()
                self.game_active = True
                # else: self.game_active = True

        if self.game_active:
            self._update_physics(dt, action_l, action_r)

        self._draw()

    # physic + reward
    def _update_physics(self, dt, action_l, action_r):
        r_l, r_r = self._check_collisions(self.ball, self.paddle_l, self.paddle_r)
        self._move(dt, action_l, action_r)
        
        sl, sr = self._check_score()
        r_l += sl; r_r += sr
        
        r_l += self._distance_penalty(self.paddle_l)
        r_r += self._distance_penalty(self.paddle_r)
        
        return r_l, r_r

    def _check_score(self):
        reward_l, reward_r = 0, 0
        if self.paddle_l.create and self.ball.pos.x < PADDLE_OFFSET:
            self.score_r += 1
            reward_l, reward_r = -10, 0
            self.winner = "RIGHT"
            self.game_active = False
        elif self.paddle_r.create and self.ball.pos.x > self.width - PADDLE_OFFSET:
            self.score_l += 1
            reward_l, reward_r = 0, -10
            self.winner = "LEFT"
            self.game_active = False
        
        return reward_l, reward_r
    
    def _distance_penalty(self, paddle):
        if paddle is not None:
            distance_penalty = abs(paddle.pos.y - self.ball.pos.y) / self.height
            return -distance_penalty 
        return 0

    def _move(self, dt, action_l, action_r):
        if action_l: self.paddle_l.move_AI(dt, action_l)
        else: self.paddle_l.move_player(dt, is_left=True)

        if action_r: self.paddle_r.move_AI(dt, action_r)
        else: self.paddle_r.move_player(dt, is_left=False)

        self.ball.move(dt)
    
    def _draw_ui_elements(self):
        score_l = font.render(str(self.score_l), True, GRAY)
        score_r = font.render(str(self.score_r), True, GRAY)
        points_l = font.render(str(self.points_l), True, GRAY)
        points_r = font.render(str(self.points_r), True, GRAY)
        self.display.blit(score_l, (self.width // 4, 50))
        self.display.blit(score_r, (self.width * 3 // 4, 50))
        self.display.blit(points_l, (self.width // 4, 80))
        self.display.blit(points_r, (self.width * 3 // 4, 80))

        fps_text = f"FPS: {self.clock.get_fps():.1f}"
        fps_surf = font.render(fps_text, True, RED)
        self.display.blit(fps_surf, (10, 10))
        
        if not self.game_active and self.mode == GameState.PLAY:
            msg = font.render("PRESS SPACE TO SERVE", True, WHITE)
            self.display.blit(msg, (self.width//2 - msg.get_width()//2, self.height//2 + 50))
    
    def _check_collisions(self, ball, paddle_l, paddle_r):
        reward_l, reward_r = 0, 0
        #ceil & floor
        if ball.pos.y + ball.r < 0: ball.dir.y = abs(ball.dir.y)
        if ball.pos.y + ball.r > self.height: ball.dir.y = -abs(ball.dir.y)

        #left paddle
        if paddle_l.create:
            if (ball.pos.x - ball.r < (paddle_l.pos.x + paddle_l.w/2)) and \
               (paddle_l.pos.y - paddle_l.h/2 <= ball.pos.y <= paddle_l.pos.y + paddle_l.h/2):
                ball.dir.x = abs(ball.dir.x)
                ball.dir.y = paddle_l.dir * 0.75
                ball.dir.y = max(-0.8, min(0.8, ball.dir.y)) # Zastąpienie ifów
                ball.dir = ball.dir.normalize()
                ball.speed *= SPEED_GROW_RATE
                reward_l, reward_r = 10, 0
                self.points_l += 1
        elif ball.pos.x < 0:
            ball.dir.x = abs(ball.dir.x)

        #right paddle
        if paddle_r.create:
            if (ball.pos.x + ball.r > (paddle_r.pos.x - paddle_r.w/2)) and \
               (paddle_r.pos.y - paddle_r.h/2 <= ball.pos.y <= paddle_r.pos.y + paddle_r.h/2):
                ball.dir.x = -abs(ball.dir.x)
                ball.dir.y = paddle_r.dir * 0.4
                ball.dir.y = max(-0.8, min(0.8, ball.dir.y))
                ball.dir = ball.dir.normalize()
                ball.speed *= SPEED_GROW_RATE
                reward_l, reward_r = 0, 10
                self.points_r += 1
        elif ball.pos.x > self.width:
            ball.dir.x = -abs(ball.dir.x)

        return reward_l, reward_r

    def get_state(self, paddle):
        return [
            paddle.pos.y / self.height,
            self.ball.pos.x / self.width,
            self.ball.pos.y / self.height,
            self.ball.dir.x,
            self.ball.dir.y,
        ]

class Paddle:
    def __init__(self, pos: Vec2, create=True, screen_height=720, width=20, height=100):
        self.start_pos = Vec2(pos)
        self.pos = Vec2(pos)
        self.screen_h = screen_height
        self.w = width
        self.h = height
        self.dir = 0
        self.create = create

    def reset(self):
        if self.create:
            self.pos = Vec2(self.start_pos)
            self.dir = 0

    def draw(self, surface, color):
        if self.create:
            rect = pygame.Rect(self.pos.x - (self.w/2), self.pos.y - (self.h/2), self.w, self.h)
            pygame.draw.rect(surface, color, rect)

    # single move function for player
    def move_player(self, dt, is_left=True):
        if not self.create: return
        keys = pygame.key.get_pressed()
        
        up_key = pygame.K_w if is_left else pygame.K_UP
        down_key = pygame.K_s if is_left else pygame.K_DOWN

        if keys[up_key]: self.dir = -1
        elif keys[down_key]: self.dir = 1
        else: self.dir = 0
            
        self._apply_movement(dt)

    def move_AI(self, dt, action):
        if not self.create: return
        if np.array_equal(action, [1,0,0]): self.dir = -1  
        elif np.array_equal(action, [0,1,0]): self.dir = 0  
        else: self.dir = 1

        self._apply_movement(dt)

    def _apply_movement(self, dt):
        pos_change = self.dir * PADDLE_SPEED * dt
        if (self.pos.y + self.h/2 + pos_change < self.screen_h) and (self.pos.y - self.h/2 + pos_change > 0):
            self.pos.y += pos_change

class Ball:
    def __init__(self, pos, radius):
        self.start_pos = Vec2(pos)
        self.pos = Vec2(pos)
        self.r = radius
        self.dir = self._get_ball_direction() 
        self.speed = START_BALL_SPEED
    
    def reset(self, width, height):
        self.pos = Vec2(width/2, height/2) 
        self.speed = START_BALL_SPEED
        self.dir = self._get_ball_direction()

    def _get_ball_direction(self):
        x = random.uniform(0.7, 1.0) * random.choice([-1, 1])
        y = random.uniform(-0.7, 0.7) 
        return Vec2(x, y).normalize()

    def draw(self, surface, color):
        pygame.draw.circle(surface, color, self.pos, self.r)
    
    def move(self, dt):
        self.pos += (self.dir * self.speed) * dt