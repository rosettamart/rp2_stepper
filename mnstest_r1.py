import time                      
from machine import Pin          
import rp2    

from hx711_pio import HX711

mtPls = Pin(2, Pin.OUT)
mtDir = Pin(3, Pin.OUT)
mtEnb = Pin(6, Pin.OUT, value=1)

detSen1 = Pin(10, Pin.IN)
detSen2 = Pin(11, Pin.IN)

pin_OUT = Pin(14, Pin.IN, pull=Pin.PULL_DOWN)
pin_SCK = Pin(15, Pin.OUT)

loadCell = HX711(pin_SCK, pin_OUT)
loadCell.tare()

print(loadCell.read())
print(loadCell.get_value())
