import sys
sys.path.insert(0, '../Modules')
from BpsRestApi import *
import Queue,time, sys
from optparse import OptionParser

# Create a two interface Network Neighborhood from scratch
# Requires BPS_NN_2_Intf_Template.bpt file
#
# example1 --- routing interfaces with virtual router
#    python bpsNN.py --SCIP <BPS WEB_UI IP> --User <Username> --Passwd <password> --VR 1 --RTR1_IP <IP> --RTR1_GW <IP> --RTR2_IP <IP> --RTR2_GW <IP> --HOST1_IP <Starting IP> --HOST2_IP <Starting IP> --nnTemp "BPS_NN_2_Intf_Template" --nnName <new NN Name>
#
# example2 --- VLAN based routing interfaces with virtual router
#    python bpsNN.py --SCIP <BPS WEB_UI IP> --User <Username> --Passwd <password> --VLAN 1 --Vid_1 1001 --Vid_2 1002 --VR 1 --RTR1_IP <IP> --RTR1_GW <IP> --RTR2_IP <IP> --RTR2_GW <IP> --HOST1_IP <Starting IP> --HOST2_IP <Starting IP> --nnTemp "BPS_NN_2_Intf_Template" --nnName <new NN Name>
#
# example3 --- VLAN based switching interfaces
#    python bpsNN.py --SCIP <BPS WEB_UI IP> --User <Username> --Passwd <password> --VLAN 1 --Vid_1 1001 --Vid_2 1001 --VR 0 --RTR1_IP <IP> --RTR1_GW <IP> --RTR1_MASK 8 --RTR2_IP <IP> --RTR2_GW <IP> --RTR2_MASK 8 --HOST1_Count 65533 --HOST2_Count 65533 --nnTemp "BPS_NN_2_Intf_Template" --nnName <new NN Name>

