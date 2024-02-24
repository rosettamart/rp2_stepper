import time
import rp2
from machine import Pin

motor_step_per_rev = 800
gear_ratio = 1
step_freq = 100000 # 800 x 60 per

steps_per_rev = motor_step_per_rev * gear_ratio
step_angle = 360 / steps_per_rev

pin_puls0 = Pin(0, Pin.OUT)
pin_puls1 = Pin(2, Pin.OUT)
pin_puls2 = Pin(4, Pin.OUT)
pin_puls3 = Pin(6, Pin.OUT)

pin_dir0 = Pin(1, Pin.OUT)
pin_dir1 = Pin(3, Pin.OUT)
pin_dir2 = Pin(5, Pin.OUT)
pin_dir3 = Pin(7, Pin.OUT)

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW)
def stepper():
    pull()
    mov(x, osr)
    pull()
    label("step")
    nop()        .side(1)
    mov(y, osr)
    label("delay")
    nop()        .side(0)
    jmp(y_dec, "delay")
    jmp(x_dec, "step")
    irq(rel(0))

sm0 = rp2.StateMachine(0, stepper, freq=step_freq, sideset_base=Pin(pin_puls0)) # PIO Block 0 sm0
sm4 = rp2.StateMachine(4, stepper, freq=step_freq, sideset_base=Pin(pin_puls1)) # PIO Block 1 sm0
sm2 = rp2.StateMachine(2, stepper, freq=step_freq, sideset_base=Pin(pin_puls2)) # PIO Block 0 sm2
sm6 = rp2.StateMachine(6, stepper, freq=step_freq, sideset_base=Pin(pin_puls3)) # PIO Block 1 sm2

sm0.irq(lambda p: print(time.ticks_ms()))
sm4.irq(lambda p: print(time.ticks_ms()))
sm2.irq(lambda p: print(time.ticks_ms()))
sm6.irq(lambda p: print(time.ticks_ms()))

sm0.active(1), sm4.active(1), sm2.active(1), sm6.active(1)

def step(step0, delay0, step1, delay1, step2, delay2, step3, delay3):
    sm0.put(step0), sm0.put(delay0)
    sm4.put(step1), sm4.put(delay1)
    sm2.put(step2), sm2.put(delay2)
    sm6.put(step3), sm6.put(delay3)
    wtime=round((((delay0*5)*step0)/48000))
    time.sleep(wtime)

step(10000, 10, 800, 10, 800, 10, 800, 10)

