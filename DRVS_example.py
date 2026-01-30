from DRVS import DRVS

stepper = DRVS(pins=[0,1,4,3], throttle=[-1,1], limit=[0, 260], wait=10, frq=50000, slow_decay=False)
stepper.step(10)
stepper.step(10, -1)

"""
### SETTING UP: ###

Attributes: pins: set, throttle: set, limit: set, wait: int, frq: int, slow_decay: bool
    `pins`: your four pins, format [A1, A2, B1, B2].
    `throttle`: negative and positive duty. max motor power (default) = [-1, 1]. 70% = [-0.7, 0.7].
    `limit`: minimum and maximum motor positions, i.e. [0, 400]. default = [0, 99999]
    `wait`: the default delay between steps, in ms. default = 5
    `frq`: PWM frequency. default = 50000
    `slow_decay`: soft throttle decay on PWM. default False.
    
Only `pins` is mandatory, the rest use defaults if not specified.
An init and single step could be done with:
    stepper=DRVS([0,1,4,3])
    stepper.step()
    
A "step" in DRVS is one electrical step. Four steps make one full mechanical step.
    If your code uses mechanical steps, movements may seem one quarter of the expected distance.
    If so, congratulations, you just gained 4 x step resolution, at the expense of
    multiplying or dividing by 4 occasionally :)
    
You can change throttle after init by changing stepper.low and stepper.high.
You can change limits after init by changing stepper.min and stepper.max
You can read or change stepper.pos any time, for example to set current position as 0.
You can change default delay after init by changing stepper.wait.
    
### USAGE: ###

.step() accepted attributes:
    steps = number of steps (default 1)
    direction = 1 for forward, -1 for backward (default 1)
    wait = delay between steps in ms (default 5 or init setting)
    halt = stop PWM on complete (default False)
    
All are optional.
    
.wait() can be used instead of time.sleep_ms(), cause why not.

Some examples, with arguments in various formats:
"""

#forward 1, back 1

stepper.step()
stepper.sleep(500)
stepper.step(direction=-1)
stepper.sleep(1000)

#forward 50, back 50

stepper.step(50)
stepper.sleep(500)
stepper.step(50, -1)
stepper.sleep(1000)

#forward & back 10, more slowly; using 40ms delay

stepper.step(10, wait=40)
stepper.sleep(500)
stepper.step(10, -1, 40)
stepper.sleep(1000)

#set throttle to 80%, default delay to 30ms, end limit to 50, current position to 0 and move 10 forward 10 back
stepper.high = 0.8
stepper.low = -0.8
stepper.wait = 30
stepper.max = 50
stepper.pos = 0
stepper.step(20)
stepper.sleep(500)
stepper.step(20, -1)
stepper.sleep(1000)

#forward 10, halt PWM, print position, back 10, halt PWM, print position.

stepper.step(wait=20, steps=10, halt=True)
print(stepper.pos)
stepper.sleep(500)
stepper.step(10, -1, 20, True)
print(stepper.pos)
stepper.sleep(1000)

"""
    step() also returns position.
    halt() can be used to stop PWM outside of a step command.
    release() can be used to fully release PWM resources.
"""

#forward 20 & print position, back 20 & print position, halt PWM, and finally, release PWM resources.
position = stepper.step(20)
print(position)
stepper.sleep(500)
print(stepper.step(20, -1))
stepper.halt()
stepper.release()
