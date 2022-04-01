from math import exp
import os
from pickle import POP
from random import randint, random
import sys
from scipy import rand

from tqdm import tqdm
from Gene import Gene
from tensorflow import config
from VideoMaker import toImage, toVideo

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
devices = config.list_physical_devices("GPU")
config.experimental.set_memory_growth(devices[0], True)


#!------------------------------------------------------------------------------------------------------------------------------------------------------
#!------------------------------------CONSTANTS------------------------------------------------------------------------------------------------
#!------------------------------------------------------------------------------------------------------------------------------------------------------

POPULATION_SIZE = 100
NUM_GENERATIONS = 30
LEARNING_RATE = 0.3
ITERATION_OFFSET = 1000.0
BOARD_SIZE = (15, 15)
SET = 'set-one'

SAVING = True

THRESHOLD = 5
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
else:
    os.mkdir(f'./Models/{SET}')
    os.mkdir(f'./Video/Raw/{SET}')
    os.mkdir(f'./Video/Image/{SET}')
    os.mkdir(f'./Video/Video/{SET}')
        
    #Make the appropiate directoriespi
        
#Save some metada information
f = open(f'./Models/{SET}/meta.txt', 'w')
f.write(f'Population Size: {POPULATION_SIZE}\nGenerations: {NUM_GENERATIONS}\nLearning Rate: {LEARNING_RATE}\nBoard Size: {BOARD_SIZE[0],BOARD_SIZE[1]}')
f.close()


#!------------------------------------------------------------------------------------------------------------------------------------------------------
#!------------------------------------GENETIC ALGORITHIM------------------------------------------------------------------------------------------------
#!------------------------------------------------------------------------------------------------------------------------------------------------------



def save(set, generation):
    if SAVING:
       population[0][1].model.save(f'./Models/{SET}/generation-{generation}')

def writeFrame(path, frameBuffer, generation, score, fitness):
    f = open(path, 'a')
    
    for iteration, frame in enumerate(frameBuffer):
        
        f.write(f'Frame :: generation ~{generation}~ || iteration ~{iteration}~ || score ~{score}~ || high score ~{High_Score}~ || fitness ~{fitness}~\n')
        for a in range(frame.shape[0]):
            for b in range(frame.shape[1]):
                f.write(f'{frame[a][b][0]} ')
            f.write('\n')
        f.write('\n')
    
    
High_Score = -1
population = []
 
for a in range(POPULATION_SIZE): 
    gene = Gene(BOARD_SIZE)
    gene.snakeGame.addConstraints(START_ITERATION_THREHOLD, FOOD_ITERATION_GAIN)
    population.append([0.0, gene])
    

for a in range(NUM_GENERATIONS):
    #! Make this into a dictionary
    players = [a for a in population]
    
    frameBuffer = dict()
    
    with tqdm(total=POPULATION_SIZE) as bar:
        while len(players) > 0:
             
            for index, (_, gene) in enumerate(players):
                success = gene.updateState()
                if not success:
                   # print('FAIL for index ', index, end=' ')
                    players[index][0] = gene.fitness(ITERATION_OFFSET)
                   # print('Fitness for index ', index, ' ', population[index][0] )
                    
                    players.pop(index)
                    bar.update(1)
                    continue
                
                if not frameBuffer.__contains__(gene):
                    frameBuffer[gene] = []
                frameBuffer[gene].append(gene.snakeGame.asBoard())

                if gene.snakeGame.score > High_Score:
                    High_Score = gene.snakeGame.score
    
    population.sort(key=lambda x: x[0], reverse=True)  
    print([fit[0] for fit in population])
    print(f'Generation {a}, High Score {High_Score}')
    print(f'Highest Fitness: {population[0][0]} Score of Highest Fitness: {population[0][1].snakeGame.score}')
    #print([f'fitness #{index}: {fit[0]}\n' for index, fit in enumerate(population)])
    #print([f'Gene #{index} || Score: {fit[1].snakeGame.score} || fitness: {fit[0]}' for index, fit in enumerate(population)])
    print(f'Average Decision Time: {population[0][1].timeSum / population[0][1].snakeGame.iterations}')
    save(f'./Models/{SET}', generation=a)
    writeFrame(f'./Video/Raw/{SET}/{SET}.txt', frameBuffer[population[0][1]], generation=a, score=population[0][1].snakeGame.score, fitness=population[0][0])
    
    del frameBuffer
    
    for c in range(THRESHOLD, POPULATION_SIZE):
        population[c][1].mutate(LEARNING_RATE, c - THRESHOLD, POPULATION_SIZE)
        
    newPop = []
   # print(f'Lengths {newLength} {oldLength} {POPULATION_SIZE}')
    while len(newPop) < POPULATION_SIZE - THRESHOLD:
        #print('Still making it....')
        randIndexOne, randIndexTwo = -1, -1
        while randIndexOne == randIndexTwo:  
            x1 = random() 
            x2 = random()
            #\frac{1}{1\ +\ e^{2-1.3x}}e^{-1.9+3x} on desmos
            randIndexOne = int(min(1.0, exp(-1.9 + 3.0 * x1) / (1.0 + exp(2.0 - 1.3 * x1))) * POPULATION_SIZE)
            randIndexTwo = int(min(1.0,exp(-1.9 + 3.0 * x2) / (1.0 + exp(2.0 - 1.3 * x2))) * POPULATION_SIZE)
            #print(f'Guessing {randIndexOne} and {randIndexTwo}')
            
        newPop.append([0.0, population[randIndexOne][1].crossOver(population[randIndexTwo][1], START_ITERATION_THREHOLD)])
     
    for c in range(THRESHOLD):
          newPop.append([0.0, population[c][1]]) 
          newPop[-1][1].reset(START_ITERATION_THREHOLD)
          
    del population
    population = newPop
    


save(SET, 30)
toImage(SET)
toVideo(SET,fps=10)

