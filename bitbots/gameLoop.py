from bitbots.Vec2D import Vec2D

__author__ = 'FamiljensMONSTER'
# encoding: utf-8
import random

import pygame
import numpy as np

from bitbots import botMethods



# Taking and storing input
# It only accepts valid input
resX = input("X resolution? (must be  multiple of 10)")
print()
while not resX.isdigit() or (not float(resX) > 0) or (not float(resX) % 10 == 0):
    resX = input("X resolution? (must be  multiple of 10)")
    print()

resY = input("Y resolution? (must be  multiple of 10)")
print()
while not resY.isdigit() or (not float(resY) > 0) or (not float(resY) % 10 == 0):
    resY = input("Y resolution? (must be  multiple of 10)")
    print()

# Converting the resolution variables to be ints and not strings
resX = int(resX)
resY = int(resY)
# Just checking and correcting resolution so it is not below 200x200
if resX < 200:
    resX = 200
if resY < 200:
    resY = 200

numBots = input("How many bitbots should exist?")
print()

while not numBots.isdigit() or (not float(numBots) > 0):
    numBots = input("How many bitbots should exist?")
    print()

isGridMode = input("Should they be spawned in a grid pattern? Y/N")
print()

while not ((isGridMode == "Y" or isGridMode == "N") or (isGridMode == "y" or isGridMode == "n")):
    isGridMode = input("Should they be spawned in a grid pattern? Y/N")
    print()

if isGridMode == "Y":
    isGridMode = True
else:
    isGridMode = False

pygame.init()

curScr = pygame.display.set_mode((resX, resY))

pygame.display.set_caption("Bitbots test")

# Setting up, initializing and storing the bitbots
bots = botMethods.makeBots(numBots, isGridMode, resX, resY, 0)


def updateGRec(dirtyRects):
    pygame.display.update(dirtyRects)


