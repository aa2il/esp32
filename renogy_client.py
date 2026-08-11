################################################################################

# renogy_client.py - Rev 1.0
# Copyright (C) 2026 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# A simple usb client for the Renogy Wanderer Charge Controller

# Use Thonny to upload code to ESP32 - Interpreter is for ESP32 VROOM varient

# In Thonny, Tools->Manage packages to install micropython-modbus - doesn't work!
# Download zip file from gitbub and copy umodbus into /lib on esp32

# The ideas behiind the renogy i/o are from:  https://github.com/wrybread/ESP32ArduinoRenogy

################################################################################

from machine import Pin
from umodbus.serial import Serial as ModbusRTUMaster
from time import sleep
import json

################################################################################

# Define UART pins (TX, RX) depending on your board
# For Raspberry Pi Pico, use a tuple of Pin objects and specify uart_id
rtu_pins = (Pin(23), Pin(22)) 
uart_id = 1

# Target device address on the bus
slave_addr = 255

################################################################################

def get_reninfo():    
    # Read info registers
    info_register_address = 0x00A
    num_info_registers = 17;
    info_registers = host.read_holding_registers(slave_addr,
                                                 info_register_address,
                                                 num_info_registers)
    """
    print("\nInfo Registers:", info_registers)

    sw_version = str( info_registers[10] ) + '.' + str( info_registers[11] )
    hw_version = str( info_registers[12] ) + '.' + str( info_registers[13] )
    serial_number = str( info_registers[14] ) + ' ' + str( info_registers[15] )
    print(sw_version)
    print(hw_version)
    print(serial_number)
    """

    sysinfo={ 'model' : 'Wanderer 10'}
    print('data=',json.dumps(sysinfo))
    
    return sysinfo

def get_renstate():
    
    # Read data registers
    data_register_address = 0x100
    num_data_registers = 35

    data_registers = host.read_holding_registers(slave_addr,
                                             data_register_address,
                                             num_data_registers)
    #print("Data Register:", data_registers)
    battery_soc = data_registers[0] 
    battery_voltage = data_registers[1] * .1
    battery_charging_amps = data_registers[2] * .1
    battery_charging_watts = battery_voltage * battery_charging_amps

    load_voltage = data_registers[4] * .1
    load_amps = data_registers[5] * .01
    load_watts = data_registers[6]

    solar_panel_voltage = data_registers[7]*.1
    solar_panel_amps = data_registers[8]*.01
    solar_panel_watts = data_registers[9]

    raw_data = data_registers[3]
    controller_temperature = raw_data >> 8
    battery_temperature = (raw_data & 255)
    #print(hex(raw_data),hex(controller_temperature),hex(battery_temperature))
    #controller_temperature = 1.8*controller_temperature +32
    #battery_temperature = 1.8*battery_temperature +32

    if solar_panel_watts > load_watts:
        isCharging=1
    else:
        isCharging=0
                
    state={ 'volts' : battery_voltage,
            'socPercent' : battery_soc,
            'wattsIn': solar_panel_watts,
            'wattsOut': load_watts,
            'temperature' : controller_temperature,
            'isCharging' : isCharging,
            'v12PortStatus' : 0,
            'usbPortStatus' : 0,
            'acPortStatus' : 0}

    if 0:
        print('\nBattery Voltage   =\t',battery_voltage,' V')
        print('Battery Charge    =\t',battery_soc,' %')
        print('Panel Wattage     =\t',solar_panel_watts,' W')
        print('Controller Temp   =\t',controller_temperature,' deg-C')
        print('Battery Temp      =\t',battery_temperature,' deg-C')

    print('data=',json.dumps(state))

    return state

def EOR():
    print('<EOR>')

################################################################################

# Initialize the RTU Master (Host)
host = ModbusRTUMaster(
    uart_id=uart_id,
    pins=rtu_pins,
    baudrate=9600,
    data_bits=8,
    stop_bits=1,
    parity=None
)

# Infinite loop to service requests from data aggregator
while True:
    cmd0=input("? ")
    cmd=cmd0.upper()

    if cmd=='RID':
        print('Renogy Wanderer Client v0.1')
        EOR()

    elif cmd=='RENINFO':
        data=get_reninfo()
        EOR()

    elif cmd=='RENSTATE':
        data=get_renstate()
        EOR()
        
