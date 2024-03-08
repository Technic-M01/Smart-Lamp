import board
import time
import digitalio
import adafruit_dht
import microcontroller
import analogio
import asyncio

import adafruit_hcsr04

import AsyncTasks

led = digitalio.DigitalInOut(board.GP10)
led.direction = digitalio.Direction.OUTPUT

def readTemp():
    tempc = microcontroller.cpu.temperature
    tempf = tempc * (9/5) + 32
    print("temp f: {} temp c: {}".format(tempf, tempc))

def blinkLed():
    led.value = True
    time.sleep(2)
    led.value = False
    time.sleep(2)

print("init")

while True:
    asyncio.run(AsyncTasks.runRelay())
    #asyncio.run(AsyncTasks.main())

