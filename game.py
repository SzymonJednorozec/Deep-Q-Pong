import pygame, sys, random,math
from pygame import Vector2 as Vec2

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

WIDTH = 1280
HEIGHT = 720

SPEED = 100

PADDLE_SPEED = 300
START_BALL_SPEED = 300

WHITE = (255, 255, 255)
BLACK = (0,0,0)

class PongGame:
    def __init__(self,paddle_offset = 40):
        self.w = WIDTH
        self.h = HEIGHT
        self.paddle_offset = paddle_offset
        self.display = pygame.display.set_mode((self.w,self.h))
        self.clock = pygame.time.Clock()
        self.running = True
        self.paddle_l = Paddle(Vec2(0+self.paddle_offset,self.h/2),self.display)
        self.paddle_r = Paddle(Vec2(self.w-self.paddle_offset,self.h/2),self.display)
        self.ball = Ball(Vec2(self.w/2,self.h/2),7,self.display)
        # self.start()  TODO
    
    def _draw(self):
        self.display.fill(BLACK)
        self.paddle_l.draw()
        self.paddle_r.draw()
        self.ball.draw()
        pygame.display.flip()

    def game_loop(self):
        dt = 0
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            self._draw()
            self._check_collisions(self.ball,self.paddle_l,self.paddle_r)
            self._move(dt)

            dt = self.clock.tick(SPEED)/1000

    def _move(self,dt):
        self.paddle_l.move_l(dt)
        self.paddle_r.move_r(dt)
        self.ball.move(dt)
    
    def _check_collisions(self,ball,paddle_l,paddle_r):
        #ceil
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
            ball.speed *= 1.05

        #right paddle
        if (ball.pos.x+ball.r>(paddle_r.pos.x - paddle_r.w/2)) and (paddle_r.pos.y-paddle_r.h/2<= ball.pos.y <= paddle_r.pos.y+paddle_r.h/2):
            ball.dir.x = -abs(ball.dir.x)
            ball.dir.y = paddle_r.dir*0.4
            if ball.dir.y > 0.8: ball.dir.y = 0.8
            if ball.dir.y < -0.8: ball.dir.y = -0.8

            ball.dir = ball.dir.normalize()
            ball.speed *= 1.05
            # ball.dir = Vec2(ball.dir.x,min(ball.dir.y + paddle_r.dir*0.75,1)).normalize()


class Paddle:
    def __init__(self, pos: Vec2, display, width=20,height=100):
        self.pos = pos
        self.display = display
        self.w = width
        self.h = height
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
           
        self.pos.y += self.dir * PADDLE_SPEED * dt
        
    def move_r(self,dt,):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.dir = -1
        elif keys[pygame.K_DOWN]:
            self.dir = 1
        else:
            self.dir=0
        
        self.pos.y += self.dir * PADDLE_SPEED * dt

class Ball:
    def __init__(self,pos,radius,display):
        self.pos=pos
        self.r=radius
        self.display=display
        self.dir=self._get_ball_direction() # ball direction
        self.speed = START_BALL_SPEED
    
    def _get_ball_direction(self):
        x = random.uniform(0.7, 1.0) * random.choice([-1, 1])
        y = random.uniform(-0.7, 0.7) 
        return Vec2(x, y).normalize()

    def draw(self):
        pygame.draw.circle(self.display,WHITE,self.pos,self.r)
    
    def move(self,dt):
        self.pos += (self.dir*self.speed)*dt

if __name__ == "__main__":
    game = PongGame()
    game.game_loop()