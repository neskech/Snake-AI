from cmath import exp
import os
from random import randint, random
import sys
from Gene import Gene
from tensorflow import config
from tqdm import tqdm

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
devices = config.list_physical_devices("GPU")
config.experimental.set_memory_growth(devices[0], True)


#!------------------------------------------------------------------------------------------------------------------------------------------------------
#!------------------------------------CONSTANTS------------------------------------------------------------------------------------------------
#!------------------------------------------------------------------------------------------------------------------------------------------------------

POPULATION_SIZE = 30
NUM_GENERATIONS = 5
LEARNING_RATE = 0.1
ITERATION_OFFSET = 10.0
BOARD_SIZE = (30, 30)
SET = 'set-one'

START_ITERATION_THREHOLD = 50
FOOD_ITERATION_GAIN = 50

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



def save(path, generation):
    population[0][1].model.save(f'{path}/generation-{generation}')

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
    bestGene = players[0][1]
    bestFitness = -1.0
    frameBuffer = []
    
    with tqdm(total=len(players)) as bar:
        while len(players) > 0:
            
            for index, (_, gene) in enumerate(players):
                success = gene.updateState()
                
                if not success:
                    population[index][0] = gene.fitness(ITERATION_OFFSET)
                    if gene is bestGene: bestFitness = population[index][0]
                    players.pop(index)
                    bar.update(1)
                    continue
                
                if gene is bestGene:
                    frameBuffer.append(gene.snakeGame.asBoard())
        
                if gene.snakeGame.score > High_Score:
                    High_Score = gene.snakeGame.score
    
    population.sort(key=lambda x: x[0])  
    for index, (_, gene) in enumerate(population):
        gene.mutate(LEARNING_RATE, index, POPULATION_SIZE)
        
    props = 0.20
    length = int(POPULATION_SIZE * props)
    for index, (_, gene) in enumerate(population[:length]):
        randIndex = -1
        while randIndex != index:    
            x = random()       
            #\frac{1}{1\ +\ e^{2-1.3x}}e^{-1.9+3x} on desmos
            randIndex = int(length * x)
        gene.crossOver(population[randIndex][1])
    
    print(f'Generation {a}, High Score {High_Score}')
    #print([f'fitness #{index}: {fit[0]}\n' for index, fit in enumerate(population)])
    print([f'Score #{index}: {fit[1].snakeGame.score}' for index, fit in enumerate(population)])
    save(f'./Models/{SET}', generation=a)
    writeFrame(f'./Video/Raw/{SET}/{SET}.txt', frameBuffer, generation=a, score=bestGene.snakeGame.score, fitness=bestFitness)
    
    for (_, gene) in population:
          gene.reset()


