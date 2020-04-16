# Title:  Demo Script made to describe a BPS RESTv2 common use case
# Actions:
#   1. Login to BPS box
#   2. Import a test and search into the database after it
#   3. Load the test and check the name
#   4. Import a network config and search for it into the database
#   5. Load the network config and make a few changes inside it
#   6. Save the changes into a new network config.
#   7. Change the network from the loaded test model.
#   8. Save the test model as a new config
#   9. Reserve ports
#  10. Run test then cancel it after a few seconds
#  11. Get stats from a given second
#  12. Evaluate a section from report
#  13. Export report, only a few sections from it.
#  14. Unreserve ports and logout.


########################################
import time, sys, os
# Add bps_restpy libpath *required if the library is not installed
libpath = os.path.abspath(__file__+"/../../..")
sys.path.insert(0,libpath)

from bps_restpy.bps import BPS,pp


########################################
# Demo script global variables
bpt_filename_to_import = "Sample_AppSim_template.bpt"
importAsTestName       = "sample_ImportedTestModel"
new_testmodel_name     = "testModel_Edited"

networkfile_to_import  = "nn_sample.bpt"
importAsNetworkName    = "sample_ImportedNetwork"
new_Network_name       = "new_network_name"

runTime     = 30
#bps system info
bps_system  = '<BPS_BOX_IP/HOSTNAME>'
bpsuser     = 'bps user'
bpspass     = 'bps pass'


slot_number = 2
port_list   = [0, 1]

########################################


########################################
# Login to BPS box
bps = BPS(bps_system, bpsuser, bpspass)
bps.login()
print("Import a test")
status = bps.testmodel.importModel(importAsTestName, bpt_filename_to_import, True)
print("  %s " % status)

print("Search for the imported test")
searchResult = bps.testmodel.search(searchString=importAsTestName, limit=5, sort="name", sortorder="ascending")
print(searchResult)

print("Load a test model")
pp(bps.testmodel.load(template=importAsTestName))

name = bps.testmodel.name.get()
print("Test Name: %s"%name)

########################################
print("Import a Network Config")
status = bps.network.importNetwork(importAsNetworkName, networkfile_to_import, True)
print("  %s " % status)

print("Search for the imported network config.")
nn_list = bps.network.search(searchString=importAsNetworkName, limit=10, sort="name", sortorder="ascending", clazz="", offset=0, userid="admin")
pp(nn_list)

print("Load the network config.")
bps.network.load(template=importAsNetworkName)

name = bps.network.name.get()
print("Network Name: %s" % name)

print("The Network Model is :")
network_model = bps.network.networkModel.get()

print("The Network Elements used in config are:")
elements = [k for k,v in network_model.items() if v != None]
print("  %s" % elements)

print("Change a few params from an interface")
print("   : mtu from Interface 1")
bps.network.networkModel.interface["Interface 1"].set({"mtu":1800, "mac_address":"02:1A:C5:03:00:00"})
print("   %s" % bps.network.networkModel.interface["Interface 1"].mac_address.get())

print("   : ip_address from Static Hosts i2_default")
bps.network.networkModel.ip_static_hosts["Static Hosts i2_default"].ip_address.set("30.0.1.1")
print("   %s" % bps.network.networkModel.ip_static_hosts["Static Hosts i2_default"].ip_address.get())

print(" Get tags from Static Hosts i2_default:")
print("   %s" % bps.network.networkModel.ip_static_hosts["Static Hosts i2_default"].tags.get())

print("Save changes made into the network config.")
bps.network.saveAs(name=new_Network_name, force=True)

########################################
print("Get the name of the network from the imported test model")
nn_name = bps.testmodel.network.get()
print("Network Name: %s" % nn_name)

print("Change the networks.")
bps.testmodel.network.set(new_Network_name)

print("Change a few things from a test component")
bps.testmodel.component["appsim_1"].set({"rateDist":{"min":"500", "max":"800", "type":"range"}})
bps.testmodel.component["appsim_1"].set({"tcp":{"mss":"1200", "retries":"3"}})
bps.testmodel.component["appsim_1"].set({"rampDist":{"steady":"00:00:30"}})

print("Save test")
bps.testmodel.saveAs(name=new_testmodel_name, force=True)


########################################
print("Reserve Ports")
for p in port_list:
    bps.topology.reserve([{'slot': slot_number, 'port': p, 'group': 2}])

########################################
print("Run test and Get Stats:")
test_id_json = bps.testmodel.run(modelname=new_testmodel_name, group=2)
run_id = test_id_json["runid"]
print("Test Run Id: %s"%run_id)

print("~Wait %s seconds" % runTime)
time.sleep(runTime)
print("~Cancel run")
bps.topology.stopRun(run_id)

print("Stats from the last second (-1): ")
pp(bps.testmodel.realTimeStats(int(run_id), "summary", -1))

print("Stats from second 3:")
pp(bps.testmodel.realTimeStats(int(run_id), "summary", 3))

#getting 3.4 Section: Synopsis Summary of Results from the Report
print ("Execution synopsis from respective report section:")
tabledata = bps.reports.getReportTable(runid=run_id, sectionId="3.4")
pp(tabledata)
print ("\n")

########################################
print("Available results for any test containing TestMod sorted descending")
pp(bps.reports.search(searchString="TestMod", limit=10, sort="name", sortorder="descending"))


print("~Export a section from report in csv format : "+ new_testmodel_name + ".csv")
bps.reports.exportReport(filepath=new_testmodel_name + ".csv", runid=run_id, reportType='csv', sectionIds='4,5')


########################################
print("Unreserve ports")
for p in port_list:
    bps.topology.unreserve([{'slot': slot_number, 'port': p}])

########################################
print("Session logout")
bps.logout()


