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

pcell = analogio.AnalogIn(board.A0)

relayPin = digitalio.DigitalInOut(board.GP13) # changed from GP7
relayPin.switch_to_output()

buttonPin = digitalio.DigitalInOut(board.GP12) #changed from gp8
buttonPin.switch_to_input(pull=digitalio.Pull.DOWN)

pir = digitalio.DigitalInOut(board.GP22)
pir.direction = digitalio.Direction.INPUT

pressed = False

old_value = pir.value

sonar = adafruit_hcsr04.HCSR04(trigger_pin=board.GP18, echo_pin=board.GP19)

def readTemp():
    tempc = microcontroller.cpu.temperature
    tempf = tempc * (9/5) + 32
    print("temp f: {} temp c: {}".format(tempf, tempc))

#dht = adafruit_dht.DHT11(board.GP6)

# rlly dark is read at about 2k-5k
def readPhotocell():
    print(pcell.value)
    time.sleep(1)

def blinkLed():
    led.value = True
    time.sleep(2)
    led.value = False
    time.sleep(2)

def testRelay():
    relayPin.value = True
    time.sleep(5)
    relayPin.value = False
    time.sleep(5)

def testButton():
    if buttonPin.value:
        pressed = True
    elif buttonPin.value and pressed:
        pressed = False
    print("button: {} pressed: {}".format(buttonPin.value, pressed))

    time.sleep(0.5)


def testPir():
    global old_value
    pir_value = pir.value
    if pir_value:
        # PIR is detecting movement. turn on LED
        led.value = True
        # check if first time movement was detected and print message
        if not old_value:
            print("motion detected")
    else:
        # PIR is not detecting movement. turn off LED
        led.value = False
        # check if this is the first time movement stopped
        if old_value:
            print("motion ended")
    old_value = pir_value

def testSonar():
    try:
        print("distance: {} cm   {} in".format(sonar.distance, (sonar.distance / 2.54)))
        #print(sonar.distance, "cm")
    except RuntimeError:
        print("retrying!")
    time.sleep(0.1)

print("init")

while True:
 #   print(dht.temperature)
    #readPhotocell()
    #testRelay()

    asyncio.run(AsyncTasks.runRelay())
    #asyncio.run(AsyncTasks.main())

    #testPir()

    #testSonar()
