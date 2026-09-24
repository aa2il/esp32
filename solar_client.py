################################################################################
#
# renogy_client.py - Rev 1.0
# Copyright (C) 2026 by Joseph B. Attili, joe DOT aa2il AT gmail DOT com
#
# This code combines the simple web clients for the Yeti GoalZero Battery
# and Renogy Charge Controller.
#
# Use Thonny to upload code to ESP32 - Interpreter is for ESP32 VROOM varient
#
# Need to upload credentials2.py and urequests2.py to ESP32.
# The easiest way to do this is to enable View->Files
# and then right-click on This Computer->....->credentials2.py -> Uploead To /
#
# The ideas behiind the yeti i/o are from:    https://github.com/tkdrob/goalzero
# The ideas behiind the renogy i/o are from:  https://github.com/wrybread/ESP32ArduinoRenogy
#
# These repositories also look relavant:
#      https://github.com/rosswarren/renogymodbus
#      https://github.com/cyrils/renogy-bt
#      https://github.com/thomasabbott/wanderer
#      https://platform.renogy.com/introduction/
#
# To Do:
#    - Trap crashes when wanderer is unplugged (e.g. to change battery)
#    - Test reading and setting battery type - seems to be 1-based instead of 0-based
#
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

BATTERY_TYPES=['?','OPEN','SEALED','GEL','LITHIUM','CUSTOM']

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

def uint16_to_bytes(registers,txt=None):
    if txt!=None:
        print(txt)
        print(registers,type(registers))

    if isinstance(registers,int):
        registers=[registers]
    elif isinstance(registers,tuple):
        registers=list(registers)
        
    if txt!=None:
        print(registers)
        
    b=[]
    for reg in registers:
        b.append( reg >> 8 )
        b.append( reg & 255 )
    return b

# I/O functions for Renogy Wander
# Messages are molded to conform to corresponding Yeti messages
def ren_get_info():    
    # Read info registers
    info_register_address = 0x00A
    num_info_registers = 17;
    info_registers = host.read_holding_registers(slave_addr,
                                                 info_register_address,
                                                 num_info_registers)
    
    # Convert 16-bit regs to bytes
    b = uint16_to_bytes(info_registers)
    #print('b=',b)
    
    model = ''.join(chr(i) for i in b[4:20])
    sw_version = ''.join(str(i) for i in b[20:24])
    hw_version = ''.join(str(i) for i in b[24:28])
    serial_no  = ''.join(str(i) for i in b[28:32])
    addr       = info_registers[16]      # This one is Read/Write
    print(addr)

    sysinfo={ 'model'        : model,
              'swVersion'    : sw_version, 
              'hwVersion'    : hw_version, 
              'serialNumber' : serial_no,
              'deviceAddr'   : addr,
              'maxVoltage'   : b[0],
              'ratedCurrent' : b[1],
              'ratedDischargeCurrent' : b[2],
              'productType'   : b[3]
             }
    
    print('data=',json.dumps(sysinfo))

    #raw_data=b[20:24]
    #print(raw_data)

    return sysinfo


