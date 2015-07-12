__author__ = 'FamiljensMONSTER'
# encoding: utf-8
import random

import numpy as np

from bitbots import Vec2D
import bitbots


class bitBot:
    def __init__(self, genNr):
        # Describing the neural network
        # Sensors, note that all these are (or should be) between 0 and 1 (maybe not for some things though):
        # (0) left eye R (1) left eye G (2) left eye B (3) left eye average proximity (4) right eye R (5) right eye G (6) right eye B (7) right eye average proximity (8) health (9) vibration sensor [amount of bot movement around it, this is not scaled]
        # (10) smell sensor [number of bots around it, this is not scaled] (11) food sensor [amount of food at this location (plant food)] (12)current R (13) current G (14) current B
        # (15) sound sensor [amount of shout from other bots in the area, not scaled] (16) back eye R (17) back eye G (18) back eye B (19) blood sensor [health of bots in front of it/included in the left or the right eye, this is scaled with totalHealth/numbots]
        # (20) amount of food needed until reproduction (21) age [in ticks](22) Clock 1 (23) Clock 2 (24) Last tick memory
        # Out/Actuators: (0) Wheel 1 [Right] (1) Wheel 2 [Left] (2) Red light emitted  (3) Green light emitted (4) Blue light emitted (5) How much of the available food at this location it should eat [0-3%]
        # (6) Is it willing to give other bots the ability to take some of its food/health? [if it is over 2.5 then it IS willing, otherwise it IS NOT willing] (7) Spike length (8) Boost (9) Sound emitting (10) Memory, from the last tick
        # Mid nodes: 20?

        self.NNet = [np.zeros((25)), np.ones((25, 20)), np.zeros((20)), np.ones((20, 11)), np.zeros((11))]
        self.NNet[0][20] = 1

        # Self explanatory
        self.posX = 0
        self.posY = 0
        self.velVector = Vec2D.Vec2D()
        self.velVector.addX(0)
        self.velVector.addY(0)
        self.genNr = genNr
        self.health = 100
        self.clock1 = random.random()
        self.clock2 = random.random()

        if self.clock1 < 0.1:
            self.clock1 += 0.1

        if self.clock2 < 0.1:
            self.clock2 += 0.1

        # Randomising the neural networks weights
        for i in range(25):
            for i2 in range(20):
                self.NNet[1][i][i2] = (random.random() * 10) - 5

        for i in range(20):
            for i2 in range(10):
                self.NNet[3][i][i2] = (random.random() * 10) - 5

    def getOutputs(self) -> np.array:

        # This calculates the mid nodes' values
        curMidNodeId = -1
        for CurMidNode in self.NNet[2]:
            curMidNodeId += 1
            for CurIn in range(25):
                CurMidNode += self.NNet[0][CurIn] * self.NNet[1][CurIn][curMidNodeId]
            CurMidNode = bitbots.botMethods.midNodeFunction(CurMidNode)
            self.NNet[2][curMidNodeId] = CurMidNode

        # This calculates the out nodes' values
        curOutNodeId = -1
        for CurOutNode in self.NNet[4]:
            curOutNodeId += 1
            for CurMid in range(20):
                CurOutNode += self.NNet[2][CurMid] * self.NNet[3][CurMid][curOutNodeId]
            self.NNet[4][curOutNodeId] = CurOutNode

        # Clamping all the color outputs to be inside 0-1

        # Clamping Red
        if self.NNet[4][2] < 0:
            self.NNet[4][2] = 0

        if self.NNet[4][2] > 1:
            self.NNet[4][2] = 1

        # Clamping Green
        if self.NNet[4][3] < 0:
            self.NNet[4][3] = 0

        if self.NNet[4][3] > 1:
            self.NNet[4][3] = 1

        # Clamping Blue
        if self.NNet[4][4] < 0:
            self.NNet[4][4] = 0

        if self.NNet[4][4] > 1:
            self.NNet[4][4] = 1

        # Clamping how much eating should be done
        if self.NNet[4][5] < 0:
            self.NNet[4][5] = 0

        if self.NNet[4][5] > 1:
            self.NNet[4][5] = 1

        # Clamping spike length
        if self.NNet[4][7] < 0:
            self.NNet[4][7] = 0

        if self.NNet[4][7] > 1:
            self.NNet[4][7] = 1

        # Clamping boost
        if self.NNet[4][8] < 0:
            self.NNet[4][8] = 0

        if self.NNet[4][8] > 1:
            self.NNet[4][8] = 1

        # Clamping sound emitting
        if self.NNet[4][9] < 0:
            self.NNet[4][9] = 0

        if self.NNet[4][9] > 1:
            self.NNet[4][9] = 1

        return self.NNet[4]

    # Returns a new bitbot with possible mutations
    def getMutated(self):
        newBot = bitBot(self.genNr + 1)

        newBot.posX = self.posX
        newBot.posY = self.posY
        newBot.velVector = self.velVector
        newBot.clock1 = random.random()
        newBot.clock2 = random.random()

        # Mutates the new bot's weights
        for i in range(24):
            for i2 in range(20):
                if random.random() > 0.999:
                    # Mutate this weight
                    newBot.NNet[1][i][i2] = self.NNet[1][i][i2] + ((random.random() * 1) - 0.5)
                else:
                    # Just get the weight of the parent
                    newBot.NNet[1][i][i2] = self.NNet[1][i][i2]

        for i in range(20):
            for i2 in range(10):
                if random.random() > 0.999:
                    # Mutate this weight
                    newBot.NNet[3][i][i2] = self.NNet[3][i][i2] + ((random.random() * 1) - 0.5)
                else:
                    # Just get the weight of the parent
                    newBot.NNet[3][i][i2] = self.NNet[3][i][i2]

        # Returns the new bot
        return newBot

    def hasEaten(self, amount):
        self.NNet[0][20] -= amount / 100
