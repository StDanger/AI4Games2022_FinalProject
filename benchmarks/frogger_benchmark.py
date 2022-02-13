import frogger as fg
from NEAT.neat import NEAT
from multiprocessing import Pool
from NEAT.utils.visualization import visualize

moves = [fg.left, fg.up, fg.right, fg.down]
simulatedFrameTime = 1 / 20
jumpFrameCount = 7
def getMove(output):
    i = 0
    maxX = 0
    maxI = 0
    for x in output:
        if x > maxX:
            maxX = x
            maxI = i
        i += 1
    if maxX > 0.5:
        return moves[maxI]
    return None

def getEnv():
    env = fg.Frogger(False, 0, simulatedFrameTime)
    env.lives = 1
    env.initForAI()
    env.frog.jumpDuration = simulatedFrameTime * jumpFrameCount
    return env

# this is temporary, later will run in batches on one instance
def frogBenchSingle(processing_function, env: fg.Frogger):
    framesToSkip = 0
    while True:

        if framesToSkip > 0:
            res = env.runForAI(None)
            framesToSkip -= 1
        else:
            i = env.getIndex(env.frog.position)
            temp = env.board[i]
            env.board[i] = 5

            output = processing_function(env.board)
            move = getMove(output)

            res = env.runForAI(move)

            env.board[i] = temp
            if move is not None and env.frog.isInAir():
                framesToSkip = jumpFrameCount

        if res >= 0:
            return res


def frogBenchSingleVisualize(processing_function, timeScaling=1):
    env = fg.Frogger(True, 1 / simulatedFrameTime * timeScaling, simulatedFrameTime)
    env.lives = 1
    env.initForAI()

    #jumpFrameCount = int(env.frog.jumpDuration / simulatedFrameTime)
    jumpFrameCount = 7
    env.frog.jumpDuration = simulatedFrameTime*jumpFrameCount

    framesToSkip = 0
    while True:

        if framesToSkip > 0:
            res = env.runForAI(None)
            framesToSkip -= 1
        else:
            i = env.getIndex(env.frog.position)
            temp = env.board[i]
            env.board[i] = 5

            output = processing_function(env.board)
            move = getMove(output)

            res = env.runForAI(move)

            env.board[i] = temp
            if move is not None and env.frog.isInAir():
                framesToSkip = jumpFrameCount

        if res >= 0:
            return res


def frogbenchBatch(pfList):
    #print(len(pfList))
    res = []
    gameInstance = getEnv()
    for processing_function in pfList:
        res.append(frogBenchSingle(processing_function, gameInstance))
        gameInstance.resetEnv()
    return res


def frogbenchMultiprocess(pfList, process_count):
    size = len(pfList)
    chunksize = int(size/process_count)
    dividedList = []
    for i in range(process_count):
        if i == process_count-1:
            dividedList.append(pfList[i * chunksize:])
        else:
            dividedList.append(pfList[i*chunksize:(i+1)*chunksize])
    with Pool(process_count) as p:
        result = p.map(frogbenchBatch, dividedList)
        #return result
        return [item for sublist in result for item in sublist]

if __name__ == '__main__':
    neat = NEAT(input_n=13 * 15, output_n=4, pop_size=100)

    individual = neat.species[0].members[0]
    for m in [specie.members[0] for specie in neat.species]:
       m.evaluate(neat.input_n, neat.output_n)

    print(frogbenchMultiprocess([m.processing for m in [specie.members[0] for specie in neat.species]], 5))
    #print(frogbenchBatch([m.processing for m in neat.species[0].members]))
    #print(frogBenchSingle(individual.processing, getEnv()))




