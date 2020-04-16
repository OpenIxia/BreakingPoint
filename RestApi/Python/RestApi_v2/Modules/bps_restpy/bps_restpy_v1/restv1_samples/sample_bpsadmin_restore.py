import os,sys,time

libpath = os.path.abspath(__file__+"/../../..")
sys.path.insert(0,libpath)

from bps_restpy_v1.bpsRest import BPS

#Restoring custum data from a previously saved export file. 

bps = bpsRest.BPS('bpsIp_or_FQDN', 'admin', 'admin')
bps.login()

#backup database and user settings
bpsstorage = BPS_Storrage(bps)
backupfile = r'C:\Users\public\Downloads\Ixia_WAF_Backup_2018_06_13_12_26_39'
print(("Attempting to restore : %s " % backupfile ))
bpsstorage.restoreBackupUserData(backupfile)
print("Done")

