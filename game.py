import pygame, sys, random
from pygame import Vector2 as Vec2

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

SPEED = 40


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
        self.paddle_l = Paddle(Vec2(self.w-self.paddle_offset,self.h/2),self.display)
        # self.start()  TODO
    
    def _draw(self):
        self.display.fill(BLACK)
        self.paddle_l.draw()
        pygame.display.flip()

    def game_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            self._draw()

            self.clock.tick(SPEED)




class Paddle:
    def __init__(self, pos: Vec2, display, width=20,height=80):
        self.pos = pos
        self.display = display
        self.w = width
        self.h = height

    def draw(self):
        pygame.draw.rect(self.display,WHITE,pygame.Rect(self.pos.x - (self.w/2),self.pos.y-(self.h/2),self.w,self.h))


if __name__ == "__main__":
    game = PongGame()
    game.game_loop()