def gameLoop():
    # Making some variables global
    global bots
    global curScr
    global numBots
    global isGridMode
    global resX
    global resY

    # Storing the food amount array
    # Food at each location will be within (0-100) represented as an float
    # Each array entry represents a 10 x 10 area

    # We use floor division here to skip type conversion and basically silently swallowing errors from the input checker
    foodArray = np.zeros((resX // 10, resY // 10))

    # Randomizing the amount of food availiable at each tile (1 tile = one 10 x 10 area)

    # We use numpy's built in multidimensional iterator instead of nested for loops and then just setting the current value to a random one
    for index, curVal in np.ndenumerate(foodArray):
        foodArray[index[0]][index[1]] = random.randrange(0, 100)

    # Storing the background color
    bgColor = (255, 255, 255)

    # Filling the background with white and updating the whole screen
    curScr.fill(bgColor)
    pygame.display.update()

    # Target fps NOTE THAT THIS WILL NEVER BE REACHED, IT LIMITS FPS TO ALWAYS BE BELOW THIS
    tFps = 80

    shouldExit = False

    # Game clock and tick manager
    clock = pygame.time.Clock()

    # List for all rects and places where a rect has been to update on the next update call
    updateRects = []

    # Current tick counter
    tick = 0

    print("Bitbots will now initiate game loop")

    while shouldExit == False:
        # wait for game tick to be at the appropritate time
        clock.tick(tFps)
        tick += 1

        # This is used to check if it should draw anything after this tick
        shouldDraw = False

        # If this is true then it will update the whole screen instead of k´just the update rectangles list
        updateFull = False

        # Do game tick here

        # Fps calculation
        curFps = 1000 / clock.get_time()
        curFps = round(curFps, 0)

        pygame.display.set_caption("Bitbots test  Tick: " + str(tick) + ". TPS/FPS: " + str(curFps) + ".")

        # Updating the sensor values for all bots
        bots = botMethods.updateSensors(bots, clock.get_time(), foodArray)

        for curBot in bots:
            curBot.NNet[4] = curBot.getOutputs()

        # Input checks
        # Checking to see if the program is getting OS keyboard input focus
        if True:  # pygame.key.get_focused(): This makes it freeze if it looses focus
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    shouldExit = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        shouldExit = True

        # Apply NN outputs

        # Apply velocities (This is done separately from the others to prevent inconsistencies based on the list order)
        for curBot in bots:
            # Calculate direction vector based on the ratio of left to right output from the NN
            workVector = Vec2D()
            workVector.setX(0)
            workVector.setY(0)

            # Adding the scaled right pointing vector
            workVector.addX(curBot.velVector.getRotatedBy(45).getX() * abs(curBot.NNet[4][0]))
            workVector.addY(curBot.velVector.getRotatedBy(45).getY() * abs(curBot.NNet[4][0]))
            # Adding the scaled left pointing vector
            workVector.addX(curBot.velVector.getRotatedBy(45).getX() * abs(curBot.NNet[4][0]))
            workVector.addY(curBot.velVector.getRotatedBy(45).getY() * abs(curBot.NNet[4][0]))
            # Normalizing the vector to 1 +  BoostVal (limited to be between 0-1) and applying sprint+boost health decrease (and the default 0.01 health decrease)
            if curBot.NNet[0][8] >= 1:
                workVector.normalizeTo(2)
                curBot.health -= 0.11
            elif curBot.NNet[0][8] <= 0:
                workVector.normalizeTo(1)
                curBot.health -= 0.01
            else:
                workVector.normalizeTo(1 + curBot.NNet[0][8])
                curBot.health -= (curBot.NNet[0][8] / 10) + 0.01

            curBot.velVector = workVector

            # Actually changing the position of the bot
            curBot.posX += workVector.getX()
            curBot.posY += workVector.getY()

        for curBot in bots:
            # Apply eating logic and eating health toll

            # Checking if it should eat this tick
            if curBot.NNet[4][5] > 2.5:
                # Clamping the food actuator value so it is not above 5
                if curBot.NNet[4][5] > 5:
                    curBot.NNet[4][5] = 5

                scaledSensor = (curBot.NNet[4][5] - 2.5) / 2.5

                # Applying eating health toll
                curBot.health -= (scaledSensor / 3) + 0.1

                # The food logic
                foodEaten = foodArray[curBot.posX // 10][curBot.posY // 10] * ((scaledSensor / 100) * 3)

                # Increasing the health of the current bot by the amount of food the bot ate
                curBot.health += foodEaten

                # Decreasing the amount of food available where the bot ate by the amount that the bot ate
                foodArray[curBot.posX // 10][curBot.posY // 10] -= foodEaten

                # Telling the bot how much it has eaten
                curBot.hasEaten(foodEaten)

            # Apply spike logic

            # Clamping the spike length actuator so it is not above 5 and not below 0
            if curBot.NNet[4][7] <= 0:
                curBot.NNet[4][7] = 0
            if curBot.NNet[4][7] > 0:
                if curBot.NNet[4][7] > 5:
                    curBot.NNet[4][7] = 5

                scaledSensor = curBot.NNet[4][7] / 5

                # Checking all bots except the current to see if it is in range to be damaged
                for curSpikeBot in bots:
                    if curSpikeBot != curBot:

                        # Setting up a vector that points from the current vector to the current spike bot
                        relVector = Vec2D()
                        relVector.setX(curSpikeBot.velVector.getX() - curBot.velVector.getX())
                        relVector.setY(curSpikeBot.velVector.getY() - curBot.velVector.getY())

                        # We dont want any division by zero
                        if relVector.getMagnitude() != 0:

                            # Checking if the current bot can damage the current spike bot (range within 50 and dot product less than 0.75)
                            if (relVector.getMagnitude() < (scaledSensor * 50)) and (
                                curBot.velVector.getDotProductFromUnitVec(relVector) > 0.75):
                                # Apply the damage
                                curSpikeBot.health -= scaledSensor
                                curBot.health += scaledSensor

                                # Telling the current bot that it has eaten
                                curBot.hasEaten(scaledSensor)
                                # Apply health checks
                                # Apply health giving logic

        # Checking if it should draw something this tick
        if shouldDraw or updateFull:
            if updateFull:
                pygame.display.update(pygame.Rect((0, 0), (resX, resY)))
            else:
                updateGRec(updateRects)
        # Preventing memory leak
        updateRects = []

        # Randomly adding some food to 5 places in the in the foodarray
        for i in range(0, 5):
            randX = random.randint(0, (resX // 10) - 1)
            randY = random.randint(0, (resY // 10) - 1)
            foodArray[randX][randY] += random.random() * 10

            # Checking and correcting the food value so that it is not above 100
            if foodArray[randX][randY] > 100:
                foodArray[randX][randY] = 100

    if shouldExit == True:
        print("Bitbots will now exit")
        pygame.quit()
        print("Bitbots has now exited")
