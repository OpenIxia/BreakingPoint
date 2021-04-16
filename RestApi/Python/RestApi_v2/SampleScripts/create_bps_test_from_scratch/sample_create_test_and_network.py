# Title:  Python Script made to create a Test Model from scrach.
# Actions:
#   1. Login to BPS box
#   2. Create a new test
#   3. Add components (AppSim + RR)
#   4. Save test
#   5. Clone components then disable the RR components.
#   6. Reserve ports
#   7. Run test and wait a few seconds
#   8. Get stats
#   9. Delete test from database and try to search it again
#  10. Unreserve ports and logout.




import time, sys, os
# Add bps_restpy libpsth *required if the library is not installed
libpath = os.path.abspath(__file__+"/../../..")
sys.path.insert(0,libpath)

from bps_restpy.bps import BPS,pp



########################################
# Demo script global variables
appsim_component_name = "tempAppsim"
test_name             = "test_model_from_restpy"
new_network_name    = 'net_from_restpy'

#bps system info
# bps_system  = '<BPS_BOX_IP/HOSTNAME>'
# bpsuser     = 'bps user'
# bpspass     = 'bps pass'
bps_system  = '17.12.12.8'
bpsuser     = 'admin'
bpspass     = 'admin'


slot_number = 7
port_list   = [0, 4]

########################################


########################################
# Login to BPS box
bps = BPS(bps_system, bpsuser, bpspass)
bps.login()


##########Create a network neighbhourhood config as in s04_Configure_Network.py sample##############################

print("New empty network object")
bps.network.new()

print("Configure L2 interface settings")
inteface1_id = 'Interface 1'
inteface2_id = 'Interface 2'
bps.network.networkModel.interface.put({'id' : inteface1_id, 'number' : 1 , 'mac_address': '02:1A:C5:01:00:00', 'mtu': 1500, 'duplicate_mac_address': True, 'ignore_pause_frames': False})
bps.network.networkModel.interface.put({'id' : inteface2_id, 'number' : 2, 'mac_address': '02:1A:C7:02:00:00', 'mtu': 1500, 'duplicate_mac_address': False, 'ignore_pause_frames': False})

print("Add IPv4_Router elements ")
vr1_id = 'virtual_router1'
vr2_id = 'virtual_router2'
bps.network.networkModel.ip_router.put({'id' : vr1_id})
bps.network.networkModel.ip_router.put({'id' : vr2_id})
print ("Getting default settings that will be changed for IPv4_Router:")
print (bps.network.networkModel.ip_router[vr1_id].get())
#Setting the 1st 2 interface ids to be used as containers for the vr elements
bps.network.networkModel.ip_router[vr1_id].patch({'default_container': inteface1_id,\
     'gateway_ip_address': '120.0.2.1', 'ip_address': '120.0.1.2','netmask': 16})
#Setting the 2nd interface as container
bps.network.networkModel.ip_router[vr2_id].patch({'default_container': inteface2_id,\
     'gateway_ip_address': '120.0.1.2', 'ip_address': '120.0.2.1', 'netmask': 16})
print ('Finished adding IPv4_Router:')
for vr in bps.network.networkModel.ip_router.get():
    print (vr)

print ("Creating corresponding ip_static_hosts and put the behind a virtuel rouuter above.")
public_hosts_tag = 'public'
private_hosts_tag = 'private'
#bps.network.networkModel.ip_static_hosts.put('count': 65534, u'default_container': vr1_id, u'enable_stats': False, u'gateway_ip_address': u'1.0.0.1', u'id': u'Static Hosts i10_default', u'ip_address': u'1.10.0.1', u'ip_selection_type': u'random_ip', u'netmask': 8, u'proxy': False, u'psn_netmask': 8, u'tags': u'i10_default'})
bps.network.networkModel.ip_static_hosts.put({
    'id': 'Public Static Hosts VR1',\
    'default_container' : vr1_id, \
    'gateway_ip_address': '23.50.0.1',\
    'ip_address': '23.50.0.10',\
    'netmask': 16, \
    'count': 1000, \
    'proxy': True, 
    'tags': public_hosts_tag \
    })

