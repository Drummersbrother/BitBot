__author__ = 'FamiljensMONSTER'
# encoding: utf-8

""" This class is for saving the state of a simulation and then unpacking it and extracting the data """


class saveFile:
    # This is used to store the data into an object so we can pickle the object and then load it back and extract the data
    def __init__(self, data):
        self.data = data

    def extractData(self):
        return self.data
