"""
createSuperFlowStrikeList.py

Description:
   Create a Test Model from scratch.

What this script does:
   - Login to BPS box
   - Create a new superflow from scratch
   - Add flow and actions to the new created superflow
   - Save the superflow
   - Edit parameters inside an action
   - Remove action
   - Create a new strike list
   - Add a few strikes
   - Remove a strike
   - Save As/ Save the strike list

Requirements:
   - Python requests module
   - BPS bpsRestPy.py module
   - BPS minimum version 9.0

Support:
   - Python 2 and Python 3
"""

# Import BPSv2 python library from outside the folder with samples.
import time, sys, os

# Add bps_restpy libpath *required if the library is not installed
libpath = os.path.abspath(__file__+"/../../..")
sys.path.insert(0,libpath)

from bps_restpy.bps import BPS, pp


########################################
# Demo script global variables
new_superflow_name = "CreatedSuperFlow"
new_strikeList_name = "CreatedStrikeList"
chassis_ip = "10.36.83.74"

########################################
# Login to BPS box
bps_session = BPS(chassis_ip, 'admin', 'admin')
bps_session.login()

########################################
# # # SUPERFLOW
########################################
print("Create a SuperFlow from scratch with no name.")
bps_session.superflow.new()

print("Add a flow")
bps_session.superflow.addFlow({"name":"plus050", "to":"Server", "from":"Client"})

print("Add action 1")
bps_session.superflow.addAction(1, "tls_start", 1, "client")

print("Save the current working superflow under a new name.")
bps_session.superflow.saveAs(new_superflow_name, True)

print("Add action 2")
bps_session.superflow.addAction(1, "tls_accept",2,"server")

print("Add action 3")
bps_session.superflow.addAction(1, "tls_start", 3, "client")

print("Save the superflow under the same name")
bps_session.superflow.save()

print("Remove action 3")
bps_session.superflow.removeAction(3)

print("Save superflow")
bps_session.superflow.save()

print("Change parameters inside action 2")
bps_session.superflow.actions["2"].set({"tls_handshake_timeout":20})
bps_session.superflow.actions["1"].set({"tls_max_version": "TLS_VERSION_3_1"})
print("Change the cipher to RSA_WITH_RC4_128_MD5. The real value can be read from the tool tip inside UI.")
bps_session.superflow.actions["1"].set({"tls_max_version": "TLS_CIPHERSUITE_0004"})

print("Save superflow")
bps_session.superflow.save()

print("Gets params inside action 2")
action_dict_param = bps_session.superflow.actions["2"].get()
timeout =  action_dict_param["tls_handshake_timeout"]
decryptMode =  action_dict_param["tls_decrypt_mode"]
print("Handshake timeout: %s  and the decrypt mode: %s"%(timeout, decryptMode))

########################################
# # # STRIKELIST
########################################

print("Create a new strike list from scratch with no name.")
bps_session.strikeList.new()

print("Save the strike list unde a new name.")
bps_session.strikeList.saveAs(new_strikeList_name, True)

print("Add a atrike using its path.")
bps_session.strikeList.add([{"id":"/strikes/exploits/webapp/exec/cve_2018_8007_couchdb_rce.xml"}])

print("Save the current strike list using its name.")
bps_session.strikeList.save()

print("Add a list of strikes.")
bps_session.strikeList.add([{"id": "/strikes/malware/malware_e26eeed42cd54e359dae49bd0ae48a3c.xml"}, {"id":"/strikes/exploits/scada/7t_scada_dir_traversal_file_read_write.xml"}])

print("Save the strike list.")
bps_session.strikeList.save()

print("Remove a strike.")
bps_session.strikeList.remove([{"id":"/strikes/exploits/webapp/exec/cve_2018_8007_couchdb_rce.xml"}])

print("Save the strike list.")
bps_session.strikeList.save()