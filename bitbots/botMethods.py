__author__ = 'FamiljensMONSTER'
# encoding: utf-8
import math
import random
from math import sqrt

from bitbots import bitBot
from bitbots.Vec2D import Vec2D


def makeBots(numBots, isGridMode, resX, resY, genNr):
    numBots = int(numBots)
    print("Spawning and creating bitbots")

    # List to store the bot entries
    botList = []

    # Putting in a bot entry at every place they should be in
    for curBotId in range(0, numBots):
        curBot = bitBot.bitBot(genNr)
        botList.append(curBot)

    if not isGridMode:
        for curBot in botList:
            curBot.posX = int(random.random() * resX)
            curBot.posY = int(random.random() * resY)
    return botList


def midNodeFunction(nodeToUse):
    # This is a scaling function / sigmoid function, it may have to be changed in the future
    nodeToUse /= (sqrt(1 + nodeToUse ** 2)) * 2
    return nodeToUse


# Update the node list with new sensor values
def updateSensors(bots, curTick, foodArray):
    # Loop through all the bot entries in the bot list and give them some inputs and get some outputs
    for curBot in bots:

        # Initializing sensor variables
        leftEyeBots = []
        rightEyeBots = []
        backEyeBots = []
        totalVibration = 0
        totalSmell = 0
        totalSound = 0
        totalEyeBotHealth = []
        eyeRange = 100

        # Main loop for all sensor that need loops
        for curSenseBot in bots:
            if curSenseBot != curBot:
                # Setting up the vector that points from the current bot to the current eye bot
                relVector = Vec2D()
                relVector.setX(curSenseBot.posX - curBot.posX)
                relVector.setY(curSenseBot.posY - curBot.posY)

                # Vector that points to the right of the current bot
                rightVector = curBot.velVector.getRotatedBy(90)

                # We don't want some kind of dividing by zero
                if relVector.getMagnitude() != 0:

                    if relVector.getMagnitude() < eyeRange:
                        # Checking if the current eye bot is able to be seen by the left eye or right eye (also adding the a bot to the totalHealth list)
                        if relVector.getDotProductFromUnitVec(curBot.velVector) > 0.5:
                            totalEyeBotHealth.append(curSenseBot)
                            if relVector.getDotProductFromUnitVec(rightVector) < 0:
                                leftEyeBots.append(curSenseBot)
                            else:
                                rightEyeBots.append(curSenseBot)

                        # Checking if the current eye bot is able to be seen by the back eye
                        if relVector.getDotProductFromUnitVec(curBot.velVector) < -0.75:
                            backEyeBots.append(curSenseBot)

                    # Vibration sensor, sound sensor, and smell sensor calculator

                    if relVector.getMagnitude() < 100:
                        totalVibration += -(relVector.getMagnitude() / 100) + 1
                        totalSmell += 1
                        totalSound += curSenseBot.NNet[4][9]

        # Making the left eye actual values
        leftEyeR = 0
        leftEyeG = 0
        leftEyeB = 0
        leftEyeAvgProx = 0
        for curCalc in leftEyeBots:
            leftEyeR += curCalc.NNet[4][2]
            leftEyeG += curCalc.NNet[4][3]
            leftEyeB += curCalc.NNet[4][4]

            relVector = Vec2D()
            relVector.addX(curCalc.posX - curBot.posX)
            relVector.addY(curCalc.posY - curBot.posY)

            leftEyeAvgProx += relVector.getMagnitude()

        if leftEyeBots.__len__() > 0:
            leftEyeR /= leftEyeBots.__len__()
            leftEyeG /= leftEyeBots.__len__()
            leftEyeB /= leftEyeBots.__len__()
            leftEyeAvgProx /= leftEyeBots.__len__()

        curBot.NNet[0][0] = leftEyeR
        curBot.NNet[0][1] = leftEyeG
        curBot.NNet[0][2] = leftEyeB
        # Scaling the avg proximity to be in a good range for the NN
        curBot.NNet[0][3] = leftEyeAvgProx / 20

        # Making the right eye actual values
        rightEyeR = 0
        rightEyeG = 0
        rightEyeB = 0
        rightEyeAvgProx = 0
        for curCalc in rightEyeBots:
            rightEyeR += curCalc.NNet[4][2]
            rightEyeG += curCalc.NNet[4][3]
            rightEyeB += curCalc.NNet[4][4]

            relVector = Vec2D()
            relVector.addX(curCalc.posX - curBot.posX)
            relVector.addY(curCalc.posY - curBot.posY)

            rightEyeAvgProx += relVector.getMagnitude()

        if rightEyeBots.__len__() > 0:
            rightEyeR /= rightEyeBots.__len__()
            rightEyeG /= rightEyeBots.__len__()
            rightEyeB /= rightEyeBots.__len__()
            rightEyeAvgProx /= rightEyeBots.__len__()

        curBot.NNet[0][4] = rightEyeR
        curBot.NNet[0][5] = rightEyeG
        curBot.NNet[0][6] = rightEyeB
        # Scaling the avg proximity to be in a good range for the NN
        curBot.NNet[0][7] = rightEyeAvgProx / 20

        # Making the back eye actual values
        backEyeR = 0
        backEyeG = 0
        backEyeB = 0
        for curCalc in rightEyeBots:
            backEyeR += curCalc.NNet[4][2]
            backEyeG += curCalc.NNet[4][3]
            backEyeB += curCalc.NNet[4][4]

            relVector = Vec2D()
            relVector.addX(curCalc.posX - curBot.posX)
            relVector.addY(curCalc.posY - curBot.posY)

        curBot.NNet[0][16] = backEyeR
        curBot.NNet[0][17] = backEyeG
        curBot.NNet[0][18] = backEyeB

        # Health sensor
        curBot.NNet[0][8] = curBot.health

        # Vibration sensor
        curBot.NNet[0][9] = totalVibration

        # Smell sensor
        curBot.NNet[0][10] = totalSmell

        # Plantfood at the current location
        curBot.NNet[0][11] = foodArray[int(curBot.posX // 50)][int(curBot.posY // 50)] / 100

        # Last tick R, G, and B
        curBot.NNet[0][12] = curBot.NNet[4][2]
        curBot.NNet[0][13] = curBot.NNet[4][3]
        curBot.NNet[0][14] = curBot.NNet[4][4]

        # Sound sensor
        curBot.NNet[0][15] = totalSound

        # Calculating the blood sensor actual values
        avgEyeBotHealth = 0
        for curCalc in totalEyeBotHealth:
            avgEyeBotHealth += curCalc.health

        if totalEyeBotHealth.__len__() != 0:
            avgEyeBotHealth /= totalEyeBotHealth.__len__()
        curBot.NNet[0][19] = avgEyeBotHealth

        # Age sensor
        curBot.NNet[0][21] = curTick

        # Calculating clock 1
        curBot.NNet[0][22] = math.sin(((curTick + 1) * curBot.clock1) / 100) * 5

        # Calculating clock 2
        curBot.NNet[0][23] = math.sin(((curTick + 1) * curBot.clock2) / 100) * 5

        # Last tick memory
        curBot.NNet[0][24] = curBot.NNet[4][10]

    return bots
