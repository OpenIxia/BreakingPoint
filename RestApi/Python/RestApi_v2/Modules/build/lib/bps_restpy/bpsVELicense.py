# license management example module to allow basic online operations
import json
import time
import os
import logging
bpsve_lic_log = logging.getLogger(__name__)



class BPSVELicenseManagement:
    def __init__(self, bps):

        #enable the class to extract IP info from either bps_restapi_v1 or bps_restapi_v2
        if hasattr(bps, 'ipstr'):
            self.ipstr = bps.ipstr
        else:
            self.ipstr = bps.host
        if hasattr(bps, 'ipstr'):
            self.username = bps.username
        else:
            self.username = bps.user
        self.password = bps.password
        self.session = bps.session
        self.bps = bps
        self.api_key = bps.session.headers['X-API-KEY']


    # def pretty_print_requests(self, req):
    #     self.bps.pretty_print_requests(req)

    #returns operation state for statusUrl
    def _getOperationInfo(self, statusUrl, retry = 3 , enableRequestPrints=False):
        jheaders = {'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}
        #try to get the response from the url in service for retry times
        while 1:
            try:
                retry = retry - 1
                r = self.session.get(statusUrl, verify=False, headers=jheaders)
                break
            except Exception as e:
                if retry == 0:
                    bpsve_lic_log.warn('Failed to access url %s with : %s ' % ( statusUrl , str(e.message)))
                    return
                bpsve_lic_log.warn('%s , Retrying after 2 seconds' % str(e.message))
                time.sleep(2)
        # if(enableRequestPrints):
        #     self.pretty_print_requests(r)
        if (r.status_code != 200):
            bpsve_lic_log.error('Request Failed...(%s). \n Unexpected response :' % statusUrl)
            raise Exception(r.content)
            return
        if (not r.json()):
            msg =  '200 OK Response for (%s). \n Did not get any informational json body' % statusUrl
            bpsve_lic_log.info(msg)
            raise Exception (msg)
        operationInfo = r.json()
        return operationInfo

    # blocking method
    def waitOnFinish(self,statusUrl,inprogress = "IN_PROGRESS", enableRequestPrints=False):
        state = inprogress
        bpsve_lic_log.debug("Waiting ..")
        start = time.time()
        while (state == inprogress ):
            time.sleep (2)
            operationInfo = self._getOperationInfo(statusUrl)
            if (not operationInfo['state']):
                msg = '200 OK Response for (%s). \ had a Json body that did not contain a <state> value.' % statusUrl
                bpsve_lic_log.info(msg)
                raise Exception (msg)
            bpsve_lic_log.info(str(operationInfo.get('type')) + ' ' +
                               str(operationInfo.get('state')) + ' ' +
                               str(operationInfo.get('progressMessage')) + ' ' +
                               str(operationInfo.get('progress')) + '%'
                               )
            state = operationInfo['state']
        duration = time.time() - start
        bpsve_lic_log.info("%s,%s,%s in %s secs" % (operationInfo.get('type'), operationInfo.get('progressMessage'), state, duration ))
        return operationInfo

    def getFromResponseUrl(self, service, enableRequestPrints=False):
        r = self.session.get(service, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            return r.json()
        else:
            raise Exception(service + ":" + str(r.content))

    def isServerOnline(self, licenseServerId, enableRequestPrints=False):
        service = 'https://' + self.ipstr + '/bps/api/v2/licensing/servers/' +str(licenseServerId)+ '/operations/testbackendconnectivity'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}
        #jdata = json.dumps()
        r = self.session.post(service, headers=jheaders, verify=False )
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            bpsve_lic_log.debug('Request Successful.')
            bpsve_lic_log.debug(r.content)
        elif(r.status_code == 202):
            service = r.json().get('url')
            bpsve_lic_log.info("Waiting for isServerOnline check..")
            self.waitOnFinish(service)
        else:
            raise Exception("isServerOnline check failed: %s - %s" % (r, r.content))
        result = self.getFromResponseUrl(service + "/result", enableRequestPrints)
        return result

    def getLicenseServers(self, enableRequestPrints=False):
        service = 'https://' + self.ipstr + '/bps/api/v1/licensing/servers'
        return self.getFromResponseUrl(service, enableRequestPrints)

    def retrieveLicenses(self, licenseServerId, enableRequestPrints=False):
        service = 'https://' + self.ipstr + '/bps/api/v2/licensing/servers/'+str(licenseServerId)+'/operations/retrievelicenses'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}
        r = self.session.post(service, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            bpsve_lic_log.debug('Request Successful.')
            bpsve_lic_log.debug(r.content)
        elif(r.status_code == 202):
            service = r.json().get('url')
            bpsve_lic_log.info("Waiting for retrieveing licenses..")
            self.waitOnFinish(service)
        else:
            raise Exception("Retrieve Licenses failed: %s - %s" % (r, r.content))
        result = self.getFromResponseUrl(service + "/result", enableRequestPrints)
        return result

    #add a new license server to the list of servers
    def addLicenseServer(self, licenseServer, enableRequestPrints=False):
        service = 'https://' + self.ipstr + '/bps/api/v2/licensing/servers'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}
        jdata = json.dumps({"host": licenseServer, "isActive": True})
        r = self.session.post(service, headers=jheaders, data=jdata, verify=False)

        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            bpsve_lic_log.debug('Request Successful.')
            bpsve_lic_log.debug(r.content)
        elif(r.status_code == 202):
            service = r.json().get('url')
            bpsve_lic_log.info("Waiting for adding license..")
            op = self.waitOnFinish(service)
        else:
            raise Exception("Failed to add server: %s - %s" % (r, r.content))

    #set license server to be active
    def setLicenseServerActive(self, licenseServer, enableRequestPrints=False):
        service = 'https://' + self.ipstr + '/bps/api/v1/licensing/servers/activeserver'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}
        jdata = json.dumps({"host": licenseServer})
        r = self.session.post(service, headers=jheaders, data=jdata, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200 or r.status_code == 204):
            bpsve_lic_log.debug('Request Successful.')
            bpsve_lic_log.debug(r.content)
        elif(r.status_code == 202):
            service = r.json().get('url')
            bpsve_lic_log.info("Waiting for activating server..")
            self.waitOnFinish(service)
        else:
            raise Exception("Activating server failed: %s - %s" % (r, r.content))
        return True

    #set license server to be active
    def retrieveActivationCodeInfo(self, licenseServerId, activationCode, enableRequestPrints=False):
        service = 'https://' + self.ipstr + '/bps/api/v2/licensing/servers/' +str(licenseServerId)+ '/operations/retrieveactivationcodeinfo'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}
        jdata = json.dumps({'activationCode': activationCode})
        r = self.session.post(service, headers=jheaders, data=jdata, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            bpsve_lic_log.debug('Request Successful.')
            bpsve_lic_log.debug(r.content)
        elif(r.status_code == 202):
            service = r.json().get('url')
            bpsve_lic_log.info("Waiting for retrieveActivationCodeInfo operation to complete")
            result = self.waitOnFinish(service)
        else:
            raise Exception("RetrieveActivationCodeInfo failed: %s - %s" % (r, r.content))
        return self.getFromResponseUrl(result['resultUrl'])

    #set license server to be active
    def activateActivationCode(self, licenseServerId, activationCode, quantity, enableRequestPrints=False):
        service = 'https://' + self.ipstr + '/bps/api/v2/licensing/servers/' +str(licenseServerId)+ '/operations/activate'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}
        jdata = json.dumps([{'activationCode': activationCode, 'quantity': quantity}])
        r = self.session.post(service, headers=jheaders, data=jdata, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            bpsve_lic_log.debug('Request Successful.')
            bpsve_lic_log.debug(r.content)
        elif(r.status_code == 202):
            service = r.json().get('url')
            bpsve_lic_log.info("Waiting for code activation operation to complete")
            result = self.waitOnFinish(service)
        else:
            raise Exception("activateActivationCode failed: %s - %s" % (r, r.content))
        return self.getFromResponseUrl(result['resultUrl'])


    #set license server to be active
    def deactivateActivationCode(self, licenseServerId, activationCode, quantity, enableRequestPrints=False):
        service = 'https://' + self.ipstr + '/bps/api/v2/licensing/servers/' +str(licenseServerId)+ '/operations/deactivate'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}
        jdata = json.dumps([{'activationCode': activationCode, 'quantity': quantity}])
        r = self.session.post(service, headers=jheaders, data=jdata, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            bpsve_lic_log.debug('Request Successful.')
            bpsve_lic_log.debug(r.content)
        elif(r.status_code == 202):
            service = r.json().get('url')
            bpsve_lic_log.info("Waiting for code deactivation operation to complete")
            result = self.waitOnFinish(service)
        else:
            raise Exception("deactivateActivationCode failed: %s - %s" % (r, r.content))
        return self.getFromResponseUrl(result['resultUrl'])

        #set license server to be active
    def retrieveCountedFeatureStats(self, licenseServerId, enableRequestPrints=False):
        service = 'https://' + self.ipstr + '/bps/api/v2/licensing/servers/' +str(licenseServerId)+ '/operations/retrievecountedfeaturestats'
        jheaders = {'content-type': 'application/json', 'x-api-key': self.api_key, 'Referrer Policy' : 'no-referrer-when-downgrade'}
        r = self.session.post(service, headers=jheaders, verify=False)
        if(enableRequestPrints):
            self.pretty_print_requests(r)
        if(r.status_code == 200):
            bpsve_lic_log.debug('Request Successful.')
            bpsve_lic_log.debug(r.content)
        elif(r.status_code == 202):
            service = r.json().get('url')
            bpsve_lic_log.info("Waiting for counted licenses features stats..")
            result = self.waitOnFinish(service)
        else:
            raise Exception("Retrievecountedfeaturestats failed: %s - %s" % (r, r.content))
        return self.getFromResponseUrl(result['resultUrl'])