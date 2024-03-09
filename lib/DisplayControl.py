import board
import displayio
import busio
import adafruit_displayio_ssd1306
import asyncio
import terminalio
from adafruit_display_text import label

displayWidth = 128
displayHeight = 64

#i2c = busio.I2C(board.GP5, board.GP4)
#display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
#display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=displayWidth, height=displayHeight)
#display.auto_refresh = False

def getRelayStateString(state):
    if state == 0:
        return "ENABLED"
    elif state == 1:
        return "DISABLED"
    elif state == 2:
        return "MOTION"
    else:
        return "UNKNOWN"


class MyDisplay:

    def __init__(self, sclPin, sdaPin, address):
    # def __init__(self, myDisplay):
        displayio.release_displays()

        #i2c = busio.I2C(board.GP5, board.GP4)
        # displayBus = displayio.I2CDisplay(i2c, device_address=address)
        # self.display = adafruit_displayio_ssd1306.SSD1306(displayBus, width=displayWidth, height=displayHeight)
        # self.display = myDisplay

        self.display.auto_refresh = False

        #variables that hold the values of readings
        self.photocellValue = 0
        self.distanceValue = 0
        self.relayValue = 0

        self.oldPhotocellValue = -1
        self.oldDistanceValue = -1
        self.oldRelayValue = -1

    async def checkValues(self):
        refreshDisplay = False

        # could make this one long if statement
        if self.distanceValue != self.oldDistanceValue:
            refreshDisplay = True
        elif self.photocellValue != self.oldPhotocellValue:
            refreshDisplay = True
        elif self.relayValue != self.oldRelayValue:
            refreshDisplay = True


        if refreshDisplay:
            self.updateDisplay()

        await asyncio.sleep(0.2)

    def updateDisplay(self):
        self.oldDistanceValue = self.distanceValue
        self.oldPhotocellValue = self.photocellValue
        self.oldRelayValue = self.relayValue

        splash = displayio.Group()
        self.display.root_group = splash

        pcellText = "photocell: {}".format(self.photocellValue)
        text_area = label.Label(terminalio.FONT, text=pcellText, color=COLOR_WHITE, x=0, y=8)
        splash.append(text_area)

        distanceText = "distance:  {} in".format(self.distanceValue)
        text_area = label.Label(terminalio.FONT, text=distanceText, color=COLOR_WHITE, x=0, y=16)
        splash.append(text_area)

        relayState = getRelayStateString(self.relayValue)
        relayText = "relay:     {}".format(relayState)
        text_area = label.Label(terminalio.FONT, text=relayText, color=COLOR_WHITE, x=0, y=32)
        splash.append(text_area)

        self.display.refresh()


    def setDistance(self, reading):
        self.distanceValue = reading

    def setRelay(self, reading):
        self.relayValue = reading

    def setPhotocell(self, reading):
        self.photocellValue = reading
