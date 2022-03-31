from cmath import exp
import os
from random import randint, random
import sys
from Gene import Gene


#!------------------------------------------------------------------------------------------------------------------------------------------------------
#!------------------------------------CONSTANTS------------------------------------------------------------------------------------------------
#!------------------------------------------------------------------------------------------------------------------------------------------------------

POPULATION_SIZE = 100
NUM_GENERATIONS = 200
LEARNING_RATE = 0.1
ITERATION_OFFSET = 10.0
BOARD_SIZE = (30, 30)
SET = 'set-one'

START_ITERATION_THREHOLD = 50
FOOD_ITERATION_GAIN = 100

#!------------------------------------------------------------------------------------------------------------------------------------------------------
#!------------------------------------VALIDATION-----------------------------------------------------------------------------------------------
#!------------------------------------------------------------------------------------------------------------------------------------------------------

#Do some validation 
if os.path.exists(f'./Models/{SET}'):
    delete = input(f'Delete all files belonging to {SET}? (yes or no)\n').lower() == 'yes'
    if not delete: sys.exit()
    
    for file in os.listdir(f'./Models/{SET}'):
        os.remove(f'./Models/{SET}/{file}')
    for file in os.listdir(f'./Video/Raw/{SET}'):
        os.remove(f'./Video/Raw/{SET}/{file}')
    for file in os.listdir(f'./Video/Image/{SET}'):
        os.remove(f'./Video/Image/{SET}/{file}')
    for file in os.listdir(f'./Video/Video/{SET}'):
        os.remove(f'./Video/Video/{SET}/{file}')
        
#Save some metada information
f = open(f'./Models/{SET}/meta.txt', 'w')
f.write(f'Population Size: {POPULATION_SIZE}\nGenerations {NUM_GENERATIONS}\nLearning Rate {LEARNING_RATE}\nBoard Size {BOARD_SIZE}')


#!------------------------------------------------------------------------------------------------------------------------------------------------------
#!------------------------------------GENETIC ALGORITHIM------------------------------------------------------------------------------------------------
#!------------------------------------------------------------------------------------------------------------------------------------------------------


High_Score = -1
population = []

def save(path, generation):
    population[0].model.save(f'{path}/generation-{generation}')

def writeFrame(path, frameBuffer, generation, score):
    f = open(path, 'a')
    
    for iteration, frame in enumerate(frameBuffer):
        
        f.write(f'Frame :: generation ~{generation}~ || iteration ~{iteration}~ || score ~{score}~ \n')
        for a in range(len(frame)):
            for b in range(len(frame[0])):
                f.write(f'{frame[a][b]} ')
            f.write('\n')
        f.write('\n')
    

   
for a in range(POPULATION_SIZE):
    gene = Gene(BOARD_SIZE)
    gene.snakeGame.addConstraints(START_ITERATION_THREHOLD, FOOD_ITERATION_GAIN)
    population.append((0.0, gene))
    

for a in range(NUM_GENERATIONS):
    #Loop through all population, waiting for all games to end
    #Record video data on all snakes, then find the best fitness at the end
    #And write his video data into a file. Dump all data out of memory
    #Of course at the end of a generation do some sorting and postprocessing 
    
    #OR instead of loading all video data into memory,take the best of the PREVIOUs generation to record. 
    #At the first iteration, choose a random one. At the last well fuk all that will be lost
    players = [a for a in population]
    bestGene = players[0]
    frameBuffer = []
    
    while len(players) > 0:
        
        for index, gene in enumerate(players):
            if gene is bestGene:
                frameBuffer.append(gene.snakeGame.asBoard())
                
            success = gene.updateState()
            
            if not success:
                population[index][0] = gene.fitness(ITERATION_OFFSET)
                players.remove(index)
                continue
    
            if gene.snakeGame.score > High_Score:
                High_Score = gene.snakeGame.score
    
    population.sort(key=lambda x: x[0])  
    for index, gene in enumerate(population):
        gene.mutate(LEARNING_RATE, index)
        
    for index, gene in enumerate(population):
        randIndex = -1
        while randIndex != index:    
            x = random()       
            #\frac{1}{1\ +\ e^{2-1.3x}}e^{-1.9+3x} on desmos
            randIndex = exp(-1.9 + 3.0 * x) / (1.0 + exp(2.0 - 1.3 * x))
        gene.crossOver(population[randIndex])
        
    for gene in population:
        gene.reset()
        
    save(f'./Models/{SET}', generation=a)
    writeFrame(f'./Video/Raw/{SET}', frameBuffer, generation=a, score=bestGene.snakeGame.score)


