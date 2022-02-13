import sys, pygame, copy, random, os
from time import perf_counter, sleep


'''
TODO:
Done for now :)

'''

#  type of obstacle, just a helper class used as an enum
class TypesOfObstacles:
    def __init__(self):
        self.cars = 1
        self.flowers = 2
        self.logs = 3


TOO = TypesOfObstacles()

printFPS = True
drawDebugObstacles = False

# jump directions
left = (-1, 0)
up = (0, -1)
right = (1, 0)
down = (0, 1)


# linear interpolation between a and b, alpha 1 = 100% a
def lerpf(a, b, alpha):
    if alpha < 0:
        alpha = 0
    if alpha > 1:
        alpha = 1
    return a * alpha + b * (1 - alpha)


class Frog:
    def __init__(self, gameInstance):
        self.jumpDuration = 0.18
        self.currJumpTime = 0
        self.jumpDestination = None
        self.bufferedJump = None
        self.startingPos = (7, 12)
        self.position = self.startingPos
        self.jumpDestination = self.position
        self.gameInstance = gameInstance
        self.normalSize = (gameInstance.tileSize[0] * 3 / 6, gameInstance.tileSize[0] * 3 / 6)
        self.mainColor = (10, 200, 30)
        self.raft = None
        self.raftOffset = 0
        self.drawOffset = 0

    def update(self, deltaTime):
        self.currJumpTime -= deltaTime
        if not self.isInAir():  # frog is not in air
            self.currJumpTime = 0
            if self.position != self.jumpDestination:
                self.moved()

            if self.raft is None:
                row = self.gameInstance.rows[self.position[1]]
                if row.emptyRange != 0:
                    if row.isWater:
                        row.tryPlacingFrog(self)
                        if self.raft is None:
                            self.kill()

                tile = self.gameInstance.getTile(self.position)
                if tile <= 0:
                    self.kill()
                if tile == 2:
                    self.gameInstance.reset(False)
                if tile == 1:
                    if self.raft is None:
                        self.raftOffset = 0
                        self.drawOffset = 0
                else:
                    self.raftOffset = 0
                    self.drawOffset = 0
            if self.bufferedJump is not None:
                self.jump(self.bufferedJump)
                self.bufferedJump = None

        else:  # frog is in air
            if self.raft is not None:
                self.raft.removeFrog()


    def draw(self, screen):
        drawPos = self.gameInstance.getCircleDrawPosition(self.position)
        size = self.normalSize[0] / 2
        if self.currJumpTime > 0:
            fPos = self.gameInstance.getCircleDrawPosition(self.jumpDestination)
            alpha = self.currJumpTime/self.jumpDuration
            drawPos = (lerpf(drawPos[0], fPos[0], alpha), lerpf(drawPos[1], fPos[1], alpha))


        pygame.draw.circle(screen, self.mainColor, (drawPos[0]+self.drawOffset, drawPos[1]), size)


        return

    def jump(self, where):
        if self.currJumpTime > 0:
            self.bufferedJump = where
            return
        self.jumpDestination = (self.position[0] + where[0], self.position[1] + where[1])
        if self.jumpDestination[0] < 0 or self.jumpDestination[1] < 0 or self.jumpDestination[0] > 14 or \
                self.jumpDestination[1] > 12:
            self.jumpDestination = self.position
            return
        self.currJumpTime = self.jumpDuration

    def moved(self):

        self.position = self.jumpDestination
        rowOffset = 0
        offset = 0
        row = self.gameInstance.rows[self.position[1]]
        if row.emptyRange != 0:
            if row.isWater:
                rowOffset = row.currOffset


        if rowOffset - self.drawOffset <= -self.gameInstance.tileSize[0] / 2:
            self.setPosition((self.position[0] + 1, self.position[1]))
            offset = -self.gameInstance.tileSize[0]
        elif rowOffset - self.drawOffset > self.gameInstance.tileSize[0] / 2:
            self.setPosition((self.position[0] - 1, self.position[1]))
            offset = self.gameInstance.tileSize[0]
        self.drawOffset += offset


    def kill(self):
        self.gameInstance.reset(True)

    def setPosition(self, pos):
        self.position = pos
        self.jumpDestination = pos

    def isInAir(self):
        return self.currJumpTime > 0



