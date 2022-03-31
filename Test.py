from black import out
import Snake
from VideoMaker import toImage, toVideo
stuff = 'generation ~10~ iteration ~11~ score ~6~'
print(stuff.split('~'))

def writeFrame(path, frameBuffer, generation, score):
    f = open(path, 'a')
    
    for iteration, frame in enumerate(frameBuffer):
        
        f.write(f'Frame :: generation ~{generation}~ || iteration ~{iteration}~ || score ~{score}~ \n')
        for a in range(len(frame)):
            for b in range(len(frame[0])):
                f.write(f'{frame[a][b]} ')
            f.write('\n')
        f.write('\n')
        
snake = Snake.game(Snake.Vec2(30, 30))
frames = [snake.asBoard()]
for a in range(5):
    snake.advance()
    frames.append(snake.asBoard())
    
#writeFrame('./Video/Raw/Test/test.txt', frames, 0, 0)
#toImage('./Video/Raw/Test/test.txt', './Video/Image/Test', Snake.Vec2(30, 30))
toVideo('./Video/Image/Test', './Video/Video/Test/test.mp4')

