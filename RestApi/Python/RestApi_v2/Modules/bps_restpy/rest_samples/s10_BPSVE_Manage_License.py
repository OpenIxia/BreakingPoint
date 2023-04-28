# Title:  Python Script Sample To Manage BPS VE Licenses.
# Actions:
#   1. Login to BPS box
#   2. Get a list of the configured license servers
#   3. Add a specific license server if is not already added
#   4. Check the active licenses on the specific server
#   5. Activate deactivate licenses
#   6. Check floating license feature statistics (check how many are available and taken)



#================

########################################
import sys
import os
# Add bps_restpy libpath *required if the library is not installed
libpath = os.path.abspath(__file__+"/../../..")
sys.path.insert(0, libpath)
import logging

from restPyWrapper import BPS, pp
from bpsVELicense import BPSVELicenseManagement
########################################


########################################
# Demo script global variables
########################################
# bps system info
bps_system  = '<BPS_BOX_IP/HOSTNAME>'
bpsuser     = 'bps user'
bpspass     = 'bps pass'

mainLicenseServer = '<License_Server_IP/HOSTNAME>'
activationCode = '<Activation_Code>'

########################################


########################################
# Login to BPS box
bps = BPS(bps_system, bpsuser, bpspass)
bps.login()

# create an instance of the BPSVELicenseManagement admin class
licenseMngr = BPSVELicenseManagement(bps)

# list license servers added
licenseServers = licenseMngr.getLicenseServers()
print ("The following license servers are added: " + str(licenseServers))

# add desired server if not already there
if not mainLicenseServer in [item['host'] for item in licenseServers if 'host' in item]:
    licenseMngr.addLicenseServer(mainLicenseServer)

# identify active server, if is not the one desired set it
activeServer = ''
for server in licenseServers:
    if 'isActive' in server and server['isActive']:
        activeServer = server

if not activeServer == mainLicenseServer:
    licenseMngr.setLicenseServerActive(mainLicenseServer)

# identify active server and store the details in  activeServer
for server in licenseServers:
    if 'isActive' in server and server['isActive']:
        activeServer = server

# extracting the id from the activeServer dictionary. We'll  use the id to identify teh server
licenseServerId = activeServer['id']
print("Server ID: %s"%licenseServerId)

# get active licenses on the active server
serverActiveLicenses = licenseMngr.retrieveLicenses(activeServer['id'])
print("The following licenses are active: " + str(serverActiveLicenses))

# is online activation possible?
status = licenseMngr.isServerOnline(activeServer['id'])
if not 'canConnectToIxiaBackend' in status or not status['canConnectToIxiaBackend']:
    print ("This server requires offline activation/deactivation process.\
         Please open license administration and follow the steps indicated.")
    print ("The rest of the steps are only aplicable to online servers. Existing...")

# retrieve information about an activation code
activationCodeStatus = licenseMngr.retrieveActivationCodeInfo(licenseServerId, activationCode)
print ("Activation code description and status: "+str(activationCodeStatus))

# activate the code
activationResult = licenseMngr.activateActivationCode(licenseServerId, activationCode, quantity=2)
print ("Activation result: "+str(activationCodeStatus))

serverActiveLicenses = licenseMngr.retrieveLicenses(activeServer['id'])
print("The following licenses are active: " + str(serverActiveLicenses))

# deactivate the code
activationResult = licenseMngr.activateActivationCode(licenseServerId, activationCode, quantity=2)
print ("Activation result: "+str(activationCodeStatus))

# disable logging
logger = logging.getLogger('bps_restpy')
logger.setLevel(logging.CRITICAL)

serverActiveLicenses = licenseMngr.retrieveLicenses(activeServer['id'])
print("The following licenses are active: " + str(serverActiveLicenses))

# retrieve license statistics. The amount of licenses used and available
licenseCountStats = licenseMngr.retrieveCountedFeatureStats(activeServer['id'])
print("The license statistics: " + str(licenseCountStats))
