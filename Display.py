
import pygame
from pygame.locals import *
import sys

from Snake import Vec2, game
 
pygame.init()
 
HEIGHT = 450
WIDTH = 400
FPS = 15
 
FramePerSec = pygame.time.Clock()
 
displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game")

snakeGame = game(Vec2(30, 30), displaysurface.get_size())
pygame.display.flip()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
            
        snakeGame.handleInput(event)
     
    displaysurface.fill((0,0,0))
    success = snakeGame.advance()
    
    if not success:
        pygame.quit()
        sys.exit()
        
    snakeGame.render(displaysurface, snakeColor=(250, 250, 250), foodColor=(200, 10, 10))
    
    pygame.display.update()
    FramePerSec.tick(FPS)
    
