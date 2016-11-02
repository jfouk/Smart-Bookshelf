#!/usr/bin/python

from ledStrip import ledstrip
import time

class LightStrip:
    ''''object that contains the whole light strip

    Variables:
        
        leds: led accessor
        numLeds: max number of leds in light strip
        onLeds: list of leds to turn on, appended on the list
    '''

    def __init__(self, numLeds):
        spidev = file("/dev/spidev0.0", "wb")  # ref to spi connection to the led bar
        self.leds   = ledstrip.LEDStrip(pixels=numLeds, spi=spidev)
        self.numLeds = numLeds
        self.onLeds = [0]*numLeds

    def turnOnLed(self, ledId):
        #check that ledId is in range
        if ledId < self.numLeds:
            self.onLeds[ledId] = 1
        else:
            print "Led ID out of range!!"

    def clearAllLeds(self):
        self.onLeds = [0] * self.numLeds

    def updateLeds(self):
        for pixels in range(0,self.numLeds):
            if self.onLeds[pixels]:
                self.leds.setPixelColorRGB(pixel=pixels, red=127, green=127, blue=127)
            else:
                self.leds.setPixelColorRGB(pixel=pixels, red=0, green=0, blue=0)
        self.leds.show()


#test code    
if __name__ == "__main__":
    lStrip = LightStrip(32)
    lStrip.turnOnLed(15)
    lStrip.turnOnLed(8)
    lStrip.updateLeds()
    time.sleep(5)
    lStrip.clearAllLeds()
    lStrip.updateLeds()

