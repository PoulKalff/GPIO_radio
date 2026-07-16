import sys
import time

events = []
blocked = True

while blocked:
    events.append(time.time())
    timePassed = events[-1] - events[0]
    if timePassed >= 1:
        blocked = False
    print("time since first event:", timePassed)


print(len(events))




