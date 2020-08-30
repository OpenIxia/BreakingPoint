import json
import time
import os
from . import bpsRest


class BPS_Updates:
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
            
            
    #request Latest Available Updates   
    def getLatestAvailableUpdates(self,follow202 = True, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/cloudupdates/operations/check'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
        #jdata = json.dumps()
        r = self.session.post(service, data='', headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print('Request Successful.')
            print(r.content)
            return 0
        if(r.status_code == 202):
            service = r.json().get('url')
            print("Waiting update list from the server")
            self.waitOnFinish ( service )
        updateList = self.cloudUpdates()
        return updateList
            
    #Get and parse the update list
    def cloudUpdates(self, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/cloudupdates'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
        #jdata = json.dumps()
        r = self.session.get(service, headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if (r.status_code != 200):
            print('Request Failed.')
            print(r.content)
            raise Exception ("Unexpected response!!!")
        updateList = r.json()
        #print "%s in %s secs" % (r.json().get('state'), duration )
        return updateList
    
    #Get and parse the installed update list
    def getInstalledPackages(self, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/cloudupdates/installedpackages'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
        #jdata = json.dumps()
        r = self.session.get(service, headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if (r.status_code != 200):
            print('Request Failed.')
            print(r.content)
            raise Exception ("Unexpected response!!!")
        installedpackages = r.json()
        #print "%s in %s secs" % (r.json().get('state'), duration )
        return installedpackages
    
    #install the online Updates provided as input
    #example input: #[{'packageName': u'ati-strikepack-bps', 'buildNoTS': 1528125898, 'versionString': u'2018-11'},  {'packageName': u'ati-malware-bps', 'buildNoTS': 1527013760, 'versionString': u'2018-May'},   {'packageName': u'ati-dailymalware-bps', 'buildNoTS': 1526020319, 'versionString': u'2018-05-11'}]
    def installCloudUpdates(self,updateList, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/cloudupdates/operations/install'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
        jdata = json.dumps(updateList)
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print('Request Successful.')
            print(r.content)
            return 0
        elif(r.status_code == 202):
            service = r.json().get('url')
            print("Waiting update list from the server")
            self.waitOnFinish ( service )
        else:
            print("Update failed: %s - %s" % (r, r.content))
        updateList = self.cloudUpdates()
        return updateList

    def uploadBpsBuildForInstall (self,bpsBuildUrl, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/applications/operations/uploadUsingUrl'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
        jdata = json.dumps({'url': bpsBuildUrl})
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print('Request Successful.')
            print(r.content)
            return 0
        elif(r.status_code == 202):
            service = r.json().get('url')
            print("Waiting for upload to complete")
            self.waitOnFinish ( service )
        else:
            print("Upload failed: %s - %s" % (r, r.content))
            return False
        return True    

    def installBpsBuild (self,bpsBuildUrl, enableRequestPrints = False):
        if not self.uploadBpsBuildForInstall(bpsBuildUrl):
            return False
        fileName = os.path.bsename(bpsBuildUrl)
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/applications/operations/install'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
        jdata = json.dumps({updateRemotePath: "/var/tmp/ixia/waf/updates/%s" % fileName , updateType: "SYSTEM_UPDATE"})
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print('Request Successful.')
            print(r.content)
            return 0
        elif(r.status_code == 202):
            service = r.json().get('url')
            print("Waiting for install to complete")
            self.waitOnFinish ( service )
        else:
            print("Install failed: %s - %s" % (r, r.content))
            return False
        return True
    
    def uninstallBpsBuild (self,versionId, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/systemrestore/versions/' + str(versionId)+ '/operations/delete'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
        jdata = json.dumps({})
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print('Request Successful.')
            print(r.content)
            return 0
        elif(r.status_code == 202):
            service = r.json().get('url')
            print("Waiting for uninstall to complete")
            self.waitOnFinish ( service )
        else:
            print("Uninstall failed: %s - %s" % (r, r.content))
            return False
        return True

    #Get and parse the installed build list
    def getInstalledBpsBuilds(self, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/systemrestore/versions'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
        #jdata = json.dumps()
        r = self.session.get(service, headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if (r.status_code != 200):
            print('Request Failed.')
            print(r.content)
            raise Exception ("Unexpected response!!!")
        installedBuilds = r.json()
        #print "%s in %s secs" % (r.json().get('state'), duration )
        return installedBuilds
    
    #Get system information
    def getInstalledBpsBuilds(self, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/systeminformation'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
        #jdata = json.dumps()
        r = self.session.get(service, headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if (r.status_code != 200):
            print('Request Failed.')
            print(r.content)
            raise Exception ("Unexpected response!!!")
        installedBuilds = r.json()
        #print "%s in %s secs" % (r.json().get('state'), duration )
        return installedBuilds    

   


class BPS_Storrage:
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
            #this handles the special case when BPS is down during the operations.
            if ( self.waitOnSystemRecovery() ):
                return { 'state' : 'BPS system is ready', 'type': '', 'progress' : '', 'progressMessage' : ''}
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
        
    #wait on system recovery                
    def waitOnSystemRecovery (self, enableRequestPrints = False):
        start = time.time()
        while ( 1 ):
            service = 'https://' + self.ipstr + '/bps/api/v1/admin/systeminformation'
            jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
            try:
                r = self.session.get(service, headers=jheaders, verify=False )
            except requests.exceptions.ConnectionError:
                print('Web Platform is not responding,  the system might be rebooting. Retry in 30 seconds')
                time.sleep(30)
                continue
            if(enableRequestPrints):
                self.pretty_print_requests(r)                
            if (r.status_code == 401):
                print('Session authentication is not valid anymore. Login & Retry in 30 seconds')
                time.sleep(30)
                self.login()
                continue
            elif (r.status_code == 404):
                print('System is unavaillable at the moment. Retry in 30 seconds')
                time.sleep(30)
                continue            
            elif (r.status_code == 503):
                print('Bps System is inaccessible at the moment. Retry in 30 seconds')
                time.sleep(30)
                continue
            elif (r.status_code != 200):
                print('Request Failed. %s %s' % (r.status_code, r.reason))
                print(r.content)
                raise Exception ("Unexpected response!!!")
            return True 
        
    #delete all execution results reports    
    def purgeReports (self,versionId, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/storage/operations/compact'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
        jdata = json.dumps({'removeReports' : 'true' })
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print('Request Successful.')
            print(r.content)
            return 0
        elif(r.status_code == 202):
            service = r.json().get('url')
            print("Waiting for purgeReports to complete")
            self.waitOnFinish( service )
        else:
            print("Uninstall failed: %s - %s" % (r, r.content))
            return False
        return True
    
    #compact the database after deleting reports   
    def compactStorage (self,versionId, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/storage/operations/compact'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
        jdata = json.dumps({})
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print('Request Successful.')
            print(r.content)
            return 0
        elif(r.status_code == 202):
            service = r.json().get('url')
            print("Waiting for compactStorage to complete")
            self.waitOnFinish( service )
        else:
            print("Uninstall failed: %s - %s" % (r, r.content))
            return False
        return True

    #backup all execution results reports    
    def backup (self, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/storage/operations/backup'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
        jdata = json.dumps({'download' : 'true' })
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print('Request Successful.')
            print(r.content)
            return 0
        elif(r.status_code == 202):
            service = r.json().get('url')
            print("Waiting for backup to complete")
            self.waitOnFinish( service )
        else:
            print("Backup failed: %s - %s" % (r, r.content))
            return False
        return True    
    
    
    #Download backup file
    def downloadBackup(self,location,enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/storage/operations/download'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
        #jdata = json.dumps()
        r = self.session.get(service, headers=jheaders, stream=True )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if (r.status_code != 200):
            print('Request Failed.')
            print(r.content)
            raise Exception ("Unexpected response!!!")
        if not os.path.isdir(location):
            os.makedirs(location)
        filename = r.headers['Content-Disposition'].split('"')[1]
        with open(os.path.join(location,filename), 'wb') as fd:
            for chunk in r.iter_content(chunk_size=1024):
                fd.write(chunk)
        fd.close()
        r.close()
        if(r.status_code == 200):
            print('Your backup:  ' + os.path.join(location,filename) + ' has been successfully downloaded')
            return os.path.join(location,filename)
        else:
            print('Failed to download backup')
            
    def uploadBackupFile (self,importFile, enableRequestPrints = False):
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/storage/operations/upload'
        jheaders = { 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'} 
        fileName = os.path.basename(importFile)
        files = {'file': (fileName, open(importFile, 'rb') , 'multipart/form-data')}      
        r = self.session.post(service, files=files , headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print('Request Successful.')
            print(r.content)
            return True
        elif(r.status_code == 202):
            service = r.json().get('url')
            print("Waiting for upload to complete")
            self.waitOnFinish( service )
        else:
            print("Upload failed: %s - %s" % (r, r.content))
            return False
        return True  

    def restoreBackupUserData (self,importFile, enableRequestPrints = False):
        if not self.uploadBackupFile(importFile, enableRequestPrints):
            return False
        fileName = os.path.basename(importFile)
        service = 'https://' + self.ipstr + '/bps/api/v1/admin/storage/operations/restore'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}        
        jdata = json.dumps({ 'upload' : 'true' })
        r = self.session.post(service, data=jdata, headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            print('Request Successful.')
            print(r.content)
            return True
        elif(r.status_code == 202):
            service = r.json().get('url')
            print("Waiting for file to upload")
            self.waitOnFinish( service )
        else:
            print("Install failed: %s - %s" % (r, r.content))
            return False
        return True
            

#separate method to compare 2 lists of updates 
def createMissingUpdateList(available, installed):
    missingUpdates = {}
    for availableType in available:
        missingUpdates[availableType["packageType"]]=[]
        for aitem in availableType['versions']:
            #searching in installed list
            found = False
            for installedType in installed:
                if not installedType['packageType'] == availableType['packageType']:
                    continue
                for iitem in installedType['versions']:
                    if str(iitem['timestamp']) ==  str(aitem ['version']):
                        found = True
                        print("SKIP   : %s update id: %s version :%s already installed." % (availableType['packageType'], aitem['version'], aitem['timestamp'] ))
            if not found: 
                print("Available :%s update packageType: %s version :%s was checked." % (availableType['packageType'], aitem['version'], aitem['timestamp'] ))
                missingUpdates[availableType["packageType"]].append (aitem)             
    return missingUpdates
