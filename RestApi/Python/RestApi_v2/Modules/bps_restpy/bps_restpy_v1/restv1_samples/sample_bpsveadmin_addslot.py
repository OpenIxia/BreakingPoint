import os,sys,time

libpath = os.path.abspath(__file__+"/../../..")
sys.path.insert(0,libpath)

from bps_restpy_v1.bpsRest import BPS
from bps_restpy_v1.bpsVEAdminRest import *


#connect to the bps system
bps = bpsRest.BPS('BPS_IP_OR_FQDN', 'admin', 'admin')
bps.login()

#create an instance of the bpsadmin class
bpsveadmin = BPSVEAdmin(bps)

slotsEmptyStatus =  bpsveadmin.getEmptySlots()

mgmtNetwork = bpsveadmin.getControllerIPSettings()
newSlotName = "VirtualBladeREST"

#hyervisor ip/hostname , credentials and type - kvm (kQEMU) or esx (kVMWare)
hypervisor = {"hostName":"Hypervisor_IP_OR_FQDN","hostUsername":"root","hostPassword":"your_hypervisor_passowrd","hostType":"kVMWare"}

#use the 1st datastore name listed by hypervisor
datastoreList = bpsveadmin.getHypervisorDatastores(hypervisor['hostName'], hypervisor['hostUsername'], 
                                              hypervisor['hostPassword'], 
                                              hypervisor['hostType'])
datastoreName = str (datastoreList[0]['name'] )

#get the networks names listed by hypervisor
networkList = bpsveadmin.getHypervisorNetworks(hypervisor['hostName'], hypervisor['hostUsername'], 
                                              hypervisor['hostPassword'], 
                                              hypervisor['hostType'])
#assume 1st network is management (this network assignment is subjective to the deployment)
mgmtNetworkName = networkList[0]['name']
#choose test interface NICS
testNetwork_1_Name = networkList[1]['name']
testNetwork_2_Name = networkList[2]['name']
testNetwork1_Config = {"adapter":"Network Adapter 1","network": testNetwork_1_Name}
testNetwork2_Config = {"adapter":"Network Adapter 2","network": testNetwork_2_Name}

#select the number of VMS/slots to be deployed with this template.
slotCount =  1

#configure the slot management static ip address. Use an empty array for DHCP or static address as in the example below 
staticMgmIpSettings = []
#staticMgmIpSettings = [{"ipAddress":"10.12.12.23","mask":"255.255.252.0","gateway":"10.12.12.1","identifier":"mgmtNic_%s" % newSlotName,"networkConfigurationType":"kStatic"}]

#the setting for the new slot 
newSlotVMSettings = {"hostInfo": hypervisor ,"defaultVmName": newSlotName,"vmNo": slotCount,"datastore": datastoreName,"mngmNetwork":mgmtNetworkName,"testNetworks":[testNetwork1_Config, testNetwork2_Config],"ipConfigs": staticMgmIpSettings}

#create deployment template the slot with the settings configured above
if bpsveadmin.prepareSlotVMDeployment(newSlotVMSettings):
    #start deployment operations
    bpsveadmin.createVMSlots()