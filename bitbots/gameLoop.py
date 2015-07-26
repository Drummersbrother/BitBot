import sys

from bitbots.Vec2D import Vec2D

__author__ = 'FamiljensMONSTER'
# encoding: utf-8
import random

import pygame
import numpy as np

from bitbots import botMethods



# Taking and storing input
# It only accepts valid input
useDefSettings = input("Use default settings?")
print()

while not ((useDefSettings == "Y" or useDefSettings == "N") or (useDefSettings == "y" or useDefSettings == "n")):
    useDefSettings = input("Use default settings?")
    print()

if (useDefSettings == "N") or (useDefSettings == "n"):
    useDefSettings = False
else:
    useDefSettings = True

drawFood = input("Draw food?")
print()

while not ((drawFood == "Y" or drawFood == "N") or (drawFood == "y" or drawFood == "n")):
    drawFood = input("Draw food?")
    print()

if (drawFood == "N") or (drawFood == "n"):
    drawFood = False
else:
    drawFood = True

if not useDefSettings:
    resX = input("X resolution? (must be  multiple of 50)")
    print()
    while not resX.isdigit() or (not float(resX) > 0) or (not float(resX) % 50 == 0):
        resX = input("X resolution? (must be  multiple of 50)")
        print()

    resY = input("Y resolution? (must be  multiple of 50)")
    print()
    while not resY.isdigit() or (not float(resY) > 0) or (not float(resY) % 50 == 0):
        resY = input("Y resolution? (must be  multiple of 50)")
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

    if isGridMode == "Y" or isGridMode == "y":
        isGridMode = True
    else:
        isGridMode = False

else:
    isGridMode = False
    resX = 1000
    resY = 700
    numBots = 50

pygame.init()

textFont = pygame.font.SysFont("Monospace", 15)

curScr = pygame.display.set_mode((resX, resY))

pygame.display.set_caption("Bitbots test")

# Setting up, initializing and storing the bitbots
bots = botMethods.makeBots(numBots, isGridMode, resX, resY, 0)


