import frogger as fg
from NEAT.neat import NEAT
from NEAT.utils.visualization import visualize

moves = [fg.left, fg.up, fg.right, fg.down]
simulatedFrameTime = 1 / 20
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

# this is temporary, later will run in batches on one instance
def frogBenchSingle(processing_function):
    env = fg.Frogger(False, 0, simulatedFrameTime)
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

def frogBenchSingleVisualize(processing_function, timeScaling=1):

    env = fg.Frogger(True, 1/simulatedFrameTime * timeScaling, simulatedFrameTime)
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





if __name__ == '__main__':


    neat = NEAT(input_n=13 * 15, output_n=4)

    individual = neat.species[0].members[0]

    individual.evaluate(neat.input_n, neat.output_n)
    print(frogBenchSingleVisualize(individual.processing, 2))


