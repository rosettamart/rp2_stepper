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

sm0Status = False
sm4Status = False
sm2Status = False
sm6Status = False

""" PIO State Machine for Stepper Motor Control"""
""" 4 Stepper Motors Control with Dual Core RP2040 """
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW)
def stepper():
    pull()
    mov(x, osr)
    pull()
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

def psCheck(): # PIO Process End Check Status
    if sm0Status and sm4Status and sm2Status and sm6Status:
        return True
    else:
        return False

def steps(step0, delay0, step1, delay1, step2, delay2, step3, delay3):
    sm0.put(step0), sm0.put(delay0)
    sm4.put(step1), sm4.put(delay1)
    sm2.put(step2), sm2.put(delay2)
    sm6.put(step3), sm6.put(delay3)

def direction(dir0, dir1, dir2, dir3):
    pin_dir0.value(dir0)
    pin_dir1.value(dir1)
    pin_dir2.value(dir2)
    pin_dir3.value(dir3)


def step(motor, step, speed, direc):
    if motor == 0:
        pin_dir0.value(direc)
        sm0.put(step), sm0.put(speed)
    elif motor == 1:
        pin_dir1.value(direc)
        sm4.put(step), sm4.put(speed)
    elif motor == 2:
        pin_dir2.value(direc)
        sm2.put(step), sm2.put(speed)
    elif motor == 3:
        pin_dir3.value(direc)
        sm6.put(step), sm6.put(speed)
