# Various ways to blink the on-board led

from machine import Pin,Timer
from time import sleep

LED_PIN=2                       # D2 is the On-board blue LED
led = Pin(LED_PIN, Pin.OUT)
   
# Callback (aka ISR) used with timer interrupt
def toggle_led(t):
    led.value(not led.value())


if False:

    # Brute-force - blocking
    while True:
        led.value(not led.value())
        sleep(1)

elif True:
    
    # Using a timer - non-blocking - periodic, changes state every 1-sec
    led_timer = Timer(1)
    led_timer.init(mode=Timer.PERIODIC,period=1000,callback=toggle_led)


elif True:
    
    # Using a timer - non-blocking - one-shot, changes state after a 2-sec delay
    led_timer = Timer(1)
    led_timer.init(mode=Timer.ONE_SHOT,period=2000,callback=toggle_led)

