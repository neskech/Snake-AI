
from pickle import FALSE
import random as rand
from pygame import draw as pydraw
from pygame import Rect
import numpy as np
import pygame

#! Call this snake not game
class game:
    def __init__(self, dimensions, screenSize = (0, 0)) -> None:
        self.snake = Snake(startLength = 3, 
                           startPos = Vec2(dimensions.x // 2, dimensions.y // 2 ), 
                           startDirection = Vec2(1, 0), 
                           foodCallback = self.newFood)
        
        self.dimensions = dimensions
        self.score = -1
        self.iterations = 0
        
        #ScreenSize of 0,0 means there is no display to be rendered
        if screenSize != (0, 0):
            self.cellWidth = screenSize[0] / dimensions.x
            self.cellHeight = screenSize[1] / dimensions.y
        
        self.useConstraints = False
        self.food = Vec2()
        self.newFood()
      
    def addConstraints(self, startIterationThreshold, foodIterationGain):
        self.useConstraints = True
        self.iterationThreshold = startIterationThreshold
        self.foodIterationGain = foodIterationGain  
        
    def newFood(self):
        PROPS = 0.10
        
        margins = Vec2(PROPS * self.dimensions.x, PROPS * self.dimensions.y)
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
            if self.iterations == self.iterationThreshold:
                return False
            
        success: bool = self.snake.advance(foodPos=self.food, dimensions=self.dimensions)
        if not success: return False

        return True
            
    def render(self, display, snakeColor, foodColor):
        for pos in self.snake.body:
            pydraw.rect(display, snakeColor, Rect(self.cellWidth * pos.x, self.cellHeight * pos.y, self.cellWidth, self.cellHeight))
            
        pydraw.rect(display, foodColor, Rect(self.cellWidth * self.food.x, self.cellHeight * self.food.y, self.cellWidth, self.cellHeight))
       
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
        board = np.empty(shape=(self.dimensions.x, self.dimensions.y), dtype=np.float32)
        board.fill(-1.0)
        
        board[(self.snake.body[0].y, self.snake.body[0].x)] = 1.0
        for pos in self.snake.body[1:]:
            board[(pos.y, pos.x)] = 0.0
        board[(self.food.y, self.food.x)] = 0.5
        
        return board

class Snake:
    def __init__(self, startLength, startPos, startDirection, foodCallback) -> None:
        self.body = []
        print(f'START HEHEHE {startLength} {startDirection}')
        for a in range(startLength):
            self.body.append(Vec2(startPos.x + -startDirection.x * a, startPos.y + -startDirection.y * a))
            
        self.direction = startDirection
        self.foodCallback = foodCallback
            
    def changeDirection(self, newDirec):
        if not (-self.direction.x == newDirec.x and -self.direction.y == newDirec.y):
             self.direction = newDirec
             
    def checkBounds(self, dimensions) -> bool:
        pos = self.body[0]
        if pos.x < 0 or pos.x >= dimensions.x or pos.y < 0 or pos.y >= dimensions.y:
            return True
        
        for p in self.body:
            if p.x == pos.x and p.y == pos.y:
                return True
            
        return False
        
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
    
