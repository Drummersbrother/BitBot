__author__ = 'FamiljensMONSTER'
# encoding: utf-8
import pygame

from bitbots import botMethods


# Taking and storing input
# It only accepts valid input
resX = input("X resolution?")
while not resX.isdigit() or (not float(resX) > 0):
    resX = input("X resolution?")
    print()
print()
resY = input("Y resolution?")
while not resY.isdigit() or (not float(resY) > 0):
    resY = input("Y resolution?")
    print()
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

curScr = pygame.display.set_mode((int(resX), int(resY)))

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
        bots = botMethods.updateSensors(bots, clock.get_time())

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

        # Apply velocities

        # Checking if it should draw something this tick
        if shouldDraw or updateFull:
            if updateFull:
                pygame.display.update(pygame.Rect((0, 0), (resX, resY)))
            else:
                updateGRec(updateRects)
        # Preventing memory leak
        updateRects = []
    if shouldExit == True:
        print("Bitbots will now exit")
        pygame.quit()
        print("Bitbots has now exited")
