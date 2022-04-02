import os
import pygame
import cv2
from Snake import Vec2

#!-----------------------------------------------------------------------------------------------------------------------------------------------------------
#!-----------------------------------------------------------------------------------------------------------------------------------------------------------
#!----------------------------FILE IO FOR CREATING VIDEOS FROM DATA COLLECTED DURING TRAINING----------------------------------------------------------------
#!-----------------------------------------------------------------------------------------------------------------------------------------------------------
#!-----------------------------------------------------------------------------------------------------------------------------------------------------------

SCREEN_SIZE = (800,800)
VIEWPORT_SIZE = (800,600)
VIEWPORT_POS = (0, 200)

BACKGROUND_COLOR = (120, 146, 213)
VIEWPORT_COLOR = (3,18,19)
SNAKE_COLOR = (250,250,250)
FOOD_COLOR = (200, 0, 0)
TEXT_COLOR = (248, 230, 240)

SNAKE_BODY, SNAKE_HEAD, SNAKE_FOOD, EMPTY = 0.0, 1.0, 0.5, -1.0

def toImage(set):
    meta = open(f'./Models/{set}/meta.txt', 'r').readlines()
    populationSize = meta[0].split(':')[1][1:-1]
    learningRate = meta[2].split(':')[1][1:-1]
    size = meta[3].split(':')[1][2:-1].split(',')
    boardSize = Vec2(int(size[0]), int(size[1]))

    
    width, height = SCREEN_SIZE[0], SCREEN_SIZE[1]
    colWidth, colHeight = VIEWPORT_SIZE[0] / boardSize.x, VIEWPORT_SIZE[1] / boardSize.y
    
    pygame.init()
    display = pygame.display.set_mode((width, height))
    pygame.display.flip()
    font = pygame.font.Font(None, 30)
    
    lines = open(f'./Video/Raw/{set}/{set}.txt').readlines()
    i = 0
    frames = 0
    while i < len(lines): 
            display.fill(BACKGROUND_COLOR)
            pygame.draw.rect(display, VIEWPORT_COLOR, pygame.Rect(VIEWPORT_POS[0], VIEWPORT_POS[1], VIEWPORT_SIZE[0], VIEWPORT_SIZE[1]))
            
            metadata = lines[i].split('~')
            generation = int(metadata[1])
            iteration = int(metadata[3])
            score = int(metadata[5])
            high_score = int(metadata[7])
            fitness = float(metadata[9])
            i += 1
            
            #Render the text
            Props = 0.10
            margins = Vec2(VIEWPORT_POS[0] * Props, VIEWPORT_POS[1] * Props)
            
            gen = font.render(f'Generation {generation}', True, TEXT_COLOR)
            it = font.render(f'High Score {high_score}', True, TEXT_COLOR)
            sc = font.render(f'Score {score}', True, TEXT_COLOR)
            hsc = font.render(f'Iteration {iteration}', True, TEXT_COLOR)
            fit = font.render(f'Fitness {fitness}', True, TEXT_COLOR)
            pop = font.render(f'Population Size {populationSize}', True, TEXT_COLOR)
            learn = font.render(f'Learning Rate {learningRate}', True, TEXT_COLOR)
            display.blit(gen, (margins.x + 50.0, margins.y))
            display.blit(sc, (margins.x + 300.0, margins.y))
            display.blit(it, (margins.x + 550.0, margins.y))
            display.blit(hsc, (margins.x + 50.0, margins.y + 60.0))
            display.blit(fit, (margins.x + 300.0, margins.y + 60.0))
            display.blit(pop, (margins.x + 550.0, margins.y + 60.0))
            display.blit(learn, (margins.x + 300.0, margins.y + 120.0))
            
            index = 0
            for row in range(boardSize.y):
                vals = lines[i].split(' ')
                i += 1
                for value in vals[:-1]:
                    val = float(value)
                    row, col = (index // boardSize.x, index % boardSize.x)
                    index += 1
                    
                    color = None
                    if val == SNAKE_BODY or val == SNAKE_HEAD:
                        color = SNAKE_COLOR
                    elif val == SNAKE_FOOD:
                        color = FOOD_COLOR
                    else:
                        continue
                    
                    pygame.draw.rect(display, color, pygame.Rect(VIEWPORT_POS[0] + colWidth * col, VIEWPORT_POS[1] + colHeight * row, colWidth, colHeight))
              
            pygame.display.update()      
            pygame.image.save(display, f'./Video/Image/{set}/{frames}.png')  
            frames += 1         
            i += 1 #Catch the extra \n at the end there
            
    pygame.quit()

def toVideo(set, fps):
      fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
      video = cv2.VideoWriter(f'./Video/Video/{set}/{set}.mp4', fourcc, fps, (SCREEN_SIZE[0], SCREEN_SIZE[1]), True)
      files = [(int(file[:file.find('.')]), file) for file in os.listdir(f'./Video/Image/{set}')]
      files.sort(key=lambda x: x[0])
      for _, file in files:
          print(file, ' ' + f'./Video/Image/{set}/{file}')
          video.write(cv2.imread(f'./Video/Image/{set}/{file}'))
          
      cv2.destroyAllWindows()
      video.release()

def deleteImageFolder(set):
    for file in os.listdir(f'./Video/Image/{set}'):
        os.remove(f'./Video/Image/{set}/{file}')