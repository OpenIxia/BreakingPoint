from __future__ import absolute_import, print_function, division
from six import with_metaclass

import requests
import json
import pprint
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl

requests.packages.urllib3.disable_warnings()
pp = pprint.PrettyPrinter(indent=1).pprint


class TlsAdapter(HTTPAdapter):

    def init_poolmanager(self, connections, maxsize, block):
        self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize, block=block,ssl_version=ssl.PROTOCOL_TLSv1_1)

### this BPS REST API wrapper is generated for version: 9.00.101.13
class BPS(object):

    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password
        self.sessionId = None
        self.session = requests.Session()
        self.session.mount('https://', TlsAdapter())
        self.network = DataModelProxy(wrapper=self, name='network')
        self.testmodel = DataModelProxy(wrapper=self, name='testmodel')
        self.appProfile = DataModelProxy(wrapper=self, name='appProfile')
        self.topology = DataModelProxy(wrapper=self, name='topology')
        self.loadProfile = DataModelProxy(wrapper=self, name='loadProfile')
        self.strikeList = DataModelProxy(wrapper=self, name='strikeList')
        self.superflow = DataModelProxy(wrapper=self, name='superflow')
        self.reports = DataModelProxy(wrapper=self, name='reports')
        self.capture = DataModelProxy(wrapper=self, name='capture')

    ### connect to the system
    def __connect(self):
        r = self.session.post(url='https://' + self.host + '/bps/api/v1/auth/session', data=json.dumps({'username': self.user, 'password': self.password}), headers={'content-type': 'application/json'}, verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            self.sessionId = r.json().get('sessionId')
            self.session.headers['sessionId'] = r.json().get('sessionId')
            self.session.headers['X-API-KEY'] = r.json().get('apiKey')
            print('Successfully connected to %s.' % self.host)
        else:
            print('Failed connecting to %s: (%s, %s)' % (self.host, r.status_code, r.content))

    ### disconnect from the system
    def __disconnect(self):
        r = self.session.delete(url='https://' + self.host + '/api/v1/auth/session', verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 204):
            self.sessionId = None
            if 'sessionId' in self.session.headers:
                del self.session.headers['sessionId']
                del self.session.headers['X-API-KEY']
            print('Successfully disconnected from %s.' % self.host)
        else:
            print('Failed disconnecting from %s: (%s, %s)' % (self.host, r.status_code, r.content))

    ### login into the bps system
    def login(self):
        self.__connect()
        r = self.session.post(url='https://' + self.host + '/bps/api/v2/core/auth/login', data=json.dumps({'username': self.user, 'password': self.password, 'sessionId': self.sessionId}), headers={'content-type': 'application/json'}, verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'') or r.content.startswith(b'['))
        if(r.status_code == 200):
            print('Login successful.\nWelcome %s. \nYour session id is %s' % (self.user, self.sessionId))
        else:
            print('Login failed.\ncode:%s, content:%s' % (r.status_code, r.content))

    ### logout from the bps system
    def logout(self):
        r = self.session.post(url='https://' + self.host + '/bps/api/v2/core/auth/logout', data=json.dumps({'username': self.user, 'password': self.password, 'sessionId': self.sessionId}), headers={'content-type': 'application/json'}, verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            print('Logout successful. \nBye %s.' % self.user)
            self.__disconnect()
        else:
            print('Logout failed: (%s, %s)' % (r.status_code, r.content))

    ### Get from data model
    def _get(self, path, responseDepth=None, **kwargs):
        requestUrl = 'https://%s/bps/api/v2/core%s%s' % (self.host, path, '?responseDepth=%s' % responseDepth if responseDepth else '')
        for key, value in list(kwargs.items()):
            requestUrl = requestUrl + "&%s=%s" % (key, value)
        headers = {'content-type': 'application/json'}
        r = self.session.get(url=requestUrl, headers=headers, verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Get from data model
    def _patch(self, path, value):
        r = self.session.patch(url='https://' + self.host + '/bps/api/v2/core/' + path, headers={'content-type': 'application/json'}, data=json.dumps(value), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code != 204):
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Get from data model
    def _put(self, path, value):
        r = self.session.put(url='https://' + self.host + '/bps/api/v2/core/' + path, headers={'content-type': 'application/json'}, data=json.dumps(value), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code != 204):
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Get from data model
    def _delete(self, path):
        requestUrl = 'https://' + self.host + '/bps/api/v2/core/'+ path
        headers = {'content-type': 'application/json'}
        r = self.session.delete(url=requestUrl, headers=headers, verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Load an existing test model template.
    @staticmethod
    def _testmodel_operations_load(self, template):
        """
        Load an existing test model template.
        :param template (string): The name of the template testmodel
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/testmodel/operations/load', headers={'content-type': 'application/json'}, data=json.dumps({'template': template}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Creates a new Test Model
    @staticmethod
    def _testmodel_operations_new(self, template=None):
        """
        Creates a new Test Model
        :param template (string): The name of the template. In this case will be empty.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/testmodel/operations/new', headers={'content-type': 'application/json'}, data=json.dumps({'template': template}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _network_operations_search(self, searchString, userid, clazz, sortorder, sort, limit, offset):
        """
        :param searchString (java.lang.String):
        :param userid (java.lang.String):
        :param clazz (java.lang.String):
        :param sortorder (java.lang.String):
        :param sort (java.lang.String):
        :param limit (java.lang.Integer):
        :param offset (java.lang.Integer):
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/network/operations/search', headers={'content-type': 'application/json'}, data=json.dumps({'searchString': searchString, 'userid': userid, 'clazz': clazz, 'sortorder': sortorder, 'sort': sort, 'limit': limit, 'offset': offset}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _testmodel_operations_search(self, searchString, limit, sort, sortorder):
        """
        :param searchString (java.lang.String): Search test name matching the string given.
        :param limit (java.lang.String): The limit of rows to return
        :param sort (java.lang.String): Parameter to sort by.
        :param sortorder (java.lang.String): The sort order (ascending/descending)
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/testmodel/operations/search', headers={'content-type': 'application/json'}, data=json.dumps({'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _topology_operations_reserve(self, reservation):
        """
        :param reservation (list):
               list of object with fields
                      user (java.lang.String):
                      group (java.lang.Integer):
                      slot (java.lang.Integer):
                      port (java.lang.Integer):
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/topology/operations/reserve', headers={'content-type': 'application/json'}, data=json.dumps({'reservation': reservation}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Deletes a given Network Neighborhood Config from the database.
    @staticmethod
    def _network_operations_delete(self, name):
        """
        Deletes a given Network Neighborhood Config from the database.
        :param name (string): The name of the Network Neighborhood Config.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/network/operations/delete', headers={'content-type': 'application/json'}, data=json.dumps({'name': name}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _strikeList_operations_exportStrikeList(self, name, filepath):
        """
        :param name (java.lang.String): The name of the strike list to be exported.
        :param filepath (java.lang.String): The local path where to save the exported object. The file should have .bap extension
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/strikeList/operations/exportStrikeList', headers={'content-type': 'application/json'}, data=json.dumps({'name': name, 'filepath': filepath}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            with open(filepath, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=1024):
                    fd.write(chunk)
            fd.close()
            r.close()
            return {'status_code': r.status_code, 'content': 'success'}
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Deletes a given Test Model from the database.
    @staticmethod
    def _testmodel_operations_delete(self, name):
        """
        Deletes a given Test Model from the database.
        :param name (string): The name of the Test Model.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/testmodel/operations/delete', headers={'content-type': 'application/json'}, data=json.dumps({'name': name}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Deletes a given Strike List from the database.
    @staticmethod
    def _strikeList_operations_delete(self, name):
        """
        Deletes a given Strike List from the database.
        :param name (string): The name of the Strike List to be deleted.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/strikeList/operations/delete', headers={'content-type': 'application/json'}, data=json.dumps({'name': name}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Load an existing Application Profile and sets it as the current one.
    @staticmethod
    def _appProfile_operations_load(self, template):
        """
        Load an existing Application Profile and sets it as the current one.
        :param template (string): The name of the template application profile
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/appProfile/operations/load', headers={'content-type': 'application/json'}, data=json.dumps({'template': template}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Creates a new Application Profile.
    @staticmethod
    def _appProfile_operations_new(self, template=None):
        """
        Creates a new Application Profile.
        :param template (string): The name of the template. In this case will be empty.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/appProfile/operations/new', headers={'content-type': 'application/json'}, data=json.dumps({'template': template}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Saves the current working Application Profiles and gives it a new name.
    @staticmethod
    def _testmodel_operations_saveAs(self, name, force):
        """
        Saves the current working Application Profiles and gives it a new name.
        :param name (string): The new name given for the current working Test Model
        :param force (boolean): Force to save the working Test Model using a new name.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/testmodel/operations/saveAs', headers={'content-type': 'application/json'}, data=json.dumps({'name': name, 'force': force}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Saves the working Test Model using the current name
    @staticmethod
    def _testmodel_operations_save(self, name=None, force=True):
        """
        Saves the working Test Model using the current name
        :param name (string): The name of the template that should be empty.
        :param force (boolean): Force to save the working Test Model with the same name.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/testmodel/operations/save', headers={'content-type': 'application/json'}, data=json.dumps({'name': name, 'force': force}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Load an existing Super Flow and sets it as the current one.
    @staticmethod
    def _superflow_operations_load(self, template):
        """
        Load an existing Super Flow and sets it as the current one.
        :param template (string): The name of the existing Super Flow template
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/superflow/operations/load', headers={'content-type': 'application/json'}, data=json.dumps({'template': template}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Creates a new Super Flow.
    @staticmethod
    def _superflow_operations_new(self, template=None):
        """
        Creates a new Super Flow.
        :param template (string): The name of the template. In this case will be empty.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/superflow/operations/new', headers={'content-type': 'application/json'}, data=json.dumps({'template': template}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _capture_operations_importCapture(self, name, filename, force):
        """
        :param name (java.lang.String): The name of the capture being imported
        :param filename (java.lang.String): The file containing the capture object
        :param force (java.lang.Boolean): Force to import the file and the object having the same name will be replaced.
        """
        appWrapper = self._wrapper
        files = {'file': (name, open(filename, 'rb'), 'application/xml')}
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/capture/operations/importCapture', files=files, data={'fileInfo':str({'name': name, 'filename': filename, 'force': force})}, verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _appProfile_operations_search(self, searchString, limit, sort, sortorder):
        """
        :param searchString (java.lang.String): Search application profile name matching the string given.
        :param limit (java.lang.String): The limit of rows to return
        :param sort (java.lang.String): Parameter to sort by.
        :param sortorder (java.lang.String): The sort order (ascending/descending)
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/appProfile/operations/search', headers={'content-type': 'application/json'}, data=json.dumps({'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Removes a flow from the current working SuperFlow.
    @staticmethod
    def _superflow_operations_removeFlow(self, id):
        """
        Removes a flow from the current working SuperFlow.
        :param id (int): The flow ID.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/superflow/operations/removeFlow', headers={'content-type': 'application/json'}, data=json.dumps({'id': id}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _loadProfile_operations_save(self):
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/loadProfile/operations/save', headers={'content-type': 'application/json'}, data=None, verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Save the active editing LoadProfile under specified name
    @staticmethod
    def _loadProfile_operations_saveAs(self, name):
        """
        Save the active editing LoadProfile under specified name
        :param name (java.lang.String):
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/loadProfile/operations/saveAs', headers={'content-type': 'application/json'}, data=json.dumps({'name': name}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Deletes a given Application Profile from the database.
    @staticmethod
    def _appProfile_operations_delete(self, name):
        """
        Deletes a given Application Profile from the database.
        :param name (string): The name of the Application Profiles.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/appProfile/operations/delete', headers={'content-type': 'application/json'}, data=json.dumps({'name': name}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _reports_operations_search(self, searchString, limit, sort, sortorder):
        """
        :param searchString (java.lang.String): Search test name matching the string given.
        :param limit (java.lang.String): The limit of rows to return
        :param sort (java.lang.String): Parameter to sort by.
        :param sortorder (java.lang.String): The sort order (ascending/descending)
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/reports/operations/search', headers={'content-type': 'application/json'}, data=json.dumps({'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Saves the current working Strike List and gives it a new name.
    @staticmethod
    def _strikeList_operations_saveAs(self, name, force):
        """
        Saves the current working Strike List and gives it a new name.
        :param name (string): The new name given for the current working Strike List
        :param force (boolean): Force to save the working Strike List using the given name.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/strikeList/operations/saveAs', headers={'content-type': 'application/json'}, data=json.dumps({'name': name, 'force': force}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Saves the current working Strike List using the current name
    @staticmethod
    def _strikeList_operations_save(self, name=None, force=True):
        """
        Saves the current working Strike List using the current name
        :param name (string): The name of the template. Default is empty.
        :param force (boolean): Force to save the working Strike List with the same name.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/strikeList/operations/save', headers={'content-type': 'application/json'}, data=json.dumps({'name': name, 'force': force}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _topology_operations_unreserve(self, unreservation):
        """
        :param unreservation (list):
               list of object with fields
                      slot (java.lang.Integer):
                      port (java.lang.Integer):
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/topology/operations/unreserve', headers={'content-type': 'application/json'}, data=json.dumps({'unreservation': unreservation}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Deletes a Test Report from the database.
    @staticmethod
    def _reports_operations_delete(self, runid):
        """
        Deletes a Test Report from the database.
        :param runid (string): The run id of the test that generated the report you want to delete.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/reports/operations/delete', headers={'content-type': 'application/json'}, data=json.dumps({'runid': runid}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Adds a list of SuperFlow to the current working Application Profile. ([{'superflow':'adadad', 'weight':'20'},{..}])
    @staticmethod
    def _appProfile_operations_add(self, add):
        """
        Adds a list of SuperFlow to the current working Application Profile. ([{'superflow':'adadad', 'weight':'20'},{..}])
        :param add (list):
               list of object with fields
                      superflow (java.lang.String): The name of the super flow
                      weight (java.lang.String): The weight of the super flow
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/appProfile/operations/add', headers={'content-type': 'application/json'}, data=json.dumps({'add': add}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Imports the a list of strikes residing in a file.
    @staticmethod
    def _strikeList_operations_importStrikeList(self, name, filename, force):
        """
        Imports the a list of strikes residing in a file.
        :param name (java.lang.String): The name of the object being imported
        :param filename (java.lang.String): The file containing the object to be imported.
        :param force (java.lang.Boolean): Force to import the file and the object having the same name will be replaced.
        """
        appWrapper = self._wrapper
        files = {'file': (name, open(filename, 'rb'), 'application/xml')}
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/strikeList/operations/importStrikeList', files=files, data={'fileInfo':str({'name': name, 'filename': filename, 'force': force})}, verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _testmodel_operations_stopRun(self, runid):
        """
        :param runid (java.lang.Integer): Test RUN ID
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/testmodel/operations/stopRun', headers={'content-type': 'application/json'}, data=json.dumps({'runid': runid}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _topology_operations_stopRun(self, runid):
        """
        :param runid (java.lang.Inetger): Test RUN ID
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/topology/operations/stopRun', headers={'content-type': 'application/json'}, data=json.dumps({'runid': runid}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Load an existing Strike List and sets it as the current one.
    @staticmethod
    def _strikeList_operations_load(self, template):
        """
        Load an existing Strike List and sets it as the current one.
        :param template (string): The name of the Strike List template
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/strikeList/operations/load', headers={'content-type': 'application/json'}, data=json.dumps({'template': template}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Creates a new Strike List.
    @staticmethod
    def _strikeList_operations_new(self, template=None):
        """
        Creates a new Strike List.
        :param template (string): The name of the template. In this case will be empty.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/strikeList/operations/new', headers={'content-type': 'application/json'}, data=json.dumps({'template': template}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _loadProfile_operations_load(self, template):
        """
        :param template (java.lang.String):
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/loadProfile/operations/load', headers={'content-type': 'application/json'}, data=json.dumps({'template': template}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _superflow_operations_search(self, searchString, limit, sort, sortorder):
        """
        :param searchString (java.lang.String): Search Super Flow name matching the string given.
        :param limit (java.lang.String): The limit of rows to return
        :param sort (java.lang.String): Parameter to sort by.
        :param sortorder (java.lang.String): The sort order (ascending/descending)
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/superflow/operations/search', headers={'content-type': 'application/json'}, data=json.dumps({'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Deletes a given Super Flow from the database.
    @staticmethod
    def _superflow_operations_delete(self, name):
        """
        Deletes a given Super Flow from the database.
        :param name (string): The name of the Super Flow.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/superflow/operations/delete', headers={'content-type': 'application/json'}, data=json.dumps({'name': name}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _testmodel_operations_exportModel(self, name, attachments, filepath, runid=None):
        """
        :param name (java.lang.String): The name of the test model to be exported.
        :param attachments (java.lang.Boolean): True if object attachments are needed.
        :param filepath (java.lang.String): The local path where to save the exported object.
        :param runid (int): Test RUN ID
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/testmodel/operations/exportModel', headers={'content-type': 'application/json'}, data=json.dumps({'name': name, 'attachments': attachments, 'filepath': filepath, 'runid': runid}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            with open(filepath, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=1024):
                    fd.write(chunk)
            fd.close()
            r.close()
            return {'status_code': r.status_code, 'content': 'success'}
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Saves the current working Application Profiles and gives it a new name.
    @staticmethod
    def _appProfile_operations_saveAs(self, name, force):
        """
        Saves the current working Application Profiles and gives it a new name.
        :param name (string): The new name given for the current working Application Profile
        :param force (boolean): Force to save the working Application Profile using the given name.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/appProfile/operations/saveAs', headers={'content-type': 'application/json'}, data=json.dumps({'name': name, 'force': force}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Saves the current working application profile using the current name
    @staticmethod
    def _appProfile_operations_save(self, name=None, force=True):
        """
        Saves the current working application profile using the current name
        :param name (string): The name of the template. Default is empty.
        :param force (boolean): Force to save the working Application Profile with the same name.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/appProfile/operations/save', headers={'content-type': 'application/json'}, data=json.dumps({'name': name, 'force': force}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Removes an action from the current working SuperFlow.
    @staticmethod
    def _superflow_operations_removeAction(self, id):
        """
        Removes an action from the current working SuperFlow.
        :param id (int): The action ID.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/superflow/operations/removeAction', headers={'content-type': 'application/json'}, data=json.dumps({'id': id}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Reboots the card. Only available for PerfectStorm and CloudStorm cards.
    @staticmethod
    def _topology_operations_reboot(self, board):
        """
        Reboots the card. Only available for PerfectStorm and CloudStorm cards.
        :param board (java.lang.Integer):
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/topology/operations/reboot', headers={'content-type': 'application/json'}, data=json.dumps({'board': board}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Removes a strike from the current working  Strike List.([{id: 'bb/c/d'}, {id: 'aa/f/g'}])
    @staticmethod
    def _strikeList_operations_remove(self, strike):
        """
        Removes a strike from the current working  Strike List.([{id: 'bb/c/d'}, {id: 'aa/f/g'}])
        :param strike (list): The list of strike ids to remove. The strike id is in fact the it's path.
               list of object with fields
                      id (java.lang.String):
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/strikeList/operations/remove', headers={'content-type': 'application/json'}, data=json.dumps({'strike': strike}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _strikeList_operations_search(self, searchString, limit, sort, sortorder):
        """
        :param searchString (java.lang.String): Search strike list name matching the string given.
        :param limit (java.lang.String): The limit of rows to return
        :param sort (java.lang.String): Parameter to sort by.
        :param sortorder (java.lang.String): The sort order (ascending/descending)
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/strikeList/operations/search', headers={'content-type': 'application/json'}, data=json.dumps({'searchString': searchString, 'limit': limit, 'sort': sort, 'sortorder': sortorder}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _reports_operations_exportReport(self, filepath, runid, reportType, sectionIds=None):
        """
        :param filepath (java.lang.String): The local path where to export the report, including the report name.
        :param runid (java.lang.Integer): Test RUN ID
        :param reportType (java.lang.String): Report file format to be exported in.
        :param sectionIds (java.lang.String): Chapter Ids. Can be extracted a chapter or many. (sectionIds=6 / sectionIds=5,6,7)
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/reports/operations/exportReport', headers={'content-type': 'application/json'}, data=json.dumps({'filepath': filepath, 'runid': runid, 'reportType': reportType, 'sectionIds': sectionIds}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            with open(filepath, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=1024):
                    fd.write(chunk)
            fd.close()
            r.close()
            return {'status_code': r.status_code, 'content': 'success'}
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Saves the current working Application Profiles and gives it a new name.
    @staticmethod
    def _superflow_operations_saveAs(self, name, force):
        """
        Saves the current working Application Profiles and gives it a new name.
        :param name (string): The new name given for the current working Super Flow
        :param force (boolean): Force to save the working Super Flow using the given name.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/superflow/operations/saveAs', headers={'content-type': 'application/json'}, data=json.dumps({'name': name, 'force': force}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Saves the working Super Flow using the current name
    @staticmethod
    def _superflow_operations_save(self, name=None, force=True):
        """
        Saves the working Super Flow using the current name
        :param name (string): The name of the template that should be empty.
        :param force (boolean): Force to save the working Super Flow with the same name.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/superflow/operations/save', headers={'content-type': 'application/json'}, data=json.dumps({'name': name, 'force': force}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Clones a component in the current working Test Model
    @staticmethod
    def _testmodel_operations_clone(self, template, type, active):
        """
        Clones a component in the current working Test Model
        :param template (java.lang.String): The ID of the test component to clone.
        :param type (java.lang.String): Component Type: appsim, sesionsender ..
        :param active (java.lang.Boolean): Set component enable (by default is active) or disable
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/testmodel/operations/clone', headers={'content-type': 'application/json'}, data=json.dumps({'template': template, 'type': type, 'active': active}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Adds a new test component to the current working test model
    @staticmethod
    def _testmodel_operations_add(self, name, component, type, active):
        """
        Adds a new test component to the current working test model
        :param name (java.lang.String): Component Name
        :param component (java.lang.String): Component template, preset.
        :param type (java.lang.String): Component Type: appsim, sesionsender ..
        :param active (java.lang.Boolean): Set component enable (by default is active) or disable
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/testmodel/operations/add', headers={'content-type': 'application/json'}, data=json.dumps({'name': name, 'component': component, 'type': type, 'active': active}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _testmodel_operations_realTimeStats(self, runid, rtsgroup, numSeconds, numDataPoints=1):
        """
        :param runid (int): Test RUN ID
        :param rtsgroup (java.lang.String): Real Time Stats group name
        :param numSeconds (java.lang.Integer): The number of seconds.  If negative, means from the end
        :param numDataPoints (java.lang.Integer): The number of data points
        :return result (com.breakingpointsys.jcontrol.model.RealTimeStatsList):
               com.breakingpointsys.jcontrol.model.RealTimeStatsList of object with fields
                      testStuck (bool):
                      time (double):
                      progress (float):
                      values (list):
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/testmodel/operations/realTimeStats', headers={'content-type': 'application/json'}, data=json.dumps({'runid': runid, 'rtsgroup': rtsgroup, 'numSeconds': numSeconds, 'numDataPoints': numDataPoints}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Adds a flow to the current working SuperFlow
    @staticmethod
    def _superflow_operations_addFlow(self, flowParams):
        """
        Adds a flow to the current working SuperFlow
        :param flowParams (com.breakingpointsys.jcontrol.commands.WorkingSuperFlowModifyFlow.FlowParams): The flow object to add.
               com.breakingpointsys.jcontrol.commands.WorkingSuperFlowModifyFlow.FlowParams of object with fields
                      name (java.lang.String): The name of the flow
                      from (java.lang.String): Traffic initiator.
                      to (java.lang.String): Traffic responder.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/superflow/operations/addFlow', headers={'content-type': 'application/json'}, data=json.dumps({'flowParams': flowParams}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _testmodel_operations_run(self, modelname, group):
        """
        :param modelname (string): Test Name to run
        :param group (int): Group to run
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/testmodel/operations/run', headers={'content-type': 'application/json'}, data=json.dumps({'modelname': modelname, 'group': group}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _topology_operations_run(self, modelname, group):
        """
        :param modelname (string): Test Name to run
        :param group (int): Group to run
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/topology/operations/run', headers={'content-type': 'application/json'}, data=json.dumps({'modelname': modelname, 'group': group}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _network_operations_load(self, template):
        """
        :param template (string): The name of the network neighborhood template
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/network/operations/load', headers={'content-type': 'application/json'}, data=json.dumps({'template': template}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Creates a new Network Neighborhood configuration with no name.
    @staticmethod
    def _network_operations_new(self, template=None):
        """
        Creates a new Network Neighborhood configuration with no name.
        :param template (string): The name of the template. In this case will be empty.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/network/operations/new', headers={'content-type': 'application/json'}, data=json.dumps({'template': template}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Adds a list of strikes to the current working Strike List.([{id: 'b/b/v/f'}, {id: 'aa/f/h'}])
    @staticmethod
    def _strikeList_operations_add(self, strike):
        """
        Adds a list of strikes to the current working Strike List.([{id: 'b/b/v/f'}, {id: 'aa/f/h'}])
        :param strike (list): The list of strikes to add.
               list of object with fields
                      id (java.lang.String): Strike path.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/strikeList/operations/add', headers={'content-type': 'application/json'}, data=json.dumps({'strike': strike}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Adds a flow to the current working SuperFlow
    @staticmethod
    def _superflow_operations_addAction(self, flowid, name, actionid, source):
        """
        Adds a flow to the current working SuperFlow
        :param flowid (java.lang.Integer): The flow id.
        :param name (java.lang.String): The name of the action definition.
        :param actionid (java.lang.Integer): The new action id.
        :param source (java.lang.String): The action source.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/superflow/operations/addAction', headers={'content-type': 'application/json'}, data=json.dumps({'flowid': flowid, 'name': name, 'actionid': actionid, 'source': source}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _network_operations_list(self, userid, clazz, sortorder, sort, limit, offset):
        """
        :param userid (string):
        :param clazz (string):
        :param sortorder (string):
        :param sort (string):
        :param limit (integer):
        :param offset (integer):
        :return returnArg (list):
               list of object with fields
                      name (string):
                      type (string):
                      author (string):
                      createdOn (string):
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/network/operations/list', headers={'content-type': 'application/json'}, data=json.dumps({'userid': userid, 'clazz': clazz, 'sortorder': sortorder, 'sort': sort, 'limit': limit, 'offset': offset}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Removes a SuperFlow from the current working Application Profile.
    @staticmethod
    def _appProfile_operations_remove(self, superflow):
        """
        Removes a SuperFlow from the current working Application Profile.
        :param superflow (string): The name of the super flow.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/appProfile/operations/remove', headers={'content-type': 'application/json'}, data=json.dumps({'superflow': superflow}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Sets the card mode of a board
    @staticmethod
    def _topology_operations_setCardMode(self, board, mode):
        """
        Sets the card mode of a board
        :param board (java.lang.Integer):
        :param mode (java.lang.Integer): the new mode: 10 for BPS-L23, 7 for BPS-L47, 3 for Non-BPS
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/topology/operations/setCardMode', headers={'content-type': 'application/json'}, data=json.dumps({'board': board, 'mode': mode}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Sets the card speed of a board
    @staticmethod
    def _topology_operations_setCardSpeed(self, board, speed):
        """
        Sets the card speed of a board
        :param board (java.lang.Integer):
        :param speed (java.lang.Integer):
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/topology/operations/setCardSpeed', headers={'content-type': 'application/json'}, data=json.dumps({'board': board, 'speed': speed}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Sets the card fanout of a board
    @staticmethod
    def _topology_operations_setCardFanout(self, board, fanout):
        """
        Sets the card fanout of a board
        :param board (java.lang.Integer):
        :param fanout (java.lang.Integer):
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/topology/operations/setCardFanout', headers={'content-type': 'application/json'}, data=json.dumps({'board': board, 'fanout': fanout}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Sets the card fanout of a board
    @staticmethod
    def _topology_operations_setPerfAcc(self, board, perfacc):
        """
        Sets the card fanout of a board
        :param board (java.lang.Integer):
        :param perfacc (java.lang.Boolean):
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/topology/operations/setPerfAcc', headers={'content-type': 'application/json'}, data=json.dumps({'board': board, 'perfacc': perfacc}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _network_operations_saveAs(self, name, regenerateOldStyle=True, force=False):
        """
        :param name (string): The new name given for the current working network config
        :param regenerateOldStyle (boolean): Force to apply the changes made on the loaded network configuration. Force to generate a network from the old one.
        :param force (boolean): Force to save the network config. It replaces a pre-existing config having the same name.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/network/operations/saveAs', headers={'content-type': 'application/json'}, data=json.dumps({'name': name, 'regenerateOldStyle': regenerateOldStyle, 'force': force}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _network_operations_save(self, name=None, regenerateOldStyle=True, force=True):
        """
        :param name (string): The new name given for the current working network config
        :param regenerateOldStyle (boolean): Force to apply the changes made on the loaded network configuration. Force to generate a network from the old one.
        :param force (boolean): Force to save the network config. It replaces a pre-existing config having the same name.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/network/operations/save', headers={'content-type': 'application/json'}, data=json.dumps({'name': name, 'regenerateOldStyle': regenerateOldStyle, 'force': force}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### null
    @staticmethod
    def _appProfile_operations_exportAppProfile(self, name, attachments, filepath):
        """
        :param name (java.lang.String): The name of the test model to be exported.
        :param attachments (java.lang.Boolean): True if object attachments are needed.
        :param filepath (java.lang.String): The local path where to save the exported object.
        """
        appWrapper = self._wrapper
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/appProfile/operations/exportAppProfile', headers={'content-type': 'application/json'}, data=json.dumps({'name': name, 'attachments': attachments, 'filepath': filepath}), verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            with open(filepath, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=1024):
                    fd.write(chunk)
            fd.close()
            r.close()
            return {'status_code': r.status_code, 'content': 'success'}
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Imports a test model, given as a file.
    @staticmethod
    def _testmodel_operations_importModel(self, name, filename, force):
        """
        Imports a test model, given as a file.
        :param name (java.lang.String): The name of the object being imported
        :param filename (java.lang.String): The file containing the object
        :param force (java.lang.Boolean): Force to import the file and the object having the same name will be replaced.
        """
        appWrapper = self._wrapper
        files = {'file': (name, open(filename, 'rb'), 'application/xml')}
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/testmodel/operations/importModel', files=files, data={'fileInfo':str({'name': name, 'filename': filename, 'force': force})}, verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Imports an application profile, given as a file.
    @staticmethod
    def _appProfile_operations_importAppProfile(self, name, filename, force):
        """
        Imports an application profile, given as a file.
        :param name (java.lang.String): The name of the object being imported
        :param filename (java.lang.String): The file containing the object
        :param force (java.lang.Boolean): Force to import the file and the object having the same name will be replaced.
        """
        appWrapper = self._wrapper
        files = {'file': (name, open(filename, 'rb'), 'application/xml')}
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/appProfile/operations/importAppProfile', files=files, data={'fileInfo':str({'name': name, 'filename': filename, 'force': force})}, verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

    ### Imports a network neighborhood model, given as a file.
    @staticmethod
    def _network_operations_importNetwork(self, name, filename, force):
        """
        Imports a network neighborhood model, given as a file.
        :param name (java.lang.String): The name of the object being imported
        :param filename (java.lang.String): The file containing the object
        :param force (java.lang.Boolean): Force to import the file and replace the object having the same name.
        """
        appWrapper = self._wrapper
        files = {'file': (name, open(filename, 'rb'), 'application/xml')}
        r = appWrapper.session.post(url='https://' + appWrapper.host + '/bps/api/v2/core/network/operations/importNetwork', files=files, data={'fileInfo':str({'name': name, 'filename': filename, 'force': force})}, verify=False)
        jsonContent = r.content is not None and (r.content.startswith(b'{') or r.content.startswith(b'['))
        if(r.status_code == 200):
            return json.loads(r.content) if jsonContent else r.content
        else:
            return {'status_code': r.status_code, 'content': json.loads(r.content) if jsonContent else r.content}

class DataModelMeta(type):
    _dataModel = {
        'network': {
            'haveImpairments': {
            },
            'schemaver': {
            },
            'author': {
            },
            'description': {
            },
            'label': {
            },
            'impairments': {
            },
            'params': {
            },
            'networkModel': {
                'enodeb': [{
                    'dns': {
                    },
                    'plmn': {
                    },
                    'psn': {
                    },
                    'psn_netmask': {
                    },
                    'sctp_over_udp': {
                    },
                    'enodebs': {
                    },
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'sctp_sport': {
                    }
                }],
                'ip_router': [{
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    }
                }],
                'ip6_router': [{
                    'hosts_ip_alloc_container': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'prefix_length': {
                    }
                }],
                'ue_info': [{
                    'imsi_base': {
                    },
                    'secret_key_step': {
                    },
                    'count': {
                    },
                    'operator_variant': {
                    },
                    'secret_key': {
                    },
                    'imei_base': {
                    },
                    'msisdn_base': {
                    },
                    'maxmbps_per_ue': {
                    },
                    'mobility_session_infos': {
                    },
                    'id': {
                    }
                }],
                'ip_ldap_server': [{
                    'auth_timeout': {
                    },
                    'ldap_username_start_tag': {
                    },
                    'ldap_user_min': {
                    },
                    'ldap_user_count': {
                    },
                    'authentication_rate': {
                    },
                    'ldap_password_start_tag': {
                    },
                    'ldap_user_max': {
                    },
                    'id': {
                    },
                    'ldap_server_address': {
                    },
                    'dn_fixed_val': {
                    }
                }],
                'mme_sgw_pgw6': [{
                    'ue_info': {
                    },
                    'max_sessions': {
                    },
                    'lease_address': {
                    },
                    'dns': {
                    },
                    'plmn': {
                    },
                    'ip_address': {
                    },
                    'sgw_advertised_sgw': {
                    },
                    'sgw_advertised_pgw': {
                    },
                    'lease_address_v6': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'prefix_length': {
                    }
                }],
                'mobility_session_info': [{
                    'password': {
                    },
                    'bearers': {
                    },
                    'id': {
                    },
                    'access_point_name': {
                    },
                    'username': {
                    },
                    'initiated_dedicated_bearers': {
                    }
                }],
                'ggsn6': [{
                    'lease_address': {
                    },
                    'count': {
                    },
                    'dns': {
                    },
                    'ggsn_advertised_control_ip_address': {
                    },
                    'ip_address': {
                    },
                    'ggsn_advertised_data_ip_address': {
                    },
                    'lease_address_v6': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'prefix_length': {
                    }
                }],
                'ip_external_hosts': [{
                    'proxy': {
                    },
                    'count': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'behind_snapt': {
                    },
                    'tags': {
                    }
                }],
                'ip_static_hosts': [{
                    'mpls_list': {
                    },
                    'ip_selection_type': {
                    },
                    'count': {
                    },
                    'dns': {
                    },
                    'psn': {
                    },
                    'psn_netmask': {
                    },
                    'ip_address': {
                    },
                    'tags': {
                    },
                    'proxy': {
                    },
                    'maxmbps_per_host': {
                    },
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'ldap': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'dns_proxy': {
                    },
                    'behind_snapt': {
                    },
                    'enable_stats': {
                    }
                }],
                'ggsn': [{
                    'lease_address': {
                    },
                    'count': {
                    },
                    'dns': {
                    },
                    'ggsn_advertised_control_ip_address': {
                    },
                    'ip_address': {
                    },
                    'ggsn_advertised_data_ip_address': {
                    },
                    'lease_address_v6': {
                    },
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'default_container': {
                    },
                    'id': {
                    }
                }],
                'interface': [{
                    'ignore_pause_frames': {
                    },
                    'duplicate_mac_address': {
                    },
                    'description': {
                    },
                    'packet_filter': {
                        'not_dest_port': {
                        },
                        'not_src_ip': {
                        },
                        'filter': {
                        },
                        'src_ip': {
                        },
                        'src_port': {
                        },
                        'vlan': {
                        },
                        'not_vlan': {
                        },
                        'dest_ip': {
                        },
                        'not_dest_ip': {
                        },
                        'dest_port': {
                        },
                        'not_src_port': {
                        }
                    },
                    'impairments': {
                        'drop': {
                        },
                        'corrupt_lt64': {
                        },
                        'rate': {
                        },
                        'corrupt_lt256': {
                        },
                        'corrupt_rand': {
                        },
                        'corrupt_chksum': {
                        },
                        'corrupt_gt256': {
                        },
                        'frack': {
                        }
                    },
                    'mtu': {
                    },
                    'vlan_key': {
                    },
                    'number': {
                    },
                    'use_vnic_mac_address': {
                    },
                    'mac_address': {
                    },
                    'id': {
                    }
                }],
                'ds_lite_b4': [{
                    'aftr_addr': {
                    },
                    'count': {
                    },
                    'ip_address': {
                    },
                    'host_ip_base_addr': {
                    },
                    'ipv6_addr_alloc_mode': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'aftr_count': {
                    },
                    'hosts_ip_increment': {
                    },
                    'id': {
                    },
                    'prefix_length': {
                    },
                    'host_ip_addr_alloc_mode': {
                    }
                }],
                'ue': [{
                    'allocation_rate': {
                    },
                    'mobility_interval_ms': {
                    },
                    'ue_info': {
                    },
                    'dns': {
                    },
                    'mobility_action': {
                    },
                    'tags': {
                    },
                    'proxy': {
                    },
                    'default_container': {
                    },
                    'mobility_with_traffic': {
                    },
                    'id': {
                    },
                    'behind_snapt': {
                    },
                    'request_ipv6': {
                    },
                    'enable_stats': {
                    }
                }],
                'ip_dns_proxy': [{
                    'dns_proxy_ip_count': {
                    },
                    'dns_proxy_src_ip_base': {
                    },
                    'id': {
                    },
                    'dns_proxy_ip_base': {
                    },
                    'dns_proxy_src_ip_count': {
                    }
                }],
                'enodeb_mme_sgw6': [{
                    'dns': {
                    },
                    'plmn': {
                    },
                    'ip_allocation_mode': {
                    },
                    'mme_ip_address': {
                    },
                    'pgw_ip_address': {
                    },
                    'ue_address': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'prefix_length': {
                    }
                }],
                'ip6_dns_proxy': [{
                    'dns_proxy_ip_count': {
                    },
                    'dns_proxy_src_ip_base': {
                    },
                    'id': {
                    },
                    'dns_proxy_ip_base': {
                    },
                    'dns_proxy_src_ip_count': {
                    }
                }],
                'vlan': [{
                    'tpid': {
                    },
                    'duplicate_mac_address': {
                    },
                    'description': {
                    },
                    'mtu': {
                    },
                    'outer_vlan': {
                    },
                    'inner_vlan': {
                    },
                    'mac_address': {
                    },
                    'default_container': {
                    },
                    'id': {
                    }
                }],
                'mme_sgw_pgw': [{
                    'ue_info': {
                    },
                    'max_sessions': {
                    },
                    'lease_address': {
                    },
                    'dns': {
                    },
                    'plmn': {
                    },
                    'ip_address': {
                    },
                    'sgw_advertised_sgw': {
                    },
                    'sgw_advertised_pgw': {
                    },
                    'lease_address_v6': {
                    },
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'default_container': {
                    },
                    'id': {
                    }
                }],
                'ds_lite_aftr': [{
                    'count': {
                    },
                    'ip_address': {
                    },
                    'ipv6_addr_alloc_mode': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'b4_count': {
                    },
                    'b4_ip_address': {
                    },
                    'id': {
                    },
                    'prefix_length': {
                    }
                }],
                'ipsec_router': [{
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'ipsec': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'ike_peer_ip_address': {
                    }
                }],
                'dhcpv6c_req_opts_cfg': [{
                    'dhcpv6v_req_preference': {
                    },
                    'dhcpv6v_req_dns_list': {
                    },
                    'dhcpv6v_req_dns_resolvers': {
                    },
                    'dhcpv6v_req_server_id': {
                    },
                    'id': {
                    }
                }],
                'sgsn': [{
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'default_container': {
                    },
                    'ggsn_ip_address': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    }
                }],
                'path_advanced': [{
                    'destination_port_count': {
                    },
                    'destination_port_base': {
                    },
                    'source_port_base': {
                    },
                    'tags': {
                    },
                    'enable_external_file': {
                    },
                    'source_container': {
                    },
                    'source_port_algorithm': {
                    },
                    'tuple_limit': {
                    },
                    'file': {
                    },
                    'destination_port_algorithm': {
                    },
                    'destination_container': {
                    },
                    'source_port_count': {
                    },
                    'xor_bits': {
                    },
                    'stream_group': {
                    },
                    'id': {
                    }
                }],
                'path_basic': [{
                    'source_container': {
                    },
                    'destination_container': {
                    },
                    'id': {
                    }
                }],
                'enodeb_mme6': [{
                    'dns': {
                    },
                    'plmn': {
                    },
                    'ip_allocation_mode': {
                    },
                    'enodebs': {
                    },
                    'mme_ip_address': {
                    },
                    'pgw_ip_address': {
                    },
                    'ue_address': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'sgw_ip_address': {
                    },
                    'id': {
                    },
                    'prefix_length': {
                    }
                }],
                'pgw': [{
                    'max_sessions': {
                    },
                    'lease_address': {
                    },
                    'dns': {
                    },
                    'plmn': {
                    },
                    'ip_address': {
                    },
                    'lease_address_v6': {
                    },
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'default_container': {
                    },
                    'id': {
                    }
                }],
                'pgw6': [{
                    'max_sessions': {
                    },
                    'lease_address': {
                    },
                    'dns': {
                    },
                    'plmn': {
                    },
                    'ip_address': {
                    },
                    'lease_address_v6': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'prefix_length': {
                    }
                }],
                'sgsn6': [{
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'ggsn_ip_address': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'prefix_length': {
                    }
                }],
                'ip6_static_hosts': [{
                    'mpls_list': {
                    },
                    'ip_alloc_container': {
                    },
                    'ip_selection_type': {
                    },
                    'count': {
                    },
                    'dns': {
                    },
                    'ip_address': {
                    },
                    'tags': {
                    },
                    'proxy': {
                    },
                    'maxmbps_per_host': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'host_ipv6_addr_alloc_mode': {
                    },
                    'prefix_length': {
                    },
                    'dns_proxy': {
                    },
                    'behind_snapt': {
                    },
                    'enable_stats': {
                    }
                }],
                'plmn': [{
                    'mnc': {
                    },
                    'description': {
                    },
                    'id': {
                    },
                    'mcc': {
                    }
                }],
                'enodeb_mme_sgw': [{
                    'dns': {
                    },
                    'plmn': {
                    },
                    'ip_allocation_mode': {
                    },
                    'mme_ip_address': {
                    },
                    'pgw_ip_address': {
                    },
                    'ue_address': {
                    },
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'default_container': {
                    },
                    'id': {
                    }
                }],
                'sgw_pgw': [{
                    'max_sessions': {
                    },
                    'lease_address': {
                    },
                    'dns': {
                    },
                    'plmn': {
                    },
                    'ip_address': {
                    },
                    'sgw_advertised_sgw': {
                    },
                    'sgw_advertised_pgw': {
                    },
                    'lease_address_v6': {
                    },
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'default_container': {
                    },
                    'id': {
                    }
                }],
                'ip6_dhcp_server': [{
                    'ia_type': {
                    },
                    'pool_size': {
                    },
                    'ip_address': {
                    },
                    'pool_prefix_length': {
                    },
                    'offer_lifetime': {
                    },
                    'max_lease_time': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'pool_base_address': {
                    },
                    'default_lease_time': {
                    },
                    'pool_dns_address1': {
                    },
                    'id': {
                    },
                    'prefix_length': {
                    },
                    'pool_dns_address2': {
                    }
                }],
                'enodeb6': [{
                    'dns': {
                    },
                    'plmn': {
                    },
                    'sctp_over_udp': {
                    },
                    'enodebs': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'prefix_length': {
                    },
                    'sctp_sport': {
                    }
                }],
                'slaac_cfg': [{
                    'use_rand_addr': {
                    },
                    'enable_dad': {
                    },
                    'id': {
                    },
                    'stateless_dhcpv6c_cfg': {
                    },
                    'fallback_ip_address': {
                    }
                }],
                'ip6_external_hosts': [{
                    'proxy': {
                    },
                    'count': {
                    },
                    'id': {
                    },
                    'ip_address': {
                    },
                    'behind_snapt': {
                    },
                    'tags': {
                    }
                }],
                'ip_dns_config': [{
                    'dns_domain': {
                    },
                    'id': {
                    },
                    'dns_server_address': {
                    }
                }],
                'dhcpv6c_tout_and_retr_cfg': [{
                    'dhcp6c_inforeq_attempts': {
                    },
                    'dhcp6c_initial_rebind_tout': {
                    },
                    'dhcp6c_sol_attempts': {
                    },
                    'dhcp6c_max_rebind_tout': {
                    },
                    'dhcp6c_release_attempts': {
                    },
                    'dhcp6c_initial_release_tout': {
                    },
                    'dhcp6c_req_attempts': {
                    },
                    'dhcp6c_max_req_tout': {
                    },
                    'dhcp6c_max_renew_tout': {
                    },
                    'dhcp6c_max_sol_tout': {
                    },
                    'dhcp6c_initial_req_tout': {
                    },
                    'dhcp6c_max_inforeq_tout': {
                    },
                    'dhcp6c_initial_sol_tout': {
                    },
                    'dhcp6c_initial_renew_tout': {
                    },
                    'dhcp6c_initial_inforeq_tout': {
                    },
                    'id': {
                    }
                }],
                'ip_dhcp_server': [{
                    'lease_address': {
                    },
                    'count': {
                    },
                    'dns': {
                    },
                    'ip_address': {
                    },
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'lease_time': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'accept_local_requests_only': {
                    }
                }],
                'ip6_dns_config': [{
                    'dns_domain': {
                    },
                    'id': {
                    },
                    'dns_server_address': {
                    }
                }],
                'sgw_pgw6': [{
                    'max_sessions': {
                    },
                    'lease_address': {
                    },
                    'dns': {
                    },
                    'plmn': {
                    },
                    'ip_address': {
                    },
                    'sgw_advertised_sgw': {
                    },
                    'sgw_advertised_pgw': {
                    },
                    'lease_address_v6': {
                    },
                    'gateway_ip_address': {
                    },
                    'default_container': {
                    },
                    'id': {
                    },
                    'prefix_length': {
                    }
                }],
                'mpls_settings': [{
                    'mpls_tags': {
                    },
                    'id': {
                    }
                }],
                'ipsec_config': [{
                    'ike_dh': {
                    },
                    'ipsec_lifetime': {
                    },
                    'ike_pfs': {
                    },
                    'ike_mode': {
                    },
                    'ike_1to1': {
                    },
                    'nat_traversal': {
                    },
                    'xauth_username': {
                    },
                    'ike_encr_alg': {
                    },
                    'psk': {
                    },
                    'dpd_enabled': {
                    },
                    'dpd_timeout': {
                    },
                    'init_rate': {
                    },
                    'setup_timeout': {
                    },
                    'esp_encr_alg': {
                    },
                    'ike_lifetime': {
                    },
                    'ike_version': {
                    },
                    'id': {
                    },
                    'left_id': {
                    },
                    'ike_prf_alg': {
                    },
                    'esp_auth_alg': {
                    },
                    'dpd_delay': {
                    },
                    'xauth_password': {
                    },
                    'initial_contact': {
                    },
                    'debug_log': {
                    },
                    'wildcard_tsr': {
                    },
                    'rekey_margin': {
                    },
                    'ike_auth_alg': {
                    },
                    'right_id': {
                    },
                    'max_outstanding': {
                    },
                    'retrans_interval': {
                    },
                    'enable_xauth': {
                    }
                }],
                'dhcpv6c_cfg': [{
                    'dhcp6c_max_outstanding': {
                    },
                    'dhcp6c_duid_type': {
                    },
                    'dhcp6c_ia_type': {
                    },
                    'dhcp6c_req_opts_config': {
                    },
                    'dhcp6c_tout_and_retr_config': {
                    },
                    'dhcp6c_renew_timer': {
                    },
                    'dhcp6c_ia_t2': {
                    },
                    'id': {
                    },
                    'dhcp6c_ia_t1': {
                    },
                    'dhcp6c_initial_srate': {
                    }
                }],
                'sixrd_ce': [{
                    'sixrd_prefix': {
                    },
                    'count': {
                    },
                    'dns': {
                    },
                    'sixrd_prefix_length': {
                    },
                    'ip_address': {
                    },
                    'tags': {
                    },
                    'br_ip_address': {
                    },
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'default_container': {
                    },
                    'hosts_per_ce': {
                    },
                    'ip4_mask_length': {
                    },
                    'id': {
                    },
                    'enable_stats': {
                    }
                }],
                'ip_dhcp_hosts': [{
                    'allocation_rate': {
                    },
                    'count': {
                    },
                    'tags': {
                    },
                    'proxy': {
                    },
                    'ldap': {
                    },
                    'default_container': {
                    },
                    'accept_local_offers_only': {
                    },
                    'id': {
                    },
                    'behind_snapt': {
                    },
                    'dns_proxy': {
                    },
                    'enable_stats': {
                    }
                }],
                'enodeb_mme': [{
                    'dns': {
                    },
                    'plmn': {
                    },
                    'ip_allocation_mode': {
                    },
                    'enodebs': {
                    },
                    'mme_ip_address': {
                    },
                    'pgw_ip_address': {
                    },
                    'ue_address': {
                    },
                    'gateway_ip_address': {
                    },
                    'netmask': {
                    },
                    'default_container': {
                    },
                    'sgw_ip_address': {
                    },
                    'id': {
                    }
                }]
            },
            'createdOn': {
            },
            'revision': {
            },
            'lockedBy': {
            },
            'createdBy': {
            },
            'name': {
            },
            'interfaceCount': {
            },
            'clazz': {
            },
            'operations': {
                'search': [{
                }],
                'delete': [{
                }],
                'load': [{
                }],
                'new': [{
                }],
                'list': [{
                }],
                'saveAs': [{
                }],
                'save': [{
                }],
                'importNetwork': [{
                }]
            }
        },
        'testmodel': {
            'lastrunby': {
            },
            'summaryInfo': {
                'totalSubnets': {
                },
                'totalMacAddresses': {
                },
                'totalUniqueStrikes': {
                },
                'totalUniqueSuperflows': {
                },
                'requiredMTU': {
                }
            },
            'schemaver': {
            },
            'author': {
            },
            'lastrun': {
            },
            'description': {
            },
            'label': {
            },
            'sharedComponentSettings': {
                'maximumConcurrentFlows': {
                },
                'totalAttacks': {
                },
                'totalBandwidth': {
                },
                'maxFlowCreationRate': {
                },
                'totalAddresses': {
                },
                'samplePeriod': {
                }
            },
            'createdOn': {
            },
            'network': {
            },
            'revision': {
            },
            'duration': {
            },
            'result': {
            },
            'component': [{
                'schemaver': {
                },
                'author': {
                },
                'originalPreset': {
                },
                'active': {
                },
                'originalPresetLabel': {
                },
                'description': {
                },
                'label': {
                },
                'type': {
                },
                '@type:liveappsim': {
                    'app': {
                        'removeUnknownTcpUdp': {
                        },
                        'replace_streams': {
                        },
                        'removeUnknownSSL': {
                        },
                        'streamsPerSuperflow': {
                        },
                        'removedns': {
                        },
                        'fidelity': {
                        }
                    },
                    'tcp': {
                        'disable_ack_piggyback': {
                        },
                        'delay_acks': {
                        },
                        'mss': {
                        },
                        'raw_flags': {
                        },
                        'psh_every_segment': {
                        },
                        'ecn': {
                        },
                        'tcp_window_scale': {
                        },
                        'initial_receive_window': {
                        },
                        'initial_congestion_window': {
                        },
                        'reset_at_end': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'aging_time_data_type': {
                        },
                        'tcp_4_way_close': {
                        },
                        'shutdown_data': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'aging_time': {
                        },
                        'add_timestamps': {
                        },
                        'retries': {
                        },
                        'handshake_data': {
                        },
                        'ack_every_n': {
                        },
                        'retry_quantum_ms': {
                        },
                        'delay_acks_ms': {
                        }
                    },
                    'inflateDeflate': {
                    },
                    'rateDist': {
                        'unit': {
                        },
                        'min': {
                        },
                        'max': {
                        },
                        'unlimited': {
                        },
                        'scope': {
                        },
                        'type': {
                        }
                    },
                    'sessions': {
                        'openFast': {
                        },
                        'closeFast': {
                        },
                        'max': {
                        },
                        'allocationOverride': {
                        },
                        'targetPerSecond': {
                        },
                        'target': {
                        },
                        'targetMatches': {
                        },
                        'maxPerSecond': {
                        },
                        'engine': {
                        },
                        'statDetail': {
                        },
                        'emphasis': {
                        },
                        'maxActive': {
                        }
                    },
                    'loadprofile': {
                        'name': {
                        },
                        'label': {
                        }
                    },
                    'ip': {
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'ip6': {
                        'flowlabel': {
                        },
                        'traffic_class': {
                        },
                        'hop_limit': {
                        }
                    },
                    'srcPortDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    },
                    'tputscalefactor': {
                    },
                    'rampUpProfile': {
                        'min': {
                        },
                        'max': {
                        },
                        'increment': {
                        },
                        'interval': {
                        },
                        'type': {
                        }
                    },
                    'concurrencyscalefactor': {
                    },
                    'delayStart': {
                    },
                    'rampDist': {
                        'upBehavior': {
                        },
                        'down': {
                        },
                        'steadyBehavior': {
                        },
                        'downBehavior': {
                        },
                        'up': {
                        },
                        'synRetryMode': {
                        },
                        'steady': {
                        }
                    },
                    'sfratescalefactor': {
                    },
                    'liveProfile': {
                    }
                },
                '@type:layer3advanced': {
                    'rateDist': {
                        'unit': {
                        },
                        'min': {
                        },
                        'max': {
                        },
                        'rate': {
                        },
                        'increment': {
                        },
                        'type': {
                        },
                        'ramptype': {
                        }
                    },
                    'bidirectional': {
                    },
                    'enableTCP': {
                    },
                    'slowStart': {
                    },
                    'Templates': {
                        'TemplateType': {
                        }
                    },
                    'slowStartFps': {
                    },
                    'duration': {
                        'disable_nd_probes': {
                        },
                        'durationTime': {
                        },
                        'durationFrames': {
                        }
                    },
                    'enablePerStreamStats': {
                    },
                    'tuple_gen_seed': {
                    },
                    'payload': {
                        'data': {
                        },
                        'type': {
                        },
                        'dataWidth': {
                        }
                    },
                    'advancedUDP': {
                        'lengthVal': {
                        },
                        'lengthField': {
                        },
                        'checksumVal': {
                        },
                        'checksumField': {
                        }
                    },
                    'delayStart': {
                    },
                    'payloadAdvanced': {
                        'udfMode': {
                        },
                        'udfLength': {
                        },
                        'udfDataWidth': {
                        },
                        'udfOffset': {
                        }
                    },
                    'sizeDist': {
                        'increment': {
                        },
                        'type': {
                        },
                        'min': {
                        },
                        'rate': {
                        },
                        'mixlen2': {
                        },
                        'mixweight6': {
                        },
                        'mixlen1': {
                        },
                        'mixweight7': {
                        },
                        'mixlen4': {
                        },
                        'mixweight4': {
                        },
                        'mixlen3': {
                        },
                        'mixweight5': {
                        },
                        'mixlen6': {
                        },
                        'mixlen5': {
                        },
                        'mixlen8': {
                        },
                        'mixweight8': {
                        },
                        'mixlen7': {
                        },
                        'mixweight9': {
                        },
                        'mixlen9': {
                        },
                        'mixweight2': {
                        },
                        'max': {
                        },
                        'mixweight3': {
                        },
                        'mixweight1': {
                        },
                        'mixlen10': {
                        },
                        'mixweight10': {
                        },
                        'unit': {
                        }
                    },
                    'advancedIPv4': {
                        'lengthVal': {
                        },
                        'optionHeaderField': {
                        },
                        'optionHeaderData': {
                        },
                        'lengthField': {
                        },
                        'checksumVal': {
                        },
                        'tos': {
                        },
                        'checksumField': {
                        },
                        'ttl': {
                        }
                    },
                    'advancedIPv6': {
                        'flowLabel': {
                        },
                        'lengthVal': {
                        },
                        'extensionHeaderField': {
                        },
                        'lengthField': {
                        },
                        'nextHeader': {
                        },
                        'trafficClass': {
                        },
                        'extensionHeaderData': {
                        },
                        'hopLimit': {
                        }
                    }
                },
                '@type:appsim': {
                    'app': {
                        'replace_streams': {
                        },
                        'streamsPerSuperflow': {
                        },
                        'removedns': {
                        },
                        'fidelity': {
                        }
                    },
                    'tcp': {
                        'disable_ack_piggyback': {
                        },
                        'delay_acks': {
                        },
                        'mss': {
                        },
                        'raw_flags': {
                        },
                        'psh_every_segment': {
                        },
                        'ecn': {
                        },
                        'tcp_window_scale': {
                        },
                        'initial_receive_window': {
                        },
                        'initial_congestion_window': {
                        },
                        'reset_at_end': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'aging_time_data_type': {
                        },
                        'tcp_4_way_close': {
                        },
                        'shutdown_data': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'aging_time': {
                        },
                        'add_timestamps': {
                        },
                        'retries': {
                        },
                        'handshake_data': {
                        },
                        'ack_every_n': {
                        },
                        'retry_quantum_ms': {
                        },
                        'delay_acks_ms': {
                        }
                    },
                    'rateDist': {
                        'unit': {
                        },
                        'min': {
                        },
                        'max': {
                        },
                        'unlimited': {
                        },
                        'scope': {
                        },
                        'type': {
                        }
                    },
                    'sessions': {
                        'openFast': {
                        },
                        'closeFast': {
                        },
                        'max': {
                        },
                        'allocationOverride': {
                        },
                        'targetPerSecond': {
                        },
                        'target': {
                        },
                        'targetMatches': {
                        },
                        'maxPerSecond': {
                        },
                        'engine': {
                        },
                        'statDetail': {
                        },
                        'emphasis': {
                        },
                        'maxActive': {
                        }
                    },
                    'loadprofile': {
                        'name': {
                        },
                        'label': {
                        }
                    },
                    'profile': {
                    },
                    'ip': {
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'experimental': {
                        'tcpSegmentsBurst': {
                        },
                        'unify_l4_bufs': {
                        }
                    },
                    'ssl': {
                        'sslReuseType': {
                        },
                        'server_record_len': {
                        },
                        'client_record_len': {
                        }
                    },
                    'ip6': {
                        'flowlabel': {
                        },
                        'traffic_class': {
                        },
                        'hop_limit': {
                        }
                    },
                    'srcPortDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    },
                    'rampUpProfile': {
                        'min': {
                        },
                        'max': {
                        },
                        'increment': {
                        },
                        'interval': {
                        },
                        'type': {
                        }
                    },
                    'delayStart': {
                    },
                    'rampDist': {
                        'upBehavior': {
                        },
                        'down': {
                        },
                        'steadyBehavior': {
                        },
                        'downBehavior': {
                        },
                        'up': {
                        },
                        'synRetryMode': {
                        },
                        'steady': {
                        }
                    }
                },
                '@type:security_all': {
                    'maxConcurrAttacks': {
                    },
                    'attackRetries': {
                    },
                    'maxPacketsPerSecond': {
                    },
                    'attackPlan': {
                    },
                    'randomSeed': {
                    },
                    'delayStart': {
                    },
                    'attackProfile': {
                    },
                    'attackPlanIterations': {
                    },
                    'attackPlanIterationDelay': {
                    },
                    'maxAttacksPerSecond': {
                    }
                },
                '@type:security_np': {
                    'attackRetries': {
                    },
                    'sessions': {
                        'max': {
                        },
                        'maxPerSecond': {
                        }
                    },
                    'rateDist': {
                        'unit': {
                        },
                        'min': {
                        },
                        'max': {
                        },
                        'unlimited': {
                        },
                        'scope': {
                        },
                        'type': {
                        }
                    },
                    'attackPlan': {
                    },
                    'randomSeed': {
                    },
                    'delayStart': {
                    },
                    'attackProfile': {
                    },
                    'attackPlanIterations': {
                    },
                    'attackPlanIterationDelay': {
                    }
                },
                '@type:layer3': {
                    'rateDist': {
                        'unit': {
                        },
                        'min': {
                        },
                        'max': {
                        },
                        'rate': {
                        },
                        'increment': {
                        },
                        'type': {
                        },
                        'ramptype': {
                        }
                    },
                    'bidirectional': {
                    },
                    'randomizeIP': {
                    },
                    'enableTCP': {
                    },
                    'slowStart': {
                    },
                    'Templates': {
                        'TemplateType': {
                        }
                    },
                    'srcPort': {
                    },
                    'slowStartFps': {
                    },
                    'duration': {
                        'disable_nd_probes': {
                        },
                        'durationTime': {
                        },
                        'durationFrames': {
                        }
                    },
                    'udpSrcPortMode': {
                    },
                    'dstPort': {
                    },
                    'payload': {
                        'data': {
                        },
                        'type': {
                        },
                        'dataWidth': {
                        }
                    },
                    'syncIP': {
                    },
                    'addrGenMode': {
                    },
                    'maxStreams': {
                    },
                    'dstPortMask': {
                    },
                    'udpDstPortMode': {
                    },
                    'advancedUDP': {
                        'lengthVal': {
                        },
                        'lengthField': {
                        },
                        'checksumVal': {
                        },
                        'checksumField': {
                        }
                    },
                    'delayStart': {
                    },
                    'payloadAdvanced': {
                        'udfMode': {
                        },
                        'udfLength': {
                        },
                        'udfDataWidth': {
                        },
                        'udfOffset': {
                        }
                    },
                    'sizeDist': {
                        'increment': {
                        },
                        'type': {
                        },
                        'min': {
                        },
                        'rate': {
                        },
                        'mixlen2': {
                        },
                        'mixweight6': {
                        },
                        'mixlen1': {
                        },
                        'mixweight7': {
                        },
                        'mixlen4': {
                        },
                        'mixweight4': {
                        },
                        'mixlen3': {
                        },
                        'mixweight5': {
                        },
                        'mixlen6': {
                        },
                        'mixlen5': {
                        },
                        'mixlen8': {
                        },
                        'mixweight8': {
                        },
                        'mixlen7': {
                        },
                        'mixweight9': {
                        },
                        'mixlen9': {
                        },
                        'mixweight2': {
                        },
                        'max': {
                        },
                        'mixweight3': {
                        },
                        'mixweight1': {
                        },
                        'mixlen10': {
                        },
                        'mixweight10': {
                        },
                        'unit': {
                        }
                    },
                    'advancedIPv4': {
                        'lengthVal': {
                        },
                        'optionHeaderField': {
                        },
                        'optionHeaderData': {
                        },
                        'lengthField': {
                        },
                        'checksumVal': {
                        },
                        'tos': {
                        },
                        'checksumField': {
                        },
                        'ttl': {
                        }
                    },
                    'srcPortMask': {
                    },
                    'advancedIPv6': {
                        'flowLabel': {
                        },
                        'lengthVal': {
                        },
                        'extensionHeaderField': {
                        },
                        'lengthField': {
                        },
                        'nextHeader': {
                        },
                        'trafficClass': {
                        },
                        'extensionHeaderData': {
                        },
                        'hopLimit': {
                        }
                    }
                },
                '@type:layer4': {
                    'tcp': {
                        'disable_ack_piggyback': {
                        },
                        'delay_acks': {
                        },
                        'mss': {
                        },
                        'raw_flags': {
                        },
                        'psh_every_segment': {
                        },
                        'ecn': {
                        },
                        'tcp_window_scale': {
                        },
                        'initial_receive_window': {
                        },
                        'initial_congestion_window': {
                        },
                        'reset_at_end': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'aging_time_data_type': {
                        },
                        'tcp_4_way_close': {
                        },
                        'shutdown_data': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'aging_time': {
                        },
                        'add_timestamps': {
                        },
                        'retries': {
                        },
                        'handshake_data': {
                        },
                        'ack_every_n': {
                        },
                        'retry_quantum_ms': {
                        },
                        'delay_acks_ms': {
                        }
                    },
                    'rateDist': {
                        'unit': {
                        },
                        'min': {
                        },
                        'max': {
                        },
                        'unlimited': {
                        },
                        'scope': {
                        },
                        'type': {
                        }
                    },
                    'sessions': {
                        'openFast': {
                        },
                        'closeFast': {
                        },
                        'max': {
                        },
                        'allocationOverride': {
                        },
                        'targetPerSecond': {
                        },
                        'target': {
                        },
                        'targetMatches': {
                        },
                        'maxPerSecond': {
                        },
                        'engine': {
                        },
                        'statDetail': {
                        },
                        'emphasis': {
                        },
                        'maxActive': {
                        }
                    },
                    'loadprofile': {
                        'name': {
                        },
                        'label': {
                        }
                    },
                    'ip': {
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'ip6': {
                        'flowlabel': {
                        },
                        'traffic_class': {
                        },
                        'hop_limit': {
                        }
                    },
                    'srcPortDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    },
                    'rampUpProfile': {
                        'min': {
                        },
                        'max': {
                        },
                        'increment': {
                        },
                        'interval': {
                        },
                        'type': {
                        }
                    },
                    'delayStart': {
                    },
                    'payload': {
                        'add_timestamp': {
                        },
                        'data': {
                        },
                        'http_type': {
                        },
                        'transport': {
                        },
                        'type': {
                        }
                    },
                    'rampDist': {
                        'upBehavior': {
                        },
                        'down': {
                        },
                        'steadyBehavior': {
                        },
                        'downBehavior': {
                        },
                        'up': {
                        },
                        'synRetryMode': {
                        },
                        'steady': {
                        }
                    },
                    'packetsPerSession': {
                    },
                    'payloadSizeDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    },
                    'dstPortDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    }
                },
                '@type:playback': {
                    'tcp': {
                        'disable_ack_piggyback': {
                        },
                        'delay_acks': {
                        },
                        'mss': {
                        },
                        'raw_flags': {
                        },
                        'psh_every_segment': {
                        },
                        'ecn': {
                        },
                        'tcp_window_scale': {
                        },
                        'initial_receive_window': {
                        },
                        'initial_congestion_window': {
                        },
                        'reset_at_end': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'aging_time_data_type': {
                        },
                        'tcp_4_way_close': {
                        },
                        'shutdown_data': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'aging_time': {
                        },
                        'add_timestamps': {
                        },
                        'retries': {
                        },
                        'handshake_data': {
                        },
                        'ack_every_n': {
                        },
                        'retry_quantum_ms': {
                        },
                        'delay_acks_ms': {
                        }
                    },
                    'rateDist': {
                        'unit': {
                        },
                        'min': {
                        },
                        'max': {
                        },
                        'unlimited': {
                        },
                        'scope': {
                        },
                        'type': {
                        }
                    },
                    'sessions': {
                        'openFast': {
                        },
                        'closeFast': {
                        },
                        'max': {
                        },
                        'allocationOverride': {
                        },
                        'targetPerSecond': {
                        },
                        'target': {
                        },
                        'targetMatches': {
                        },
                        'maxPerSecond': {
                        },
                        'engine': {
                        },
                        'statDetail': {
                        },
                        'emphasis': {
                        },
                        'maxActive': {
                        }
                    },
                    'loadprofile': {
                        'name': {
                        },
                        'label': {
                        }
                    },
                    'ip': {
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'modification': {
                        'startpacket': {
                        },
                        'originalport': {
                        },
                        'newport': {
                        },
                        'replay': {
                        },
                        'bpfstring': {
                        },
                        'single': {
                        },
                        'loopcount': {
                        },
                        'endpacket': {
                        },
                        'independentflows': {
                        },
                        'serveripinjection': {
                        }
                    },
                    'ip6': {
                        'flowlabel': {
                        },
                        'traffic_class': {
                        },
                        'hop_limit': {
                        }
                    },
                    'srcPortDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    },
                    'rampUpProfile': {
                        'min': {
                        },
                        'max': {
                        },
                        'increment': {
                        },
                        'interval': {
                        },
                        'type': {
                        }
                    },
                    'delayStart': {
                    },
                    'file': {
                    },
                    'rampDist': {
                        'upBehavior': {
                        },
                        'down': {
                        },
                        'steadyBehavior': {
                        },
                        'downBehavior': {
                        },
                        'up': {
                        },
                        'synRetryMode': {
                        },
                        'steady': {
                        }
                    },
                    'behavior': {
                    }
                },
                '@type:layer2': {
                    'bidirectional': {
                    },
                    'maxStreams': {
                    },
                    'rateDist': {
                        'unit': {
                        },
                        'min': {
                        },
                        'max': {
                        },
                        'rate': {
                        },
                        'increment': {
                        },
                        'type': {
                        },
                        'ramptype': {
                        }
                    },
                    'advanced': {
                        'ethTypeField': {
                        },
                        'ethTypeVal': {
                        }
                    },
                    'slowStart': {
                    },
                    'slowStartFps': {
                    },
                    'duration': {
                        'disable_nd_probes': {
                        },
                        'durationTime': {
                        },
                        'durationFrames': {
                        }
                    },
                    'delayStart': {
                    },
                    'payloadAdvanced': {
                        'udfMode': {
                        },
                        'udfLength': {
                        },
                        'udfDataWidth': {
                        },
                        'udfOffset': {
                        }
                    },
                    'sizeDist': {
                        'increment': {
                        },
                        'type': {
                        },
                        'min': {
                        },
                        'rate': {
                        },
                        'mixlen2': {
                        },
                        'mixweight6': {
                        },
                        'mixlen1': {
                        },
                        'mixweight7': {
                        },
                        'mixlen4': {
                        },
                        'mixweight4': {
                        },
                        'mixlen3': {
                        },
                        'mixweight5': {
                        },
                        'mixlen6': {
                        },
                        'mixlen5': {
                        },
                        'mixlen8': {
                        },
                        'mixweight8': {
                        },
                        'mixlen7': {
                        },
                        'mixweight9': {
                        },
                        'mixlen9': {
                        },
                        'mixweight2': {
                        },
                        'max': {
                        },
                        'mixweight3': {
                        },
                        'mixweight1': {
                        },
                        'mixlen10': {
                        },
                        'mixweight10': {
                        },
                        'unit': {
                        }
                    },
                    'payload': {
                        'data': {
                        },
                        'type': {
                        },
                        'dataWidth': {
                        }
                    }
                },
                '@type:stackscrambler': {
                    'tcp': {
                        'disable_ack_piggyback': {
                        },
                        'delay_acks': {
                        },
                        'mss': {
                        },
                        'raw_flags': {
                        },
                        'psh_every_segment': {
                        },
                        'ecn': {
                        },
                        'tcp_window_scale': {
                        },
                        'initial_receive_window': {
                        },
                        'initial_congestion_window': {
                        },
                        'reset_at_end': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'aging_time_data_type': {
                        },
                        'tcp_4_way_close': {
                        },
                        'shutdown_data': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'aging_time': {
                        },
                        'add_timestamps': {
                        },
                        'retries': {
                        },
                        'handshake_data': {
                        },
                        'ack_every_n': {
                        },
                        'retry_quantum_ms': {
                        },
                        'delay_acks_ms': {
                        }
                    },
                    'scrambleOptions': {
                        'maxCorruptions': {
                        },
                        'badIPFlags': {
                        },
                        'badIPFragOffset': {
                        },
                        'badIPLength': {
                        },
                        'badUrgentPointer': {
                        },
                        'badIPFlowLabel': {
                        },
                        'badEthType': {
                        },
                        'badTCPOptions': {
                        },
                        'badGTPNext': {
                        },
                        'handshakeTCP': {
                        },
                        'badIPChecksum': {
                        },
                        'badSCTPLength': {
                        },
                        'badTCPFlags': {
                        },
                        'badICMPType': {
                        },
                        'badIPTTL': {
                        },
                        'badIPProtocol': {
                        },
                        'badSCTPFlags': {
                        },
                        'badGTPFlags': {
                        },
                        'badIPVersion': {
                        },
                        'badL4HeaderLength': {
                        },
                        'badL4Checksum': {
                        },
                        'badIPOptions': {
                        },
                        'badSCTPType': {
                        },
                        'badSCTPChecksum': {
                        },
                        'badGTPNpdu': {
                        },
                        'badICMPCode': {
                        },
                        'badSCTPVerificationTag': {
                        },
                        'badIPTOS': {
                        },
                        'badIPTotalLength': {
                        },
                        'badGTPLen': {
                        },
                        'badGTPType': {
                        },
                        'badGTPSeqno': {
                        }
                    },
                    'rateDist': {
                        'unit': {
                        },
                        'min': {
                        },
                        'max': {
                        },
                        'unlimited': {
                        },
                        'scope': {
                        },
                        'type': {
                        }
                    },
                    'sessions': {
                        'openFast': {
                        },
                        'closeFast': {
                        },
                        'max': {
                        },
                        'allocationOverride': {
                        },
                        'targetPerSecond': {
                        },
                        'target': {
                        },
                        'targetMatches': {
                        },
                        'maxPerSecond': {
                        },
                        'engine': {
                        },
                        'statDetail': {
                        },
                        'emphasis': {
                        },
                        'maxActive': {
                        }
                    },
                    'loadprofile': {
                        'name': {
                        },
                        'label': {
                        }
                    },
                    'ip': {
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'ip6': {
                        'flowlabel': {
                        },
                        'traffic_class': {
                        },
                        'hop_limit': {
                        }
                    },
                    'prng': {
                        'seed': {
                        },
                        'offset': {
                        }
                    },
                    'srcPortDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    },
                    'rampUpProfile': {
                        'min': {
                        },
                        'max': {
                        },
                        'increment': {
                        },
                        'interval': {
                        },
                        'type': {
                        }
                    },
                    'delayStart': {
                    },
                    'payload': {
                        'data': {
                        },
                        'transport': {
                        },
                        'type': {
                        }
                    },
                    'rampDist': {
                        'upBehavior': {
                        },
                        'down': {
                        },
                        'steadyBehavior': {
                        },
                        'downBehavior': {
                        },
                        'up': {
                        },
                        'synRetryMode': {
                        },
                        'steady': {
                        }
                    },
                    'payloadSizeDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    },
                    'dstPortDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    }
                },
                '@type:clientsim': {
                    'app': {
                        'replace_streams': {
                        },
                        'streamsPerSuperflow': {
                        },
                        'removedns': {
                        },
                        'fidelity': {
                        }
                    },
                    'tcp': {
                        'disable_ack_piggyback': {
                        },
                        'delay_acks': {
                        },
                        'mss': {
                        },
                        'raw_flags': {
                        },
                        'psh_every_segment': {
                        },
                        'ecn': {
                        },
                        'tcp_window_scale': {
                        },
                        'initial_receive_window': {
                        },
                        'initial_congestion_window': {
                        },
                        'reset_at_end': {
                        },
                        'dynamic_receive_window_size': {
                        },
                        'tcp_connect_delay_ms': {
                        },
                        'aging_time_data_type': {
                        },
                        'tcp_4_way_close': {
                        },
                        'shutdown_data': {
                        },
                        'tcp_keepalive_timer': {
                        },
                        'aging_time': {
                        },
                        'add_timestamps': {
                        },
                        'retries': {
                        },
                        'handshake_data': {
                        },
                        'ack_every_n': {
                        },
                        'retry_quantum_ms': {
                        },
                        'delay_acks_ms': {
                        }
                    },
                    'rateDist': {
                        'unit': {
                        },
                        'min': {
                        },
                        'max': {
                        },
                        'unlimited': {
                        },
                        'scope': {
                        },
                        'type': {
                        }
                    },
                    'sessions': {
                        'openFast': {
                        },
                        'closeFast': {
                        },
                        'max': {
                        },
                        'allocationOverride': {
                        },
                        'targetPerSecond': {
                        },
                        'target': {
                        },
                        'targetMatches': {
                        },
                        'maxPerSecond': {
                        },
                        'engine': {
                        },
                        'statDetail': {
                        },
                        'emphasis': {
                        },
                        'maxActive': {
                        }
                    },
                    'loadprofile': {
                        'name': {
                        },
                        'label': {
                        }
                    },
                    'ip': {
                        'tos': {
                        },
                        'ttl': {
                        }
                    },
                    'ssl': {
                        'sslReuseType': {
                        },
                        'server_record_len': {
                        },
                        'client_record_len': {
                        }
                    },
                    'ip6': {
                        'flowlabel': {
                        },
                        'traffic_class': {
                        },
                        'hop_limit': {
                        }
                    },
                    'srcPortDist': {
                        'min': {
                        },
                        'max': {
                        },
                        'type': {
                        }
                    },
                    'rampUpProfile': {
                        'min': {
                        },
                        'max': {
                        },
                        'increment': {
                        },
                        'interval': {
                        },
                        'type': {
                        }
                    },
                    'delayStart': {
                    },
                    'rampDist': {
                        'upBehavior': {
                        },
                        'down': {
                        },
                        'steadyBehavior': {
                        },
                        'downBehavior': {
                        },
                        'up': {
                        },
                        'synRetryMode': {
                        },
                        'steady': {
                        }
                    },
                    'superflow': {
                    }
                },
                'createdOn': {
                },
                'tags': {
                    'tag': [{
                        'id': {
                        },
                        'type': {
                        },
                        'domainId': {
                            'name': {
                            },
                            'iface': {
                            },
                            'external': {
                            }
                        }
                    }]
                },
                'revision': {
                },
                'lockedBy': {
                },
                'createdBy': {
                },
                'reportResults': {
                },
                'timeline': {
                    'timesegment': [{
                        'label': {
                        },
                        'size': {
                        },
                        'type': {
                        }
                    }]
                },
                'id': {
                },
                'clazz': {
                }
            }],
            'lockedBy': {
            },
            'createdBy': {
            },
            'name': {
            },
            'clazz': {
            },
            'operations': {
                'load': [{
                }],
                'new': [{
                }],
                'search': [{
                }],
                'delete': [{
                }],
                'saveAs': [{
                }],
                'save': [{
                }],
                'stopRun': [{
                }],
                'exportModel': [{
                }],
                'clone': [{
                }],
                'add': [{
                }],
                'realTimeStats': [{
                }],
                'run': [{
                }],
                'importModel': [{
                }]
            }
        },
        'appProfile': {
            'schemaver': {
            },
            'lockedBy': {
            },
            'createdBy': {
            },
            'author': {
            },
            'name': {
            },
            'superflow': [{
                'percentFlows': {
                },
                'schemaver': {
                },
                'seed': {
                },
                'hosts': [{
                    'params': {
                        'iface': {
                        },
                        'hostname': {
                        },
                        'ip': {
                            'type': {
                            }
                        }
                    },
                    'id': {
                    }
                }],
                'author': {
                },
                'estimate_bytes': {
                },
                'estimate_flows': {
                },
                'weight': {
                },
                'description': {
                },
                'label': {
                },
                'createdOn': {
                },
                'revision': {
                },
                'lockedBy': {
                },
                'flows': [{
                    'singleNP': {
                    },
                    'name': {
                    },
                    'from': {
                    },
                    'label': {
                    },
                    'id': {
                    },
                    'to': {
                    },
                    'params': {
                    },
                    'flowcount': {
                    }
                }],
                'generated': {
                },
                'createdBy': {
                },
                'percentBandwidth': {
                },
                'name': {
                },
                'actions': [{
                    'flowlabel': {
                    },
                    'gotoBlock': {
                    },
                    'exflows': {
                    },
                    'matchBlock': {
                    },
                    'id': {
                    },
                    'source': {
                    },
                    'label': {
                    },
                    'type': {
                    },
                    'params': {
                    },
                    'flowid': {
                    }
                }],
                'clazz': {
                }
            }],
            'description': {
            },
            'label': {
            },
            'createdOn': {
            },
            'clazz': {
            },
            'revision': {
            },
            'operations': {
                'load': [{
                }],
                'new': [{
                }],
                'search': [{
                }],
                'delete': [{
                }],
                'add': [{
                }],
                'saveAs': [{
                }],
                'save': [{
                }],
                'remove': [{
                }],
                'exportAppProfile': [{
                }],
                'importAppProfile': [{
                }]
            }
        },
        'topology': {
            'ixoslicensed': {
            },
            'ixos': {
            },
            'runningTest': [{
                'phase': {
                },
                'timeRemaining': {
                },
                'runtime': {
                },
                'label': {
                },
                'completed': {
                },
                'initProgress': {
                },
                'result': {
                },
                'port': [{
                }],
                'capturing': {
                },
                'progress': {
                },
                'testid': {
                },
                'state': {
                },
                'user': {
                },
                'currentTest': {
                }
            }],
            'model': {
            },
            'slot': [{
                'port': [{
                    'owner': {
                    },
                    'number': {
                    },
                    'note': {
                    },
                    'exportProgress': {
                    },
                    'reservedBy': {
                    },
                    'capturing': {
                    },
                    'model': {
                    },
                    'id': {
                    },
                    'group': {
                    },
                    'link': {
                    },
                    'state': {
                    },
                    'speed': {
                    }
                }],
                'model': {
                },
                'mode': {
                },
                'state': {
                },
                'id': {
                }
            }],
            'serialNumber': {
            },
            'operations': {
                'reserve': [{
                }],
                'unreserve': [{
                }],
                'stopRun': [{
                }],
                'reboot': [{
                }],
                'run': [{
                }],
                'setCardMode': [{
                }],
                'setCardSpeed': [{
                }],
                'setCardFanout': [{
                }],
                'setPerfAcc': [{
                }]
            }
        },
        'loadProfile': {
            'phase': [{
                'duration': {
                },
                'phaseId': {
                },
                'type': {
                },
                'phaseParameters': {
                    'sessions.max': {
                    },
                    'sessions.maxPerSecond': {
                    },
                    'rateDist.unit': {
                    },
                    'rateDist.min': {
                    },
                    'rampDist.steadyBehavior': {
                    },
                    'rateDist.type': {
                    },
                    'rateDist.scope': {
                    }
                }
            }],
            'schemaver': {
            },
            'author': {
            },
            'regen': {
            },
            'description': {
            },
            'label': {
            },
            'createdOn': {
            },
            'summaryData': {
                'deviceType': {
                },
                'unknownUdpAppNames': {
                },
                'unknownSslSuperflowName': {
                },
                'magicNumber': {
                },
                'downloadBytesSum': {
                },
                'version': {
                },
                'phaseDuration': {
                },
                'unknownTcpAppNames': {
                },
                'uploadBytesSum': {
                },
                'summaryName': {
                },
                'basisOfRegeneration': {
                },
                'activeFlowsSum': {
                },
                'miniSlotDuration': {
                },
                'unknownSslAppNames': {
                },
                'dynamicSuperflowName': {
                },
                'appStat': [{
                }],
                'startTime': {
                },
                'endTime': {
                },
                'dynamicAppNames': {
                }
            },
            'revision': {
            },
            'lockedBy': {
            },
            'createdBy': {
            },
            'name': {
            },
            'clazz': {
            },
            'presets': [{
                'phase': [{
                    'duration': {
                    },
                    'phaseId': {
                    },
                    'type': {
                    },
                    'phaseParameters': {
                        'sessions.max': {
                        },
                        'sessions.maxPerSecond': {
                        },
                        'rateDist.unit': {
                        },
                        'rateDist.min': {
                        },
                        'rampDist.steadyBehavior': {
                        },
                        'rateDist.type': {
                        },
                        'rateDist.scope': {
                        }
                    }
                }],
                'schemaver': {
                },
                'author': {
                },
                'regen': {
                },
                'description': {
                },
                'label': {
                },
                'createdOn': {
                },
                'summaryData': {
                    'deviceType': {
                    },
                    'unknownUdpAppNames': {
                    },
                    'unknownSslSuperflowName': {
                    },
                    'magicNumber': {
                    },
                    'downloadBytesSum': {
                    },
                    'version': {
                    },
                    'phaseDuration': {
                    },
                    'unknownTcpAppNames': {
                    },
                    'uploadBytesSum': {
                    },
                    'summaryName': {
                    },
                    'basisOfRegeneration': {
                    },
                    'activeFlowsSum': {
                    },
                    'miniSlotDuration': {
                    },
                    'unknownSslAppNames': {
                    },
                    'dynamicSuperflowName': {
                    },
                    'appStat': [{
                    }],
                    'startTime': {
                    },
                    'endTime': {
                    },
                    'dynamicAppNames': {
                    }
                },
                'revision': {
                },
                'lockedBy': {
                },
                'createdBy': {
                },
                'name': {
                },
                'clazz': {
                }
            }],
            'operations': {
                'save': [{
                }],
                'saveAs': [{
                }],
                'load': [{
                }]
            }
        },
        'strikeList': {
            'schemaver': {
            },
            'author': {
            },
            'description': {
            },
            'label': {
            },
            'queryString': {
            },
            'params': {
            },
            'createdOn': {
            },
            'smart': {
            },
            'revision': {
            },
            'lockedBy': {
            },
            'createdBy': {
            },
            'name': {
            },
            'clazz': {
            },
            'numStrikes': {
            },
            'operations': {
                'exportStrikeList': [{
                }],
                'delete': [{
                }],
                'saveAs': [{
                }],
                'save': [{
                }],
                'importStrikeList': [{
                }],
                'load': [{
                }],
                'new': [{
                }],
                'remove': [{
                }],
                'search': [{
                }],
                'add': [{
                }]
            }
        },
        'superflow': {
            'percentFlows': {
            },
            'schemaver': {
            },
            'seed': {
            },
            'hosts': [{
                'params': {
                    'iface': {
                    },
                    'hostname': {
                    },
                    'ip': {
                        'type': {
                        }
                    }
                },
                'id': {
                }
            }],
            'author': {
            },
            'estimate_bytes': {
            },
            'estimate_flows': {
            },
            'weight': {
            },
            'description': {
            },
            'label': {
            },
            'createdOn': {
            },
            'revision': {
            },
            'lockedBy': {
            },
            'flows': [{
                'singleNP': {
                },
                'name': {
                },
                'from': {
                },
                'label': {
                },
                'id': {
                },
                'to': {
                },
                'params': {
                },
                'flowcount': {
                }
            }],
            'generated': {
            },
            'createdBy': {
            },
            'percentBandwidth': {
            },
            'name': {
            },
            'actions': [{
                'flowlabel': {
                },
                'gotoBlock': {
                },
                'exflows': {
                },
                'matchBlock': {
                },
                'id': {
                },
                'source': {
                },
                'label': {
                },
                'type': {
                },
                'params': {
                },
                'flowid': {
                }
            }],
            'clazz': {
            },
            'operations': {
                'load': [{
                }],
                'new': [{
                }],
                'removeFlow': [{
                }],
                'search': [{
                }],
                'delete': [{
                }],
                'removeAction': [{
                }],
                'saveAs': [{
                }],
                'save': [{
                }],
                'addFlow': [{
                }],
                'addAction': [{
                }]
            }
        },
        'reports': {
            'endtime': {
            },
            'starttime': {
            },
            'label': {
            },
            'testname': {
            },
            'network': {
            },
            'duration': {
            },
            'result': {
            },
            'size': {
            },
            'isPartOfResiliency': {
            },
            'name': {
            },
            'iteration': {
            },
            'testid': {
            },
            'user': {
            },
            'operations': {
                'search': [{
                }],
                'delete': [{
                }],
                'exportReport': [{
                }]
            }
        },
        'capture': {
            'operations': {
                'importCapture': [{
                }]
            }
        }
    }

    @staticmethod
    def _get_from_model(path):
        model_data = DataModelMeta._dataModel
        model_path = ""
        for path_part in path.split('/'):
            if len(path_part) == 0: continue
            if isinstance(model_data, list):
                model_data = model_data[0]
                continue
            if path_part not in model_data: return (None, None)
            model_data = model_data[path_part]
            model_path = model_path + "/" + path_part
        return (model_path, model_data)

    @staticmethod
    def _decorate_model_object(obj):
        (data_model_path, data_model) = DataModelMeta._get_from_model(obj.__data_model_path__())
        if data_model is None:
            return obj
        if isinstance(data_model, list):
            setattr(obj, '_getitem_', lambda x: DataModelProxy(wrapper=obj._wrapper, name=str(x), path=obj.__full_path__(), model_path=obj.__data_model_path__()))
            return obj
        for key in data_model:
            if key.startswith("@"):
                continue
            if key == 'operations':
                for operation in data_model[key]:
                    if obj.__full_path__().replace("/", "") == '':
                        continue
                    method_name = data_model_path.replace("/", "_") + '_operations_' + operation
                    setattr(obj, operation, obj._wrapper.__getattribute__(method_name).__get__(obj))
                    setattr(getattr(obj, operation).__func__, '__name__', operation)
            setattr(obj, key, DataModelProxy(wrapper=obj._wrapper, name=key, path=obj.__full_path__(), model_path=obj.__data_model_path__()))
        for key in data_model:
            if not key.startswith("@") or ":" not in key:
                continue
            [fieldName, fieldValue] = key.split(":")
            fieldName = fieldName.replace("@", "")
            if obj._wrapper._get(obj.__full_path__()+"/"+fieldName) != fieldValue:
                continue
            for extField in data_model[key]:
                ext_path = obj.__full_path__()
                ext_dm_path = obj.__data_model_path__() + "/" + key
                setattr(obj, extField, DataModelProxy(wrapper=obj._wrapper, name=extField, path=ext_path, model_path=ext_dm_path))
            print(key)
        return obj

    def __call__(cls, *args, **kwds):
        return DataModelMeta._decorate_model_object(type.__call__(cls, *args, **kwds))

class DataModelProxy(with_metaclass(DataModelMeta, object)):
    def __init__(self, wrapper, name,  path='', model_path=None):
        self._wrapper = wrapper
        self._name = name
        self._path = path
        if model_path is None:
            self._model_path = self._path
        else:
            self._model_path = model_path

    def __full_path__(self):
        return '%s/%s' % (self._path, self._name)

    def __data_model_path__(self):
        return '%s/%s' % (self._model_path, self._name)

    def __url__(self):
        return 'https://%s/bps/api/v2/core%s' % (self._wrapper.host, self.__full_path__())

    def __repr__(self):
        return 'proxy object for \'%s\' ' % (self.__url__())

    def __getitem__(self, item):
        return self._getitem_(item)

    def get(self, responseDepth=None, **kwargs):
        return self._wrapper._get(self._path+'/'+self._name, responseDepth, **kwargs)

    def patch(self, value):
        return self._wrapper._patch(self._path+'/'+self._name, value)

    def set(self, value):
        return self.patch(value)

    def put(self, value):
        return self._wrapper._put(self._path+'/'+self._name, value)

    def delete(self):
        return self._wrapper._delete(self._path+'/'+self._name)

'''
class DataModelProxy_backup(object, metaclass=DataModelMeta):
    def __init__(self, wrapper, name,  path='', model_path=None):
        self._wrapper = wrapper
        self._name = name
        self._path = path
        if model_path is None:
            self._model_path = self._path
        else:
            self._model_path = model_path

    def __full_path__(self):
        return '%s/%s' % (self._path, self._name)

    def __data_model_path__(self):
        return '%s/%s' % (self._model_path, self._name)

    def __url__(self):
        return 'https://%s/bps/api/v2/core%s' % (self._wrapper.host, self.__full_path__())

    def __repr__(self):
        return 'proxy object for \'%s\' ' % (self.__url__())

    def __getitem__(self, item):
        return self._getitem_(item)

    def get(self, responseDepth=None, **kwargs):
        return self._wrapper._get(self._path+'/'+self._name, responseDepth, **kwargs)

    def patch(self, value):
        return self._wrapper._patch(self._path+'/'+self._name, value)

    def set(self, value):
        return self.patch(value)

    def put(self, value):
        return self._wrapper._put(self._path+'/'+self._name, value)

    def delete(self):
        return self._wrapper._delete(self._path+'/'+self._name)
'''
