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


# ================

########################################
import time
import sys
import os
import logging

# Add bps_restpy libpath *required if the library is not installed
libpath = os.path.abspath(__file__+"/../../..")
sys.path.insert(0, libpath)

from bps_restpy.bps import BPS, pp

########################################


########################################
# Demo script global variables
########################################
# Demo script global variables
canned_test_name = 'AppSim'
# bps system info
# bps_system  = '<BPS_BOX_IP/HOSTNAME>'
# bpsuser     = 'bps user'
# bpspass     = 'bps pass'
bps_system  = '10.36.83.74'
bpsuser     = 'admin'
bpspass     = 'admin'

slot_number = 4
port_list   = [0, 1]
########################################


########################################

script_log = logging.getLogger(__name__)

########################################
# Login to BPS box
bps = BPS(bps_system, bpsuser, bpspass)
#disable module level output but still leave script level logs
bps.disablePrints(True)
script_log.setLevel(logging.INFO)
bps.login()
########################################
script_log.info("Load a canned test: ")
bps.testmodel.load(canned_test_name)

########################################
script_log.info("Reserve Ports")
for p in port_list:
    bps.topology.reserve([{'slot': slot_number, 'port': p, 'group': 2}])

########################################
script_log.info("Run test and Get Stats:")
test_id_json = bps.testmodel.run(modelname=canned_test_name, group=2)
testid = str( test_id_json["runid"] )
run_id = 'TEST-' + testid
script_log.info("Test Run Id: %s"%run_id)

# enable bps_restpy Info logging
logger = logging.getLogger('bps_restpy')
logger.setLevel(logging.INFO)

#get the ids for all tests running on the chassis
runningTests_Ids = [test['id'] for  test in bps.topology.runningTest.get()] 
#wait while the test is still running
while run_id in runningTests_Ids:
    run_state = bps.topology.runningTest[run_id].get()
    #print progress if test started
    try: script_log.info('progress: %s%% , runtime %ss' % (run_state['progress'], run_state['runtime'] ))
    except: script_log.info("Starting...")
    time.sleep(2)
    #update the current running tests
    runningTests_Ids = [test['id'] for  test in bps.topology.runningTest.get()] 

script_log.info("~The test finished the execution.")
results = bps.reports.search(searchString=canned_test_name, limit=10, sort="endTime", sortorder="descending")
result = results[0]
script_log.info("%s execution duration %s ended with status: %s " % (result['name'], result['duration'], result['result']) )

#getting 3.4 Section: Synopsys Summary of Results from the Report
tabledata = bps.reports.getReportTable(runid=testid, sectionId="3.4")
pp(tabledata)


script_log.info("Unreserving the ports")
for p in port_list:
    bps.topology.unreserve([{'slot': slot_number, 'port': p, 'group': 2}])

bps.logout()
script_log.info("-----Done-----")
