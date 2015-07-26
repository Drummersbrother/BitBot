__author__ = 'FamiljensMONSTER'
# encoding: utf-8
import math

import bitbots


class Vec2D:
    # This method does not seem too take parameters correctly :/
    # Because of this the other methods may seem to be too long but it is necessary if this should work
    def __init__(self, inx=0.0, iny=0.0):
        self.x = inx
        self.y = iny

    def getMagnitude(self) -> float:
        return math.sqrt((float(self.x) ** 2.0) + (float(self.y) ** 2.0))

    def getAddedTo(self, other):
        Return = bitbots.Vec2D()
        Return.addX(self.x + other.x)
        Return.addY(self.y + other.y)
        return Return

    def addTo(self, other):
        self.x += other.x
        self.y += other.y

    def getNormalizedTo(self, length):
        mag = bitbots.Vec2D.Vec2D.getMagnitude(self)
        scale = mag / length

        Return = bitbots.Vec2D.Vec2D()
        Return.addX(self.x / scale)
        Return.addY(self.y / scale)

        return Return

    def normalizeTo(self, length):
        mag = self.getMagnitude()
        scale = mag / length

        self.x /= scale
        self.y /= scale

    def addX(self, X):
        self.x += X

    def addY(self, Y):
        self.y += Y

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def setX(self, X):
        self.x = X

    def setY(self, Y):
        self.y = Y

    def getDotProductTo(self, other) -> float:
        dotProduct = (self.x * other.x) + (self.y * other.y)
        return dotProduct

    def getDotProductFromUnitVec(self, other) -> float:
        selfMag = self.getMagnitude()
        otherMag = other.getMagnitude()
        dotProduct = ((self.x / selfMag) * (other.x / otherMag)) + ((self.y / selfMag) * (other.y / otherMag))
        return dotProduct

    # Get a vector that is rotated by angle degrees from the used vector object
    def getRotatedBy(self, angle):
        # Dont ask me how this works, I found it on a unity forum and my old code didn't work -_-
        Return = Vec2D()
        Return.x = 0
        Return.y = 0

        angleRad = math.radians(angle)

        sinAng = math.sin(angleRad)
        cosAng = math.cos(angleRad)

        Return.x = self.x * cosAng - self.y * sinAng
        Return.y = self.x * sinAng + self.y * cosAng

        Return.normalizeTo(self.getMagnitude())

        return Return

    def rotateBy(self, angle):
        prevX = self.x
        prevY = self.y

        angleRad = math.radians(angle)

        sinAng = math.sin(angleRad)
        cosAng = math.cos(angleRad)

        self.x = prevX * cosAng - prevY * sinAng
        self.y = prevX * sinAng + prevY * cosAng
