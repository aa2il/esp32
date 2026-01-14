# ESP32 MUSINGS

Various programs/scripts to explore MicroPython on the ESP32.

1) Install thonny and esptool:

   uvinit

2) Run Thonny and burn latest firmware - See 
      
   https://www.espboards.dev/blog/micropython-esp32-getting-started/
   PDF is in this dir

   uv run thonny

3) Load up blinky.py and run it - it works!   

4) C sketches and Arduino IDE still work with new firmware!

###########################################################################

OLD:

Commands to install micro-python firmware:

1) Go to micropython website and download latest firmaware

2) Install esptool, the script that burns the firmware
      
pip install esptool
rehash

3) Clear flash and burn micropython firmware
   
esptool.py --port /dev/ttyUSB2 erase_flash

esptool.py --chip esp32 --port /dev/ttyUSB2 write_flash -z 0x1000 esp32-20220618-v1.19.1.bin 

4) There are a few IDEs available - Thonny looks like a decent choice
   
sudo apt install python3-tk thonny
rehash