# Input Parameters
if __name__ == "__main__":
   
   parser = OptionParser()
   parser.add_option('--SCIP', dest="SCIP", type=str, default="10.36.18.45")
   parser.add_option('--User', dest="User", type=str, default="admin")
   parser.add_option('--Passwd', dest="Passwd", type=str, default="admin")
   parser.add_option('--VLAN', dest="VLAN", type=int, default=0)
   parser.add_option('--Vid_2', dest="Vid_2", type=int, default=101)
   parser.add_option('--Vid_1', dest="Vid_1", type=int, default=101)
   parser.add_option('--VR', dest="VR", type=int, default=1)
   parser.add_option('--RTR1_IP', dest="RTR1_IP", type=str, default="172.16.0.2")
   parser.add_option('--RTR1_GW', dest="RTR1_GW", type=str, default="172.16.0.1")
   parser.add_option('--RTR1_MASK', dest="RTR1_MASK", type=int, default=24)
   parser.add_option('--RTR2_IP', dest="RTR2_IP", type=str, default="172.16.0.1")
   parser.add_option('--RTR2_GW', dest="RTR2_GW", type=str, default="172.16.0.2")
   parser.add_option('--RTR2_MASK', dest="RTR2_MASK", type=int, default=24)
   parser.add_option('--HOST1_IP', dest="HOST1_IP", type=str, default="10.10.11.2")
   parser.add_option('--HOST1_Count', dest="HOST1_Count", type=int, default=253)
   parser.add_option('--HOST2_IP', dest="HOST2_IP", type=str, default="10.10.12.2")
   parser.add_option('--HOST2_Count', dest="HOST2_Count", type=int, default=253)
   parser.add_option('--force', dest="force", type=str, default="true")
   parser.add_option('--nnTemp', dest="nnTemp", type=str, default="BPS_NN_2_Intf_Template")
   parser.add_option('--nnName', dest="nnName", type=str, default="NN_2_Intf_Scratch")
   
   
   # Display input parameters
   (options,args) = parser.parse_args()
   print "option = %s, args = %s" %(options, args)
   
   # login and load the template
   bps = BPS(options.SCIP,options.User, options.Passwd)
   # login
   bps.login()
   # load the NN template
   nnFileName = "%s.bpt" %options.nnTemp
   bptName = os.path.join(os.getcwd(),nnFileName)
   bps.uploadBPT(bptName, options.force, False)

   # Retrieve network
   bps.retrieveNetwork(options.nnTemp)

   if options.VLAN == 1:
      bps.modifyNetwork('Vlan i1_default', 'inner_vlan', options.Vid_1)
      bps.modifyNetwork('Vlan i2_default', 'inner_vlan', options.Vid_2)

      if options.VR == 1:
         if options.RTR1_IP != None:
            bps.modifyNetwork('Virtual Router i1_default', 'gateway_ip_address', 'null')
            bps.modifyNetwork('Virtual Router i1_default', 'ip_address', options.RTR1_IP)
            bps.modifyNetwork('Virtual Router i1_default', 'netmask', options.RTR1_MASK)
            bps.modifyNetwork('Virtual Router i1_default', 'gateway_ip_address', options.RTR1_GW)
   
         if options.RTR2_IP != None:
            bps.modifyNetwork('Virtual Router i2_default', 'gateway_ip_address', 'null')
            bps.modifyNetwork('Virtual Router i2_default', 'ip_address', options.RTR2_IP)
            bps.modifyNetwork('Virtual Router i2_default', 'netmask', options.RTR2_MASK)
            bps.modifyNetwork('Virtual Router i2_default', 'gateway_ip_address', options.RTR2_GW)

         if options.HOST1_IP != None:
            bps.modifyNetwork('Static Hosts i1_default', 'ip_address', options.HOST1_IP)
            bps.modifyNetwork('Static Hosts i1_default', 'count', options.HOST1_Count)

         if options.HOST2_IP != None:
            bps.modifyNetwork('Static Hosts i2_default', 'ip_address', options.HOST2_IP)
            bps.modifyNetwork('Static Hosts i2_default', 'count', options.HOST2_Count)
     
      else:
         if options.RTR1_IP != None:
            bps.modifyNetwork('Static Hosts i1_default', 'ip_address', options.RTR1_IP)
            bps.modifyNetwork('Static Hosts i1_default', 'count', options.HOST1_Count)
            bps.modifyNetwork('Static Hosts i1_default', 'netmask', options.RTR1_MASK)
            bps.modifyNetwork('Static Hosts i1_default', 'gateway_ip_address', options.RTR1_GW)
            bps.modifyNetwork('Static Hosts i1_default', 'default_container', 'Vlan i1_default')

         if options.RTR2_IP != None:
            bps.modifyNetwork('Static Hosts i2_default', 'ip_address', options.RTR2_IP)
            bps.modifyNetwork('Static Hosts i2_default', 'count', options.HOST2_Count)
            bps.modifyNetwork('Static Hosts i2_default', 'netmask', options.RTR2_MASK)
            bps.modifyNetwork('Static Hosts i2_default', 'gateway_ip_address', options.RTR2_GW)
            bps.modifyNetwork('Static Hosts i2_default', 'default_container', 'Vlan i2_default')

   elif options.VR == 1:
      bps.modifyNetwork('Virtual Router i1_default', 'default_container', 'Interface 1')
      bps.modifyNetwork('Virtual Router i2_default', 'default_container', 'Interface 2')

      if options.RTR1_IP != None:
         bps.modifyNetwork('Virtual Router i1_default', 'gateway_ip_address', 'null')
         bps.modifyNetwork('Virtual Router i1_default', 'ip_address', options.RTR1_IP)
         bps.modifyNetwork('Virtual Router i1_default', 'netmask', options.RTR1_MASK)
         bps.modifyNetwork('Virtual Router i1_default', 'gateway_ip_address', options.RTR1_GW)
   
      if options.RTR2_IP != None:
         bps.modifyNetwork('Virtual Router i2_default', 'gateway_ip_address', 'null')
         bps.modifyNetwork('Virtual Router i2_default', 'ip_address', options.RTR2_IP)
         bps.modifyNetwork('Virtual Router i2_default', 'netmask', options.RTR2_MASK)
         bps.modifyNetwork('Virtual Router i2_default', 'gateway_ip_address', options.RTR2_GW)

      if options.HOST1_IP != None:
         bps.modifyNetwork('Static Hosts i1_default', 'ip_address', options.HOST1_IP)
         bps.modifyNetwork('Static Hosts i1_default', 'count', options.HOST1_Count)

      if options.HOST2_IP != None:
         bps.modifyNetwork('Static Hosts i2_default', 'ip_address', options.HOST2_IP)
         bps.modifyNetwork('Static Hosts i2_default', 'count', options.HOST2_Count)

   else:
      if options.RTR1_IP != None:
         bps.modifyNetwork('Static Hosts i1_default', 'ip_address', options.RTR1_IP)
         bps.modifyNetwork('Static Hosts i1_default', 'count', options.HOST1_Count)
         bps.modifyNetwork('Static Hosts i1_default', 'netmask', options.RTR1_MASK)
         bps.modifyNetwork('Static Hosts i1_default', 'gateway_ip_address', options.RTR1_GW)

      if options.RTR2_IP != None:
         bps.modifyNetwork('Static Hosts i2_default', 'ip_address', options.RTR2_IP)
         bps.modifyNetwork('Static Hosts i2_default', 'count', options.HOST2_Count)
         bps.modifyNetwork('Static Hosts i2_default', 'netmask', options.RTR2_MASK)
         bps.modifyNetwork('Static Hosts i2_default', 'gateway_ip_address', options.RTR2_GW)

      bps.modifyNetwork('Static Hosts i1_default', 'default_container', 'Interface 1')
      bps.modifyNetwork('Static Hosts i2_default', 'default_container', 'Interface 2')

   # save the modified network neighborhood
   bps.saveNetwork(options.nnName, options.force, False)

   # Logout
   bps.logout()
