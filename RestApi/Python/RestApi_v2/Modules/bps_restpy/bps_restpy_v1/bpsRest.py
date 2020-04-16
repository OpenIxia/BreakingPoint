import requests
import json
import time
import os
import sys
from os.path import basename
from os.path import join
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl

requests.packages.urllib3.disable_warnings()

class TlsAdapter(HTTPAdapter):
   def init_poolmanager(self, connections, maxsize, block=False):
      self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize, block=block,ssl_version=ssl.PROTOCOL_TLSv1_1)

class BPS:
    def pretty_print_requests(self, req):
        request = req.request
        print(('\n\n{}\n{}\n{}\n\n{}'.format(
            '-----------REQUEST START-----------',
            request.method + ' ' + request.url,
            '\n'.join('{}: {}'.format(k, v) for k, v in list(request.headers.items())),
            request.body,
        )))
        print('-----------REQUEST END-----------')
        print('\n\n-----------RESPONSE START-----------')
        print(req.status_code)
        print('\n')
        print(req.headers.get('content-type'))
        print(req.content)
        print('-----------RESPONSE END-----------')
        print('\n\n')
     
    def __init__(self, ipstr, username, password):
        self.ipstr = ipstr
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.mount('https://', TlsAdapter())
        
#Login        
    def login(self, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/api/v1/auth/session'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'username':self.username, 'password':self.password})
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            apiKey = r.json().get('apiKey')                        
            self.session.headers['X-API-KEY'] = apiKey
            print('Login successful. Welcome ' + self.username)
        else:
        	print(r.status_code)
        	print(r.content)
        	sys.exit(0)
 
#Logout
    def logout(self, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/api/v1/auth/session'
        r = self.session.delete(service, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 204):
            if 'X-API-KEY' in self.session.headers:
                del self.session.headers['X-API-KEY']
            print('User logout successful')

#Port state
    def portsState(self, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/api/v1/bps/ports/'
        r = self.session.get(service, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print(r.json().get('portReservationState'))

#Port state printed in json format
    def portsStateJson(self, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/api/v1/bps/ports?prettyprint=true'
        r = self.session.get(service, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print(r.json().get('portReservationState'))

#Port reserve   
    def reservePorts(self, slot, portList, group, force, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/api/v1/bps/ports/operations/reserve'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'slot':slot, 'portList':portList, 'group':group, 'force':force})
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print('Port reservation successful.')
        print(r.content)

            
#Port Unreserved            
    def unreservePorts(self, slot, portList, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/api/v1/bps/ports/operations/unreserve'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'slot':slot, 'portList':portList})
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print('Port unreservation successful')
        print(r.content)
        
#Reboot Card
    def rebootCard(self, cardNumber, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/api/v1/bps/ports/operations/rebootcard'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'cardNumber':cardNumber})
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print('Card %s is rebooting.' %cardNumber)
        else:
            print(r.text)

#View the running tests
    def runningTestInfo(self, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/api/v1/bps/tests'
        jheaders = {'content-type': 'application/json'}
        r = self.session.get(service, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print(r.json().get('runningTestInfo'))
            
    def formattedRunningTestInfo(self, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/api/v1/bps/tests/operations/getFormattedRunningTestInfo'
        jheaders = {'content-type': 'application/json'}
        r = self.session.post(service, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            result = r.json().get('result')
            return result
            
#Run Test       
    def runTest(self, modelname, group, neighborhood = None, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/api/v1/bps/tests/operations/start'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'modelname':modelname, 'group':group, 'neighborhood':neighborhood})
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print('Test started successfully with testid: [' + json.loads(r.text).get('testid')+ '].')
            runid = json.loads(r.text).get('testid')
            return runid
        else:
            print(r.status_code)
            print('Some error occurred while starting the test.')
            print(r.json().get('error'))
            return -1

#Stop Test
#Setting testid by default to None in order to keep backwards compatibility
    def stopTest(self, testid = None, enableRequestPrints = False):
        print('Currently running tests:')
        self.runningTestInfo()
        if testid is None:
            testid = input('Enter the complete testid to cancel the running test: ')
        service = 'https://' + self.ipstr + '/api/v1/bps/tests/operations/stop'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'testid':testid})
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print('Test: [' + testid + '] has been successfully stopped.')
        else:
            print('Some error occurred while cancelling the running test: [' + testid + ']')
            
            
#Get Run time stats            
    def getRTS(self, runid, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/api/v1/bps/tests/operations/getRTS'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'runid':runid})
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print("RTS Values: ", r.json().get('rts'))
            return json.loads(r.text).get('progress')
    
    def getRealTimeStatistics(self, runid, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/api/v1/bps/tests/operations/getRealTimeStatistics'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'runid':runid})
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            return r.json().get('rts')

    def getRealTimeStatByName(self, runid, statname, enableRequestPrints = False):
        response = self.getRealTimeStatistics(runid)
        if response != None:
            values = json.loads(response).get('values')
            if values != None:
                statValue = values.get(statname)
                return statValue
            
    def getTestProgress(self, runid, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/api/v1/bps/tests/operations/getRTS'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'runid':runid})
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):              
            return json.loads(r.text).get('progress')        
            
    def getTestResult(self, runid, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/api/v1/bps/tests/operations/result'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'runid':runid})
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            result = json.loads(r.text).get('result');
            print(result)
            return result
    
    def getTestFailureDescription(self, runid, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/api/v1/bps/tests/operations/failuredescription'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'runid':runid})
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            result = json.loads(r.text).get('result');
            print(result)
            return result

    def getSharedComponentSettings(self, modelName, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/api/v1/bps/tests/operations/getSharedComponentSettings'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'modelName': modelName})
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print(r.status_code)
        if(r.status_code == 200):
            result = r.json().get('result');
            return result     
        return r.text  
            
    def createSharedComponentSettingArg(self, name, value):
        arg = {}
        arg['paramName'] = name
        arg['paramValue'] = value
        return arg        

    def setSharedComponentSettings(self, modelName, componentSettingArgs, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/api/v1/bps/tests/operations/setSharedComponentSettings'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'modelName': modelName, 'sharedComponentSettings': componentSettingArgs})
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print(r.status_code)
        if(r.status_code == 200):
            result = r.json().get('result');
            return result
        return r.text  

# Network Neighbourhood   
    def retrieveNetwork(self, NN_name=None, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/network/operations/retrieve'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'name':NN_name})
        print(jdata)
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For retrieve Network %s" %r)
        print("For retrieve Network json object %s" %(r.json()))
            
    def viewNetwork(self, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/network'
        jheaders = {'content-type': 'application/json'}
        r = self.session.get(service)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print(r.status_code)
        print("For view Network %s" %r)
        print("For view Network json object %s" %(r.json()))
    
    def modifyNetwork(self, componentId, elementId, Value, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/network/operations/modify'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'componentId':componentId, 'elementId':elementId, 'value':Value})
        print(jdata)
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For modify Network %s" %r)
        print("For modify Network json object %s" %(r.json()))
        
    def createModifyBatchArg(self, componentId, elementId, Value):
        batchArg = {}
        batchArg['componentId'] = componentId
        batchArg['elementId'] = elementId
        batchArg['value'] = Value
        return batchArg
        
    def modifyBatchNetwork(self, modifyBatchArgs, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/api/v1/bps/network/operations/modifyBatch'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'networkArgs':modifyBatchArgs})
        print(jdata)
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For modify batch Network %s" %r)
        print("For modify batch Network json object %s" %(r.json()))
        
    def saveNetwork(self, name_, force, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/network/operations/saveas'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'name':name_, 'force': force})
        print(jdata)
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For save Network %s" %r)
        print("For save Network json object %s" %(r.json()))
        
        
 # Component modification     
    def setNormalTest(self, NN_name=None, enableRequestPrints = False):
         service  = 'https://' + self.ipstr + '/api/v1/bps/workingmodel'
         jheaders = {'content-type': 'application/json'}
         jdata = json.dumps({'template':NN_name})
         print(jdata)
         r = self.session.patch(service, data=jdata, headers=jheaders, verify=False)
         if(enableRequestPrints):
            self.pretty_print_requests(r)
         print("For set working model %s" %r)
             
    def viewNormalTest(self, enableRequestPrints = False):
         service  = 'https://' + self.ipstr + '/api/v1/bps/workingmodel/settings'
         jheaders = {'content-type': 'application/json'}
         #jdata = json.dumps({'name':NN_name})
         #print jdata
         r = self.session.get(service)
         if(enableRequestPrints):
            self.pretty_print_requests(r)
         print("For view working model %s" %r.json())
         
    def uploadCapture(self, filePath, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/api/v1/bps/upload/capture'
        fileName = basename(filePath)
        files = {'file': (fileName, open(filePath, 'rb'), 'multipart/form-data')}
        r = self.session.post(service, files=files, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print('The Capture was uploaded and saved with name: [' + json.loads(r.text).get('result') + ']')
            return json.loads(r.text).get('result')
        else:
            print("Failed to load Capture")
            print("For Upload Capture json object %s" %(r.json()))
            return
     
    def modifyNormalTest(self, componentId, elementId, Value, enableRequestPrints = False):
         service  = 'https://' + self.ipstr + '/api/v1/bps/workingmodel'
         jheaders = {'content-type': 'application/json'}
         jdata = json.dumps({'newParams':{'componentId':componentId, 'elementId':elementId, 'value':Value}})
         print(jdata)
         r = self.session.patch(service, data=jdata, headers=jheaders, verify=False)
         if(enableRequestPrints):
            self.pretty_print_requests(r)
         print("For modify working model %s" %r)
         if(r.status_code != 204):
            print("For modify working model json object %s" %(r.json()))
            
    def modifyNormalTest2(self, componentId, elementId, paramId, Value, enableRequestPrints = False):
         service  = 'https://' + self.ipstr + '/api/v1/bps/workingmodel'
         jheaders = {'content-type': 'application/json'}
         jdata = json.dumps({'newParams':{'componentId':componentId, 'elementId':elementId, 'paramId':paramId, 'value':Value}})
         print(jdata)
         r = self.session.patch(service, data=jdata, headers=jheaders, verify=False)
         if(enableRequestPrints):
            self.pretty_print_requests(r)
         print("For modify working model %s" %r)
         if(r.status_code != 204):
            print("For modify working model json object %s" %(r.json()))
         
# the name parameter is kept for backwards compatibility with older scripts
# in order to save the test with a different name use the saveAsNormalTest method
    def saveNormalTest(self, name_, force, enableRequestPrints = False):
         service  = 'https://' + self.ipstr + '/api/v1/bps/workingmodel/operations/save'
         jheaders = {'content-type': 'application/json'}
         jdata = json.dumps({'name':name_, 'force': force})
         print(jdata)
         r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
         if(enableRequestPrints):
            self.pretty_print_requests(r)
         print("For save working model %s" %r)
         print("For save working model json object %s" %(r.json()))
         
    def saveAsNormalTest(self, name, force, enableRequestPrints = False):
         service  = 'https://' + self.ipstr + '/api/v1/bps/workingmodel/operations/saveAs'
         jheaders = {'content-type': 'application/json'}
         jdata = json.dumps({'name':name, 'force': force})
         print(jdata)
         r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
         if(enableRequestPrints):
            self.pretty_print_requests(r)
         print("For save as working model %s" %r)
         print("For save as working model json object %s" %(r.json()))
        
# sessionsender Lab
    def setSessionSender(self, template, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/sessionlabtest/'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'template':template})
        print(jdata)
        r = self.session.patch(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For set template status code -- %s" %r.status_code)
        if r.status_code != 204:
           print("For set template json object %s" %(r.json()))

    def viewSessionSender(self, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/sessionlabtest/'
        jheaders = {'content-type': 'application/json'}
        r = self.session.get(service)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print(r.status_code)
        print("For view template json object %s" %(r.json()))
           
           
    def modifySessionSender(self, elementId, Value, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/sessionlabtest/'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'sessionlabParams':{'elementId':elementId, 'value':Value}})
        print(jdata)
        r = self.session.patch(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print(r.status_code)
        if r.status_code != 204:
           print("For modify template json object %s" %(r.json()))
        
        
    def saveSessionSender(self, name_, force, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/sessionlabtest/operations/saveas'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'name':name_, 'force':force})
        print(jdata)
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print(r.status_code)
        print("For save template json object %s" %(r.json()))
        


#Lawful test
    def setLawful(self, template, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/lawfulinterceptlabtest/'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'template':template})
        print(jdata)
        r = self.session.patch(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For set template %s" %r)
        if r.status_code != 204:
           print("For set template json object %s" %(r.json()))

    def viewLawful(self, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/lawfulinterceptlabtest/'
        jheaders = {'content-type': 'application/json'}
        r = self.session.get(service)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For view template %s" %r)
        print("For view template json object %s" %(r.json()))        
           
           
    def modifyLawful(self, elementId, Value, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/lawfulinterceptlabtest/'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'lawfulInterceptlabParams':{'elementId':elementId, 'value':Value}})
        print(jdata)
        r = self.session.patch(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For modify template %s" %r)
        if r.status_code != 204:
           print("For modify template json object %s" %(r.json()))
        
        
    def saveLawful(self, name_, force, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/lawfulinterceptlabtest/operations/saveas'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'name':name_, 'force':force})
        print(jdata)
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For save template %s" %r)
        
        
#RFC2544 test
    def setRfc(self, template, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/rfc2544test/'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'template':template})
        print(jdata)
        r = self.session.patch(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For set template %s" %r)           
   
    def viewRfc(self, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/rfc2544test/'
        jheaders = {'content-type': 'application/json'}
        r = self.session.get(service)
        print("For view template %s" %r)      
              
              
    def modifyRfc(self, elementId, Value, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/rfc2544test/'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'rfc2544Params':{'elementId':elementId, 'value':Value}})
        print(jdata)
        r = self.session.patch(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For modify template %s" %r)
        if r.status_code != 204:
           print("For modify template json object %s" %(r.json()))   
           
    def saveRfc(self, name, force, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/rfc2544test/operations/saveas'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'name':name, 'force':force})
        print(jdata)
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For save template %s" %r)
        print("For save template json object %s" %(r.json()))


#Multicast Lab test
    def setMulticast(self, template, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/multicasttest/'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'template':template})
        print(jdata)
        r = self.session.patch(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For set template %s" %r)
           
   
    def viewMulticast(self, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/multicasttest/'
        jheaders = {'content-type': 'application/json'}
        r = self.session.get(service)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For view template %s" %r)    
                       
              
    def modifyMulticast(self, elementId, paramId, Value, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/multicasttest/'
        jheaders = {'content-type': 'application/json'}
        source = ['10.1.1.3']
        jdata = json.dumps({'multicastNewParams':{'elementId':elementId, 'paramId':paramId, 'value':Value, "sourceIp":source}})
        print(jdata)
        r = self.session.patch(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For modify template %s" %r)
        if r.status_code != 204: 
           print("For modify template json object %s" %(r.json()))
        
        
    def addSource(self, type_, ipAddress, multicastAddress, Rate, enableRequestPrints = False):
         service  = 'https://' + self.ipstr + '/api/v1/bps/multicasttest/operations/add'
         jheaders = {'content-type': 'application/json'}
         jdata = json.dumps({'type':type_, 'ipAddress':ipAddress, 'multicastAddress':multicastAddress, 'rate':Rate})
         print(jdata)
         r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
         if(enableRequestPrints):
            self.pretty_print_requests(r)
         print("For Add source %s" %r)
         print("For Add source json object %s" %(r.json()))
         
    def deleteSource(self, elementId, enableRequestPrints = False):
         service  = 'https://' + self.ipstr + '/api/v1/bps/multicasttest/operations/delete'
         jheaders = {'content-type': 'application/json'}
         jdata = json.dumps({'elementId':elementId})
         print(jdata)
         r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
         if(enableRequestPrints):
            self.pretty_print_requests(r)
         print("For Delete source %s" %r)
         print("For Delete source json object %s" %(r.json()))
         
         
    def addSubscriber(self, type_, maxSubscribers, groupAddress, enableRequestPrints = False):
         service  = 'https://' + self.ipstr + '/api/v1/bps/multicasttest/operations/add'
         jheaders = {'content-type': 'application/json'}
         jdata = json.dumps({'type':type_, 'maxSubscribers':maxSubscribers, 'groupAddress':groupAddress})
         print(jdata)
         r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
         if(enableRequestPrints):
            self.pretty_print_requests(r)
         print("For Add Subscriber %s" %r)
         print("For Add Subscriber json object %s" %(r.json()))
         
    def deleteSubscriber(self, elementId, enableRequestPrints = False):
         service  = 'https://' + self.ipstr + '/api/v1/bps/multicasttest/operations/delete'
         jheaders = {'content-type': 'application/json'}
         jdata = json.dumps({'elementId':elementId})
         print(jdata)
         r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
         if(enableRequestPrints):
            self.pretty_print_requests(r)
         print("For Delete Subscriber %s" %r)         
         print("For Delete Subscriber json object %s" %(r.json()))
         
         
    def saveMulticast(self, enableRequestPrints = False):
         service  = 'https://' + self.ipstr + '/api/v1/bps/multicasttest/operations/save'
         jheaders = {'content-type': 'application/json'}
         r = self.session.post(service, headers=jheaders, verify=False)
         if(enableRequestPrints):
            self.pretty_print_requests(r)
         print("For save template %s" %r)
           
    def saveasMulticast(self, name, force, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/multicasttest/operations/saveas'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'name':name, 'force':force})
        print(jdata)
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For save template %s" %r)
        print("For save template json object %s" %(r.json()))


#LTE lab test
    def setLte(self, template, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/ltelabtest/'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'template':template})
        print(jdata)
        r = self.session.patch(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For set template %s" %r)
           
   
    def viewLte(self, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/ltelabtest/'
        jheaders = {'content-type': 'application/json'}
        r = self.session.get(service)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For view template %s" %r)   
                     
              
    def modifyLte(self, elementId, Value, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/ltelabtest/'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'lteLabParams':{'elementId':elementId, 'value':Value}})
        print(jdata)
        r = self.session.patch(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For modify template %s" %r)
        if r.status_code != 204:
           print("For modify template json object %s" %(r.json())) 
        
    def addMmeLte(self, mme_ip, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/ltelabtest/operations/addmme'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'mme_ip':mme_ip})
        print(jdata)
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For Add MME %s" %r)
        print("For Add MME json object %s" %(r.json()))
        
    
    def modifyMmeLte(self, oldMme, newMme, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/ltelabtest/operations/modifymme'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'oldMme':oldMme, 'newMme':newMme})
        print(jdata)
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For modify MME %s" %r)
        print("For modify MME json object %s" %(r.json()))
        
    def deleteMmeLte(self, mme_ip, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/ltelabtest/operations/removemme'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'mme_ip':mme_ip})
        print(jdata)
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For Delete MME %s" %r)
        print("For Delete MME json object %s" %(r.json()))
        
           
    def saveLte(self, name, force, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/ltelabtest/operations/saveas'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'name':name, 'force':force})
        print(jdata)
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For save template %s" %r)
        print("For save template json object %s" %(r.json()))


#Importing bpt
    def uploadBPT(self, filePath, force, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/api/v1/bps/upload'
        fileName = basename(filePath)
        files = {'file': (fileName, open(filePath, 'rb'), 'application/xml')}
        jdata = {'force':force}
        print(jdata)
        r = self.session.post(service, files=files, data=jdata, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("For upload template status code %s" %r.status_code)
        if(r.status_code == 200):
            print('The bpt was uploaded and saved with name: [' + json.loads(r.text).get('result') + ']')
            return json.loads(r.text).get('result')
        else:
            print("Failed to load BPT")
            print("For upload template json object %s" %(r.json()))
            return

#Export Report
    def exportTestReport(self, testId, reportName, location, enableRequestPrints = False):
        reportFormat = reportName.split('.')[1].lower()
        service = 'https://' + self.ipstr + '/api/v1/bps/export/report/' + testId + '/' + reportFormat
        print('Please wait while your report is being downloaded. You will be informed once the download is complete')
        r = self.session.get(service, verify=False, stream=True)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if not os.path.isdir(location):
            os.makedirs(location)
        with open(join(location,reportName), 'wb') as fd:
            for chunk in r.iter_content(chunk_size=1024):
                fd.write(chunk)
        fd.close()
        r.close()
        if(r.status_code == 200):
            print('Your report for the testid: [' + testId + '] has been successfully downloaded')

  
#Export BPT
    def exportTestBPT(self, bptName, testId=None, testName=None, location='.//', enableRequestPrints = False):
        bptName = bptName + '.bpt'
        if (testId is not None) and (testName is None):
            service = 'https://' + self.ipstr + '/api/v1/bps/export/bpt/testid/' + testId
            print('Please wait while your bpt is being downloaded. You will be informed once the download is complete')
            r = self.session.get(service, verify=False, stream=True)
            if(enableRequestPrints):
                self.pretty_print_requests(r)
            with open(join(location,bptName), 'wb') as fd:
                for chunk in r.iter_content(chunk_size=1024):
                    fd.write(chunk)
            fd.close()
            r.close()
            if(r.status_code == 200):
                print('Your bpt having the testid: [' + testId + '] has been successfully downloaded')
        elif (testId is None) and (testName is not None):
            service = 'https://' + self.ipstr + '/api/v1/bps/export/bpt/testname/' + testName
            print('Please wait while your bpt is being downloaded. You will be informed once the download is complete')
            r = self.session.get(service, verify=False, stream=True)
            if(enableRequestPrints):
                self.pretty_print_requests(r)
            with open(join(location,bptName), 'wb') as fd:
                for chunk in r.iter_content(chunk_size=1024):
                    fd.write(chunk)
            fd.close()
            r.close()
            if(r.status_code == 200):
                print('Your bpt for the test: [' + testName + '] has been successfully downloaded')
        else :
            print('Wrong usage. You can only use of the two methods to export the test model.')
            
    def exportTestsCsv(self, csvName, location='.//', enableRequestPrints = False):
        csvName = csvName + '.csv'
        service = 'https://' + self.ipstr + '/api/v1/bps/export/tests'
        print('Please wait while your csv is being downloaded. You will be informed once the download is complete')
        r = self.session.get(service, verify=False, stream=True)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        with open(join(location,csvName), 'wb') as fd:
            for chunk in r.iter_content(chunk_size=1024):
                fd.write(chunk)
        fd.close()
        r.close()
        if(r.status_code == 200):
            print('Your csv having the test details has been successfully downloaded')
            
#Aggregate stats            
    def aggStats(self, testid, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/tests/operations/getAggregateStats'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'testid':testid})
        print(jdata)
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("Aggregate statistics ****** %s" %r.json())
        return r.json()
        
#Component Level stats
    def compStats(self, testid, componentId, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/tests/operations/getComponentStats'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'testid':testid, 'componentId':componentId})
        print(jdata)
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("Component statistics ****** %s" %r.json())
        return r.json()
        
#Protocol Level stats       
    def protoStats(self, testid, componentId, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/tests/operations/getProtocolStats'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'testid':testid, 'componentId':componentId})
        print(jdata)
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("Protocol statistics ****** %s" %r.json())
    
#Get all components   
    def testComponents(self, modelName, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/tests/operations/getTestComponents'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'modelName':modelName})
        print(jdata)
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("Component Names ****** %s" %r.json())
        return r.json()

    def compName(self, modelName, enableRequestPrints = False):
        service  = 'https://' + self.ipstr + '/api/v1/bps/tests/operations/getComponents'
        jheaders = {'content-type': 'application/json'}
        jdata = json.dumps({'modelName':modelName})
        print(jdata)
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        print("Component Names ****** %s" %r.json())
