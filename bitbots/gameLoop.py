__author__ = 'FamiljensMONSTER'
# encoding: utf-8
import os
import random
import sys

try:
    import cPickle as pickle
except:
    import pickle

import numpy as np
import pygame

from bitbots import Vec2D
from bitbots import botMethods
from bitbots import saveTemplate


# Method for loading (de-serializing via pickle) a saved simulation
def loadSim():
    # The directory we are in
    path = os.path.dirname(os.path.realpath(__file__))

    # Directory separator so we can have cross-platform compatibility
    dirSep = os.sep

    # Infinite loop because there is no code after it and we can break out by returning something
    while True:
        # Storing all the subdirectories to the root dir
        subDirs = next(os.walk('.'))[1]

        # Printing how many subdirectories we found and the names of all the subdirectories
        print("Found %d subdirectories in '%s':" % (subDirs.__len__(), path))
        for curSubDir in subDirs:
            print("\t%s" % curSubDir)
        print()

        # Asking the user what subdirectory they want to look for savefiles in. We use the OS dir sep (os.sep) so we dont have to care about specific OS
        subDir = dirSep + input("Please input save directory.")
        print()

        # Checking if the user-specified directory exists and is a directory, if it does not pass then we will continue/redo the loop
        if not os.path.isdir(path + subDir):
            print("The path '%s%s' is not a directory or doesn't exist." % (path, subDir))
            continue

        # Putting all the files in the user-specified subdirectory in a list
        filenames = next(os.walk(path + subDir))[2]

        # Removing all the filenames that dont end with ".bbs", note the use of [:] (list slice that covers the whole list) which makes the loop loop through a shallow copy of the list whilst removing the values from the real list. Using [:] prevents the loop from prematurely stopping without having processed all the entries.
        for file in filenames[:]:
            if not file.endswith(".bbs"):
                filenames.remove(file)

        # Printing the number of files in the specified directory that conform to "*.bbs"
        print("Found %d savefiles (*.bbs) in '%s':" % (filenames.__len__(), path + subDir))

        # Printing all the files that conform to the "*.bbs" pattern
        for file in filenames:
            print("\t%s" % file)
        print()

        # Asking the user if they want to choose a file in the previously specified subdirectory
        if input("Do you want to load a file in this directory? y/n ").lower() == "n":
            print()
            # The user doesnt want to choose a file in the subdirectory they specified, so we ask them if they want to load a save file at all
            if input("Do you want to use another subdirectory? y/n ").lower() == "y":
                # We just continue/redo the loop
                print()
                continue
            else:
                # We skip using save files at all, so we return False.
                print()
                print("Will now use regular settings instead of saved simulation.")
                print()
                return False
        else:
            print()

            # This will be used to check if the user has specified a valid filename to load
            newFile = True

            while newFile:
                # Asking the user what file they want to load
                fileToLoad = input("Please input saved simulation name ")

                # Checking if the file is in the list of filenames, is a file, and then checking if it exists to reduce race conditions
                if filenames.__contains__(fileToLoad):
                    if os.path.exists(path + subDir) and os.path.isfile(path + subDir + dirSep + fileToLoad):

                        print()
                        print("Will now load '%s'" % path + subDir + dirSep + fileToLoad)

                        # Loading the file (via pickle)
                        pickleIn = open(path + subDir + dirSep + fileToLoad, "rb")
                        loadedFile = pickle.load(pickleIn)
                        pickleIn.close()

                        # Return the loaded file
                        return loadedFile
                    else:
                        # Giving the user an error message
                        print("The file '%s' did not exist in '%s' or is not a file." % (fileToLoad, path + subDir))
                        print()
                else:
                    # Giving the user an error message
                    print("The file '%s' did not exist in '%s' or is not a file." % (fileToLoad, path + subDir))
                    print()

                # Asking the user if they want to choose another file, if they dont we will go to the subdirectory choosing loop
                if input("Do you want to choose another file in this directory? y/n ").lower() == "y":
                    continue
                else:
                    newFile = False


# Checking if the user wants to use a saved simulation
useSavedSim = input("Load a saved simulation? ")
print()

while not (useSavedSim.lower() == "y" or useSavedSim.lower() == "n"):
    useSavedSim = input("Load a saved simulation? ")
    print()

if useSavedSim.lower() == "y":
    # We will try to load a saved simulation and if we cant we will just pretend that the user didnt want to use one
    saveFile = loadSim()
    if not saveFile:
        useSavedSim = False
    else:
        useSavedSim = True
