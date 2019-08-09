"""
loadConfigs.py

Description:
   Sample script to show BPS RESTv2 common use case

What this script does:
   - Login to BPS box
   - Import a test and search into the database after it
   - Load the test and check the name
   - Import a network config and search for it into the database
   - Load the network config and make a few changes inside it
   - Save the changes into a new network config.
   - Change the network from the loaded test model.
   - Save the test model as a new config
   - Reserve ports
   - Run test then cancel it after a few seconds
   - Get stats from a given second
   - Export report, only a few sections from it.
   - Unreserve ports and logout.

Requirements:
   - Python requests module
   - BPS bpsRestPy.py module
   - BPS minimum version 9.0

Support:
   - Python 2 and Python 3
"""

# Import BPSv2 python library from outside the folder with samples.
import time, sys, os

sys.path.insert(0, (os.path.dirname(os.path.abspath(__file__)).replace('SampleScripts', 'Modules')))
from bpsRestPy import BPS, pp

########################################
# Demo script global variables
Bpt_Name_To_Load = "sampleAppSimTemplate.bpt"
Test_Name = Bpt_Name_To_Load.split('.')[0]
new_test_model_name = "TestModel_Edited"

Bpt_NN_To_Load = "networkNeighborhoodSample.bpt"
NN_name = Bpt_NN_To_Load.split('.')[0]
new_NN_name = "new_NN_name"

chassis_ip = "10.36.18.44"
slot_number = 1
port_list   = [0, 1]
runTime     = 20

########################################
# Login to BPS box
bps_session = BPS(chassis_ip, 'admin', 'admin')
bps_session.login()


########################################
print("Import a test")
status = bps_session.testmodel.importModel(Test_Name, Bpt_Name_To_Load, True)
print("  %s " % status)

print("Search for the imported test")
searchResult = bps_session.testmodel.search(searchString=Test_Name, limit=5, sort="name", sortorder="ascending")
print(searchResult)

print("Load a test model")
pp(bps_session.testmodel.load(template=Test_Name))

name = bps_session.testmodel.name.get()
print("Test Name: %s"%name)

########################################
print("Import a Network Config")
status = bps_session.network.importNetwork(NN_name, Bpt_NN_To_Load, True)
print("  %s " % status)

print("Search for the imported network config.")
nn_list = bps_session.network.search(searchString=NN_name, limit=10, sort="name", sortorder="ascending", clazz="", offset=0, userid="admin")
pp(nn_list)

print("Load the network config.")
bps_session.network.load(template=NN_name)

name = bps_session.network.name.get()
print("Network Name: %s" % name)

print("The Network Model is :")
network_model = bps_session.network.networkModel.get()

print("The Network Elements used in config are:")
elements = [k for k,v in network_model.items() if v != None]
print("  %s" % elements)

print("Change a few params from an interface")
print("   : mtu from Interface 1")
bps_session.network.networkModel.interface["Interface 1"].set({"mtu":1800, "mac_address":"02:1A:C5:03:00:00"})
print("   %s" % bps_session.network.networkModel.interface["Interface 1"].mac_address.get())

print("   : ip_address from Static Hosts i2_default")
bps_session.network.networkModel.ip_static_hosts["Static Hosts i2_default"].ip_address.set("30.0.1.1")
print("   %s" % bps_session.network.networkModel.ip_static_hosts["Static Hosts i2_default"].ip_address.get())

print(" Get tags from Static Hosts i2_default:")
print("   %s" % bps_session.network.networkModel.ip_static_hosts["Static Hosts i2_default"].tags.get())

print("Save changes made into the network config.")
bps_session.network.saveAs(name=new_NN_name, force=True)

########################################
print("Get the name of the network from the imported test model")
nn_name = bps_session.testmodel.network.get()
print("Network Name: %s" % nn_name)

print("Change the networks.")
bps_session.testmodel.network.set(new_NN_name)

print("Change a few things from a test component")
bps_session.testmodel.component["appsim_1"].set({"rateDist":{"min":"500", "max":"800", "type":"range"}})
bps_session.testmodel.component["appsim_1"].set({"tcp":{"mss":"1200", "retries":"3"}})
bps_session.testmodel.component["appsim_1"].set({"rampDist":{"steady":"00:00:30"}})

print("Save test")
bps_session.testmodel.saveAs(name=new_test_model_name, force=True)


########################################
print("Reserve Ports")
for p in port_list:
    bps_session.topology.reserve([{'slot': slot_number, 'port': p, 'group': 1}])

########################################
print("Run test and Get Stats:")
test_id_json = bps_session.testmodel.run(modelname=new_test_model_name, group=1)
run_id = test_id_json["runid"]
print("Test Run Id: %s"%run_id)

print("~Wait %s seconds" % runTime)
time.sleep(runTime)
print("~Cancel run")
bps_session.topology.stopRun(run_id)

print("Stats from the last second (-1): ")
pp(bps_session.testmodel.realTimeStats(int(run_id), "summary", -1))

print("Stats from second 3:")
pp(bps_session.testmodel.realTimeStats(int(run_id), "summary", 3))

########################################
print("~Export a section from report")
status = bps_session.reports.exportReport(filepath="test_test_report.csv", runid=run_id, reportType='csv', sectionIds='4,5')
print("   Export status: %s" % status)

print("Search Reports")
pp(bps_session.reports.search(searchString="", limit=30, sort="started at", sortorder="descending"))
pp(bps_session.reports.search(searchString="", limit=2, sort="name", sortorder="descending"))
pp(bps_session.reports.search(searchString="TestMod", limit=2, sort="name", sortorder="descending"))


########################################
print("Unreserve ports")
for p in port_list:
    bps_session.topology.unreserve([{'slot': slot_number, 'port': p}])

########################################
print("Session logout")
bps_session.logout()
