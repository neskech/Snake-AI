import tensorflow as tf
import pygame
from pygame.locals import *
import sys
from Snake import Vec2, game
from numpy import expand_dims, argmax

#!-----------------------------------------------------------------------------------------------------------------------------------------------------------
#!-----------------------------------------------------------------------------------------------------------------------------------------------------------
#!----------------------------LOADS A MODEL FROM THE MODELS FOLDER AND LETS IT PLAY THE GAME IN REAL TIME----------------------------------------------------
#!-----------------------------------------------------------------------------------------------------------------------------------------------------------
#!-----------------------------------------------------------------------------------------------------------------------------------------------------------

Set = 'set-one'
Generation = 29

model = tf.keras.models.load_model(f'./Models/{Set}/Generation-{Generation}')

SCREEN_SIZE = Vec2(500, 500)
VIEWPORT_SIZE = Vec2(500, 400)
VIEWPORT_POS = Vec2(0, 100)
FPS = 15
BOARD = (30, 30)   
DIRECTIONS = [Vec2(1, 0), Vec2(-1, 0), Vec2(0, 1), Vec2(0, -1)]

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
            
    
    modelInput = snakeGame.asVector()
    modelOutput = model.predict_step(expand_dims(modelInput, axis=0))
    print(modelOutput)
    direction = DIRECTIONS[argmax(modelOutput)]
    print(direction)
    snakeGame.snake.changeDirection(direction)
    
    displaysurface.fill((10,100,150))
    success = snakeGame.advance()
    
    if not success:
        snakeGame.reset()
        
    snakeGame.render(displaysurface, SCREEN_SIZE, VIEWPORT_SIZE, VIEWPORT_POS, snakeColor=(250, 250, 250), foodColor=(200, 10, 10), 
                     viewPortColor=(5, 10, 22), font=font, fontColor=(220, 230, 230))  
    pygame.display.update()
    FramePerSec.tick(FPS)