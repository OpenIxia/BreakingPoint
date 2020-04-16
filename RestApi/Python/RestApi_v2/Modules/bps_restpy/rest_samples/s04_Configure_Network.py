# Title:  Python Script made to edit the test network configuration.
# Actions:
#   1. Login to BPS box
#   2. Load a canned Network Configuration
#   3. Add a new network element type
#   4. Add elements and properties
#   5. Asign the network to a test model
#   6. Saving the test model


#================

import time, sys, os
# Add bps_restpy libpath *required if the library is not installed
libpath = os.path.abspath(__file__+"/../../..")
sys.path.insert(0,libpath)

from bps_restpy.bps import BPS,pp


########################################
# Demo script global variables
canned_network_name = 'BreakingPoint Switching'
new_network_name    = 's04_example_nn'
new_testmodel_name  = 's04_example_tm'
#bps system info
bps_system  = '<BPS_BOX_IP/HOSTNAME>'
bpsuser     = 'bps user'
bpspass     = 'bps pass'

slot_number = 1
port_list   = [0, 1]

########################################

# Login to BPS box
bps = BPS(bps_system, bpsuser, bpspass)
bps.login()

########################################
print("Example of network search: ")
net_search_result = bps.network.search("name:'%s'" % canned_network_name,\
 userid='',clazz='', sortorder='ascending', sort='name', limit=2, offset=0 )

print("Load the name of the first result list element: ", net_search_result[0]['name'])
bps.network.load(net_search_result[0]['name'])

print("Add IPv4_Router elements ")
vr1_id = 'virtual_router1'
vr2_id = 'virtual_router2'
bps.network.networkModel.ip_router.put({'id' : vr1_id})
bps.network.networkModel.ip_router.put({'id' : vr2_id})
print ("Getting default settings that will be changed for IPv4_Router:")
print (bps.network.networkModel.ip_router[vr1_id].get())
#Setting the 1st 2 interface ids to be used as containers for the vr elements
for interface in bps.network.networkModel.interface.get():
    interfaceid = interface['id']
    if interface['number'] == 1:
        interface_id1 = interfaceid
    elif interface['number'] == 2:
        interface_id2 = interfaceid
    else:
        print ('Deleting unused interface element : ', interfaceid)
        bps.network.networkModel.interface[interfaceid].delete()
bps.network.networkModel.ip_router[vr1_id].patch({'default_container': interface_id1,\
     'gateway_ip_address': '120.0.2.1', 'ip_address': '120.0.1.2','netmask': 16})
#Setting the 2nd interface as container
bps.network.networkModel.ip_router[vr2_id].patch({'default_container': interface_id2,\
     'gateway_ip_address': '120.0.1.2', 'ip_address': '120.0.2.1', 'netmask': 16})
print ('Finished adding IPv4_Router:')
for vr in bps.network.networkModel.ip_router.get():
    print (vr)

print "Moving corresponding ip_static_hosts to virtual Router and  deleting unused."
ip_ranges=bps.network.networkModel.ip_static_hosts.get()
for ip_range in ip_ranges:
    iprange_id = ip_range['id']
    if ip_range['default_container'] == interface_id1:
        print ('Moving entry %s to: %s' % (iprange_id,vr1_id) )
        bps.network.networkModel.ip_static_hosts[iprange_id].default_container.set(vr1_id)
    elif ip_range['default_container'] == interface_id2:
        print ('Moving entry %s to: %s' % (iprange_id,vr2_id) )
        bps.network.networkModel.ip_static_hosts[iprange_id].default_container.set(vr2_id)
    else:
        print ('Deleting unused static host entry  %s' % (iprange_id) )
        bps.network.networkModel.ip_static_hosts[iprange_id].delete()

print ("Saving network as : %s" % new_network_name)
bps.network.saveAs(new_network_name, force=True)

print ('Assigning the network in a existing testmodel')
bps.testmodel.load('AppSim')
bps.testmodel.network.set(new_network_name)
print ('Saving  testmodel as : %s' % new_testmodel_name)
bps.testmodel.saveAs(new_testmodel_name,force= True)

bps.logout()

