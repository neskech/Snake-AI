
import random as rand
from pygame import draw as pydraw
from pygame import Rect
import numpy as np
import pygame

#! Call this snake not game
class game:
    def __init__(self, dimensions) -> None:
        self.dimensions = Vec2(dimensions[0], dimensions[1])
        
        DIRECTIONS = [Vec2(1, 0), Vec2(-1, 0), Vec2(0, 1), Vec2(0, -1)]
        self.snake = Snake(startLength = 3, 
                           startPos = Vec2(self.dimensions.x // 2, self.dimensions.y // 2 ), 
                           startDirection = DIRECTIONS[int(rand.randint(0, 3))], 
                           foodCallback = self.newFood)
        
        self.score = -1
        self.iterations = 0
    
        self.useConstraints = False
        self.food = Vec2()
        self.newFood()
      
    def addConstraints(self, startIterationThreshold, foodIterationGain):
        self.useConstraints = True
        self.iterationThreshold = startIterationThreshold
        self.foodIterationGain = foodIterationGain  
        
    def newFood(self):
        PROPS = 0.10
        
        margins = Vec2(int(PROPS * self.dimensions.x), int(PROPS * self.dimensions.y))
        x = rand.randint(0 + margins.x, self.dimensions.x - 1 - margins.x)
        y = rand.randint(0 + margins.y, self.dimensions.y - 1 - margins.y)
        self.food.x = x
        self.food.y = y
        
        self.score += 1
        if self.useConstraints:
            self.iterationThreshold += self.foodIterationGain
        
    def advance(self) -> bool:
        self.iterations += 1
        
        if self.useConstraints:
            if self.iterations >= self.iterationThreshold:
                return False
            
        success: bool = self.snake.advance(foodPos=self.food, dimensions=self.dimensions)
        if not success: return False

        return True
            
    def render(self, display, screenSize, viewPortSize, viewPortPos, snakeColor, foodColor, viewPortColor, font, fontColor):
        self.cellWidth = viewPortSize.x / self.dimensions.x
        self.cellHeight = viewPortSize.y / self.dimensions.y
        
        scoreImg = font.render(f'Score: {self.score}', True, fontColor)
        display.blit(scoreImg, (screenSize.x / 2.0 - 100.0, 50.0))
        pydraw.rect(display, viewPortColor, Rect(viewPortPos.x, viewPortPos.y, viewPortSize.x, viewPortSize.y))
        
        for pos in self.snake.body:
            pydraw.rect(display, snakeColor, Rect(viewPortPos.x + self.cellWidth * pos.x, viewPortPos.y + self.cellHeight * pos.y, self.cellWidth, self.cellHeight))
            
        pydraw.rect(display, foodColor, Rect(viewPortPos.x + self.cellWidth * self.food.x, viewPortPos.y + self.cellHeight * self.food.y, self.cellWidth, self.cellHeight))
       
    def handleInput(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self.snake.changeDirection(Vec2(-1, 0))
            elif event.key == pygame.K_d:
                self.snake.changeDirection(Vec2(1, 0))
            elif event.key == pygame.K_w:
                self.snake.changeDirection(Vec2(0, -1))
            elif event.key == pygame.K_s:
                self.snake.changeDirection(Vec2(0, 1))
     
    def asBoard(self) -> np.ndarray:
        board = np.empty(shape=(self.dimensions.x, self.dimensions.y, 1), dtype=np.float32)
        board.fill(-1.0)
        
        board[(self.snake.body[0].y, self.snake.body[0].x)] = 1.0
        for pos in self.snake.body[1:]:
            board[(pos.y, pos.x)] = 0.0
        board[(self.food.y, self.food.x)] = 0.5
        
        return board
    
    def asVector(self) -> np.ndarray:
       Direcs = [Vec2(1, 0), Vec2(-1, 0), Vec2(0, 1), Vec2(0, -1), Vec2(1, 1), Vec2(-1, -1), Vec2(1, -1), Vec2(-1, 1)]
       vector = np.empty(shape=(24,), dtype=np.float32)
       a = 0
       for direc in Direcs:
           vals = self.directionalData(direc)
           vector[a] = vals[0]
           vector[a + 1] = vals[1]
           vector[a + 2] = vals[2]
           a += 3
       return vector
    
    def directionalData(self, direction):
        values = [0.0, 0.0, 0.0]
        newPos = self.snake.body[0] + direction
        distance = 0.0
        
        while not self.snake.wallCollision(newPos, self.dimensions):
            if newPos.x == self.food.x and newPos.y == self.food.y:
               values[0] = 1.0
            elif self.snake.bodyCollision(newPos):
                values[1] = 1.0
            newPos = newPos + direction
            distance += 1.0
            
        values[2] = 1 / (1 + distance)
        return values
    
    def reset(self):
        
        DIRECTIONS = [Vec2(1, 0), Vec2(-1, 0), Vec2(0, 1), Vec2(0, -1)]
        self.snake.reset(3, Vec2(self.dimensions.x // 2, self.dimensions.y // 2 ), startDirection = DIRECTIONS[int(rand.randint(0, 3))])
        
        self.score = -1
        self.iterations = 0
        self.food = Vec2()
        self.newFood()
        
     
class Snake:
    def __init__(self, startLength, startPos, startDirection, foodCallback) -> None:
        self.body = []
        for a in range(startLength):
            self.body.append(Vec2(startPos.x + -startDirection.x * a, startPos.y + -startDirection.y * a))
            
        self.direction = startDirection
        self.foodCallback = foodCallback
            
    def changeDirection(self, newDirec):
        if not (-self.direction.x == newDirec.x and -self.direction.y == newDirec.y):
             self.direction = newDirec
             
    def checkBounds(self, dimensions) -> bool:
        pos = self.body[0]
        if self.wallCollision(pos, dimensions):
            return False
        
        if self.bodyCollision(pos): 
            return False
        
        return True
    
    def bodyCollision(self, head) -> bool:
          for p in self.body[1:]:
            if p.x == head.x and p.y == head.y:
                return True
          return False
      
    def wallCollision(self, head, dimensions) -> bool:
        return head.x < 0 or head.x >= dimensions.x or head.y < 0 or head.y >= dimensions.y
    
    def advance(self, foodPos, dimensions) -> bool:
        direc = self.body[0] - self.body[1]
        self.body[0] = self.body[0] + self.direction
        
        #If we hit the outer edge or the snake itself. If so, return false
        if not self.checkBounds(dimensions): return False
        
        #Check if it hit a food position. If so, call the food change callback
        gotFood = self.body[0].x == foodPos.x and self.body[0].y == foodPos.y
        if gotFood: self.foodCallback()
             
        for a in range(1, len(self.body)):
            tempDirec = direc
            if a != len(self.body) - 1:
                    direc = self.body[a] - self.body[a + 1]
                    
            self.body[a].x =  self.body[a].x + tempDirec.x
            self.body[a].y =  self.body[a].y + tempDirec.y  
        
        if gotFood:
            direc = Vec2(-direc.x, -direc.y)
            newPos = self.body[-1] + direc
            self.body.append(newPos)
            
        return True
    
    def reset(self, startLength, startPos, startDirection):
        self.body = []
        for a in range(startLength):
            self.body.append(Vec2(startPos.x + -startDirection.x * a, startPos.y + -startDirection.y * a))
        

class Vec2:
    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x
        self.y = y
        
    def __str__(self):
        return f'({self.x},{self.y})'
    
    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def distSQ(self, other):
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2
    
