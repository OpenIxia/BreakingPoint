# Samole:  Python Script Sample To Create from Scratch a test based on a json definition.
# Actions:
#   1. Using the bps_helper parse and create the test
#   2. Reserve ports
#   3. Run the created test
#   4. Wait for the test to finish
#   5. Get test result
#   6. Get and print the Synopsis page from report
#   7. Unreserve ports
#   8. Logout


import os
import time
from bps_helper import BPS_Helper
from bps import BPS,pp


########################################
# Demo script global variables
########################################
# Demo script global variables
canned_test_name = 'AppSim'
#bps system info
# bps_system  = '<BPS_BOX_IP/HOSTNAME>'
# bpsuser     = 'bps user'
# bpspass     = 'bps pass'

file = os.path.join(os.path.dirname(__file__), 'http_https.json')
slot_number = 5
port_list   = [0, 4]

########################################


########################################
# Login to BPS box
bps = BPS(bps_system, bpsuser, bpspass)
bps.login()



# parse json and create test model
bps_create = BPS_Helper(bps_object=bps, json_data = file)
bps_create.create_superflow()
bps_create.create_application_profile()
bps_create.create_nso_testmodel()


print("Reserve Ports")
for p in port_list:
    bps.topology.reserve([{'slot': slot_number, 'port': p, 'group': 2}])


print("Running test: " + bps_create.test_name)
test_id_json = bps.testmodel.run(modelname=bps_create.test_name, group=2)
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
results = bps.reports.search(searchString=bps_create.test_name, limit=10, sort="endTime", sortorder="descending")
result  = results[0]
print ("%s execution duration %s ended with status: %s " % (result['name'], result['duration'], result['result']) )

#getting 3.4 Section: Synopsys Summary of Results from the Report
tabledata = bps.reports.getReportTable(runid=testid, sectionId="3.4")
pp(tabledata)

print ("Unreserving the ports")
for p in port_list:
    bps.topology.unreserve([{'slot': slot_number, 'port': p, 'group': 2}])

bps.logout()