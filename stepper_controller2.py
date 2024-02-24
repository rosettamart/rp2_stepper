import time                     
from machine import Pin          
import rp2                      

motor_1 = False                
x_last = 0                    

activation_pin = Pin(25, Pin.OUT) 

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_HIGH) 
def step_counter():
    pull(block)                    
    mov(x, osr)                    
    wait(1, gpio, 25)              
    label("count")                 
    jmp(not_x, "end") .side(0) [5] 
    irq(5) .side(1)                
    irq(block, 4)                  
    jmp(x_dec, "count")            
    label("end")                   
    irq(block, rel(0))             

#@rp2.asm_pio(autopull=True)       
@rp2.asm_pio()       
def step_speed():
    pull(block)
    mov(y, osr)
    wait(1, irq, 5)         
    #set(y, 10)              
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
sm_1 = rp2.StateMachine(1, step_speed, freq=ss_freq)

sm_0.irq(pio_0_handler)    

sm_0.active(1)
sm_1.active(1) 

def steps(x, speed): 
    global motor_1
    global x_last
    x_last = 0
    x_last = x + x_last
    motor_1 = False
    x_steps = round(x)
    print("Step 01")
    if int(x) < 0:
        dir_pin_1.value(1)
        x_steps = x_steps * (-1)
    print("Step 02")
    sm_0.put(x_steps)
    print("Step 03")
    sm_1.put(speed)
    print("Step 04")
    activation_pin.value(1)
    while True:
        if motor_1:
            print("Step 05")
            dir_pin_1.value(0)
            activation_pin.value(0) 
            return
        time.sleep_ms(1)

#machine.freq(250_000_000)
steps(10000, 5)   
