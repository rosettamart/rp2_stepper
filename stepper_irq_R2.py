import time                      
from machine import Pin          
import rp2                       

         
motor_1 = False                   
x_last = 0                        

drv_ms = 16               
motor_steps_per_rev = 200 
gear_ratio = 1            
steps_per_rev = motor_steps_per_rev * drv_ms * gear_ratio 
step_angle = 360 / steps_per_rev 
lead_screw_pitch = 2 
step_pitch = lead_screw_pitch / steps_per_rev 
print("For gears, belts and arms.")
print("Steps per revolution:", steps_per_rev, "steps.",
      "\nOne step is", step_angle, "degrees.\n")
print("For lead screws.")
print ("[mm] per revolution:", lead_screw_pitch,
       "\nOne steps is", step_pitch, "[mm].\n")

         
activation_pin = Pin(25, Pin.OUT) 
                                  
@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW) 
def step_counter():
    pull(block)                    
    mov(x, osr)                    
    wait(1, gpio, 25)              
    label("count")                 
    jmp(not_x, "end") .side(1) [1] 
    irq(5) .side(0)                
    irq(block, 4)                  
    jmp(x_dec, "count")            
    label("end")                   
    irq(block, rel(0))             

@rp2.asm_pio(autopull=True)                         
def step_speed():
    pull(block)
    wait(1, irq, 5)         
    #set(y, 5)
    mov(y, osr)
    label("delay")          
    nop() [9]               
    jmp(y_dec, "delay")     
    irq(clear, 4)           

def pio_0_handler(sm): 
    global motor_1
    motor_1 = True
    print(sm, "x:", x_last)

sc_freq = 1_000_000 
ss_freq = 1_000_000 

step_pin_1 = Pin(0, Pin.OUT)
dir_pin_1 = Pin(1, Pin.OUT)         
sm_0 = rp2.StateMachine(0, step_counter, freq=sc_freq, sideset_base=step_pin_1)
sm_0.irq(pio_0_handler)              
sm_1 = rp2.StateMachine(1, step_speed, freq=ss_freq)


sm_0.active(1), sm_1.active(1) 

def steps(x, y): 
    global motor_1
    motor_1 = False
    x_steps = round(x)
    if int(x) < 0:
        dir_pin_1.value(1)
        x_steps = x_steps * (-1)
    sm_0.put(x_steps)
    sm_1.put(y) 
    activation_pin.value(1)
    while True:
        if motor_1:
            dir_pin_1.value(0)
            activation_pin.value(0) 
            return
        time.sleep_ms(1)

