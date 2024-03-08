import board
import time
import digitalio
import adafruit_dht
import microcontroller
import analogio
import asyncio

import terminalio
from adafruit_display_text import label

import adafruit_hcsr04
import busio
import bitbangio

import displayio
import adafruit_displayio_ssd1306

import AsyncTasks

led = digitalio.DigitalInOut(board.GP10)
led.direction = digitalio.Direction.OUTPUT

displayWidth = 128
displayHeight = 64


displayio.release_displays()
i2c = busio.I2C(board.GP5, board.GP4)

#i2c.try_lock()
#print(i2c.scan())
#i2c.unlock()
#i2c.deinit()

displayWidth = 128
displayHeight = 64
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=displayWidth, height=displayHeight)
display.auto_refresh = False


def readTemp():
    tempc = microcontroller.cpu.temperature
    tempf = tempc * (9/5) + 32
    print("temp f: {} temp c: {}".format(tempf, tempc))

def blinkLed():
    led.value = True
    time.sleep(2)
    led.value = False
    time.sleep(2)

def getRelayStateString(state):
    if state == 0:
        return "ENABLED"
    elif state == 1:
        return "DISABLED"
    elif state == 2:
        return "MOTION"
    else:
        return "UNKNOWN"


COLOR_WHITE = 0xFFFFFF


class MyDisplay:

    def __init__(self, sclPin, sdaPin, address, dis):
#        displayio.release_displays()

        #i2c = busio.I2C(board.GP5, board.GP4)
        #displayBus = displayio.I2CDisplay(i2c, device_address=address)
        #self.display = adafruit_displayio_ssd1306.SSD1306(displayBus, width=displayWidth, height=displayHeight)
        self.display = dis

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

        while True:

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

        print("         UPDATING DISPLAY")

        splash = displayio.Group()
        display.root_group = splash

        #pcellText = self.photocellValue
        pcellText = "photocell: {}".format(self.photocellValue)
        text_area = label.Label(terminalio.FONT, text=pcellText, color=COLOR_WHITE, x=0, y=5)
        splash.append(text_area)

        #distaceText = self.distanceValue # format it with 'cm'
        distanceText = "distance:  {} in".format(self.distanceValue)
        text_area = label.Label(terminalio.FONT, text=distanceText, color=COLOR_WHITE, x=0, y=16)
        splash.append(text_area)

        #relayText = self.relayValue # format it with actual text
        relayState = getRelayStateString(self.relayValue)

        relayText = "relay:     {}".format(relayState)
        text_area = label.Label(terminalio.FONT, text=relayText, color=COLOR_WHITE, x=0, y=27)
        splash.append(text_area)

        self.display.refresh()


    def setDistance(self, reading):
        self.distanceValue = reading

    def setRelay(self, reading):
        self.relayValue = reading

    def setPhotocell(self, reading):
        self.photocellValue = reading

    def test(self):
        splash = displayio.Group()
        display.root_group = splash

        #pcellText = self.photocellValue
        pcellText = "photocell: test123"
        text_area = label.Label(terminalio.FONT, text=pcellText, color=COLOR_WHITE, x=0, y=8)
        splash.append(text_area)
        self.display.refresh()


d = MyDisplay(board.GP2, board.GP1, 0x3C, display)
AsyncTasks.setDisplay(d)

#d.test()
#time.sleep(5)

print("init")


while True:
    asyncio.run(AsyncTasks.runRelay())

    #testDisplay()
    #splashDisplay()
