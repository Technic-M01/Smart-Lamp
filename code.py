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

from adafruit_display_shapes.rect import Rect

led = digitalio.DigitalInOut(board.GP10)
led.direction = digitalio.Direction.OUTPUT

displayWidth = 128
displayHeight = 64


displayio.release_displays()
time.sleep(1)
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
COLOR_BLACK = 0x000000

BORDER = 5

class DisplayControl:

    def __init__(self, dis):
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

    # sensor value should be the percentage of a given reading from the max reading
    def drawGauge(self, displayGroup, offsetY, sensorValue):
        GAUGE_WIDTH = displayWidth - 10
        GAUGE_HEIGHT = 10

        # POS_X = 0
        POS_X = 5
        POS_Y = offsetY

        # bitmap to draw a border
        color_bitmap = displayio.Bitmap(GAUGE_WIDTH, GAUGE_HEIGHT, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = COLOR_WHITE

        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=POS_X, y=POS_Y)
        displayGroup.append(bg_sprite)

        # background
        inner_bitmap = displayio.Bitmap(GAUGE_WIDTH-BORDER+1, 6, 1)
        inner_palette = displayio.Palette(1)
        inner_palette[0] = COLOR_BLACK
        inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=POS_X+BORDER-3, y=POS_Y+BORDER-3)
        displayGroup.append(inner_sprite)

        # bar to indicate reading level
        full = GAUGE_WIDTH-(BORDER*2)+2
        percent = (sensorValue/100)*full

        #gauge_bitmap = displayio.Bitmap(GAUGE_WIDTH-(BORDER*2)+2, 2, 1)
        gauge_bitmap = displayio.Bitmap(int(percent), 2, 1)
        gauge_palette = displayio.Palette(1)
        gauge_palette[0] = COLOR_WHITE
        gauge_sprite = displayio.TileGrid(gauge_bitmap, pixel_shader=gauge_palette, x=POS_X+BORDER-1, y=POS_Y+BORDER-1)
        displayGroup.append(gauge_sprite)

    def updateDisplay(self):
        self.oldDistanceValue = self.distanceValue
        self.oldPhotocellValue = self.photocellValue
        self.oldRelayValue = self.relayValue

        splash = displayio.Group()
        self.display.root_group = splash

        relayState = getRelayStateString(self.relayValue)
        relayText = "relay:     {}".format(relayState)
        text_area = label.Label(terminalio.FONT, text=relayText, color=COLOR_WHITE, x=0, y=5)
        splash.append(text_area)

        # max reading is 65000
        pcellText = "photocell: {}".format(self.photocellValue)
        text_area = label.Label(terminalio.FONT, text=pcellText, color=COLOR_WHITE, x=0, y=18)
        splash.append(text_area)

        pcellPercentage = (self.photocellValue/65000)*100

        self.drawGauge(splash, 25, pcellPercentage)

        distanceText = "distance:  {} in".format(self.distanceValue)
        text_area = label.Label(terminalio.FONT, text=distanceText, color=COLOR_WHITE, x=0, y=46)
        splash.append(text_area)

        # max distance is usually around 162
        
        # handling for when the us sensor is out of range or reports an error
        if self.distanceValue == -1:
            distancePercentage = 100
        else:
            distancePercentage = (self.distanceValue / 162) * 100


        self.drawGauge(splash, 53, distancePercentage)

        '''
        # GAUGE_WIDTH = 50
        GAUGE_WIDTH = displayWidth - 10
        GAUGE_HEIGHT = 10

        # POS_X = 0
        POS_X = 5
        POS_Y = 50

        # bitmap to draw a border
        color_bitmap = displayio.Bitmap(GAUGE_WIDTH, GAUGE_HEIGHT, 1)
        color_palette = displayio.Palette(1)
        color_palette[0] = COLOR_WHITE

        bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=POS_X, y=POS_Y)
        splash.append(bg_sprite)

        # background
        inner_bitmap = displayio.Bitmap(GAUGE_WIDTH-BORDER+1, 6, 1)
        inner_palette = displayio.Palette(1)
        inner_palette[0] = COLOR_BLACK
        inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=POS_X+BORDER-3, y=POS_Y+BORDER-3)
        splash.append(inner_sprite)

        # bar to indicate reading level
        gauge_bitmap = displayio.Bitmap(GAUGE_WIDTH-(BORDER*2)+2, 2, 1)
        gauge_palette = displayio.Palette(1)
        gauge_palette[0] = COLOR_WHITE
        gauge_sprite = displayio.TileGrid(gauge_bitmap, pixel_shader=gauge_palette, x=POS_X+BORDER-1, y=POS_Y+BORDER-1)
        splash.append(gauge_sprite)

        #self.drawGauge(splash)

        # rec = Rect(70, 85, 61, 30, outline=0x0, stroke=3)
        # splash.append(rec)
        '''

        self.display.refresh()


    def setDistance(self, reading):
        self.distanceValue = reading

    def setRelay(self, reading):
        self.relayValue = reading

    def setPhotocell(self, reading):
        self.photocellValue = reading


control = DisplayControl(display)
AsyncTasks.setDisplay(control)

print("init")


while True:
    asyncio.run(AsyncTasks.runRelay())

    #testDisplay()
    #splashDisplay()
