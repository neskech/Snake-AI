import os
import pygame
import cv2

from Snake import Vec2

SCREEN_SIZE = (800,800)
VIEWPORT_SIZE = (800,600)
VIEWPORT_POS = (0, 200)

BACKGROUND_COLOR = (100,120,40)
VIEWPORT_COLOR = (3,20,5)
SNAKE_COLOR = (250,250,250)
FOOD_COLOR = (200, 0, 0)

SNAKE_BODY, SNAKE_HEAD, SNAKE_FOOD, EMPTY = 0.0, 1.0, 0.5, -1.0

def toImage(inPath, outDirectory, boardSize):
    width, height = SCREEN_SIZE[0], SCREEN_SIZE[1]
    colWidth, colHeight = VIEWPORT_SIZE[0] / boardSize.x, VIEWPORT_SIZE[1] / boardSize.y
    
    pygame.init()
    display = pygame.display.set_mode((width, height))
    pygame.display.flip()
    font = pygame.font.Font(None, 30)
    
    lines = open(inPath).readlines()
    i = 0
    while i < len(lines): 
            display.fill(BACKGROUND_COLOR)
            pygame.draw.rect(display, VIEWPORT_COLOR, pygame.Rect(VIEWPORT_POS[0], VIEWPORT_POS[1], VIEWPORT_SIZE[0], VIEWPORT_SIZE[1]))
            
            metadata = lines[i].split('~')
            generation = int(metadata[1])
            iteration = int(metadata[3])
            score = int(metadata[5])
            i += 1
            
            #Render the text
            Props = 0.10
            margins = Vec2(VIEWPORT_POS[0] * Props, VIEWPORT_POS[1] * Props)
            
            gen = font.render(f'Generation {generation}', True, (230, 220, 230))
            it = font.render(f'Iteration {iteration}', True, (230, 220, 230))
            sc = font.render(f'Score {score}', True, (230, 220, 230))
            display.blit(gen, (margins.x + 150.0, margins.y))
            display.blit(it, (margins.x + 400.0, margins.y))
            display.blit(sc, (margins.x + 600.0, margins.y))
            
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
            pygame.image.save(display, f'{outDirectory}/{iteration}.png')           
            i += 1 #Catch the extra \n at the end there
            
    pygame.quit()
    
    

def toVideo(inPath, outPath):
      fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
      video = cv2.VideoWriter(outPath, fourcc, 1, (SCREEN_SIZE[0], SCREEN_SIZE[1]), True)
      files = [file for file in os.listdir(inPath)]
      files.sort()
      for file in files:
          print(file, ' ' + f'{inPath}/{file}')
          video.write(cv2.imread(f'{inPath}/{file}'))
          
      cv2.destroyAllWindows()
      video.release()

