import pygame, sys, random
from pygame import Vector2 as Vec2

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

SPEED = 100

PADDLE_SPEED = 300

WHITE = (255, 255, 255)
BLACK = (0,0,0)

class PongGame:
    def __init__(self, width = 1280, height = 720, paddle_offset = 40):
        self.w = width
        self.h = height
        self.paddle_offset = paddle_offset
        self.display = pygame.display.set_mode((self.w,self.h))
        self.clock = pygame.time.Clock()
        self.running = True
        self.paddle_l = Paddle(Vec2(0+self.paddle_offset,self.h/2),self.display)
        self.paddle_r = Paddle(Vec2(self.w-self.paddle_offset,self.h/2),self.display)
        # self.start()  TODO
    
    def _draw(self):
        self.display.fill(BLACK)
        self.paddle_l.draw()
        self.paddle_r.draw()
        pygame.display.flip()

    def game_loop(self):
        dt = 0
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            self._draw()
            self._move(dt)

            dt = self.clock.tick(SPEED)/1000

    def _move(self,dt):
        self.paddle_l.move_l(dt)
        self.paddle_r.move_r(dt)


class Paddle:
    def __init__(self, pos: Vec2, display, width=20,height=100):
        self.pos = pos
        self.display = display
        self.w = width
        self.h = height

    def draw(self):
        pygame.draw.rect(self.display,WHITE,pygame.Rect(self.pos.x - (self.w/2),self.pos.y-(self.h/2),self.w,self.h))

    def move_l(self,dt,):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.pos.y -= PADDLE_SPEED * dt
        if keys[pygame.K_s]:
           self.pos.y += PADDLE_SPEED * dt
        
    def move_r(self,dt,):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.pos.y -= PADDLE_SPEED * dt
        if keys[pygame.K_DOWN]:
           self.pos.y += PADDLE_SPEED * dt

class Ball:
    def __init__(self,pos,radius,display):
        self.pos=pos
        self.r=radius
        self.display=display

    def draw(self):
        pygame.draw.circle(self.display,WHITE,self.pos,self.r)
    
    def move(self):

if __name__ == "__main__":
    game = PongGame()
    game.game_loop()