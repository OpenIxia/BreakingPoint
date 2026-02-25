# Title:  Python Script Sample To Run a Canned Test.
# Actions:
#   1. Login to BPS box
#   2. Reserve ports
#   3. Load a test from the box and start the run
#   4. Wait for the test to finish
#   5. Get test result
#   6. Get and print the Synopsis page from report
#   7. Unreserve ports
#   8. Logout


#================

########################################
import time, sys, os
# Add bps_restpy libpath *required if the library is not installed
libpath = os.path.abspath(__file__+"/../../..")
sys.path.insert(0,libpath)

from bps_restpy.bps import BPS,pp

########################################

########################################
# Demo script global variables
########################################
# Demo script global variables
canned_test_name = 'AppSim'
#bps system info
bps_system  = '<BPS_BOX_IP/HOSTNAME>'
bpsuser     = 'bps user'
bpspass     = 'bps pass'

slot_number = 3
port_list   = [0, 1]

########################################


########################################
# Login to BPS box
bps = BPS(bps_system, bpsuser, bpspass)
bps.login()


########################################
print("Load a canned test: ")
bps.testmodel.load(canned_test_name)

########################################
print("Fanout the ports")
fanout_result = bps.topology.getFanoutModes(slot_number)

'''
The fan type represented by an integer id. Get card specific fanout modes by calling 'topology.getFanoutModes(<card_id>)'. 
For CloudStorm: 0(100G), 1(40G), 2(25G), 3(10G), 4(50G). For PerfectStorm 40G: 0(40G), 1(10G). 
For PerfectStorm 100G: 0(100G), 1(40G), 2(10G)
'''

print("The list of Fanout options:")
for li in fanout_result["fanouts"]:
    print("The ID {0} is referring to the fanout mode {1}".format(li["id"], li["name"]))
#Specify the fanout mode here
fanid = 2
print("Fanning out the ports...")
#Grabing the status URL and polling the latest fan out status progress
pollUrl = bps.topology.setCardFanout(slot_number,fanid)["url"]
response = bps.session.get(url=pollUrl, headers={'content-type': 'application/json'}, verify=False)
if(response.status_code in [200, 204]):
    print("Fan out state {0}: {1}".format(response.json()["state"],response.json()["message"]), end="\r")      
else:
    bps.logout()
    raise Exception("Error: ", response.json())
while response.json()["state"] == "IN_PROGRESS":
    response = bps.session.get(url=pollUrl, headers={'content-type': 'application/json'}, verify=False)
    if(response.status_code in [200, 204]):
        print("Fan out state {0}: {1}".format(response.json()["state"],response.json()["message"]), end="\r")        
    else:
        bps.logout()
        raise Exception("Error: ", response.json())
    time.sleep(2)

if response.json()["state"] == "SUCCESS":
    print("Fanout completed!")
    time.sleep(3)
    print("\nInitializing ports..")
    time.sleep(3)
else:
    bps.logout()
    raise Exception("Something wrong while fanning out ports!")
    

#######################################
print("Reserve Ports")
for p in port_list:
    bps.topology.reserve([{'slot': slot_number, 'port': p, 'group': 2}])


########################################
print("Run test and Get Stats:")
test_id_json = bps.testmodel.run(modelname=canned_test_name, group=2)
testid = str( test_id_json["runid"] )
run_id = 'TEST-' + testid
print("Test Run Id: %s"%run_id)

#get the ids for all tests running on the chassis
runningTests_Ids = [test['id'] for  test in bps.topology.runningTest.get()] 
#wait while the test is still running
while run_id in runningTests_Ids:
     run_state =  bps.topology.runningTest[run_id].get()
     #print progress if test started
     try: print ('progress: %s%% , runtime %ss' % (run_state['progress'], run_state['runtime'] ), end="\r")
     except: print ("\nStarting...")
     time.sleep(2)
     #update the current running tests
     runningTests_Ids = [test['id'] for  test in bps.topology.runningTest.get()] 

print("~The test finished the execution.")
results = bps.reports.search(searchString=canned_test_name, limit=10, sort="endTime", sortorder="descending")
result  = results[0]
print ("%s execution duration %s ended with status: %s " % (result['name'], result['duration'], result['result']) )

#getting 3.4 Section: Synopsys Summary of Results from the Report
tabledata = bps.reports.getReportTable(runid=testid, sectionId="3.4")
pp(tabledata)

print ("Unreserving the ports")
for p in port_list:
    bps.topology.unreserve([{'slot': slot_number, 'port': p, 'group': 2}])

bps.logout()

