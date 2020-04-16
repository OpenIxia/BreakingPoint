import os,sys,time

libpath = os.path.abspath(__file__+"/../../..")
sys.path.insert(0,libpath)

from bps_restpy_v1.bpsRest import BPS
from bps_restpy_v1.bpsAdminRest import *

bps = bpsRest.BPS('bpsIp_or_FQDN', 'admin', 'admin')
bps.login()

#optionally it is recomended to backup database and user settings before update
bpsstorage = BPS_Storrage(bps)
location = r'C:\Users\Public\Downloads'
bpsstorage.backup()
backupfile= bpsstorage.downloadBackup(location)

#####Uptdate ATI with latest 2 available missing packages ###############
#get the list of available on-line updates and update
bpswp = BPS_Updates(bps)
updateList = bpswp.getLatestAvailableUpdates()
installedpackages = bpswp.getInstalledPackages()
#create a list of possible upgrades : keys - ati-dailymalware-bps, ati-malware-bps, ati-evergreen-bps
missingupdates = createMissingUpdateList (updateList, installedpackages)
#pick the last 2 updates available from ati-dailymalware-bps
myupdatetype = "ati-dailymalware-bps"
update1 = missingupdates[myupdatetype][-1]
update2 = missingupdates[myupdatetype][-2]
print("Install ", update1, update2)
mydailyupdates = [{"packageType": myupdatetype , "versions" : [ update1, update2] }]

#install latest 2 daily ati  updates
bpswp.installCloudUpdates(mydailyupdates)
#after installation is complete bps will be restarted. 

print("Done")

