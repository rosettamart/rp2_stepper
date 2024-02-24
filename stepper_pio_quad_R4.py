import time
import rp2
from machine import Pin

motor_step_per_rev = 800
gear_ratio = 1
step_freq = 160000 # 800 x 60 per

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

sm0Status = False
sm4Status = False
sm2Status = False
sm6Status = False

""" PIO State Machine for Stepper Motor Control"""
""" 4 Stepper Motors Control with Dual Core RP2040 """
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW)
def stepper():
    pull(block)             # Wait for the first pulse
    mov(x, osr)             # Load the number of pulses
    pull(block)             # Wait for the delay
    label("step")           # Pulse Count
    nop()        .side(1)   # Pulse pin set high
    nop()
    nop()
    nop()
    mov(y, osr)             # Load delay counter, mov() do not clear osr
    label("delay")          # Pulse Delay Count, Stepper Motor Speed control
    nop()        .side(0)   # Pulse pin set low
    jmp(y_dec, "delay")
    jmp(x_dec, "step")
    irq(rel(0))             # IRQ of end process    


def sm0_Status(sm):
    global sm0Status
    sm0Status = True        # PIO Block 0 sm0 IRQ of end process

def sm4_Status(sm):
    global sm4Status
    sm4Status = True        # PIO Block 1 sm4 IRQ of end process

def sm2_Status(sm):
    global sm2Status
    sm2Status = True        # PIO Block 0 sm2 IRQ of end process

def sm6_Status(sm):
    global sm6Status
    sm6Status = True        # PIO Block 1 sm6 IRQ of end process

sm0 = rp2.StateMachine(0, stepper, freq=step_freq, sideset_base=Pin(pin_puls0)) # PIO Block 0 sm0
sm4 = rp2.StateMachine(4, stepper, freq=step_freq, sideset_base=Pin(pin_puls1)) # PIO Block 1 sm0
sm2 = rp2.StateMachine(2, stepper, freq=step_freq, sideset_base=Pin(pin_puls2)) # PIO Block 0 sm2
sm6 = rp2.StateMachine(6, stepper, freq=step_freq, sideset_base=Pin(pin_puls3)) # PIO Block 1 sm2

sm0.irq(sm0_Status) # PIO Block 0 sm0 IRQ of end process
sm4.irq(sm4_Status) # PIO Block 1 sm0 IRQ of end process
sm2.irq(sm2_Status) # PIO Block 0 sm2 IRQ of end process
sm6.irq(sm6_Status) # PIO Block 1 sm2 IRQ of end process

sm0.active(1), sm4.active(1), sm2.active(1), sm6.active(1)

mtFunc = {"0" : sm0.put, "1" : sm4.put, "2" : sm2.put, "3" : sm6.put}
mtDir = {"0" : pin_dir0, "1" : pin_dir1, "2" : pin_dir2, "3" : pin_dir3}
mtStatus = {"0" : sm0Status, "1" : sm4Status, "2" : sm2Status, "3" : sm6Status}

def accstep(motor, step, speed, direc): # Acceleration Stepper Motor Control
    mtDir[ str(motor)].value(direc) # Set Direction
    if step < 200 or speed == 100: # 200 steps is minimum step for acceleration
        mtFunc[str(motor)](step), mtFunc[str(motor)](speed)
    else:
        maxspeed = speed
        minspeed = 100
        for i in range(0, 100, 10): # Acceleration
            mtFunc[str(motor)](10), mtFunc[str(motor)](minspeed - (maxspeed * i)//100)
        mtFunc[str(motor)](step - 200), mtFunc[str(motor)](speed)
        for i in range(0, 100, 10): # Deceleration
            mtFunc[str(motor)](10), mtFunc[str(motor)](maxspeed + (minspeed * i)//100)

def step(motor, step, speed, direc): # Stepper Motor Control
    mtDir[ str(motor)].value(direc) # Set Direction
    mtFunc[str(motor)](step), mtFunc[str(motor)](speed)
