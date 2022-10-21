

from random import random
from Snake import game
from Snake import Vec2
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras import Sequential
import numpy as np

#!-----------------------------------------------------------------------------------------------------------------------------------------------------------
#!-----------------------------------------------------------------------------------------------------------------------------------------------------------
#!----------------------------GENETIC REPRESENTATION OF THE SNAKE AND ITS 'BRAIN'----------------------------------------------------------------------------
#!-----------------------------------------------------------------------------------------------------------------------------------------------------------
#!-----------------------------------------------------------------------------------------------------------------------------------------------------------

DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

class Gene:
    def __init__(self, boardSize) -> None:
        self.boardSize = boardSize
        
        self.snakeGame = game(boardSize)
        
        self.model = Sequential([
             tf.keras.Input(shape=(24,)),
             layers.Dense(40, activation='relu'),
             layers.Dense(40, activation='relu'),
             layers.Dense(4, activation='softmax')
        ])
        self.model.compile()
    
    
    def combine(self, ConvWeights, DenseWeights):
         a, b = 0, 0
         for myLayer in self.model.layers:
           if type(myLayer) == layers.Conv2D:
                myLayer.set_weights(ConvWeights[a])
                a += 1

           elif type(myLayer) == layers.Dense:
                myLayer.set_weights(DenseWeights[b])
                b += 1

    def updateState(self) -> bool:
        board = self.snakeGame.asVector()
        
        model_output = np.argmax(self.model.predict_step(np.expand_dims(board, axis=0)))
        direction = DIRECTIONS[model_output]
        direction = Vec2(direction[0], direction[1])

        del board
        
        self.snakeGame.snake.changeDirection(direction)
        success = self.snakeGame.advance()
        if not success: return False
        
        return True
    
    def mutate(self, learningRate, fitnessIndex, populationSize):
        scalar = (fitnessIndex + 1) / populationSize
        scalar = 1.0
        for layer in self.model.layers:
           if type(layer) == layers.Conv2D:
                KernelNoise = scalar * learningRate * tf.random.normal(shape=layer.get_weights()[0].shape)
                BiasNoise = scalar * learningRate * tf.random.normal(shape=layer.get_weights()[1].shape)
                layer.set_weights([tf.clip_by_value(KernelNoise + layer.get_weights()[0], -1.0, 1.0),
                                   tf.clip_by_value(BiasNoise + layer.get_weights()[1], -1.0, 1.0)])

           elif type(layer) == layers.Dense:
                WeightsNoise = scalar * learningRate * tf.random.normal(shape=layer.get_weights()[0].shape)
                BiasNoise = scalar * learningRate * tf.random.normal(shape=layer.get_weights()[1].shape)
                layer.set_weights([tf.clip_by_value(WeightsNoise + layer.get_weights()[0], -1.0, 1.0), 
                                   tf.clip_by_value(BiasNoise + layer.get_weights()[1], -1.0, 1.0)])
                    

    
    def crossOver(self, other, startIterationThreshold):
        ConvWeights, DenseWeights = [], []
        for myLayer, otherLayer in zip(self.model.layers, other.model.layers):
           if type(myLayer) == layers.Conv2D:
                KernelNoise = crossWeights(myLayer.get_weights()[0], otherLayer.get_weights()[0]) 
                BiasNoise = crossBiases(myLayer.get_weights()[1], otherLayer.get_weights()[1])
                ConvWeights.append([KernelNoise, BiasNoise])

           elif type(myLayer) == layers.Dense:
                WeightsNoise = crossWeights(myLayer.get_weights()[0], otherLayer.get_weights()[0]) 
                BiasNoise = crossBiases(myLayer.get_weights()[1], otherLayer.get_weights()[1]) 
                DenseWeights.append([WeightsNoise, BiasNoise])
                
        newGene = Gene(self.boardSize)
        if self.snakeGame.useConstraints:
          newGene.snakeGame.addConstraints(startIterationThreshold, self.snakeGame.foodIterationGain)
        newGene.combine(ConvWeights, DenseWeights)
        return newGene
    
    def fitness(self, iterOffset):  
        #IterOffset makes having higher iteration count (longer life) less desirable
        #Than having a lot of score / food  
        return 10 ** self.snakeGame.score * (self.snakeGame.iterations / iterOffset)
    
    def reset(self, startIterationThreshold):
        temp = game(self.boardSize)
        if self.snakeGame.useConstraints:
          temp.addConstraints(startIterationThreshold, self.snakeGame.foodIterationGain)
        del self.snakeGame
        self.snakeGame = temp
        self.timeSum = 0.0
        


def crossWeights(weights1, weights2) -> np.ndarray:
    newWeights = np.empty(shape=weights1.shape)
    #These two guys should have the same shape
    randRow = int(random() * weights1.shape[0])
    randCol = int(random() * weights1.shape[1])
    for r in range(weights1.shape[0]):
        for c in range(weights1.shape[1]):
            if r <= randRow and c <= randCol:
                newWeights[r, c] = weights2[r, c]
            else:
                newWeights[r, c] = weights1[r, c]
    return newWeights
                
def crossBiases(bias1, bias2) -> np.ndarray:
    newBias = np.empty(shape=bias1.shape)
    #These two guys should have the same shape
    randIndex = int(random() * bias1.shape[0])
    for index in range(bias1.shape[0]):
            if index <= randIndex:
                newBias[index] = bias1[index]
            else:
                newBias[index] = bias2[index]
    return newBias