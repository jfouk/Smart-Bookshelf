#!/usr/bin/python

from lightControl import LightStrip

class BookShelf:
    ''' Book shelf object, use this class to control leds

        Variables:
            
            ledWidth: width between each led
            offset: offset on the edge of the bookshelf
            rows:   number of rows on the bookshelf
            numLeds:    number of leds per row
            lights: LightStrip class
    '''

    def __init__(self,ledWidth,offset,rows,numLeds):
        self.ledWidth = ledWidth
        self.offset = offset
        self.rows = rows
        self.numLeds = numLeds
        self.lights = LightStrip(32)

    def moveBook(self, row, pos):
        if row > self.rows:
            return -1
        else:
            value = pos - self.offset
            value = value/self.ledWidth
            value = round(value)
            ledId = value + row * self.numLeds
            print "illuminating id: " + str(ledId)
            self.lights.turnOnLed((ledId,))
            self.lights.showLeds(5)


#test code    
if __name__ == "__main__":
    bShelf = BookShelf(1.25,0,3,9)
    bShelf.moveBook(0,5.6)
    bShelf.moveBook(2,13.7)

