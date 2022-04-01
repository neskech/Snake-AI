

from re import sub
import time
from Snake import game
from Snake import Vec2
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras import Sequential
import numpy as np

DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

class Gene:
    def __init__(self, boardSize) -> None:
        self.boardSize = boardSize
        
        self.snakeGame = game(boardSize, (0, 0))
        
        self.model = Sequential([
             tf.keras.Input(shape=(boardSize[0], boardSize[1], 1)),
             layers.Conv2D(filters=8, kernel_size=3, strides=2),
             layers.LeakyReLU(0.2),
             layers.Conv2D(filters=16, kernel_size=3, strides=2),
             layers.LeakyReLU(0.2),
             layers.Flatten(),
             layers.Dense(4, activation='softmax')
        ])
        self.model.compile()
        #print(self.model.summary())
    
    def updateState(self) -> bool:
        board = self.snakeGame.asBoard()
        board = tf.convert_to_tensor(board.reshape((1,) + board.shape))
        
        start = time.time()
        model_output = np.argmax(self.model.predict(board))
        direction = DIRECTIONS[model_output]
        direction = Vec2(direction[0], direction[1])
        #print(f'Direc index {model_output} || Direction {direction} || time {time.time() - start}')
        del board
        
        self.snakeGame.snake.changeDirection(direction)
        success = self.snakeGame.advance()
        if not success: return False
        
        return True
    
    def mutate(self, learningRate, fitnessIndex, populationSize):
        scalar = (fitnessIndex + 1) / populationSize
        for layer in self.model.layers:
           if type(layer) == layers.Conv2D:
                KernelNoise = scalar * learningRate * tf.random.normal(shape=layer.get_weights()[0].shape)
                BiasNoise = scalar * learningRate * tf.random.normal(shape=layer.get_weights()[1].shape)
                layer.set_weights([KernelNoise + layer.get_weights()[0], BiasNoise + layer.get_weights()[1]])

           elif type(layer) == layers.Dense:
                WeightsNoise = scalar * learningRate * tf.random.normal(shape=layer.get_weights()[0].shape)
                BiasNoise = scalar * learningRate * tf.random.normal(shape=layer.get_weights()[1].shape)
                layer.set_weights([WeightsNoise + layer.get_weights()[0], BiasNoise + layer.get_weights()[1]])
                    

    
    def crossOver(self, other):
        for myLayer, otherLayer in zip(self.model.layers, other.model.layers):
           if type(myLayer) == layers.Conv2D:
                KernelNoise = (myLayer.get_weights()[0] + otherLayer.get_weights()[0]) / 2.0
                BiasNoise = (myLayer.get_weights()[1] + otherLayer.get_weights()[1]) / 2.0
                myLayer.set_weights([KernelNoise, BiasNoise])

           elif type(myLayer) == layers.Dense:
                WeightsNoise = (myLayer.get_weights()[0] + otherLayer.get_weights()[0]) / 2.0
                BiasNoise = (myLayer.get_weights()[1] + otherLayer.get_weights()[1]) / 2.0
                myLayer.set_weights([WeightsNoise, BiasNoise])
    
    def fitness(self, iterOffset):
        return (1 + self.snakeGame.score) * (self.snakeGame.iterations / iterOffset)
    
    def reset(self):
        del self.snakeGame
        self.snakeGame = game(self.boardSize)
        
