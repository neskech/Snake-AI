

from telnetlib import SE
from Snake import game
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras import losses
from tensorflow.keras import optimizers
from tensorflow.keras import Sequential

DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

class Gene:
    def __init__(self, boardSize) -> None:
        self.boardSize = boardSize
        
        self.snakeGame = game(boardSize, (0, 0))
        
        self.model = Sequential([
             layers.Input(shape=(boardSize[0], boardSize[1])),
             layers.Conv2D(filters=16, kernel_size=3, strides=2),
             layers.LeakyReLU(0.2),
             layers.Conv2D(filters=32, kernel_size=3, strides=2),
             layers.LeakyReLU(0.2),
             layers.Flatten(),
             layers.Dense(4, activation='softmax')
        ]),

        self.model.compile()
    
    def updateState(self) -> bool:
        board = self.snakeGame.asBoard()
        model_output = self.model(board)
        direction = DIRECTIONS[model_output]
        
        self.snakeGame.snake.changeDirection(direction)
        success = self.snakeGame.advance()
        if not success: return False
        
        return True
    
    def mutate(self, learningRate, fitnessIndex, populationSize):
        scalar = (fitnessIndex + 1) / populationSize
        randomWeights = tf.random.normal(shape=self.model.trainable_weights.shape)
        randomWeights *= scalar * learningRate
        
        self.model.trainable_weights += randomWeights
    
    def crossOver(self, other):
        self.model.trainable_weights = (self.model.trainable_weights + other.model.trainable_weights) / 2,0
    
    def fitness(self, iterOffset):
        return self.snakeGame.score * (self.snakeGame.iterations / iterOffset)
    
    def reset(self):
        self.snakeGame = game(self.boardSize, self.screenSize)
        