else:
    # We are not going to use a saved simulation
    useSavedSim = False

if not useSavedSim:
    # Checking if the user wants to use the default settings
    useDefSettings = input("Use default settings? y/n ")
    print()

    while not ((useDefSettings == "Y" or useDefSettings == "N") or (useDefSettings == "y" or useDefSettings == "n")):
        useDefSettings = input("Use default settings? y/n ")
        print()

    if (useDefSettings == "N") or (useDefSettings == "n"):
        useDefSettings = False
    else:
        useDefSettings = True

    # Checking if the user wants to draw the food grid
    drawFood = input("Draw food? y/n ")
    print()

    while not ((drawFood == "Y" or drawFood == "N") or (drawFood == "y" or drawFood == "n")):
        drawFood = input("Draw food? y/n ")
        print()

    if (drawFood == "N") or (drawFood == "n"):
        drawFood = False
    else:
        drawFood = True

    if not useDefSettings:

        # Asking the user about what resolution the simulation should be run at, both dimensions must be multiples of 50 (X % 50 == 0 && Y % 50 == 0) because of the food grid having 50*50 tiles
        resX = input("X resolution? (must be  multiple of 50) ")
        print()
        while not resX.isdigit() or (not float(resX) > 0) or (not float(resX) % 50 == 0):
            resX = input("X resolution? (must be  multiple of 50) ")
            print()

        resY = input("Y resolution? (must be  multiple of 50) ")
        print()
        while not resY.isdigit() or (not float(resY) > 0) or (not float(resY) % 50 == 0):
            resY = input("Y resolution? (must be  multiple of 50) ")
            print()

        # Converting the resolution variables to be ints and not strings
        resX = int(resX)
        resY = int(resY)
        # Just checking and correcting resolution so it is not below 200x200
        if resX < 200:
            resX = 200
        if resY < 200:
            resY = 200

        numBots = input("How many bitbots should exist? ")
        print()

        while not numBots.isdigit() or (not float(numBots) > 0):
            numBots = input("How many bitbots should exist? ")
            print()

        maxBots = input("What should be the maximum amount of bots that can exist? ")
        print()

        while not maxBots.isdigit() or (not float(maxBots) > 0):
            maxBots = input("What should be the maximum amount of bots that can exist? ")
            print()

        isGridMode = input("Should they be spawned in a grid pattern? y/n ")
        print()

        while not ((isGridMode == "Y" or isGridMode == "N") or (isGridMode == "y" or isGridMode == "n")):
            isGridMode = input("Should they be spawned in a grid pattern? y/n ")
            print()

        if isGridMode == "Y" or isGridMode == "y":
            isGridMode = True
        else:
            isGridMode = False

        frameDivider = input("How many ticks per draw frame should there be? ")
        print()

        while not frameDivider.isdigit() or (not float(frameDivider) > 0):
            frameDivider = float(input("How many ticks per draw frame should there be? "))
            print()

    else:
        isGridMode = False
        resX = 1000
        resY = 700
        numBots = 50
        maxBots = 200
        frameDivider = 1


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
    global maxBots
    global shouldDrawNN
    global frameDivider
    global useSavedSim
    global saveFile
    global drawFood

    # Target fps BEWARE THAT THIS WILL NEVER BE REACHED, IT LIMITS FPS TO ALWAYS BE BELOW THIS
    tFps = 200

    shouldExit = False

    # Game clock and tick manager
    clock = pygame.time.Clock()

    # List for all rects and places where a rect has been to update on the next update call
    updateRects = []
    updateRectsNN = []

    # Checking if we should load a save file / saved simulation
    if useSavedSim:
        print("Bitbots is loading the specified saved simulation")

        # Loading all the saved variables/objects into the real ones
        bots, numBots, isGridMode, resX, resY, shouldDraw, shouldDrawNN, textFont, maxBots, frameDivider, foodArray, tick, isControllingBot, controlBot, drawFood = saveFile.extractData()

        print("Bitbots has now loaded the specified saved simulation")

    else:

        # Current tick counter
        tick = 0

        # Storing if the user is currently moving/viewing a bot
        isControllingBot = False

        # Storing which bot the player is controlling
        controlBot = -1

        shouldDrawNN = True

        # Storing the food amount array
        # Food at each location will be within (0-100) represented as an float
        # Each array entry represents a 50 x 50 area

        # We use floor division here to skip type conversion and basically silently swallowing errors from the input checker
        # We use one extra row and column to prevent errors
        foodArray = np.zeros(((resX // 50) + 1, (resY // 50) + 1))

        # Randomizing the amount of food availiable at each tile (1 tile = one 50 x 50 area)

        # We use numpy's built in multidimensional iterator instead of nested for loops and then just setting the current value to a random one
        for index, curVal in np.ndenumerate(foodArray):
            foodArray[index[0]][index[1]] = random.randrange(0, 100)

    if not frameDivider:
        frameDivider = 1

    pygame.init()

    textFont = pygame.font.SysFont("Monospace", 15)
    smallFont = pygame.font.SysFont("Monospace", 12)

    curScr = pygame.display.set_mode((resX + 800, resY))

    pygame.display.set_caption("Bitbots")

    # Storing the background color
    bgColor = (0, 0, 0)

    # Filling the background with the background color and updating the whole screen
    curScr.fill(bgColor)
    pygame.display.update()

    # Setting up, initializing and storing the bitbots
    bots = botMethods.makeBots(numBots, isGridMode, resX, resY, 0)

    print("Bitbots will now initiate game loop")

    while not shouldExit:
        if tick % frameDivider == 0:
            updateRects.append(pygame.draw.rect(curScr, bgColor, pygame.Rect(0, 0, resX + 800, resY)))

        # wait for game tick to be at the appropriate time
        clock.tick(tFps)
        tick += 1

        # This is used to check if it should draw anything after this tick
        shouldDraw = False

        # Do game tick here

        # Fps calculation
        curFps = 1000 / clock.get_time()
        curFps = round(curFps, 2)

        pygame.display.set_caption("Bitbots  Tick: " + str(tick) + ". TPS/FPS: " + str(curFps) + ".")

        # Moving the controlled bot to the mouse position (if the player is controlling a bot)
        if isControllingBot:
            bots[controlBot].posX = pygame.mouse.get_pos()[0]
            bots[controlBot].posY = pygame.mouse.get_pos()[1]

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
        bots = botMethods.updateSensors(bots, (1 / tick) * 25, foodArray)

        # Updating the NNet of all bots
        for curBot in bots:
            curBot.getOutputs()

        # User keyboard and mouse control handling
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                shouldExit = True
            if event.type == pygame.KEYDOWN:
                if event.type == pygame.K_ESCAPE:
                    shouldExit = True
            # Checking if the pygame window is focused (is the current window) or not
            if pygame.mouse.get_focused():
                # Checking for clicking
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and not isControllingBot:
                        closestBotId = -1

                        # This should be the drawing radius of the bots so that we get accurate clicking
                        closestBotDist = 10

                        # Looping through all the bots to find a bot that the user can select (this has inconsistencies based on list order in some cases)
                        for i in range(bots.__len__()):
                            # The distance between the click position and the bot position
                            botDist = Vec2D.Vec2D(bots[i].posX - event.pos[0],
                                                  bots[i].posY - event.pos[1]).getMagnitude()

                            # Checking the current bot to see if it is the closest bot to the click pos
                            if botDist <= closestBotDist:
                                closestBotId = i
                                closestBotDist = botDist

                        if closestBotId != -1:
                            controlBot = closestBotId
                            isControllingBot = True

                    # If the user rightclicks then the controlled bot will not be controlled anymore
                    if event.button == 3 and isControllingBot:
                        isControllingBot = False
                        controlBot = -1

        # Apply NN outputs (All steps are done separately to prevent inconsistencies based on list order (although there may still be some small inconsistencies))

        for curBot in bots:
            # Apply velocities

            # Health decrease constant (health decreases by this every tick)
            healthDecrease = 0.001

            # Calculate direction vector based on the ratio of left to right output from the NN
            workVector = Vec2D.Vec2D()
            workVector.setX(0)
            workVector.setY(0)

            # Adding the scaled right pointing vector
            workVector.addX(curBot.velVector.getRotatedBy(15).getX() * abs(curBot.NNet[4][0]))
            workVector.addY(curBot.velVector.getRotatedBy(15).getY() * abs(curBot.NNet[4][0]))
            # Adding the scaled left pointing vector
            workVector.addX(curBot.velVector.getRotatedBy(-15).getX() * abs(curBot.NNet[4][1]))
            workVector.addY(curBot.velVector.getRotatedBy(-15).getY() * abs(curBot.NNet[4][1]))
            # Normalizing the vector to 1 + BoostVal (limited to be between 0-1) and applying sprint+boost health decrease (and the default 0.01 health decrease)
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
                        relVector = Vec2D.Vec2D(curSpikeBot.posX - curBot.posX, curSpikeBot.posY - curBot.posY)

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

        if isControllingBot:
            if controlBot >= bots.__len__():
                if bots[controlBot].health <= 0:
                    del bots[controlBot]
                    isControllingBot = False
                    controlBot = -1

        for i in range(bots.__len__()):
            # Apply health checks again

            if i < bots.__len__():
                curBot = bots[i]

                # Checking if the bot should be dead/removed
                if curBot.health <= 0:
                    del bots[i]


                else:
                    # Checking and correcting so the bot doesnt have health over 100
                    if curBot.health > 100:
                        curBot.health = 100

        for curBot in bots:
            # Apply health giving logic (health giving does not have a health toll)

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

        if isControllingBot:
            if controlBot >= bots.__len__():
                if bots[controlBot].health <= 0:
                    del bots[controlBot]
                    isControllingBot = False
                    controlBot = -1

        for i in range(bots.__len__()):
            # Apply health checks again

            if i < bots.__len__():
                curBot = bots[i]

                # Checking if the bot should be dead/removed
                if curBot.health <= 0:
                    del bots[i]


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

        if bots.__len__() > float(maxBots):
            for i in range(0, bots.__len__() - maxBots):
                bots.pop()

        for curBot in bots:
            # Clamp color output to be inside 0-25

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
        if drawFood and tick % frameDivider == 0:
            for index, curVal in np.ndenumerate(foodArray):
                updateRects.append(
                        pygame.draw.rect(curScr, ((curVal / 100) * 255, (curVal / 100) * 255, (curVal / 100) * 255),
                                         pygame.Rect(index[0] * 50, index[1] * 50, (index[0] * 50) + 50,
                                                     (index[1] * 50) + 50)))

        if tick % frameDivider == 0:
            for curBot in bots:
                # Drawing the current bot as a circle
                circleRect1 = pygame.draw.circle(curScr, (
                    curBot.NNet[4][2] * (255 / 25), curBot.NNet[4][3] * (255 / 25), curBot.NNet[4][4] * (255 / 25)),
                                                 (int(curBot.posX), int(curBot.posY)), 10)

                # Drawing the eye range as a circle
                eyeRange = 100
                circleRect2 = pygame.draw.circle(curScr, (50, 50, 50), (int(curBot.posX), int(curBot.posY)),
                                                 eyeRange // 2,
                                                 2)

                updateRects.append(circleRect2)
                updateRects.append(circleRect1)

                # Draw the bot's spike as a line
                scaledSpikeActuator = curBot.NNet[4][7] / 5
                lineRect1 = pygame.draw.line(curScr, (200, 0, 0), (curBot.posX, curBot.posY), (
                    curBot.posX + int(curBot.velVector.getNormalizedTo(50).x * scaledSpikeActuator),
                    curBot.posY + int(curBot.velVector.getNormalizedTo(50).y * scaledSpikeActuator)))

                # Draw the bot's spike angular range as 2 lines
                lineRect2 = pygame.draw.line(curScr, (0, 200, 0), (curBot.posX, curBot.posY), (
                    curBot.posX + int(curBot.velVector.getRotatedBy(22.5).getNormalizedTo(50).x),
                    curBot.posY + int(curBot.velVector.getRotatedBy(22.5).getNormalizedTo(50).y)))

                lineRect3 = pygame.draw.line(curScr, (0, 200, 0), (curBot.posX, curBot.posY), (
                    curBot.posX + int(curBot.velVector.getRotatedBy(-22.5).getNormalizedTo(50).x),
                    curBot.posY + int(curBot.velVector.getRotatedBy(-22.5).getNormalizedTo(50).y)))

                updateRects.append(lineRect3)
                updateRects.append(lineRect2)
                updateRects.append(lineRect1)

                # Draw a white pixel at each bot so we can see them even when they're black
                pixelRect1 = pygame.draw.circle(curScr, (255, 255, 255), (int(curBot.posX), int(curBot.posY)), 2)
                updateRects.append(pixelRect1)

                # Draw the amount of health a bot has as a rectangle to the left of the bot
                healthRect1 = pygame.Rect(curBot.posX - 13, curBot.posY - 10, 3, int((curBot.health // 10) * 1.25))
                pygame.draw.rect(curScr,
                                 (
                                     int((((curBot.health / 100) * -1) + 1) * 255 % 256),
                                     int((curBot.health / 100) * 255 % 256),
                                     int(0)),
                                 healthRect1)
                updateRects.append(healthRect1)

                shouldDraw = True

        # Drawing the selected bot's NN and parameters
        if controlBot != -1:
            drawBot = bots[controlBot]

            # Drawing the input nodes
            for i in range(30):
                nodeRect = pygame.draw.circle(curScr, (
                    int((abs(drawBot.NNet[0][i]) * 50) % 255), int((abs(drawBot.NNet[0][i]) * 50) % 255),
                    int((abs(drawBot.NNet[0][i]) * 50) % 255)), (resX + 60 + i * 20, 20), 5)
                updateRectsNN.append(nodeRect)

            # Drawing the mid nodes
            for i in range(20):
                nodeRect = pygame.draw.circle(curScr, (
                    int((abs(drawBot.NNet[2][i]) * 1000 - 200) % 255),
                    int((abs(drawBot.NNet[2][i]) * 1000 - 200) % 255),
                    int((abs(drawBot.NNet[2][i]) * 1000 - 200) % 255)), (resX + 230 + i * 20, 220), 5)
                updateRectsNN.append(nodeRect)

            # Drawing the out nodes
            for i in range(11):
                nodeRect = pygame.draw.circle(curScr, (
                    int((abs(drawBot.NNet[4][i]) * 50) % 255), int((abs(drawBot.NNet[4][i]) * 50) % 255),
                    int((abs(drawBot.NNet[4][i]) * 50) % 255)), (resX + 140 + i * 60, 420), 5)
                updateRectsNN.append(nodeRect)

            # Drawing all the in-mid node links
            for i in range(30):
                for i2 in range(20):
                    linkRect = pygame.draw.aaline(curScr, (int(abs(drawBot.NNet[0][i] * drawBot.NNet[1][i][i2]) % 255),
                                                           int(abs(drawBot.NNet[0][i] * drawBot.NNet[1][i][i2]) % 255),
                                                           int(abs(drawBot.NNet[0][i] * drawBot.NNet[1][i][i2]) % 255)),
                                                  (resX + 60 + i * 20, 20), (resX + 230 + i2 * 20, 220))
                    updateRectsNN.append(linkRect)

            # Drawing all the mid-end node links
            for i in range(20):
                for i2 in range(11):
                    linkRect = pygame.draw.aaline(curScr, (
                        int(abs(drawBot.NNet[2][i] * drawBot.NNet[3][i][i2]) * 50 % 255),
                        int(abs(drawBot.NNet[2][i] * drawBot.NNet[3][i][i2]) * 50 % 255),
                        int(abs(drawBot.NNet[2][i] * drawBot.NNet[3][i][i2]) * 50 % 255)), (resX + 230 + i * 20, 220),
                                                  (resX + 140 + i2 * 60, 420))
                    updateRectsNN.append(linkRect)

            # Drawing all important values as red text
            updateRectsNN.append(
                    curScr.blit(smallFont.render(drawBot.displayString(), True, (255, 0, 0)), (resX + 60, 30)))

            shouldDrawNN = True

        # Display how many bots are alive (blitting a font render to the curScr)
        curScr.blit(textFont.render((str(bots.__len__())), True, (0, 255, 0)), (0, 0))
        shouldDraw = True

        # Checking if it should draw something this tick
        if shouldDraw:
            pygame.display.update(updateRects)

        if shouldDrawNN:
            pygame.display.update(updateRectsNN)

        # Preventing memory leak
        updateRects.clear()
        updateRectsNN.clear()

        # Randomly adding some food to 5 places in the in the foodarray
        for i in range(0, 5):
            randX = random.randint(0, (resX // 50) - 1)
            randY = random.randint(0, (resY // 50) - 1)
            foodArray[randX][randY] += random.random() * 10

            # Checking and correcting the food value so that it is not above 100
            if foodArray[randX][randY] > 100:
                foodArray[randX][randY] = 100

    if shouldExit:
        # Asking the user if they want to save the simulation
        print()
        if input("Do you want to save the state of the simulation? y/n ") == "y":
            print()

            # The directory we are in
            path = os.path.dirname(os.path.realpath(__file__))

            # Directory separator so we can have cross-platform compatibility
            dirSep = os.sep

            # Storing all the subdirectories in the root dir
            subDirs = next(os.walk('.'))[1]

            # Printing how many subdirectories we found and the names of all the subdirectories
            print("Found %d subdirectories in '%s':" % (subDirs.__len__(), path))
            for curSubDir in subDirs:
                print("\t%s" % curSubDir)
            print()

            redoSaveInte = True

            # We use a while loop here so that the user can create new directories and then be directed to the existing directory part of the code
            while redoSaveInte:

                # Asking the user if they want to choose a subdirectory
                if input("Do you want save the simulation in to one of the existing subdirectories? y/n ") == "y":

                    print()

                    # Asking the user which subdirectory they want to save the simulation in
                    saveDir = input("What subdirectory do you want to save the simulation in? ")
                    print()

                    # Checking if the user specified subdirectory exists
                    if not subDirs.__contains__(saveDir):
                        # We tell the user that they did not specify an existing directory and then we redo the loop
                        print("The directory '%s' does not exist in '%s'! " % (saveDir, path + dirSep))
                        print()

                        continue

                    # Putting all the files in the userspecified subdirectory in a list
                    filenames = next(os.walk(path + dirSep + saveDir))[2]

                    # Giving the user info about which and how many files that were found in the user specified subdirectory
                    print("Found %s files in %s: " % (filenames.__len__(), path + dirSep + saveDir))

                    # Printing all the files in the user specified subdirectory
                    for file in filenames:
                        print("\t%s" % file)
                    print()

                    # Asking the user what filename they want the savefile to have
                    saveName = input(
                            "What filename do you want the simulation to have? (excluding the .bbs extension) ") + ".bbs"
                    print()

                    # Checking if the user specified filename already exists
                    if filenames.__contains__(saveName):
                        # We tell the user that they specified an already existing file and then we redo the loop
                        print("The file '%s' already exists in '%s'! " % (saveName, path + dirSep + saveDir))
                        print()

                        continue

                    # Telling the user that saving is in progress
                    print("Saving simulation to file '%s' in '%s' in progress. " % (saveName, path + dirSep + saveDir))

                    # Creating the save object
                    # TODO Create and save the object via pickle
                    # Putting all the variables we need to save in a list so we can save it
                    saveList = [bots, numBots, isGridMode, resX, resY, shouldDraw, shouldDrawNN, textFont, maxBots,
                                frameDivider, foodArray, tick, isControllingBot, controlBot, drawFood]

                    # Putting the list into the savefile object
                    saveObject = saveTemplate.saveFile(saveList)

                    # Opening a file handle to the user specified filename (with "wb" for writing bytes to the file)
                    pickleOut = open(saveDir + dirSep + saveName, "wb")

                    # Dumping the savefile object to the file
                    pickle.dump(saveObject, pickleOut)

                    # Closing the file handle
                    pickleOut.close()

                    print("Simulation saved. ")
                    print()

                    # We exit the while loop because of failed while conditions
                    redoSaveInte = False

                else:

                    print()

                    redoDirCreate = True

                    # We use a loop here so the user can do infinitely many tries in creating a directory
                    while redoDirCreate:

                        # Asking the user if they want to create a new subdirectory
                        if input("Do you want to create a new subdirectory in '%s'? y/n " % path).lower() == "y":

                            print()

                            # Asking the user what name they want the new subdirectory to have
                            newSubDirName = input("What name do you want the new subdirectory to have? ")

                            print()

                            # Checking if the specified name for a subdirectory already exists
                            if subDirs.__contains__(newSubDirName):

                                # Telling the user that the directory already exists
                                print("The directory '%s' already exists. " % path + dirSep + newSubDirName + dirSep)
                                print()

                                # Asking the user if they want to try creating a new directory again
                                if input("Do you want to try to create a new directory again? y/n ").lower() == "y":
                                    print()

                                else:

                                    # The user doesnt want to use save files, we stop the loop
                                    redoDirCreate = False
                                    print()

                            else:

                                # We create the subdirectory
                                print("Will now create directory '%s' in '%s'. " % (newSubDirName, path))
                                print()
                                os.mkdir(path + dirSep + newSubDirName)

                                # We relist the subdirectories in the root dir so they user can use the new dir
                                subDirs = next(os.walk('.'))[1]

                                # We break out of the loop so the user can choose the directory they just created
                                redoDirCreate = False

                        else:

                            # The user does not want to create a new directory or save the simulation in an existing directory
                            print("Bitbots will not save the current state of the simulation. ")
                            print()

                            # We break out of the loop here so the execution resumes to the exiting stage of the simulation
                            redoDirCreate = False
                            redoSaveInte = False

        print("Bitbots will now exit ")
        pygame.quit()
        print("Bitbots has now exited ")
        sys.exit()