# if fixed frame time is set, the game will act as if this time has passed in each frame,
# no matter what time actually passed. So, if MaxFPS is 200, and fixedFrametime is 1/100
# the game will run at double speed. Useful for speeding up simulation.
# the fastest setting is maxFPS uncapped, and fixedFrametime something realistic, I'd say at least 1/30

class Frogger:
    def __init__(self, bDisplay=True, MaxFPS=0, fixedFrametime=0):

        # 0 for unlimited
        self.maxFPS = MaxFPS

        self.wSize = (800, 950)
        self.tileSize = (int(self.wSize[0] / 15), int(self.wSize[1] / 14))
        self.bDisplay = bDisplay

        self.gameEnded = False
        self.roundTime = 30  # time limit for player/ai
        self.timeRemaining = self.roundTime  # current time remaining
        self.score = 0
        self.totalScore = 0
        self.scoreForGoal = 400
        self.scoreForSecond = 3
        self.scorePerY = 10

        self.deltaTime = 0.00001  # frame time in seconds, updated in run()
        self.initTime = perf_counter()
        self.lastFrameTime = perf_counter()
        self.fixedFrametime = fixedFrametime

        self.currLevel = 1
        self.goalsCollected = 0


        if bDisplay:
            pygame.init()
            self.screen = pygame.display.set_mode(self.wSize)
            self.font = pygame.font.Font(None, int(self.wSize[1] / 25))
            self.highScore = 0
            if os.path.isfile("highscores.txt"):
                f = open("highscores.txt", "r")
                self.highScore = int(f.readline())


        # 0 - kills frog
        # 1 - doesn't kill frog
        # 2 - goal
        # 5 - frog
        # -1 - already collected goal, also kills frog
        # moving obstacles update this board in real time (or scaled real time)
        self.board = [
            0, 2, 0, 0, 2, 0, 0, 2, 0, 0, 2, 0, 0, 2, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        ]
        self.initialBoard = copy.deepcopy(self.board)  # this board remains unchanged

        self.frog = None

        self.rows = []
        self.level1()
        self.lives = 3

    class Row:
        def __init__(self, emptyRange, filledRange, speed, index, type, isWater, gameInstance):

            self.emptyRange = emptyRange

            #  this goes up to tile width, then the row is shifted
            self.currOffset = 0

            if emptyRange == 0:
                return

            self.filledRange = filledRange
            self.speed = speed
            self.startWithFilled = random.randint(0, 1)
            self.type = type
            self.index = index
            self.isWater = isWater
            self.gInst: Frogger = gameInstance
            self.hasFrog = False



            #  this is what comes out of the edge
            self.emptyToSpawn = 0
            self.filledToSpawn = 0

            if speed > 0:
                self.spawnPos = 0
            else:
                self.spawnPos = 14

            self.obstacles = []

            if self.startWithFilled == 0:
                self.spawnEmpty()
            else:
                self.spawnFilled()

        class Obstacle:
            def __init__(self, positionX, size, parentRow, isGoingLeft):
                self.isLeft = isGoingLeft
                self.sizeX = size
                self.pos = [positionX, parentRow.index]
                self.realXOffset = 0
                self.type = parentRow.type
                self.parentRow = parentRow
                self.color = (255, 0, 0)
                self.drawYSize = parentRow.gInst.tileSize[1]*4/6
                self.frog: Frog = None
                carColors = [(200, 200, 200), (200, 40, 40), (200, 80, 200), (200, 200, 50), (0, 200, 200)]
                if self.type == TOO.logs:
                    self.color = (130, 70, 50)
                if self.type == TOO.cars:
                    self.color = random.choice(carColors)
                    mult = random.uniform(0.4, 1.2)
                    self.color = (self.color[0]*mult, self.color[1]*mult, self.color[2]*mult)
                if self.type == TOO.flowers:
                    self.color = (200, 10, 10)
                    self.drawYSize = parentRow.gInst.tileSize[0]/2

                # positions that this obstacle occupies
                self.possToDraw = []

                for i in range(self.sizeX):
                    j = -1
                    if self.isLeft:
                        j = 1
                    self.possToDraw.append([self.pos[0] + i * j, self.pos[1]])
                return

            def update(self, deltaTime, realXOffset, posXChange, offsetChange):
                self.pos[0] += posXChange
                for p in self.possToDraw:
                    p[0] += posXChange
                self.realXOffset = realXOffset
                if self.frog is not None:
                    if not self.frog.isInAir():
                        self.frog.setPosition((self.frog.position[0] + posXChange, self.frog.position[1]))
                        self.frog.raftOffset = self.realXOffset
                        self.frog.drawOffset -= posXChange*self.parentRow.gInst.tileSize[0]
                        if self.frog.position[0] < 0:
                            self.frog.setPosition((0, self.frog.position[1]))
                        if self.frog.position[0] > 14:
                            self.frog.setPosition((14, self.frog.position[1]))
                        tile = self.parentRow.gInst.getTile(self.frog.position)
                        self.frog.drawOffset += offsetChange
                        if tile <= 0:
                            self.removeFrog()


                if self.pos[0] + self.sizeX < 0 or self.pos[0] - self.sizeX > 14:
                    self.parentRow.removeObstacle(self)

                return

            def draw(self, screen):
                size = (self.parentRow.gInst.tileSize[0], self.drawYSize)
                for p in self.possToDraw:
                    if self.type == TOO.flowers:
                        drawPos = self.parentRow.gInst.getCircleDrawPosition(tuple(p))
                        pygame.draw.circle(screen, self.color, (drawPos[0]+self.realXOffset, drawPos[1]), self.drawYSize)
                    else:
                        drawPos = self.parentRow.gInst.getRectDrawPosition(tuple(p), size)
                        pygame.draw.rect(screen, self.color, (drawPos[0]+self.realXOffset, drawPos[1], size[0], size[1]))
                return

            def setFrog(self, frog: Frog):
                self.frog = frog
                self.frog.raft = self

            def removeFrog(self):
                self.parentRow.hasFrog = False
                self.frog.raft = None
                self.frog = None



        def spawnEmpty(self):
            self.emptyToSpawn = random.randint(self.emptyRange[0], self.emptyRange[1])

        def spawnFilled(self):
            self.filledToSpawn = random.randint(self.filledRange[0], self.filledRange[1])
            xPos = self.spawnPos
            if self.speed > 0:
                xPos -= 1
            else:
                xPos += 1
            self.obstacles.insert(0, self.Obstacle(xPos, self.filledToSpawn, self, self.speed < 0))

        def update(self, deltaTime):
            if self.emptyRange == 0:
                return
            offsetChange = deltaTime * self.speed * self.gInst.tileSize[0]
            self.currOffset += offsetChange

            absOff = abs(self.currOffset)
            shift = 0
            shouldSpawn = False
            if absOff >= self.gInst.tileSize[0]:
                absOff -= self.gInst.tileSize[0]

                # shifting the whole row
                yIndex = self.gInst.getIndex((0, self.index))
                newSpawnIndex = yIndex + self.spawnPos
                if self.speed > 0:
                    self.currOffset = absOff
                    shift = 1
                    for i in range(14, 0, -1):
                        self.gInst.board[yIndex + i] = self.gInst.board[yIndex + i - 1]
                else:
                    shift = -1
                    self.currOffset = -absOff
                    for i in range(0, 14):
                        self.gInst.board[yIndex + i] = self.gInst.board[yIndex + i + 1]

                if self.emptyToSpawn > 0:
                    self.emptyToSpawn -= 1
                    self.gInst.board[newSpawnIndex] = int(not self.isWater)  # if it's water, then the tile we spawn is friendly
                    if self.emptyToSpawn == 0:
                        shouldSpawn = True
                elif self.filledToSpawn > 0:
                    self.filledToSpawn -= 1
                    self.gInst.board[newSpawnIndex] = int(self.isWater)
                    if self.filledToSpawn == 0:
                        self.spawnEmpty()


            for o in self.obstacles:
                o.update(deltaTime, self.currOffset, shift, offsetChange)
            if shouldSpawn:
                self.spawnFilled()

        def draw(self, screen):
            if self.emptyRange == 0:
                return
            for o in self.obstacles:
                o.draw(screen)

        def removeObstacle(self, obstacle):
            self.obstacles.remove(obstacle)

        def tryPlacingFrog(self, frog: Frog):

            '''offset = 0
            print(self.currOffset, frog.raftOffset, frog.drawOffset)
            if self.currOffset - frog.raftOffset <= -self.gInst.tileSize[0]/2:
                frog.setPosition((frog.position[0] + 1, frog.position[1]))
                offset = -self.gInst.tileSize[0]
            elif self.currOffset - frog.raftOffset > self.gInst.tileSize[0]/2:
                frog.setPosition((frog.position[0] - 1, frog.position[1]))
                offset = self.gInst.tileSize[0]
            #frog.raftOffset += offset
            frog.drawOffset += offset'''


            if self.gInst.getTile(frog.position) == 1:
                for o in self.obstacles:
                    if list(frog.position) in o.possToDraw:
                        o.setFrog(frog)
                        return


    def level1(self, hardReset=False):
        self.currLevel = 1
        self.rows.clear()
        firstRow = [self.getTile((x, 0)) for x in range(15)]
        self.board = copy.deepcopy(self.initialBoard)
        if not hardReset:
            for x in range(15):
                self.board[x] = firstRow[x]

        self.rows.append(self.Row(0, 0, 0, 0, 0, 0, self))
        self.rows.append(self.Row((2, 3), (3, 3), 2, 1, TOO.logs, True, self))
        self.rows.append(self.Row((3, 4), (2, 2), -3.2, 2, TOO.flowers, True, self))
        self.rows.append(self.Row((3, 4), (4, 5), 2.5, 3, TOO.logs, True, self))
        self.rows.append(self.Row((3, 7), (2, 2), 1.8, 4, TOO.logs, True, self))
        self.rows.append(self.Row((2, 2), (3, 3), -2.9, 5, TOO.flowers, True, self))
        self.rows.append(self.Row(0, 0, 0, 6, 0, 0, self))
        self.rows.append(self.Row((5, 11), (2, 2), -2.1, 7, TOO.cars, False, self))
        self.rows.append(self.Row((8, 17), (1, 1), 2.3, 8, TOO.cars, False, self))
        self.rows.append(self.Row((4, 9), (1, 1), -1.7, 9, TOO.cars, False, self))
        self.rows.append(self.Row((4, 7), (1, 1), 1.7, 10, TOO.cars, False, self))
        self.rows.append(self.Row((4, 7), (1, 1), -1.5, 11, TOO.cars, False, self))
        self.rows.append(self.Row(0, 0, 0, 12, 0, 0, self))

    def level2(self, hardReset=False):
        self.currLevel = 2
        self.rows.clear()
        firstRow = [self.getTile((x, 0)) for x in range(15)]
        self.board = copy.deepcopy(self.initialBoard)
        if not hardReset:
            for x in range(15):
                self.board[x] = firstRow[x]

        self.rows.append(self.Row(0, 0, 0, 0, 0, 0, self))
        self.rows.append(self.Row((2, 4), (2, 4), 3.1, 1, TOO.logs, True, self))
        self.rows.append(self.Row((3, 4), (3, 3), -4.2, 2, TOO.flowers, True, self))
        self.rows.append(self.Row((3, 4), (2, 5), 2.5, 3, TOO.logs, True, self))
        self.rows.append(self.Row((2, 7), (2, 3), -3.8, 4, TOO.flowers, True, self))
        self.rows.append(self.Row((3, 5), (2, 4), 3.5, 5, TOO.logs, True, self))
        self.rows.append(self.Row((5, 11), (2, 2), -3.1, 6, TOO.cars, False, self))
        self.rows.append(self.Row((5, 11), (2, 2), -2.1, 7, TOO.cars, False, self))
        self.rows.append(self.Row((8, 17), (1, 1), 3.3, 8, TOO.cars, False, self))
        self.rows.append(self.Row((4, 9), (1, 1), -2.7, 9, TOO.cars, False, self))
        self.rows.append(self.Row((4, 7), (1, 1), 2.7, 10, TOO.cars, False, self))
        self.rows.append(self.Row((4, 7), (1, 1), 3.5, 11, TOO.cars, False, self))
        self.rows.append(self.Row(0, 0, 0, 12, 0, 0, self))

    def reset(self, didDie):
        # this is the score for current life, it should maybe be sent to the AI
        tempScore = 0
        if didDie:

            self.lives -= 1
            tempScore += self.scorePerY*(12 - self.frog.position[1])
            if self.lives <= 0:
                self.gameEnded = True

                self.totalScore += tempScore
                #self.saveHighscore()
                return
        else:

            tempScore += self.scoreForGoal
            tempScore += self.scoreForSecond*self.timeRemaining
            self.goalsCollected += 1
            self.board[self.getIndex(self.frog.position)] = -1

        self.score = tempScore
        self.totalScore += tempScore
        self.frog.position = self.frog.startingPos
        self.frog.jumpDestination = self.frog.startingPos
        self.frog.currJumpTime = 0
        self.frog.bufferedJump = None
        self.timeRemaining = self.roundTime
        if self.goalsCollected >= 5:
            self.goalsCollected = 0
            if self.currLevel == 1:
                self.level2(True)
            else:
                self.level1(True)
            return
        if self.currLevel == 1:
            self.level1()
        else:
            self.level2()

    def resetEnv(self):
        self.frog.position = self.frog.startingPos
        self.frog.jumpDestination = self.frog.startingPos
        self.frog.currJumpTime = 0
        self.frog.bufferedJump = None
        self.timeRemaining = self.roundTime
        self.score = 0
        self.totalScore = 0
        self.goalsCollected = 0
        self.gameEnded = False
        self.lives = 1

        self.level1()


    def __drawBackground(self):

        waterColor = (20, 80, 200)
        pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, self.wSize[0], self.wSize[1]))

        pygame.draw.rect(self.screen, waterColor, (0, 0, self.wSize[0], self.tileSize[1] * 6))
        pygame.draw.rect(self.screen, (20, 250, 40), (0, 0, self.wSize[0], self.tileSize[1]))

        # 2*groundSize + puddleSize = 3!!! 0.9*2 + 1.2 = 3
        groundSize = int(self.tileSize[0] * 0.9)
        puddleSize = int(self.tileSize[0] * 1.2)
        currOffset = groundSize
        topOffset = int(self.tileSize[1] / 5)

        # drawing goal puddles
        for i in range(5):
            pygame.draw.rect(self.screen, waterColor, (currOffset, topOffset, puddleSize, self.tileSize[1] - topOffset))
            currOffset += groundSize * 2 + puddleSize

        pygame.draw.rect(self.screen, (90, 150, 255), (0, self.tileSize[1] * 6, self.wSize[0], self.tileSize[1]))
        pygame.draw.rect(self.screen, (20, 20, 20), (0, self.tileSize[1] * 7, self.wSize[0], self.tileSize[1]*5))
        pygame.draw.rect(self.screen, (90, 150, 255), (0, self.tileSize[1] * 12, self.wSize[0], self.tileSize[1]))

    def __draw(self):
        self.__drawBackground()

        # drawing the grid status
        if drawDebugObstacles:
            for x in range(15):
                for y in range(13):
                    if self.getTile((x, y)) == 0:
                        pygame.draw.rect(self.screen, (255, 0, 0, 0),
                                         (x * self.tileSize[0], y * self.tileSize[1], self.tileSize[0], self.tileSize[1]))
                    else:
                        pygame.draw.rect(self.screen, (255, 255, 255, 0),
                                         (x * self.tileSize[0], y * self.tileSize[1], self.tileSize[0], self.tileSize[1]))

        for x in range(15):
            if self.getTile((x, 0)) == -1:
                pygame.draw.circle(self.screen, (0, 100, 15), self.getCircleDrawPosition((x, 0)),self.tileSize[0]/2)

        for r in self.rows:
            r.draw(self.screen)
        if drawDebugObstacles:
            pygame.draw.rect(self.screen, (0, 255, 0, 0),
                             (self.frog.position[0] * self.tileSize[0], self.frog.position[1] * self.tileSize[1], self.tileSize[0], self.tileSize[1]))

        self.frog.draw(self.screen)

        displayScore = (12 - self.frog.position[1])*self.scorePerY + self.totalScore

        scoreText = self.font.render('CURRENT SCORE: ' + str(int(displayScore)), True, (255, 255, 255))
        timeText = self.font.render('TIME LEFT: ' + str(int(self.timeRemaining)), True, (255, 255, 255))
        livesText = self.font.render('LIVES: ' + str(self.lives), True, (255, 30, 30))

        hs = self.highScore
        if hs < displayScore:
            hs = displayScore

        highscoreText = self.font.render('HIGHSCORE: ' + str(int(hs)), True, (255, 255, 255))

        self.screen.blit(scoreText, (5, 13*self.tileSize[1]+5))
        self.screen.blit(timeText, (self.tileSize[0]*10, 13 * self.tileSize[1]+5))
        self.screen.blit(livesText, (self.tileSize[0] * 10, 13 * self.tileSize[1] + 10 + timeText.get_size()[1]))
        self.screen.blit(highscoreText, (5, 13 * self.tileSize[1] + 10 + scoreText.get_size()[1]))

        pygame.display.flip()

    def __update(self):
        # update logic here

        if self.timeRemaining <= 0:
            self.reset(True)
            return

        for r in self.rows:
            r.update(self.deltaTime)

        self.frog.update(self.deltaTime)

        if self.bDisplay:
            self.__draw()

    def run(self):
        self.frog = Frog(self)
        while not self.gameEnded:
            currTime = perf_counter()
            self.deltaTime = currTime - self.lastFrameTime
            if self.maxFPS > 0:
                diff = 1.0 / self.maxFPS - self.deltaTime
                if diff > 0:
                    sleep(diff)
                    currTime = perf_counter()
                    self.deltaTime = currTime - self.lastFrameTime
            self.lastFrameTime = currTime
            #if int((currTime - self.initTime) * 100) % 100 == 0 and printFPS:
                #print("FPS=", 1.0 / self.deltaTime)

            if self.fixedFrametime > 0:
                self.deltaTime = self.fixedFrametime

            self.timeRemaining -= self.deltaTime

            #  --------EVENTS-------
            if self.bDisplay:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            self.frog.jump(left)
                        if event.key == pygame.K_UP:
                            self.frog.jump(up)
                        if event.key == pygame.K_RIGHT:
                            self.frog.jump(right)
                        if event.key == pygame.K_DOWN:
                            self.frog.jump(down)
                    if event.type == pygame.VIDEORESIZE:
                        # There's some code to add back window content here.
                        self.wSize = (event.w, event.h)
                        self.tileSize = (int(self.wSize[0] / 15), int(self.wSize[1] / 14))
                        self.__draw()
            self.__update()
        return self.totalScore

    def initForAI(self):
        self.frog = Frog(self)

    def runForAI(self, move):
        currTime = perf_counter()
        self.deltaTime = currTime - self.lastFrameTime
        if self.maxFPS > 0:
            diff = 1.0 / self.maxFPS - self.deltaTime
            if diff > 0:
                sleep(diff)
                currTime = perf_counter()
                self.deltaTime = currTime - self.lastFrameTime
        self.lastFrameTime = currTime
        #if int((currTime - self.initTime) * 100) % 100 == 0 and printFPS:
            #print("FPS=", 1.0 / self.deltaTime)

        if self.fixedFrametime > 0:
            self.deltaTime = self.fixedFrametime

        self.timeRemaining -= self.deltaTime

        if move is not None:
            self.frog.jump(move)

        #  --------EVENTS-------
        if self.bDisplay:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.VIDEORESIZE:

                    self.wSize = (event.w, event.h)
                    self.tileSize = (int(self.wSize[0] / 15), int(self.wSize[1] / 14))
                    self.__draw()
        self.__update()

        if self.gameEnded:
            return self.totalScore
        else:
            return -1

    def getRectDrawPosition(self, pos, size):
        diff = (self.tileSize[0] - size[0], self.tileSize[1] - size[1])
        pos = (pos[0] * self.tileSize[0], pos[1] * self.tileSize[1])
        return pos[0] + diff[0] / 2, pos[1] + diff[1] / 2

    def getCircleDrawPosition(self, pos):
        return pos[0] * self.tileSize[0] + self.tileSize[0] / 2, pos[1] * self.tileSize[1] + self.tileSize[1] / 2

    def getTile(self, pos):
        return self.board[self.getIndex(pos)]

    # returns tile X from a real X position
    def getTileX(self, x: float):
        return round(x / self.tileSize[0]) * self.tileSize[0]

    def getIndex(self, pos):
        return pos[0] + 15 * pos[1]

    def saveHighscore(self):
        if self.totalScore >= self.highScore:
            f = open("highscores.txt", "w")
            f.write(str(int(self.totalScore)))
            f.close()

if __name__ == '__main__':
    gameInst = Frogger(True, 200, 1/200)
    gameInst.run()
