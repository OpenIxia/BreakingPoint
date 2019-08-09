"""
createNewTest.py

Description
   Create a Test Model from scrach.

What this script does:
   - Login to BPS box
   - Create a new test
   - Add components (AppSim)
   - Save test
   - Clone component
   - Reserve ports
   - Run test and wait a few seconds
   - Get stats
   - Delete test from database and try to search it again
   - Unreserve ports and logout.

Requirements:
   - Python requests module
   - BPS bpsRestPy.py module
   - BPS minimum version 9.0

Support:
   - Python 2 and Python 3
"""

# Import BPSv2 libs
import time, sys, os

sys.path.insert(0, (os.path.dirname(os.path.abspath(__file__)).replace('SampleScripts', 'Modules')))
from bpsRestPy import BPS, pp


########################################
# Demo script global variables
chassis_ip = "10.36.18.44"
appsim_component_name = "tempAppsim"
test_name             = "Test_Model"

slot_number = 1
port_list   = [0, 1]
runTime     = 10

try:

    ########################################
    # Login to BPS box
    bps_session = BPS(chassis_ip, 'admin', 'admin')
    bps_session.login()

    ########################################
    print("Create a new test: ")
    bps_session.testmodel.new()

    print("Add components to the test.")
    bps_session.testmodel.add(name=appsim_component_name, type="appsim", active=True, component="appsim")

    comp_Name = bps_session.testmodel.component["appsim_1"].label.get()
    print("Component Name is: %s" % comp_Name)

    bps_session.testmodel.save(name=test_name, force=True)
    test = bps_session.testmodel.search(searchString=test_name, limit=2, sort="name", sortorder="ascending")
    print("Search result after save: ")
    print(test)

    print("Clone the components: ")
    bps_session.testmodel.clone("appsim_1", 'appsim', True)

    print("Change name for the cloned componets:")
    bps_session.testmodel.component["appsim_2"].set({"label":"App2"})

    print("Components Status: ")
    pp(bps_session.testmodel.component.get())


    ########################################
    print("Save test:")
    bps_session.testmodel.save()

    ########################################
    print("Reserve Ports")
    for p in port_list:
        bps_session.topology.reserve([{'slot': slot_number, 'port': p, 'group': 1}])


    ########################################
    print("Run test and Get Stats:")
    test_id_json = bps_session.testmodel.run(modelname=test_name, group=1)
    run_id = test_id_json['runid']
    print("Test Run Id: %s" % run_id)

    print("~Wait %s seconds" % runTime)
    time.sleep(runTime)

    progress = bps_session.topology.runningTest['TEST-%s'%run_id].progress.get()
    while(type(progress) != dict and int(progress) <= 100):
        pp(bps_session.testmodel.realTimeStats(int(run_id), "summary", -1))
        progress = bps_session.topology.runningTest['TEST-%s'%run_id].progress.get()
        time.sleep(runTime)


    ########################################
    print("Delete Test")
    bps_session.testmodel.delete(name=test_name)
    test = bps_session.testmodel.search(searchString=test_name, limit=2, sort="name", sortorder="ascending")
    print("Search result after delete")
    print(test)

    ########################################
    print("Unreserve ports")
    for p in port_list:
        bps_session.topology.unreserve([{'slot': slot_number, 'port': p}])

    ########################################
    print("Session logout")
    bps_session.logout()

except Exception as errMsg:
    print('\nException:', errMsg)
