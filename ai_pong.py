import pygame, sys, random,math
from pygame import Vector2 as Vec2
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 25)
large_font = pygame.font.SysFont('arial', 60)

WINNING_SCORE = 5

WIDTH = 1280
HEIGHT = 720

SPEED = 100

PADDLE_SPEED = 300
START_BALL_SPEED = 300
SPEED_GROW_RATE = 1.005

WHITE, BLACK, GRAY, RED = (255, 255, 255), (0, 0, 0), (150, 150, 150), (255, 50, 50)

class PongGame:
    def __init__(self,paddle_offset = 40):
        self.paddle_offset = paddle_offset
        self.display = pygame.display.set_mode((WIDTH,HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.winner = None
        
        self.score_l = 0
        self.score_r = 0

        self.paddle_l = Paddle(Vec2(0+self.paddle_offset,HEIGHT/2),self.display)
        self.paddle_r = Paddle(Vec2(WIDTH-self.paddle_offset,HEIGHT/2),self.display)
        self.ball = Ball(Vec2(WIDTH/2,HEIGHT/2),7,self.display)

    def reset_game(self):
        self.score_l = 0
        self.score_r = 0
        self.winner = None
        self.full_reset()

    def full_reset(self):
        self.winner = None
        self.ball.reset()
        self.paddle_l.reset()
        self.paddle_r.reset()
        self.game_active = False
    
    def _draw(self):
        self.display.fill(BLACK)
        self._draw_ui()
        self.paddle_l.draw()
        self.paddle_r.draw()
        self.ball.draw()
        pygame.display.flip()

    def play_step(self,dt,action_l=None,action_r=None):
        game_over = False
        reward_l , reward_r = 0,0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        if not self.winner:
            reward_l , reward_r += self._check_collisions(self.ball,self.paddle_l,self.paddle_r)
            self._move(dt,action_l=None,action_r=None)
            reward_l , reward_r += self._check_score()
        else: game_over = True

        self._draw()
        dt = self.clock.tick(SPEED)/1000
        return reward_l,reward_r, game_over, self.score_l, self.score_r

    def _check_score(self):
        if self.ball.pos.x < self.paddle_offset:
            self.score_r += 1
            self.full_reset()
            reward_l,reward_r = -10,10
        elif self.ball.pos.x > WIDTH - self.paddle_offset:
            self.score_l += 1
            self.full_reset()
            reward_l,reward_r = 10,-10
        else: reward_l,reward_r = 0,0
        
        if self.score_l >= WINNING_SCORE: self.winner = "LEFT"
        if self.score_r >= WINNING_SCORE: self.winner = "RIGHT"
        return reward_l,reward_r

    def _move(self,dt,action_l,action_r):
        self.paddle_l.move_AI(dt,action_l)
        self.paddle_r.move_AI(dt,action_r)
        self.ball.move(dt)
    
    def _draw_ui(self):
        score_l = font.render(str(self.score_l), True, GRAY)
        score_r = font.render(str(self.score_r), True, GRAY)
        self.display.blit(score_l, (WIDTH // 4, 50))
        self.display.blit(score_r, (WIDTH * 3 // 4, 50))
        
        # if self.winner:
        #     txt = f"PLAYER {self.winner} WINS!"
        #     win_surf = large_font.render(txt, True, RED)
        #     sub_surf = font.render("PRESS SPACE TO RESTART", True, WHITE)
        #     self.display.blit(win_surf, (WIDTH//2 - win_surf.get_width()//2, HEIGHT//2 - 100))
        #     self.display.blit(sub_surf, (WIDTH//2 - sub_surf.get_width()//2, HEIGHT//2))
        # elif not self.game_active:
        #     msg = font.render("PRESS SPACE TO SERVE", True, WHITE)
        #     self.display.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 + 50))
    
    def _check_collisions(self,ball,paddle_l,paddle_r):
        #ceil
        reward_l,reward_r = 0,0
        if ball.pos.y+ball.r<0:
            ball.dir.y = abs(ball.dir.y)
        #floor
        if ball.pos.y+ball.r>HEIGHT:
            ball.dir.y = -abs(ball.dir.y)
        #left paddle
        if (ball.pos.x-ball.r<(paddle_l.pos.x + paddle_l.w/2)) and (paddle_l.pos.y-paddle_l.h/2<= ball.pos.y <= paddle_l.pos.y+paddle_l.h/2):
            ball.dir.x = abs(ball.dir.x)
            ball.dir.y = paddle_l.dir*0.75
            if ball.dir.y > 0.8: ball.dir.y = 0.8
            if ball.dir.y < -0.8: ball.dir.y = -0.8

            ball.dir = ball.dir.normalize()
            ball.speed *= SPEED_GROW_RATE
            reward_l,reward_r = 1,0

        #right paddle
        if (ball.pos.x+ball.r>(paddle_r.pos.x - paddle_r.w/2)) and (paddle_r.pos.y-paddle_r.h/2<= ball.pos.y <= paddle_r.pos.y+paddle_r.h/2):
            ball.dir.x = -abs(ball.dir.x)
            ball.dir.y = paddle_r.dir*0.4
            if ball.dir.y > 0.8: ball.dir.y = 0.8
            if ball.dir.y < -0.8: ball.dir.y = -0.8

            ball.dir = ball.dir.normalize()
            ball.speed *= SPEED_GROW_RATE
            reward_l,reward_r = 0,1
        return reward_l,reward_r


class Paddle:
    def __init__(self, pos: Vec2, display, width=20,height=100):
        self.start_pos = Vec2(pos)
        self.pos = Vec2(pos)
        self.display = display
        self.w = width
        self.h = height
        self.dir = 0

    def reset(self):
        self.pos = Vec2(self.start_pos)
        self.dir = 0

    def draw(self):
        pygame.draw.rect(self.display,WHITE,pygame.Rect(self.pos.x - (self.w/2),self.pos.y-(self.h/2),self.w,self.h))

    def move_l(self,dt,):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.dir = -1
        elif keys[pygame.K_s]:
            self.dir = 1
        else:
            self.dir=0
           
        pos_change = self.dir * PADDLE_SPEED * dt
        if (self.pos.y + self.h/2 + pos_change < HEIGHT) and (self.pos.y - self.h/2 + pos_change > 0):
            self.pos.y += pos_change
        
    def move_r(self,dt,):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.dir = -1
        elif keys[pygame.K_DOWN]:
            self.dir = 1
        else:
            self.dir=0
        pos_change = self.dir * PADDLE_SPEED * dt
        if (self.pos.y + self.h/2 + pos_change < HEIGHT) and (self.pos.y - self.h/2 + pos_change > 0):
            self.pos.y += pos_change
        
    def move_AI(self,dt,action):
        if np.array_equal(action[1,0,0]):  self.dir = -1  
        elif np.array_equal(action[0,1,0]): self.dir = 0  
        else: self.dir = 1

        pos_change = self.dir * PADDLE_SPEED * dt
        if (self.pos.y + self.h/2 + pos_change < HEIGHT) and (self.pos.y - self.h/2 + pos_change > 0):
            self.pos.y += pos_change


class Ball:
    def __init__(self,pos,radius,display):
        self.start_pos=Vec2(pos)
        self.pos=Vec2(pos)
        self.r=radius
        self.display=display
        self.dir=self._get_ball_direction() # ball direction
        self.speed = START_BALL_SPEED
    
    def reset(self):
        self.pos = Vec2(self.start_pos)
        self.speed = START_BALL_SPEED
        self.dir = self._get_ball_direction()

    def _get_ball_direction(self):
        x = random.uniform(0.7, 1.0) * random.choice([-1, 1])
        y = random.uniform(-0.7, 0.7) 
        return Vec2(x, y).normalize()

    def draw(self):
        pygame.draw.circle(self.display,WHITE,self.pos,self.r)
    
    def move(self,dt):
        self.pos += (self.dir*self.speed)*dt
