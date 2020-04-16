# Title:  Python Script made to create a Test Model from scratch.
# Date:   April 2019
# Author: Maria Turcu
# Actions:
#   1. Login to BPS box
#   2. Create a new superflow from scratch
#   3. Add flow and actions to the new created superflow
#   4. Save the superflow
#   5. Edit parameters inside an action
#   6. Add the created superflow to a Application Mix
#   7. Run a test with the AppMix and get the result.


# Import BPSv2 python library from outside the folder with samples.

########################################
import time, sys, os
# Add bps_restpy libpath *required if the library is not installed
libpath = os.path.abspath(__file__+"/../../..")
sys.path.insert(0,libpath)

from bps_restpy.bps import BPS,pp


########################################
# Demo script global variables
# Demo script global variables
new_superflow_name  =  "CreatedSuperFlow"
new_appprofile_name =  "CreatedAppProfile"
new_testmodel_name  =  "TestModel_Edited"

#bps system info
bps_system  = '<BPS_BOX_IP/HOSTNAME>'
bpsuser     = 'bps user'
bpspass     = 'bps pass'

slot_number = 1
port_list   = [0, 1]

########################################


########################################
# Login to BPS box
bps = BPS(bps_system, bpsuser, bpspass)
bps.login()


# # # SUPERFLOW
########################################
print("Create a SuperFlow from scratch with no name.")
bps.superflow.new()

print("Add host a new host besides the defaults Server/Client")
newhost = 'Auth Server'
bps.superflow.hosts.put({'id' : newhost})
bps.superflow.hosts[newhost].patch({u'iface': u'origin', u'hostname': u'client%n.example.int'})
bps.superflow.hosts[newhost].ip.type.set('random')
print (bps.superflow.hosts[newhost].get())


print("Get all available canned flows that have 'plus' in the name.")
for flow in bps.superflow.flows.getCannedFlows():
    if 'plus' in flow['name']:
        print ("name: %s, label: %s" % (flow['name'], flow['label']) )

print("Add a flow")
bps.superflow.addFlow(
    {"name": "plus050", "to": "Server", "from": "Client"})

print("Add action 1")
bps.superflow.addAction(flowid = 1, type = "tls_accept", actionid = 1, source = "server")


print("Save the current working superflow under a new name.")
bps.superflow.saveAs(new_superflow_name, True)

print("Add action 2")
bps.superflow.addAction(flowid = 1, type = "tls_start", actionid = 2, source ="client")

print("Add action 3")
bps.superflow.addAction(1, "register_request", 3, "client")

print("Save the superflow under the same name")
bps.superflow.saveAs(new_superflow_name, force = True)

print("Remove action 3")
bps.superflow.removeAction(3)

print("Save superflow")
bps.superflow.save()

print("Change parameters inside action 2")
bps.superflow.actions["2"].set({"tls_handshake_timeout": 20})
bps.superflow.actions["1"].set({"tls_max_version": "TLS_VERSION_3_1"})
print("Change the cipher to RSA_WITH_RC4_128_MD5. The real value can be read from the tool tip inside UI.")
bps.superflow.actions["1"].set({"tls_max_version": "TLS_VERSION_3_1"})

print("Save superflow")
bps.superflow.save()

print("Gets params inside action 2")
action_dict_param = bps.superflow.actions["2"].get()
timeout = action_dict_param["tls_handshake_timeout"]
decryptMode = action_dict_param["tls_decrypt_mode"]
print("Handshake timeout: %s  and the decrypt mode: %s" %
      (timeout, decryptMode))

print("Save superflow")
bps.superflow.save()

print "Create a new appProfile"
bps.appProfile.new()
bps.appProfile.name.set(new_appprofile_name)


print ('Preparing to add: %s' % new_superflow_name)
superflows_to_use = [{"superflow": new_superflow_name, "weight": 2 }]
print ("Find 2 more canned SIP flows")
sip_canned_flows = bps.superflow.search('sip',limit = 100, sort='name', sortorder = 'ascending')
print ('Preparing to add: ', sip_canned_flows[0]['name'])
superflows_to_use.append({"superflow": sip_canned_flows[0]['name'], "weight": 1 })
print ('Preparing to add: ', sip_canned_flows[1]['name'])
superflows_to_use.append({"superflow": sip_canned_flows[1]['name'], "weight": 2 })
print ('Adding superflows to approfile: %s' % new_appprofile_name)
bps.appProfile.add(superflows_to_use)
bps.appProfile.saveAs(new_appprofile_name, force = True)

print ("Create a new testmodel to use the newly created aplication mix")
bps.testmodel.new()
print('Adding an application simulator component ')
bps.testmodel.add(name='my_appsim', type='appsim', active=True, component='appsim')
print('Configure with the created application profile ')
pset={"profile": new_appprofile_name}
#get the id of the 1st component
cmpid = bps.testmodel.component.get()[0]['id']
#set the profile on the component
bps.testmodel.component[cmpid].patch(pset)
bps.testmodel.saveAs(new_testmodel_name, force = True)

####
########################################
print("Reserve Ports")
for p in port_list:
    bps.topology.reserve([{'slot': slot_number, 'port': p, 'group': 2}])


########################################
print("Run test and Get Progress:")
test_id_json = bps.testmodel.run(modelname=new_testmodel_name, group=2)
testid = str( test_id_json["runid"] )
run_id = 'TEST-' + testid
print("Test Run Id: %s"%run_id)

#get the ids for all tests running on the chassis
runningTests_Ids = [test['id'] for  test in bps.topology.runningTest.get()] 
#wait while the test is still running
while run_id in runningTests_Ids:
     run_state =  bps.topology.runningTest[run_id].get()
     #print progress if test started
     try: print ('progress: %s%% , runtime %ss' % (run_state['progress'], run_state['runtime'] ))
     except: print ("Starting...")
     time.sleep(2)
     #update the current running tests
     runningTests_Ids = [test['id'] for  test in bps.topology.runningTest.get()] 

print("~The test finished the execution.")
results = bps.reports.search(searchString=new_testmodel_name, limit=10, sort="endTime", sortorder="descending")
result  = results[0]
print ("%s execution duration %s ended with status: %s " % (result['name'], result['duration'], result['result']) )

#getting 3.4 Section: Synopsis Summary of Results from the Report
tabledata = bps.reports.getReportTable(runid=testid, sectionId="3.4")
pp(tabledata)

print ("Unreserving the ports")
for p in port_list:
    bps.topology.unreserve([{'slot': slot_number, 'port': p, 'group': 2}])

bps.logout()





