#!/usr/bin/python

from lightControl import LightStrip

class BookShelfLight:
    ''' Book shelf object, use this class to control leds

        Variables:
            
            isInit:   True if has been init already
            ledWidth: width between each led
            offset: offset on the edge of the bookshelf
            rows:   number of rows on the bookshelf
            numLeds:    number of leds per row
            staticfile: name of staticfile to read and write data to
            lights: LightStrip class
    '''
    def __init__(self,staticfile):
        self.ledWidth = 0.0
        self.offset = 0.0
        self.rows = 0
        self.numLeds = 0
        self.staticfile = staticfile
        self.lights = LightStrip(54)
        if self.readValues():
            self.isInit = True
        else:
            self.isInit = False


    # init values
    # initialize class with necessary variables
    # must run on first start up if no staticfile created
    def initValues(self,ledWidth,offset,rows,numLeds):
        self.ledWidth = ledWidth
        self.offset = offset
        self.rows = rows
        self.numLeds = numLeds
        self.isInit = True
        self.storeValues()

    # light shelf
    # light lights at specified row and pos
    # DONE add width of book to light multiple lights if necessary
    # TODO test this
    # TODO add confirmation button
    def lightShelf(self, row, pos,width):
        if self.isInit is False:
            return False
        elif row > self.rows:
            print ("Requested row is more than supported rows!\n")
            return False
        elif pos > self.ledWidth*self.numLeds+self.offset*2:
            print ("Exceeded bounds!\n")
            return False
        else:
            #print multiple lights depending on width
            leds = []
            value = pos - self.offset
            value = value/self.ledWidth
            roundedvalue = round(value)
            ledId = roundedvalue + row * self.numLeds
            leds.append(ledId)
            if value > roundedvalue:    #if in between 2 leds, illuminate both leds
                ledId = ledId + 1
                leds.append(ledId)
            #account for width
            widthValue = width/self.ledWidth
            roundedvalue = round(widthValue)
            if widthValue > roundedvalue:    #if in between 2 leds, illuminate both leds
                roundedvalue = roundedvalue + 1
            for x in range(0,int(roundedvalue)): # added on all the extra width of leds
                ledId = ledId + 1
                leds.append(ledId)
            
            print ("illuminating id: " + str(ledId))
            # TODO add wait to decide when to turn this off
            self.lights.turnOnLed(leds)   #illuminate whole list
            self.lights.showLeds(5)
            return True

    # store static values of this shelf in a file
    # this will store ledWidth, offset, rows, and num LEDs
    def storeValues(self):
        with open(self.staticfile, "w") as newFile:
            newFile.write(str(self.ledWidth) + "\n")
            newFile.write(str(self.offset) + "\n")
            newFile.write(str(self.rows)+ "\n")
            newFile.write(str(self.numLeds) + "\n")

    # read static values of this shelf from file
    def readValues(self):
        try:
            with open(self.staticfile,"r") as storedFile:
                self.ledWidth = float(storedFile.readline())
                self.offset = float(storedFile.readline())
                self.rows = int(storedFile.readline())
                self.numLeds = int(storedFile.readline())
            return True

        except EnvironmentError:
            print (self.staticfile + " does not exist!")
            return False

        

#test code    
if __name__ == "__main__":
    # bShelf = BookShelfLight(1.25,0,3,9,"bookshelf_config.txt")
    bShelf = BookShelfLight("bookshelf_config.txt")
    if bShelf.lightShelf(1,2.3,1) is False:
        print ("failed");
    bShelf.lightShelf(0,3,2)
    print (bShelf.ledWidth)
    print (bShelf.offset)
    print (bShelf.rows)
    print (bShelf.numLeds)
    # bShelf.moveBook(0,5.6)
    # bShelf.moveBook(2,13.7)

