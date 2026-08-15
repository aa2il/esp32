################################################################################

# renogy_client.py - Rev 1.0
# Copyright (C) 2026 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# This code combines the simple web clients for the Yeti GoalZero Battery
# and Renogy Charge Controller.

# Use Thonny to upload code to ESP32 - Interpreter is for ESP32 VROOM varient

# Need to upload credentials2.py and urequests2.py to ESP32.
# The easiest way to do this is to enable View->Files
# and then right-click on This Computer->....->credentials2.py -> Uploead To /

# The ideas behiind the yeti i/o are from:    https://github.com/tkdrob/goalzero
# The ideas behiind the renogy i/o are from:  https://github.com/wrybread/ESP32ArduinoRenogy

# This repository also looks relavant:        https://github.com/rosswarren/renogymodbus
# Need to check if Vcc is available from RJ12 connector

################################################################################

# Needed for Yeti GZ I/O
import network
import urequests2 as urequests
import time
from credentials2 import *

# Needed Renogy I/o
from machine import Pin
from umodbus.serial import Serial as ModbusRTUMaster
import json

################################################################################

# Defs for Yeti GZ
URL='http://10.1.1.1'
HEADER = {
    "Content-Type": "application/json",
    "User-Agent": "YetiApp/1340 CFNetwork/1125.2 Darwin/19.4.0",
    "Connection": "keep-alive",
    "Accept": "application/json",
    "Accept-Language": "en-us",
    "Accept-Encoding": "gzip, deflate",
    "Cache-Control": "no-cache",
}

# Defs for Renogy Wander
rtu_pins = (Pin(22), Pin(23))          # GPIO pins to use for UART TX and RX
uart_id = 1

# Target device address on the bus
slave_addr = 255

################################################################################

# Function to connect to Yeti Wi-Fi network
def connect_to_wifi(SSID,PASSWORD):

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    print("Connecting to Wi-Fi...")
    ntries=0
    while not wlan.isconnected() and ntries<10:
        ntries+=1
        print('...waiting...')
        time.sleep(1)
    if wlan.isconnected():
        print('Connected! Network configuration:', wlan.ifconfig())
    else:
        print('Unable to connect to ',SSID,
              ' - Use RECONNECT command to try again :-(')
    
    return wlan

################################################################################

# I/O functions for Yeti GZ
def EOR():
    print('<EOR>')

def send_get_request(URL,VERBOSITY=0):
    try:

        data={}
        if VERBOSITY>0:
            print(f"Sending GET request to {URL}")
        response = urequests.get(URL,timeout=5)

        #print('state=',json.dumps(self.state,indent=4))
        #print('Status=',resp.status_code)
        
        # Process the response payload
        if response.status_code == 200:
            if VERBOSITY>0:
                print("Success!")
            data = response.json()
            print('data=',data)
        else:
            print("Failed. Status Code:", response.status_code)
        
        # Always close your network connection socket
        response.close()

    except Exception as e:
        print("An error occurred:", e)

    return data


def set_state(URL,key,onoff):
    print('\n=========== SET STATE ==============\n')

    post={}
    payload = { key : onoff }
    try:
        resp = urequests.post(URL+'/state',headers=HEADER,json=payload)
        post = resp.json()
        print('Status=',resp.status_code)
        print('post=',post)

    except Exception as e:
        print("YETI CLIENT - SET STATE: An error occurred:", e)
    
    return post

################################################################################

# I/O functions for Renogy Wander
# Messages are molded to conform to corresponding Yeti messages
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

################################################################################
            
# Here we go ... connect to yeti wireless server ...
wlan=connect_to_wifi(SSID,PASSWORD)

# ... and to the Renergy RTU Master (Host)
host = ModbusRTUMaster(
    uart_id=uart_id,
    pins=rtu_pins,
    baudrate=9600,
    data_bits=8,
    stop_bits=1,
    parity=None
)

################################################################################
            
# Infinite loop to service requests from data aggregator
while True:
    cmd0=input("? ")
    cmd=cmd0.upper()

    # Yeti-related commands
    if cmd=='ID':
        print('Solar Web Client v0.1 for Yeti GZ and Renogy Wander')
        EOR()

    elif cmd=='NET':
        if wlan.isconnected():
            print("Network configuration:", wlan.ifconfig())
        else:
            print('No network connection :-(')
        EOR()

    elif cmd=='RECONNECT':
        wlan=connect_to_wifi(SSID,PASSWORD)
        EOR()

    elif cmd=='SYSINFO':
        data=send_get_request(URL+"/sysinfo")
        EOR()
        
    elif cmd=='STATE':
        data=send_get_request(URL+"/state")
        EOR()
        
    elif cmd[0:4]=='SET ':
        a=cmd0.split(' ')
        key=a[1]
        status=a[2]
        set_state(URL,key,status)
        EOR()
    
    # Renogy-related commands - need to add SET command (e.g. turn on/off "street light" load)
    elif cmd=='RENINFO':
        data=get_reninfo()
        EOR()

    elif cmd=='RENSTATE':
        data=get_renstate()
        EOR()
        
    else:
        print('Unrecognized cmd=',cmd)
        EOR()

    