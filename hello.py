#! /usr/bin/python3

import sys
import os
#import psutil
#import shutil

# A very simple Hello World - Let's see what works with micropython - not much!

print("\nHello World! - Plain text, no gui\n")

# Let's see how the various system path discovery mechanisms work
"""
PYTHON_EXE=os.path.dirname(sys.executable)
print('Path to PYTHON EXECUTABLE   =\t',PYTHON_EXE)

HOME = os.path.expanduser('~/')
print('Path to HOME         =\t',HOME)
print('Path to FILE         =\t',__file__)

EXE_PATH=os.path.realpath(sys.executable)
print('Path to EXECUTABLE   =\t',EXE_PATH)
"""

CWD=os.getcwd()
print('Current Working Dir  =\t',CWD)

"""
os.chdir('..')
CWD2=os.getcwd()
print('Current Working Dir2 =\t',CWD2)
"""

# Get disk usage statistics
print('\nDisk Usage:')
"""
disk_stats = psutil.disk_usage('/')

print("Total: {:.2f} G".format(disk_stats.total / (2**30)))
print("Used: {:.2f} G".format(disk_stats.used / (2**30)))
print("Free: {:.2f} G".format(disk_stats.free / (2**30)))


# Fetching disk usage details
total, used, free = shutil.disk_usage("/")

print("\nTotal: {:.2f} G".format(total // (2**30)))
print("Used: {:.2f} G".format(used // (2**30)))
print("Free: {:.2f} G".format(free // (2**30)))
"""

statvfs = os.statvfs('/')
print('\nstatvfs=',statvfs)                                        

if 0:
    # Linux
    total=statvfs.f_frsize * statvfs.f_blocks     # Size of filesystem in bytes
    free=statvfs.f_frsize * statvfs.f_bfree      # Actual number of free bytes
    available=statvfs.f_frsize * statvfs.f_bavail     # Number of free bytes that ordinary users
                                        # are allowed to use (excl. reserved space
 
else:
    # Micropython
    total = statvfs[0] * statvfs[2]
    free = statvfs[0] * statvfs[3]
    used = total - free


print("\nTotal: {:.2f} K".format(total // (2**10)))
print("Used: {:.2f} K".format(used // (2**10)))
print("Free: {:.2f} K".format(free // (2**10)))
#print("Available: {:.2f} G".format(available // (2**30)))

# How about file IO? - Looks gooed
fp=open('junk.dat','a+')
fp.write('Hello World!\n')
fp.close()

                                        
