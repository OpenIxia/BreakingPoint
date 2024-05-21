"""
Title:  Python Script Sample To Run a layer2 Test.
Actions:
    1.  Login to BPS box
    2.  Create new test
    3.  Add components
    4.  Set component values
    5.  Clone components
    6.  Reserve ports and resources
    7.  Run Test
    8.  Get live stats
    9.  Wait for the test to finish
    10. Get test result
    11. Get and print the Synopsis page from report
    12. Unreserve ports resources
    13. Logout
"""


########################################

# Necessary Imports
import time
import sys
import os
# Add bps_restpy libpath *required if the library is not installed
libpath = os.path.abspath(__file__+"/../../..")
sys.path.insert(0, libpath)
# pylint: disable=wrong-import-position
# pylint: disable=import-error
from bps_restpy.bps import BPS, pp  # noqa: E402

########################################


########################################

# Demo script global variables
TEST_NAME = 's11_bitblaster'

# BPS System Info
BPS_SYSTEM = '<BPS_BOX_IP/HOSTNAME>'
BPSUSER = 'bps user'
BPSPASS = 'bps pass'

SLOT_NUMBER = 1
GROUP_NUMBER = 2
PORT_LIST = ["3.0", "4.0"]

########################################


########################################

# Login to BPS box:
bps = BPS(BPS_SYSTEM, BPSUSER, BPSPASS)
bps.login()

########################################


########################################

# Create a new test:
bps.testmodel.new()

########################################


########################################

# Add a Component to the test:
value = bps.testmodel.add(
    name='bitblaster_1', type="layer2", active=True, component="bitblaster")

# Modify Component Values:
# Set Frame size to 64
bps.testmodel.component['bitblaster_1'].sizeDist.set({'min': '64'})
bps.testmodel.component['bitblaster_1'].payload.set({'type': 'ones'})
# Set test duration to 2 minutes & 30 seconds
bps.testmodel.component['bitblaster_1'].duration.set(
    {'durationTime': '00:02:30'})
# Send 100gbps
bps.testmodel.component['bitblaster_1'].rateDist.set({'min': '100000'})
# Update Description
bps.testmodel.component['bitblaster_1'].set(
    {'description': 'Sample API Script for Bit Blaster'})

# Duplicate or "Clone" Component
bps.testmodel.clone(template='bitblaster_1', type='layer2', active=True)

# Change name for the cloned componets:
bps.testmodel.component["bitblaster_2"].set({"label": "BB2"})

########################################


########################################

# Check Components:
print("Components Status: ")
pp(bps.testmodel.component.get())

# Save Test:
bps.testmodel.save(name=TEST_NAME, force=True)

########################################


########################################

# Reserve Resources:
for p in PORT_LIST:
    bps.topology.reserve(
        [{'group': GROUP_NUMBER, 'slot': SLOT_NUMBER, 'port': p, 'capture': True}], False)


print("Reserve L23 resources...")
for r in range(16):
    bps.topology.reserveResource(group = GROUP_NUMBER, resourceId = r, resourceType = "l23")
########################################


########################################

# Run test and Get Stats:
test_id_json = bps.testmodel.run(modelname=TEST_NAME, group=GROUP_NUMBER)
TEST_ID = str(test_id_json["runid"])
RUN_ID = 'TEST-' + TEST_ID
print(f"Test Run Id: {RUN_ID}")

# get the ids for all tests running on the chassis
runningTests_Ids = [test['id'] for test in bps.topology.runningTest.get()]

# wait while the test is still running
dot_count = 1
while RUN_ID in runningTests_Ids:
    data = bps.testmodel.realTimeStats(
        test_id_json["runid"], "summary", -1)
    if data:
        print(f"Time Passed: {data['time']}s")
        # Print each Real Time Statistic
        for counter, data_point in enumerate(data['values'].items()):
            print(end='\n' if counter % 3 == 0 else '')
            print(
                f"| {data_point[0][:25]:25s}: {str(data_point[1])[:12]:12s} ", end='')
            progress = int(data['progress'])
        print(
            f"\nProgress: |{('#'*progress):100s}| {int(data['progress'])}%")
    else:
        print(f"Starting{'.'*dot_count}     ", end='\r')
        dot_count = dot_count+1 if dot_count < 3 else 1
    time.sleep(.25)
    # update the current running tests
    runningTests_Ids = [test['id'] for test in bps.topology.runningTest.get()]
print("~The test finished the execution.")

########################################


########################################

# Print Final Data:
# Find results from history
results = bps.reports.search(
    searchString=TEST_NAME, limit=10, sort="endTime", sortorder="descending")
result = results[0]
print(f"{result['name']}:")
print(f"\texecution duration: {result['duration']}")
print(f"\tended with status: {result['result']}")
# getting 3.4 Section: Synopsys Summary of Results from the Report
tabledata = bps.reports.getReportTable(runid=TEST_ID, sectionId="3.4")
for column in enumerate(tabledata):
    print(f"{list(tabledata[column[0]].keys())[0]:15s}", end='')
for row in range(len(list(tabledata[0].values())[0])):
    print(f"\n{'-'*45}")
    for column in enumerate(tabledata):
        print(f"{list(tabledata[column[0]].values())[0][row]:15s}", end='')


########################################


########################################

# Unreserving the resources:
for p in PORT_LIST:
    bps.topology.unreserve(
        [{'slot': SLOT_NUMBER, 'port': p}])
print("\nReleasing resources...")
for r in range(16):
    bps.topology.releaseResource(group = GROUP_NUMBER, resourceId = r, resourceType = "l23")
########################################


########################################

bps.logout()
print("\nLogged out.")

########################################
