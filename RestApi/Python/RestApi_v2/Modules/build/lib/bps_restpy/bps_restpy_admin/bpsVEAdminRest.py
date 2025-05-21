import json
import time
import os
from . import bpsRest

class BPSVEAdmin:
    def __init__(self,bps):
        self.ipstr = bps.ipstr
        self.username = bps.username
        self.password = bps.password
        self.session = bps.session
        self.bps = bps
        self.api_key = bps.session.headers['X-API-KEY']  

    def pretty_print_requests(self, req):
        self.bps.pretty_print_requests(req)
    
    #Login        
    def login(self, enableRequestPrints = False):
        self.bps.login()
        self.session = self.bps.session
        self.api_key = self.session.headers['X-API-KEY']
   
    #returns operation state for statusUrl    
    def _getOperationInfo(self, statusUrl, retry = 3 , enableRequestPrints = False):
        jheaders = {'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}
        #try to get the response from the url in service for retry times
        while 1:
            try:
                retry = retry - 1
                r = self.session.get(statusUrl, verify=False, headers=jheaders)
                break
            except Exception as e:
                if retry == 0:
                    print('Failed to access url %s with : %s ' % ( statusUrl , str(e.message)))
                    return
                print('%s , Retrying after 2 seconds' % str(e.message)) 
                time.sleep(2)
        if(enableRequestPrints):
            self.pretty_print_requests(r)            
        if (r.status_code != 200):
            print('Request Failed...(%s). \n Unexpected response :' % statusUrl)
            print(r.content)
            return
        if (not r.json()):
            msg =  '200 OK Response for (%s). \n Did not get any informational json body' % statusUrl
            print(msg)
            raise Exception (msg)
        operationInfo = {}
        operationInfo ['state'] = r.json().get('state')        
        operationInfo ['type'] = r.json().get('type')
        operationInfo ['progress'] = r.json().get('progress')
        operationInfo ['progressMessage'] = r.json().get('progressMessage')        
        return operationInfo
                
    #blocking method                  
    def waitOnFinish (self,statusUrl,inprogress = "IN_PROGRESS", enableRequestPrints = False):
        state = inprogress
        print("Waiting ..")
        start = time.time()
        while (state == inprogress ):
            time.sleep (2)
            operationInfo  = self._getOperationInfo(statusUrl)
            if (not operationInfo['state']):
                msg =  '200 OK Response for (%s). \ had a Json body that did not contain a <state> value.' % statusUrl
                print(msg)
                raise Exception (msg)
            print(operationInfo['type'], operationInfo['state'], operationInfo['progressMessage'], operationInfo['progress'], "%")
            state = operationInfo['state']
        duration = time.time() - start
        print("%s,%s,%s in %s secs" % (operationInfo['type'], operationInfo['progressMessage'], state, duration ))
     
    #connect to hypervisor "hostType":"kVMWare" or "kQEMU"   
    def isHypervisorUp (self,hostName, hostUsername, hostPassword, hostType, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/vmdeployment/hypervisor'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
        jdata = json.dumps({"hostName": hostName,"hostUsername": hostUsername,"hostPassword": hostPassword, "hostType": hostType})
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print('Connect to', hostName, 'Successful.')
            print(r.content)
            return True
        else:
            print("Connect to %s failed: %s - %s" % (hostName ,r , r.content)) 
            return False

    #connect to hypervisor "hostType":"kVMWare" or "kQEMU"   
    def getHypervisorNetworks (self,hostName, hostUsername, hostPassword, hostType, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/vmdeployment/hypervisor/networks'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
        jdata = json.dumps({"hostName": hostName,"hostUsername": hostUsername,"hostPassword": hostPassword, "hostType": hostType})
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            return r.json()
        else:
            raise Exception ("Connect to %s failed: %s - %s" % (hostName ,r , r.content) )
        
    #connect to hypervisor "hostType":"kVMWare" or "kQEMU"   
    def getHypervisorDatastores (self,hostName, hostUsername, hostPassword, hostType, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/vmdeployment/hypervisor/datastores'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
        jdata = json.dumps({"hostName": hostName,"hostUsername": hostUsername,"hostPassword": hostPassword, "hostType": hostType})
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            return r.json()
        else:
            raise Exception ("Connect to %s failed: %s - %s" % (hostName ,r , r.content) )

    def getControllerIPSettings(self, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/vmdeployment/controller/ipDefaultSettings'
        r = self.session.get(service, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            return r.json()    

    #create operation template 
    def prepareSlotVMDeployment (self,slotsSettings, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/vmdeployment/operation'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
        jdata = json.dumps(slotsSettings)
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 201):
            print('Prepared operations for deployment:')
            print(r.content)
        else:
            print("Deploy template failed: %s - %s" % (r, r.content))
            return False
        return True
    
    #deploy a new slot VM on the hypervisor    
    def createVMSlots (self, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/vmdeployment/operation/create'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
        #jdata = json.dumps()
        r = self.session.post(service, headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print('Request Successful.')
            print(r.content)       
        elif(r.status_code == 202):
            service = r.json().get('url')
            print("Waiting for deploy operation to complete")
            self.waitOnFinish( service )
        else:
            print("Deploy failed: %s - %s" % (r, r.content))
            return False
        return True    

    #disconnectSlot   
    def disconnectSlot (self, slotId, slotIP, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/vmdeployment/controller/unassignSlotsFromController'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
        jdata = json.dumps([{"slotId":slotId,"ipAddress":slotIP,"status":"kNone","message":""}])
        r = self.session.delete(service, data=jdata, headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print(r.content)
        elif(r.status_code == 202):
            service = r.json().get('url')
            print("Waiting for detach to complete")
            self.waitOnFinish( service )
        else:
            print("Detach failed: %s - %s" % (r, r.content))
            return False
        return True

    def getEmptySlots(self, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/vmdeployment/controller/emptySlots'
        r = self.session.get(service, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            return r.json()

    #validate new slot   
    def validateProposedSlotValues (self, slotId, ipAddress, enableRequestPrints = False):        
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/vmdeployment/controller/validateProposedSlotValues'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
        jdata = json.dumps([{"slotId": slotId, "ipAddress": ipAddress,"status":"kNone","message":"","id":"VmDeployment.model.AssignSlots-%s" % slotId,"combinedSlot":"Slot %s" % slotId}])
        r = self.session.delete(service, data=jdata, headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print(r.content)
        elif(r.status_code == 202):
            service = r.json().get('url')
            print("Waiting for validation to complete")
            self.waitOnFinish( service )
        else:
            print("Validation failed: %s - %s" % (r, r.content))
            return False
        return True    
    
    #assign new slot   
    def assignSlotsToController (self, slotId, ipAddress, enableRequestPrints = False):        
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/vmdeployment/controller/assignSlotsToController'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
        jdata = json.dumps([{"slotId":slotId,"ipAddress":ipAddress,"status":"kOk","message":"Validation OK"}])
        r = self.session.delete(service, data=jdata, headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print(r.content)
        elif(r.status_code == 202):
            service = r.json().get('url')
            print("Assign new slot complete")
            self.waitOnFinish( service )
        else:
            print("Slot assignment failed: %s - %s" % (r, r.content))
            return False
        return True    
 