import os,sys,time

libpath = os.path.abspath(__file__+"/../../..")
sys.path.insert(0,libpath)
sys.path.insert(0,"./BreakingPoint/RestApi/Python/RestApi_v2/Modules")

#import restv2 bps lib
from bps_restpy.bps import BPS
#import storage functions bps lib
from bps_restpy.bps_restpy_admin.bpsAdminRest import BPS_Storrage


bps = BPS('bpsIp_or_FQDN', 'admin', 'admin')
bps.login()

#backup database and user settings
bpsstorage = BPS_Storrage(bps)

print("!!!!\nAttempting to purge database (This will delete all your results files and cannot be undone).\n!!!!!" )
confirm = "Are you sure you want to permanently delete all test results on  " + bpsstorage.ipstr + " [y/n]:"
if sys.version_info[0] >= 3:
    response = str(input(confirm)).lower().strip()
else:
    response = str(raw_input(confirm)).lower().strip()
if response == 'y':
    #purging & compact the database
    bpsstorage.purgeReports()
    bpsstorage.compactStorage()
else:
    print ("Skiping purge.")

print("Done")

