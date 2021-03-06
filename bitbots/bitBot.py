__author__ = 'FamiljensMONSTER'
# encoding: utf-8
import random

import numpy as np

import bitbots
from bitbots import Vec2D

class bitBot:
    def __init__(self, genNr):
        # Describing the neural network
        # Sensors, note that all these are (or should be) between 0 and 1 (maybe not for some things though):
        # (0) left eye R (1) left eye G (2) left eye B (3) left eye average proximity (4) right eye R (5) right eye G (6) right eye B (7) right eye average proximity (8) health (9) vibration sensor [amount of bot movement around it, this is not scaled]
        # (10) smell sensor [number of bots around it, this is not scaled] (11) food sensor [amount of food at this location (plant food)] (12)current R (13) current G (14) current B
        # (15) sound sensor [amount of shout from other bots in the area, not scaled] (16) back eye R (17) back eye G (18) back eye B (19) blood sensor [health of bots in front of it/included in the left or the right eye, this is scaled with totalHealth/numbots]
        # (20) amount of food needed until reproduction (21) age [in ticks](22) Clock 1 (23) Clock 2 (24) Last tick memory (25) Constant 1 (26) Constant 2 (27)Constant 3 (28) Constant 4 (29) Constant 5
        # Out/Actuators: (0) Wheel 1 [Right] (1) Wheel 2 [Left] (2) Red light emitted  (3) Green light emitted (4) Blue light emitted (5) How much of the available food at this location it should eat [0-3%]
        # (6) Is it willing to give other bots the ability to take some of its food/health? [if it is over 2.5 then it IS willing, otherwise it IS NOT willing] (7) Spike length (8) Boost (9) Sound emitting (10) Memory, from the last tick
        # Mid nodes: 20?

        self.NNet = [np.zeros((30)), np.ones((30, 20)), np.zeros((20)), np.ones((20, 11)), np.zeros((11))]
        self.NNet[0][20] = 2

        # Self explanatory
        self.posX = 500
        self.posY = 500
        self.velVector = Vec2D.Vec2D()
        self.velVector.setX(0)
        self.velVector.setY(1)
        self.genNr = genNr
        self.health = 100
        self.clock1 = random.random()
        self.clock2 = random.random()
        self.NNet[0][25] = random.random() * 5
        self.NNet[0][26] = random.random() * 5
        self.NNet[0][27] = random.random() * 5
        self.NNet[0][28] = random.random() * 5
        self.NNet[0][29] = random.random() * 5

        if self.clock1 < 0.1:
            self.clock1 += 0.1

        if self.clock2 < 0.1:
            self.clock2 += 0.1

        # Randomising the neural networks weights
        for i in range(30):
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
            for CurIn in range(30):
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

        return self.NNet[4]

    # Returns a new bitbot with possible mutations
    def getMutated(self):
        self.NNet[0][20] = 2

        newBot = bitBot(self.genNr + 1)
        newBot.NNet[0][20] = 2

        newBot.posX = self.posX
        newBot.posY = self.posY
        newBot.velVector = self.velVector
        newBot.clock1 = random.random() * 5
        newBot.clock2 = random.random() * 5

        # Mutates the parent bot's weights
        for i in range(30):
            for i2 in range(20):
                if random.random() > 0.999:
                    # Mutate this weight
                    newBot.NNet[1][i][i2] = self.NNet[1][i][i2] + ((random.random() * 1) - 0.5)
                else:
                    # Just get the weight of the parent
                    newBot.NNet[1][i][i2] = self.NNet[1][i][i2]

        for i in range(20):
            for i2 in range(11):
                if random.random() > 0.999:
                    # Mutate this weight
                    newBot.NNet[3][i][i2] = self.NNet[3][i][i2] + ((random.random() * 1) - 0.5)
                else:
                    # Just get the weight of the parent
                    newBot.NNet[3][i][i2] = self.NNet[3][i][i2]

        # Mutates the parent bot's constants
        self.NNet[0][25] += (random.random() / 5) - 0.1
        self.NNet[0][26] += (random.random() / 5) - 0.1
        self.NNet[0][27] += (random.random() / 5) - 0.1
        self.NNet[0][28] += (random.random() / 5) - 0.1
        self.NNet[0][29] += (random.random() / 5) - 0.1

        # Returns the new bot
        return newBot

    def hasEaten(self, amount):
        self.NNet[0][20] -= amount / 100

    def displayString(self):
        return str(round(self.NNet[0][20], 1)) + " | " + str(round(self.health, 1)) + " | Gen " + str(self.genNr)
