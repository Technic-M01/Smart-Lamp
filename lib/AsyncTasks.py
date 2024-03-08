import asyncio
import board
import digitalio
import keypad
import time
import adafruit_hcsr04
import analogio
from Timer import PauseTimer
import array

# relay states
ENABLE = 0
DISABLE = 1
AUTOMOTION = 2

# Reading Sample Size
SAMPLE_SIZE = 5

# Array to hold distance and photocell readings to average out later
distanceReadings = []
photocellReadings = []

class RelayState:
    # holds value for relay state.
    # use .value to read or write

    def __init__(self, initial_state):
        self.value = initial_state

    def indexState(self):
        print("indexing relay state. old value: ", self.value)
        if self.value != 2:
            self.value += 1
        elif self.value == 2:
            self.value = 0
        print("                new value: ", self.value)

class PhotocellState:
    def __init__(self, initial_state):
        self.value = initial_state

def measureDistance(sensor):
    try:
        conversion = sensor.distance / 2.54 # convert cm to in
        print("distance: {} cm   {} in".format(sensor.distance, (sensor.distance / 2.54)))
        #print(sonar.distance, "cm")
        return conversion
    except RuntimeError:
        print("retrying!")
        return -1

class Interval:
    # holds interval value. use .value to read or write

    def __init__(self, initial_interval):
        self.value = initial_interval


async def monitorStateButtons(buttonStatePin, buttonSensorPin, relayState):
    # monitor the button to toggle state

    # assume button is active lower
    with keypad.Keys((buttonStatePin, buttonSensorPin), value_when_pressed=False, pull=True) as keys:
        while True:
            key_event = keys.events.get()
            if key_event and key_event.pressed:
                if key_event.key_number == 0:
                    # change relay state
                    print("change relay state")
                    relayState.indexState()
                else:
                    print("change motion state")
                    #motionState.indexState()

            # let another task run
            await asyncio.sleep(0)

async def monitor_interval_buttons(pin_slower, pin_faster, interval):
    # monitor two buttons, one lengthens interval, one shortens iter

    #assume buttons are active lower
    with keypad.Keys((pin_slower, pin_faster), value_when_pressed=False, pull=True) as keys:
        while True:
            key_event = keys.events.get()
            if key_event and key_event.pressed:
                if key_event.key_number == 0:
                    # lengthen the interval
                    interval.value += 0.1
                else:
                    # shorten the interval
                    interval.value = max(0.1, interval.value - 0.1)
                print("interval is now: ", interval.value - 0.1)
            # let another task run
            await asyncio.sleep(0)

async def handleRelay(relayPin, relayState, photocellState, printDebug=False):
    # handle relay state. disable/enable/pause
    global distanceReadings

    pTimer = PauseTimer(5)

    autoTimer = PauseTimer(3)

    with digitalio.DigitalInOut(relayPin) as relay:
        relay.switch_to_output()
        while True:
            currentState = relayState.value

            if currentState == ENABLE:
                if printDebug:
                    print("handleRelay. current state: ENABLE")

                relay.value = photocellState.value #switches relay based on pcell readings

            elif currentState == DISABLE: # turns relay off
                if printDebug:
                    print("handleRelay. current state: DISABLE")
                relay.value = False
            elif currentState == AUTOMOTION:
                # abstract pin numbers to constructor
                with adafruit_hcsr04.HCSR04(trigger_pin=board.GP16, echo_pin=board.GP17) as sonar:
                        distance = measureDistance(sonar)
                        distanceReadings.append(distance)

                        # start timer that will automatically shut off relay without any movement detected
                        autoTimer.run()

                        #TODO add logic from removing invalid readings (-1) from array, and then averaging from new array size
                        # take multiple readings to average out the distance
                        if len(distanceReadings) >= SAMPLE_SIZE:
                            print(distanceReadings)
                            avgDistance = sum(distanceReadings) / len(distanceReadings)
                            print(avgDistance)
                            distanceReadings = []

                            if avgDistance < 0 and autoTimer.getStatus() == True:
                                relay.value = False

                                print("             avg distance -1")
                            elif avgDistance >= 50 and autoTimer.getStatus() == True:
                                relay.value = False
                            elif avgDistance < 50:
                                relay.value = True
                                autoTimer.reset()


            #relay.value = not relay.value
            await asyncio.sleep(0.2)

async def handlePhotocell(pin, photocellState): # should be A0
    global photocellReadings
    transitionThreshold = 30000 # arbitrary value. will have to measure actual values later

    with analogio.AnalogIn(pin) as pcell:

        while True:
            reading = pcell.value
            photocellReadings.append(reading)

            if len(photocellReadings) >= SAMPLE_SIZE:
                avgReading = sum(photocellReadings)/len(photocellReadings)
                photocellReadings = []

                print("avg photocell reading: ", avgReading)

                if avgReading < transitionThreshold:
                    photocellState.value = True
                elif avgReading > transitionThreshold and photocellState.value == True:
                    photocellState.value = False

            await asyncio.sleep(0.5)

async def blink(pin, interval):
    # blink the given pin forever. blink rate is supplied by interval object

    with digitalio.DigitalInOut(pin) as led:
        led.switch_to_output()
        while True:
            led.value = not led.value
            await asyncio.sleep(interval.value)


async def runRelay():
    relayState = RelayState(ENABLE)
    photocellState = PhotocellState(False)

    photocellTask = asyncio.create_task(handlePhotocell(board.A1, photocellState))
    relayTask = asyncio.create_task(handleRelay(board.GP7, relayState, photocellState)) #can enable/disable debug prints
    relayStateTask = asyncio.create_task(monitorStateButtons(board.GP8, board.GP9, relayState))

    await asyncio.gather(photocellTask, relayTask, relayStateTask)


async def main():
    # start blinking 0.5 sec on, 0.5 sec off
    interval = Interval(0.5)

    led_task = asyncio.create_task(blink(board.GP10, interval))
    interval_task = asyncio.create_task(monitor_interval_buttons(board.GP8, board.GP9, interval))

    # will run forever, because neither task ever exits
    await asyncio.gather(led_task, interval_task)