bps.network.networkModel.ip_static_hosts.put({
    'id': 'Private Static Hosts VR2',\
    'default_container' : vr2_id, \
    'gateway_ip_address': '23.55.0.1',\
    'ip_address': '23.55.0.10',\
    'netmask': 16, \
    'count': 1000, \
    'proxy': True, 
    'tags': private_hosts_tag \
    })

print ("Saving network as : %s" % new_network_name)
bps.network.saveAs(new_network_name, force=True)


##########Create a Test as in s07_TestModel_Run.py sample##############################
print( "Create a new test: ")
bps.testmodel.new()

print( "Add components to the test.")
bps.testmodel.add(name=appsim_component_name, type="appsim", active=True, component="appsim")

comp_Name = bps.testmodel.component["appsim_1"].label.get()
print( "Component Name is: %s" % comp_Name)

########################################
#asign the previously saved network to the  test
bps.testmodel.network.set(new_network_name)
#delete all component tags
oldNetworkHostTags = bps.testmodel.component["appsim_1"].tags.get()
for tag in oldNetworkHostTags:
    oldtag= tag['id']
    print ('Removing default component old network tag : %s ' % oldtag)
    bps.testmodel.component["appsim_1"].tags[oldtag].delete()
print ('Adding new component network tag : %s ' % oldtag)
bps.testmodel.component["appsim_1"].tags.put({'domainId': None, 'id': public_hosts_tag, 'type': 'client'})
bps.testmodel.component["appsim_1"].tags.put({'domainId': None, 'id': private_hosts_tag, 'type': 'server'})
########################################
print( "Save test:")
bps.testmodel.saveAs(test_name, force=True)

########################################
print( "Reserve Ports")
for p in port_list:
    bps.topology.reserve([{'slot': slot_number, 'port': p, 'group': 1}])


########################################
print( "Run test and Get Stats:")
test_id_json = bps.testmodel.run(modelname=test_name, group=1)
run_id = test_id_json["runid"]
print( "Test Run Id: %s"%run_id)

print( "~Wait for test to begin initialization.")
runningTests = bps.topology.runningTest['TEST-%s'%run_id].get()
while (runningTests["initProgress"] == None):
    runningTests = bps.topology.runningTest['TEST-%s'%run_id].get()
    print( "...")
    time.sleep(1)

print( "~Wait for the initialization process ")
init_progress = bps.topology.runningTest['TEST-%s'%run_id].initProgress.get()
while( int(init_progress) <= 100 and runningTests["progress"] == None):
    init_progress = bps.topology.runningTest['TEST-%s'%run_id].initProgress.get()
    runningTests = bps.topology.runningTest['TEST-%s'%run_id].get()
    time.sleep(1)
    print( "Initialization progress:   %s%s" % (init_progress, '%'))

print( "~Test is running. Get stats at every 2 seconds.")
while True:
    run_state = bps.topology.runningTest['TEST-%s'%run_id].get()
    try:
        state = run_state['completed']
    except KeyError: # The key does not exist in a completed test-> should be treated as completed.
        state = True
    if state:
        break
    else:
        print("Time Elapsed: " + str(run_state['runtime']))
        if run_state['progress'] is None:
            time.sleep(2)
        continue


########################################
# print( "Delete Test")
# bps.testmodel.delete(name=test_name)
# test = bps.testmodel.search(searchString=test_name, limit=2, sort="name", sortorder="ascending")
# print( "Search result after delete")
# print( test)

########################################
print( "Unreserve ports")
time.sleep(3)
for p in port_list:
    bps.topology.unreserve([{'slot': slot_number, 'port': p}])

########################################
print( "Session logout")
bps.logout()