def ren_get_state():
    
    # Read data registers
    data_register_address = 0x100
    num_data_registers = 10   # 35 - we only use the first 10 for now
    data_registers = host.read_holding_registers(slave_addr,
                                             data_register_address,
                                             num_data_registers)
    #print("Data Register:", data_registers)
    
    battery_soc = data_registers[0] 
    battery_voltage = data_registers[1] * .1
    battery_charging_amps = data_registers[2] * .1
    battery_charging_watts = battery_voltage * battery_charging_amps

    b = uint16_to_bytes(data_registers[3])
    controller_temperature = b[0]
    battery_temperature = b[1]
    #print('b=',b)
 
    load_voltage = data_registers[4] * .1
    load_current = data_registers[5] * .01
    load_watts = data_registers[6]

    solar_panel_voltage = data_registers[7]*.1
    solar_panel_amps = data_registers[8]*.01
    solar_panel_watts = data_registers[9] 

    if solar_panel_watts > load_watts:
        isCharging=1
    else:
        isCharging=0
        
    # There is a bunch more info available but I think this satisfies most of what I need for now
    # except for the following
    
    # Read load and charging state
    reg = host.read_holding_registers(slave_addr,0x0120,1)
    b = uint16_to_bytes(reg)
    load_on_off = ( b[0] & 0x80 ) >> 7
    load_brightness = b[0] & 0xef
    charging_state = b[1]
    
    # Might be useful to read fault/error info also
    
    # Some values are stored in EEPROM.  There are many of these
    # but we'll only read the ones we're interested in for now
    eeprom = host.read_holding_registers(slave_addr,0xe001,4)
    b = uint16_to_bytes(eeprom)   # ,'eeprom')
    #print('ee=',eeprom,b)
    
    dimming          = eeprom[0]
    battery_capacity = eeprom[1]
    #print('dim=',dimming,battery_capacity)
    
    sys_voltage = b[4]
    rec_voltage = b[5]
    #print('volts=',sys_voltage,rec_voltage)
    
    battery_type = BATTERY_TYPES[ eeprom[3] ]
    #print('bt=',battery_type)
           
    state={ 'volts'           : battery_voltage,
            'socPercent'      : battery_soc,
            'wattsIn'         : solar_panel_watts,
            'wattsOut'        : load_watts,
            'isCharging'      : isCharging,
            'chargingState'   : charging_state,
            'temperature'     : controller_temperature,
            'loadVoltage'     : load_voltage,
            'loadCurrent'     : load_current,
            'loadBrightness'  : load_brightness,
            'dimming'         : dimming,
            'sysVoltage'      : sys_voltage,
            'recVoltage'      : rec_voltage,
            'batteryType'     : battery_type,
            'batteryCapacity' : battery_capacity,
            'v12PortStatus'   : load_on_off,
            'usbPortStatus'   : 0,
            'acPortStatus'    : 0}

    print('data=',json.dumps(state))

    return state


def ren_set_state(key,val,VERBOSITY=0):

    if VERBOSITY>0:
        print('REN_SET_STATE: key=',key,'\tval=',val)

    if key=='deviceAddr':
        # 0x001A is device address
        addr=0x001A
    elif key=='v12PortStatus':
        # 0x010A is load on/off  - write only
        addr=0x010A
    elif key=='batteryType':
        # 0xE004 is battery type 
        addr=0xE004
        if val.upper() in BATTERY_TYPES:
            val=BATTERY_TYPES.index(val.upper())
        else:
            print('\n*** REN_SET_STATE *** Invalid battery type',key,val)
            return
    else:
        print('\n*** REN_SET_STATE *** Invalid key',key,val)

    if VERBOSITY>0:
        print('REN_SET_STATE: slave_addr=',slave_addr,'\taddr=',addr,'\tval=',val)
    adu = host.write_single_register(slave_addr,addr,int(val))
    if VERBOSITY>0:
        print('REN_SET_STATE: adu=',adu,'\tkey=',key,'\tval=',val)

    time.sleep(1)
    post=ren_get_state()
    print('post=',post)
    
    return post


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

# Devel and Test
if 0:
    #data=ren_get_info()
    state=ren_get_state()
    load = state['v12PortStatus']
    print('load on off=',load)

    adu=ren_set_state('v12PortStatus',1-load)
    time.sleep(1)
    state=ren_get_state()
    load = state['v12PortStatus']
    print('toggled load on off=',load)

# Infinite loop to service requests from data aggregator
Done=False
while not Done:
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
        data=ren_get_info()
        EOR()

    elif cmd=='RENSTATE':
        data=ren_get_state()
        EOR()
        
    elif cmd[0:7]=='RENSET ':
        #print('RENSET: cmd0=',cmd0,' ...')
        a=cmd0.split(' ')
        key=a[1]
        status=a[2]
        ren_set_state(key,status,VERBOSITY=0)
        EOR()
    
    elif cmd=='EXIT':
        Done=True
        EOR()
        
    else:
        print('Unrecognized cmd=',cmd)
        EOR()

    
