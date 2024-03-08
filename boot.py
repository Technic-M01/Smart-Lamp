# Write your code here :-)

import board
import digitalio
import storage

write_pin = digitalio.DigitalInOut(board.GP0)
write_pin.direction = digitalio.Direction.INPUT
write_pin.pull = digitalio.Pull.UP

# if write pin is connected to ground on start-up, CircuitPython can write to CIRCUITPY file system
if not write_pin.value:
    storage.remount("/", readonly=False)
