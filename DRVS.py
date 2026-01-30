from machine import Pin, PWM
from time import sleep_ms

class DRV8833:
    FAST_DECAY = 0
    SLOW_DECAY = 1
    MAX_DUTY_CYCLE = 0xFFFF  # 65535
    MIN_DUTY_CYCLE = 0

    def throttle_a(self, throttle: float, decay_mode: int = SLOW_DECAY):
        self.__throttle(self.motor_a_in_1, self.motor_a_in_2, throttle, decay_mode)

    def throttle_b(self, throttle: float, decay_mode: int = SLOW_DECAY):
        self.__throttle(self.motor_b_in_1, self.motor_b_in_2, throttle, decay_mode)

    def stop_a(self, hard: bool = False):
        if hard:
            self.throttle_a(0.0)
        else:
            self.__stop(self.motor_a_in_1, self.motor_a_in_2)

    def stop_b(self, hard: bool = False):
        if hard:
            self.throttle_b(0.0)
        else:
            self.__stop(self.motor_b_in_1, self.motor_b_in_2)

    def deinit(self):
        self.stop_a()
        self.stop_b()
        self.motor_a_in_1.deinit()
        self.motor_a_in_2.deinit()
        self.motor_b_in_1.deinit()
        self.motor_b_in_2.deinit()
        pass

    def __stop(self, pin1: PWM, pin2: PWM):
        pin1.duty_u16(self.MIN_DUTY_CYCLE)
        pin2.duty_u16(self.MIN_DUTY_CYCLE)

    def __throttle(self, pin1: PWM, pin2: PWM, throttle: float, decay_mode: int):
        if not -1.0 <= throttle <= 1.0:
            raise ValueError("Throttle value is out of range [ -1, 1 ]!")

        duty_cycle = int(abs(throttle) * self.MAX_DUTY_CYCLE)
        if throttle == 0:
            self.__stop(pin1, pin2)
        if decay_mode == self.SLOW_DECAY:
            if 0 < throttle <= 1:
                pin1.duty_u16(self.MAX_DUTY_CYCLE - duty_cycle)
                pin2.duty_u16(self.MAX_DUTY_CYCLE)
            elif -1 <= throttle < 0:
                pin1.duty_u16(self.MAX_DUTY_CYCLE)
                pin2.duty_u16(self.MAX_DUTY_CYCLE - duty_cycle)
        elif decay_mode == self.FAST_DECAY:
            if 0 < throttle <= 1:
                pin1.duty_u16(self.MIN_DUTY_CYCLE)
                pin2.duty_u16(duty_cycle)
            elif -1 <= throttle < 0:
                pin1.duty_u16(duty_cycle)
                pin2.duty_u16(self.MIN_DUTY_CYCLE)
        else:
            raise ValueError(
                "decay_mode must be one of either FAST_DECAY or SLOW_DECAY!"
            )

    def __init__(self, ain1, ain2: PWM, bin1: PWM, bin2: PWM) -> None:
        self.motor_a_in_1 = ain1
        self.motor_a_in_2 = ain2
        self.motor_b_in_1 = bin1
        self.motor_b_in_2 = bin2

    def __del__(self):
        self.deinit()

class DRVS:
    pos = 0
    seq_pos = 0
    delay = 5
    seq = {}
    def __init__(self, pins=[], throttle=[-1,1], limit=[0, 99999], wait=delay, slow_decay=False, frq=50000):
        
        self.seq_pos = 0
        self.pos = 0
        self.min = limit[0]
        self.max = limit[1]
        self.low = throttle[0]
        self.high = throttle[1]
        self.delay = wait
        
        self.seq = {
            0: {
                0: self.high,
                1: self.high
            },
            1: {
                0: self.low,
                1: self.high
            },
            2: {
                0: self.low,
                1: self.low
            },
            3: {
                0: self.high,
                1: self.low
            }
        }
    
        self.drv = DRV8833(
            PWM(Pin(pins[0], Pin.OUT), freq=frq),
            PWM(Pin(pins[1], Pin.OUT), freq=frq),
            PWM(Pin(pins[2], Pin.OUT), freq=frq),
            PWM(Pin(pins[3], Pin.OUT), freq=frq)
        )
        
    def seq_set(self):
        self.seq = {
            0: {
                0: self.high,
                1: self.high
            },
            1: {
                0: self.low,
                1: self.high
            },
            2: {
                0: self.low,
                1: self.low
            },
            3: {
                0: self.high,
                1: self.low
            }
        }
        
    def seq_n(self, direction=1):
        if direction == 1:
            if self.seq_pos >= 3:
                return 0
            else:
                return self.seq_pos + 1
        else:
            if self.seq_pos <= 0:
                return 3
            else:
                return self.seq_pos - 1
            
    def step(self, steps=1, direction=1, wait=delay, halt=False):
        self.seq_set()
        remaining_steps = steps
        for _ in range(steps):
            if self.pos+direction >= self.min and self.pos+direction <= self.max:
                thisStep = self.seq_n(direction)
                self.drv.throttle_a(self.seq[thisStep][0])
                self.drv.throttle_b(self.seq[thisStep][1])
                self.seq_pos = thisStep
                self.pos+=direction
                remaining_steps -= 1
                sleep_ms(wait)
            else:
                exceeded = "Min"
                if self.pos+direction >= self.max:
                    exceeded = "Max"
                raise ValueError(
                    exceeded + " travel reached. Could not complete " + str(remaining_steps) + " remaining steps."
                )
                break
            
        if halt == True:
            self.drv.stop_a()
            self.drv.stop_b()
        
        return self.pos
            
    def sleep(self, wt=wait):
        sleep_ms(wt)
            
    def halt(self):
        self.drv.stop_a()
        self.drv.stop_b()
        
    def release(self):
        self.drv.deinit()

