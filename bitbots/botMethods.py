from bitbots.Vec2D import Vec2D

__author__ = 'FamiljensMONSTER'
# encoding: utf-8
from math import sqrt
from bitbots import bitBot
def makeBots(numBots, isGridMode, resX, resY, genNr):
    numBots = int(numBots)
    resX = int(resX)
    resY = int(resY)
    print("Spawning and creating bitbots")

    #List to store the bot entries
    botList = []

    #Putting in a bot entry at every place they should be in
    for curBotId in range(0, numBots):
        curBot = bitBot.bitBot(genNr)
        botList.append(curBot)
    return botList

def midNodeFunction(nodeToUse):
    #This is a scaling function / sigmoid function, it may have to be changed in the future
    nodeToUse /= sqrt(1 + nodeToUse ** 2)
    return nodeToUse

#Update the node list with new sensor values
def updateSensors(bots):

    #Loop through all the bot entries in the bot list and give them some inputs and get some outputs
    for curBot in bots:

        #Initializing sensor variables
        leftEyeBots = []
        rightEyeBots = []
        totalVibration = 0
        totalSmell = 0

        #Main loop for all sensor that need loops
        for curSenseBot in bots:
            if curSenseBot != curBot:
                #Left eye sensor calculator

                #Setting up the vector that points from the current bot to the current eye bot
                relVector = Vec2D()
                relVector.addX(curSenseBot.x - curBot.x)
                relVector.addY(curSenseBot.y - curBot.y)

                #Vector that points to the right of the current bot
                rightVector = curBot.velVector.getRotatedBy(90)

                #We don't want some kind of dividing by zero
                if relVector.getMagnitude() != 0:

                    #Checking if the current eye bot is in range to be seen
                    if relVector.getMagnitude() < 50:
                        if relVector.getDotProductFromUnitVec(curBot.velVector) > 0.5:
                            if relVector.getDotProductFromUnitVec(rightVector) < 0:
                                leftEyeBots.append(curSenseBot)

                    #Right eye sensor calculator

                    #Checking if the current eye bot is in range to be seen
                    if relVector.getMagnitude() < 50:
                        if relVector.getDotProductFromUnitVec(curBot.velVector) > 0.5:
                            if relVector.getDotProductFromUnitVec(rightVector) > 0:
                                rightEyeBots.append(curSenseBot)

                    #Vibration sensor and smell sensor calculator

                    if relVector.getMagnitude() < 100:
                        totalVibration += -(relVector.getMagnitude() / 100) + 1
                        totalSmell += 1

        #Making the left eye actual values
        leftEyeR = 0
        leftEyeG = 0
        leftEyeB = 0
        leftEyeAvgProx = 50
        for curCalc in leftEyeBots:
            leftEyeR += curCalc.NNet[4][2]
            leftEyeG += curCalc.NNet[4][3]
            leftEyeB += curCalc.NNet[4][4]

            relVector = Vec2D()
            relVector.addX(curCalc.x - curBot.x)
            relVector.addY(curCalc.y - curBot.y)

            leftEyeAvgProx += relVector.getMagnitude()

        if leftEyeBots.__len__() > 0:

            leftEyeR /= leftEyeBots.__len__()
            leftEyeG /= leftEyeBots.__len__()
            leftEyeB /= leftEyeBots.__len__()
            leftEyeAvgProx /= leftEyeBots.__len__()

        curBot.NNet[0][0] = leftEyeR
        curBot.NNet[0][1] = leftEyeG
        curBot.NNet[0][2] = leftEyeB
        curBot.NNet[0][3] = leftEyeAvgProx

        #Making the right eye actual values
        rightEyeR = 0
        rightEyeG = 0
        rightEyeB = 0
        rightEyeAvgProx = 50
        for curCalc in rightEyeBots:
            rightEyeR += curCalc.NNet[4][2]
            rightEyeG += curCalc.NNet[4][3]
            rightEyeB += curCalc.NNet[4][4]

            relVector = Vec2D()
            relVector.addX(curCalc.x - curBot.x)
            relVector.addY(curCalc.y - curBot.y)

            rightEyeAvgProx += relVector.getMagnitude()

        if rightEyeBots.__len__() > 0:

            rightEyeR /= rightEyeBots.__len__()
            rightEyeG /= rightEyeBots.__len__()
            rightEyeB /= rightEyeBots.__len__()
            rightEyeAvgProx /= rightEyeBots.__len__()

        curBot.NNet[0][4] = rightEyeR
        curBot.NNet[0][5] = rightEyeG
        curBot.NNet[0][6] = rightEyeB
        curBot.NNet[0][7] = rightEyeAvgProx

        #Health sensor
        curBot.NNet[0][8] = curBot.health

        #Vibration sensor
        curBot.NNet[0][9] = totalVibration

        #Smell sensor
        curBot.NNet[0][10] = totalSmell

        #Plantfood at the current location


        #Last tick R, G, and B
        curBot.NNet[0][12] = curBot.NNet[4][2]
        curBot.NNet[0][13] = curBot.NNet[4][3]
        curBot.NNet[0][14] = curBot.NNet[4][4]

    return bots
