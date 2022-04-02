
import pygame
from pygame.locals import *
import sys
from Snake import Vec2, game

#!-----------------------------------------------------------------------------------------------------------------------------------------------------------
#!-----------------------------------------------------------------------------------------------------------------------------------------------------------
#!----------------------------SNAKE GAME THAT THE USER CAN PLAY----------------------------------------------------------------------------------------------
#!-----------------------------------------------------------------------------------------------------------------------------------------------------------
#!-----------------------------------------------------------------------------------------------------------------------------------------------------------

FPS = 15
BOARD = (30, 30)   
DIRECTIONS = [Vec2(1, 0), Vec2(-1, 0), Vec2(0, 1), Vec2(0, -1)]

SCREEN_SIZE = Vec2(800, 800)
VIEWPORT_SIZE = Vec2(800, 700)
VIEWPORT_POS = Vec2(0, 100)

pygame.init()
 
FramePerSec = pygame.time.Clock()
displaysurface = pygame.display.set_mode((SCREEN_SIZE.x, SCREEN_SIZE.y))
pygame.display.set_caption("Game")

snakeGame = game(BOARD)
pygame.display.flip()

font = pygame.font.Font(None, 30)
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            
        snakeGame.handleInput(event)
   
    
    displaysurface.fill((10,100,150))
    success = snakeGame.advance()
    
    if not success:
        snakeGame.reset()
        
    snakeGame.render(displaysurface, SCREEN_SIZE, VIEWPORT_SIZE, VIEWPORT_POS, snakeColor=(250, 250, 250), foodColor=(200, 10, 10), 
                     viewPortColor=(5, 10, 22), font=font, fontColor=(220, 230, 230))  
    pygame.display.update()
    FramePerSec.tick(FPS)