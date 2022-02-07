from random import randint

class XOR:
    def __init__(self):
        self.a = randint(0, 1)
        self.b = randint(0, 1)

    def getInput(self):
        return self.a, self.b

    # better score = closer to correct answer, 1.0 = 100% correct
    def getScore(self, output):
        correct = (self.a + self.b) % 2
        return 1.0 - abs(correct - output)

