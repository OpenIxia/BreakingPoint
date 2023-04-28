# Title:  Change modes on BPS PerfectStorm and CloudStorm Cards.
# Date:   Nov 2019
# Actions:
#   1. Get some card/port informations
#   2. xample on how to change mode or speed and wait for the status

# Install bps_restpy with pip or download the library from git
########################################
import time, sys, os
# Add bps_restpy libpath *required if the library is not installed
libpath = os.path.abspath(__file__+"/../../..")
sys.path.insert(0,libpath)

from bps_restpy.bps import BPS,pp

########################################
import re

# Demo script global variables

#bps system info
# bps_system  = '<BPS_BOX_IP/HOSTNAME>'
# bpsuser     = 'bps user'
# bpspass     = 'bps pass'
bps_system  = '10.36.66.31'
bpsuser     = 'admin'
bpspass     = 'admin'

slot_number = 6
port_list   = [0, 1]
########################################
# utility procedure to wait for long operations like card change mode, reboot, speed change
# implicit values are to wait for (key)progress to be (keyvalue)100% checking every 2 s with a 1000s timeout
# r is the return value of the operation call
# bps is the connection object

def  waitForComplete(bps, r, key="progress", keyValue=100, timeout=1000, rate=2):
    r = bps.session.get(r['url']) 
    r = r.json()
    print (key, ": ",  r[key])
    print ("type :", r['type'])
    print ("state :", r['state'])
    while not r[key] == keyValue:
        time.sleep(rate)
        r = bps.session.get(r['url'])
        r = r.json()
        print (key, ": ",  r[key])
        print ("type :", r['type'])
        print ("state :", r['state'])

########################################
# Login to BPS box
bps = BPS(bps_system, bpsuser, bpspass)
bps.login()

print ("Get the a description of the entire chassis:")
chassis = bps.topology.get()
pp(chassis)

print ("Get the details on one slot from the chassis:")
slot = bps.topology.slot[slot_number].get()

# in case the slot is not ready- wait for ports to become availlable
retry = 10
while retry>0 and not slot['port']:
    retry -=1
    print ("The slot " + str(slot_number) + " has no ports - wait 20s (retry left %s)" % retry)
    time.sleep(20)
    slot = bps.topology.slot[slot_number].get()

pp(slot)

print ("Get the details on one port from the chassis:")
port_id_to_querry = port_list[0]
port = bps.topology.slot[slot_number].port[port_id_to_querry].get()
pp(port)

print ("Get the list of tests in execution:")
runningTests = bps.topology.runningTest.get()
pp(runningTests)

print ("The slot/port details.")
slot_operation_mode = slot['mode']
slot_model_type = slot['model']
print ("Slot " + str(slot_number) +\
     " type: " + slot_model_type + \
     " current operation mode: " + slot_operation_mode)

port_speed = port['speed']
port_link_status = port['link']
port_reservedby_status = port['reservedBy']
print ("Slot " + str(slot_number) +\
    " port " + str(port_id_to_querry) +\
     " speed: " + str(port_speed) + \
     " link status: " + port_link_status +\
     " reservedby: " + port_reservedby_status + '(Empty if not reserved)')


print ('The setCardMode, setCardSpeed, setCardSpeed can be exercised. See the help in restapi browser for more options')

print ('setCardMode to BPS mode--')
# 10(BPS-L23), 7(BPS L4-7), 3(IxLoad), 11(BPS QT L2-3), 12(BPS QT L4-7)
r = bps.topology.setCardMode(board=slot_number, mode=10)
waitForComplete(bps, r)

# in case the slot is not ready- wait for ports to become availlable
retry = 10
while retry>0 and not slot['port']:
    retry -=1
    print ("The slot " + str(slot_number) + " has no ports - wait 20s (retry left %s)" % retry)
    time.sleep(20)
    slot = bps.topology.slot[slot_number].get()

print ('setCardFanout to BPS mode--')
# The fan type represented by an integer id. For CloudStorm: 0(100G), 1(40G), 2(25G), 3(10G), 4(50G). For PerfectStorm 40G: 0(40G), 1(10G). For PerfectStorm 100G: 0(100G), 1(40G), 2(10G)
r = bps.topology.setCardFanout(board=slot_number, fanid=1)
waitForComplete(bps, r)

bps.logout()