def gameLoop():
    # Making some variables global
    global bots
    global curScr
    global numBots
    global isGridMode
    global resX
    global resY
    global shouldDraw
    global textFont

    # Storing the food amount array
    # Food at each location will be within (0-100) represented as an float
    # Each array entry represents a 50 x 50 area

    # We use floor division here to skip type conversion and basically silently swallowing errors from the input checker
    # We use one extra wor and column to prevent errors
    foodArray = np.zeros(((resX // 50) + 1, (resY // 50) + 1))

    # Randomizing the amount of food availiable at each tile (1 tile = one 50 x 50 area)

    # We use numpy's built in multidimensional iterator instead of nested for loops and then just setting the current value to a random one
    for index, curVal in np.ndenumerate(foodArray):
        foodArray[index[0]][index[1]] = random.randrange(0, 100)

    # Storing the background color
    bgColor = (0, 0, 0)

    # Filling the background with white and updating the whole screen
    curScr.fill(bgColor)
    pygame.display.update()

    # Target fps NOTE THAT THIS WILL NEVER BE REACHED, IT LIMITS FPS TO ALWAYS BE BELOW THIS
    tFps = 200

    shouldExit = False

    # Game clock and tick manager
    clock = pygame.time.Clock()

    # List for all rects and places where a rect has been to update on the next update call
    updateRects = []

    # Current tick counter
    tick = 0

    print("Bitbots will now initiate game loop")

    while not shouldExit:
        updateRects.append(pygame.draw.rect(curScr, bgColor, pygame.Rect(0, 0, resX, resY)))
        shouldDraw = True

        # wait for game tick to be at the appropritate time
        clock.tick(tFps)
        tick += 1

        # This is used to check if it should draw anything after this tick
        shouldDraw = False

        # Do game tick here

        # Fps calculation
        curFps = 1000 / clock.get_time()
        curFps = round(curFps, 0)

        pygame.display.set_caption("Bitbots test  Tick: " + str(tick) + ". TPS/FPS: " + str(curFps) + ".")

        for curBot in bots:
            # Apply position correcting/clamping so the bots are not outside the screen

            if curBot.posX < 0:
                curBot.posX = 0

            if curBot.posX > resX - 1:
                curBot.posX = resX - 1

            if curBot.posY < 0:
                curBot.posY = 0

            if curBot.posY > resY - 1:
                curBot.posY = resY - 1

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

        # Apply NN outputs (All steps are done separately to prevent inconsistencies based on list order)

        for curBot in bots:
            # Apply velocities

            # Health decrease constant
            healthDecrease = 0.001

            # Calculate direction vector based on the ratio of left to right output from the NN
            workVector = Vec2D()
            workVector.setX(0)
            workVector.setY(0)

            # Adding the scaled right pointing vector
            workVector.addX(curBot.velVector.getRotatedBy(15).getX() * abs(curBot.NNet[4][0]))
            workVector.addY(curBot.velVector.getRotatedBy(15).getY() * abs(curBot.NNet[4][0]))
            # Adding the scaled left pointing vector
            workVector.addX(curBot.velVector.getRotatedBy(-15).getX() * abs(curBot.NNet[4][1]))
            workVector.addY(curBot.velVector.getRotatedBy(-15).getY() * abs(curBot.NNet[4][1]))
            # Normalizing the vector to 1 +  BoostVal (limited to be between 0-1) and applying sprint+boost health decrease (and the default 0.01 health decrease)
            if curBot.NNet[0][8] >= 1:
                workVector.normalizeTo(2)
                curBot.health -= 0.1 + healthDecrease
            elif curBot.NNet[0][8] <= 0:
                workVector.normalizeTo(1)
                curBot.health -= healthDecrease
            else:
                workVector.normalizeTo(1 + curBot.NNet[0][8])
                curBot.health -= (curBot.NNet[0][8] / 10) + healthDecrease

            curBot.velVector = workVector

            # Actually changing the position of the bot
            curBot.posX += workVector.getX()
            curBot.posY += workVector.getY()

        for curBot in bots:
            # Apply eating logic and eating health toll

            # Checking if it should eat this tick
            if curBot.NNet[4][5] > 0:
                # Clamping the food actuator value so it is not above 5
                if curBot.NNet[4][5] > 5:
                    curBot.NNet[4][5] = 5

                scaledSensor = curBot.NNet[4][5] / 5

                # Applying eating health toll
                curBot.health -= (scaledSensor / 9)

                # The food logic
                foodEaten = foodArray[curBot.posX // 50][curBot.posY // 50] * ((scaledSensor / 100) * 3)

                # Increasing the health of the current bot by the amount of food the bot ate
                curBot.health += foodEaten

                # Decreasing the amount of food available where the bot ate by the amount that the bot ate
                foodArray[curBot.posX // 50][curBot.posY // 50] -= foodEaten

                # Telling the bot how much it has eaten
                curBot.hasEaten(foodEaten)

        for curBot in bots:
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

        for curBot in bots:
            # Apply health checks

            # Checking if the bot should be dead/removed
            if curBot.health < 0:
                bots.remove(curBot)

            else:
                # Checking and correcting so the bot doesnt have health over 100
                if curBot.health > 100:
                    curBot.health = 100

        for curBot in bots:
            # Apply health giving logic (health giving does ont have a health toll)

            # Checking the eat sensor so it is not below 2.5 (we have already scaled to be under 5 in the regular eat logic)
            if curBot.NNet[4][5] > 2.5:
                scaledEatActuator = (curBot.NNet[4][5] - 2.5) / 2.5

                for curGiveBot in bots:
                    if curGiveBot != curBot:

                        # Checking if the current give bot wants to give health
                        if curGiveBot.NNet[4][6] > 2.5:
                            # Do the health exchange logic (the current bot takes 0-0.5% of the other bots health based on the current bots eating actuator)
                            healthGiven = (curGiveBot.health * scaledEatActuator) / 200

                            # Applying the health change
                            curBot.health += healthGiven
                            curGiveBot.health -= healthGiven

                            # Telling the current bot that it has eaten
                            curBot.hasEaten(healthGiven)

        for curBot in bots:
            # Apply health checks again

            # Checking if the bot should be dead/removed
            if curBot.health < 0:
                bots.remove(curBot)

            else:
                # Checking and correcting so the bot doesnt have health over 100
                if curBot.health > 100:
                    curBot.health = 100

        for curBot in bots:
            # Apply bot division

            # Check if the current bot is able to duplicate and mutate
            if curBot.NNet[0][20] <= 0 and curBot.health > 50:
                # Duplicating and mutating the current bot
                bots.append(curBot.getMutated())

        # TODO User input this value
        maxBots = 200
        if bots.__len__() > maxBots:
            for i in range(0, bots.__len__() - maxBots):
                bots.pop()

        for curBot in bots:
            # Clamp color output to be inside 0-15

            if curBot.NNet[4][2] < 0:
                curBot.NNet[4][2] = 0

            if curBot.NNet[4][2] > 25:
                curBot.NNet[4][2] = 25

            if curBot.NNet[4][3] < 0:
                curBot.NNet[4][3] = 0

            if curBot.NNet[4][3] > 25:
                curBot.NNet[4][3] = 25

            if curBot.NNet[4][4] < 0:
                curBot.NNet[4][4] = 0

            if curBot.NNet[4][4] > 25:
                curBot.NNet[4][4] = 25

        # TODO Improve bot drawing / graphics

        # Drawing the amount of food available if the user wanted to
        if drawFood:
            for index, curVal in np.ndenumerate(foodArray):
                updateRects.append(
                    pygame.draw.rect(curScr, ((curVal / 100) * 255, (curVal / 100) * 255, (curVal / 100) * 255),
                                     pygame.Rect(index[0] * 50, index[1] * 50, (index[0] * 50) + 50,
                                                 (index[1] * 50) + 50)))

        for curBot in bots:
            # Drawing the current bot as a circle
            circleRect1 = pygame.draw.circle(curScr, (
                curBot.NNet[4][2] * (255 / 25), curBot.NNet[4][3] * (255 / 25), curBot.NNet[4][4] * (255 / 25)),
                                             (int(curBot.posX), int(curBot.posY)), 10)

            # Drawing the eye range as a circle
            eyeRange = 100
            circleRect2 = pygame.draw.circle(curScr, (15, 15, 15), (int(curBot.posX), int(curBot.posY)), eyeRange // 2,
                                             2)

            updateRects.append(circleRect2)
            updateRects.append(circleRect1)

            # Draw the bot's spike as a line
            scaledSpikeActuator = curBot.NNet[4][7] / 5
            lineRect1 = pygame.draw.line(curScr, (50, 0, 0), (curBot.posX, curBot.posY), (
            curBot.posX + int(curBot.velVector.getNormalizedTo(50).x * scaledSpikeActuator),
            curBot.posY + int(curBot.velVector.getNormalizedTo(50).y * scaledSpikeActuator)))

            # Draw the bot's spike angular range as 2 lines
            lineRect2 = pygame.draw.line(curScr, (0, 50, 0), (curBot.posX, curBot.posY), (
                curBot.posX + int(curBot.velVector.getRotatedBy(22.5).getNormalizedTo(50).x),
                curBot.posY + int(curBot.velVector.getRotatedBy(22.5).getNormalizedTo(50).y)))

            lineRect3 = pygame.draw.line(curScr, (0, 50, 0), (curBot.posX, curBot.posY), (
                curBot.posX + int(curBot.velVector.getRotatedBy(-22.5).getNormalizedTo(50).x),
                curBot.posY + int(curBot.velVector.getRotatedBy(-22.5).getNormalizedTo(50).y)))

            updateRects.append(lineRect3)
            updateRects.append(lineRect2)
            updateRects.append(lineRect1)

            # Draw a white pixel at each bot so we can see them even when they're black
            pixelRect1 = pygame.draw.circle(curScr, (255, 255, 255), (int(curBot.posX), int(curBot.posY)), 0)
            updateRects.append(pixelRect1)

            # Draw the amount of health a bot has as a rectangle to the right of the bot
            healthRect1 = pygame.Rect(curBot.posX - 13, curBot.posY - 10, 3, int((curBot.health // 10) * 1.25))
            pygame.draw.rect(curScr,
                             (
                             int((((curBot.health // 100) * -1) + 1) * 255), int((curBot.health // 100) * 255), int(0)),
                             healthRect1)
            updateRects.append(healthRect1)

            shouldDraw = True

        # Display how many bots are alive (blitting a font render to the curScr)
        curScr.blit(textFont.render((str(bots.__len__())), True, (0, 255, 0)), (0, 0))
        shouldDraw = True

        # Checking if it should draw something this tick
        if shouldDraw:
            pygame.display.update(updateRects)
        # Preventing memory leak
        updateRects = []

        # Randomly adding some food to 5 places in the in the foodarray
        for i in range(0, 5):
            randX = random.randint(0, (resX // 50) - 1)
            randY = random.randint(0, (resY // 50) - 1)
            foodArray[randX][randY] += random.random() * 10

            # Checking and correcting the food value so that it is not above 100
            if foodArray[randX][randY] > 100:
                foodArray[randX][randY] = 100

    if shouldExit:
        print("Bitbots will now exit")
        pygame.quit()
        sys.exit()
        print("Bitbots has now exited")
