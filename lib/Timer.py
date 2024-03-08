import time

class PauseTimer:

    def __init__(self, offset):
        self.offset = offset
        self.done = False
        self.running = False
        self.startTime = -1

    def run(self):
        if self.running == False and self.done == False:
            self.startTime = time.monotonic()
            self.running = True

        if self.running == True:
            now = time.monotonic()

            if (self.startTime + self.offset) >= now:
                print("timer running.   countdown at: ", now - (self.startTime + self.offset))
            else:
                print("timer done running")
                self.done = True

    def reset(self):
        self.running = False
        self.done = False

    def getStatus(self):
        return self.done
