# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division

import copy
import json
import ssl
import string
import textwrap
import threading
import time
import uuid
from copy import deepcopy
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin
from warnings import warn
try:
    import http.client as httplib
except ImportError:
    import httplib
try:
    from http.cookiejar import CookieJar
except ImportError:
    from cookielib import CookieJar
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

try:
    basestring = basestring
except NameError:
    basestring = str
	
try:
    long = long
except NameError:
    long = int
	
# a list of supported scriptapi versions.
kSupportedScriptApiVersions = ['v1']

# default SSL protocol for requests.Session instance
kDefaultSslProtocol = ssl.PROTOCOL_TLSv1_1

# Properties that require renaming on the way in.
#   Sometimes json includes names that mess up our python, so we rename them to something safe,
#   and then rename them back before we use them
kJsonPropertyRenameMap = {"self": "_self_", "$type": "objectType"}
# A map back the other way
kJsonRenamedPropertyMap = {}
for key, value in kJsonPropertyRenameMap.items():
    kJsonRenamedPropertyMap[value] = key

try:
    requests.packages.urllib3.disable_warnings()
except AttributeError:
    # not all versions of the requests library have this functionality
    pass


def waitForProperty(obj, propertyName, targetValues, validValues=[], invalidValues=[], timeout=None, trace=False):
    """Utility method to wait for a property on an object to change to an expected value.

    Object must support getattr and implement the httpRefresh() method. Object is polled once per second.
    @param obj: the object to query
    @param propertyName: the name of the property to check
    @param targetValues: a collection with the list of values for propertyName to wait for
    @param validValues: a collection with a list of values for propertyName that are allowed (any other causes exception)
    @param invalidValues: a collection with a list of values for propertyName that cause an exception to be raised
    @param timeout: max number of seconds to wait
    @param trace: if True, then the property value is printed out each polling cycle.
    """
    startTime = time.time()
    while True:
        obj.httpRefresh()
        value = getattr(obj, propertyName)
        if trace:
            print("property %s = %s" % (propertyName, value))
        if value in targetValues:
            return
        if (validValues and value not in validValues) or value in invalidValues:
            raise WebException("waitForProperty(): %s has invalid %s == %s" % (obj.__class__, propertyName, value))
        if timeout and time.time() - startTime > timeout:
            raise WebApiTimeout("waitForProperty(): %s timed out waiting for %s in %s" % (obj.__class__, propertyName, targetValues))
        time.sleep(1)


def checkForPropertyValue(obj, propertyName, expectedValues, refresh=False):
    """Utility method to check if a property on an object has one of the expected values.
    @param obj: the object to query
    @param propertyName: the name of the property to check
    @param expectedValues: a collection with the list of values for propertyName to check
    @param refresh: if True, then the object is refreshed using its httpRefresh() method
    """
    if refresh:
        obj.httpRefresh()
    value = getattr(obj, propertyName)
    if value in expectedValues:
        return True
    return False


class Validators(object):
    """A set of static validator methods for use in this module.
    """

    kFormatIsRequired = "The '%s' parameter is required."
    kFormatRequiresType = "The '%s' parameter requires %s. Got a(n) %s: %s."

    @staticmethod
    def checkString(param, paramName):
        if not isinstance(param, basestring):
            raise ValueError(Validators.kFormatRequiresType % (paramName, 'a string', type(param), param))

    @staticmethod
    def checkNonEmptyString(param, paramName):
        Validators.checkString(param, paramName)
        if not param:
            raise ValueError(Validators.kFormatIsRequired % paramName)

    @staticmethod
    def checkNotNone(param, paramName):
        if param is None:
            raise ValueError("The '%s' parameter may not be None." % paramName)

    @staticmethod
    def checkSessionType(sessionType, paramName="sessionType"):
        Validators.checkNonEmptyString(sessionType, paramName)

    @staticmethod
    def checkConfigName(configName, paramName="configName"):
        Validators.checkNonEmptyString(configName, paramName)

    @staticmethod
    def checkFile(fileParam, paramName):
        if isinstance(fileParam, basestring):
            raise ValueError(Validators.kFormatRequiresType % (paramName, 'a file handle', type(fileParam), fileParam))
        if not fileParam:
            raise ValueError(Validators.kFormatIsRequired % paramName)

    @staticmethod
    def checkInt(intParam, paramName):
        try:
            int(intParam)
        except:
            raise ValueError("The '%s' parameter must be an integer. Was %s." % (paramName, intParam))

    @staticmethod
    def checkLong(longParam, paramName):
        try:
            long(longParam)
        except:
            raise ValueError("The '%s' parameter must be a long. Was %s." % (paramName, longParam))

    @staticmethod
    def checkList(param, paramName):
        if not isinstance(param, list):
            raise ValueError(Validators.kFormatRequiresType % (paramName, 'a list', type(param), param))


class _JsonEncoder(json.JSONEncoder):
    """Internal class to expose an object's __dict__ as the json representation."""

    def default(self, obj):
        if isinstance(obj, dict) or isinstance(obj, list):
            return super(_JsonEncoder, self).default(obj)
        # proxy object
        return obj._jsonProperties_


class WebObjectLocation(object):
    """An object representing the source of a web object.

    This is populated by the webApi get and post 
    methods, and later by put() methods, to return
    the object from whence it came.
    """
    kLinksParam = "links"
    kEmbeddedParam = "embedded"

    def __init__(self, convention, url, *urlExts):
        Validators.checkNotNone(convention, "convention")
        Validators.checkString(url, "url")
        for urlExt in urlExts:
            url = HttpConvention.urljoin(url, urlExt)
        self.convention = convention
        self.url = url

    def httpPut(self, target):
        """Put target object back to the contained location"""
        return self.convention.httpPut(self.url, target)

    def httpPatch(self, target):
        """Patch the target object on the contained location"""
        return self.convention.httpPatch(self.url, target)

    def httpGet(self):
        """Regets the object from the original location and returns it (as a WebObject)."""
        return self.convention.httpGet(self.url)

    def httpGetProperty(self, url):
        """Gets a non-shallow property of this object"""
        return self.convention.httpGet(url, params={self.kLinksParam: True, self.kEmbeddedParam: False})

    def httpDelete(self):
        """Delete the current object object from the web server"""
        return self.convention.httpDelete(self.url)

    def httpPost(self, data):
        """Create a new object on the web server"""
        return self.convention.httpPost(self.url, data)


class WebObjectBase(object):
    """ The base class for Json Proxy object and list.

    Note that internal and seldom-used method names are embedded in underscores ("_")
    to help prevent name collosions with properties defined in proxied JSON text.
    """
    kLockedProperty = "_locked_"
    kSourceProperty = "_source_"
    kChangedProperty = "_changed_"
    kLinksProperty = "links"
    kSelfLink = "self"
    kAlwaysSend = set(["id", "$type"])
    kNonJsonProperties = [kLockedProperty, kSourceProperty, kLinksProperty]

    def __init__(self, source=None):
        self._locked_ = False
        self._setSource_(source)

    def __setattr__(self, propertyName, value):
        """Internal method to implement lock/unlock."""
        # rename the properties back to their original
        propertyName = kJsonRenamedPropertyMap.get(propertyName, propertyName)
        if propertyName not in [self.kLockedProperty, self.kChangedProperty] and self._locked_ and propertyName not in self.__dict__:
            try:
                links = super(WebObjectBase, self).__getattribute__(WebObjectBase.kLinksProperty)
                for link in links:
                    if link.rel == propertyName:
                        return super(WebObjectBase, self).__setattr__(propertyName, value)
            except AttributeError:
                pass
            raise KeyError("Cannot define new property when Json proxy is locked. Proxies may be unlocked and relocked using _unlock_() and _lock_() methods.")
        return super(WebObjectBase, self).__setattr__(propertyName, value)

    def __getattr__(self, propertyName):
        """Internal method to automatically request data from web server for shallow web objects"""
        if self._source_:
            try:
                links = super(WebObjectBase, self).__getattribute__(WebObjectBase.kLinksProperty)
            except AttributeError:
                return super(WebObjectBase, self).__getattribute__(propertyName)

            for link in links:
                if link.rel == propertyName:
                    result = self._source_.httpGetProperty(link.href)
                    self._setNewField(propertyName, result)
                    return result

        return super(WebObjectBase, self).__getattribute__(propertyName)

    @property
    def _json_(self):
        """Returns the json representation (in lists and dictionaries) for the WebObject."""
        return json.loads(str(self))

    @property
    def _pretty_(self):
        return json.dumps(self._json_, sort_keys=True, indent=4, separators=(',', ': '))

    def __str__(self):
        """Convenience override of str() method to return the json representation for the object."""
        return json.dumps(self, cls=_JsonEncoder)

    @property
    def _jsonProperties_(self):
        properties = self.__dict__.copy()
        for propertyName in self.kNonJsonProperties:
            if propertyName in properties:
                del properties[propertyName]
        return properties

    def _setNewField(self, fieldName, value):
        """Unlock the object if needed and add a new field"""
        if self._locked_:
            self._unlock_()
            try:
                self.__setattr__(fieldName, value)
            finally:
                self._lock_()
        else:
            self.__setattr__(fieldName, value)

    def _setNewFieldLock_(self, value):
        """set the property-creation lock.

        @param value: the new value of the property-creation lock
        """
        self._locked_ = value

    def _lock_(self):
        """Lock this object against creating fields by assigning to non-existent properties."""
        self._setNewFieldLock_(True)

    def _unlock_(self):
        """Unlock this object, allowing new fields to be created by assigning to non-existent properties."""
        self._setNewFieldLock_(False)

    def _setSource_(self, source):
        """Set the web location to send this object back to when httpPut() or httpPatch() is called

           @param source: The origin of the object
        """
        self._source_ = source

    def _update_(self, other):
        self.__dict__.update(other.__dict__)

    def httpRefresh(self):
        """Updates the state of this object from its source url."""
        if not self._source_:
            raise WebException("WebObject.httpRefresh(): cannot refresh because source was not specified when object was created")

        newData = self._source_.httpGet()
        try:
            for link in self.links:
                if link.rel in self.__dict__:
                    del self.__dict__[link.rel]
        except AttributeError:
            pass

        self._update_(newData)

    def httpDelete(self):
        """Delete the source of this object.

        Note that this is only valid for WebObjects initialized with a source.
        The get and post methods automatically set these values
        """
        if not self._source_:
            raise WebException("WebObject.httpDelete(): cannot delete object from source because source was not specified when object was created")
        self._source_.httpDelete()

    def getUrl(self):
        """Returns the url of this object."""
        if not self._source_:
            raise WebException("WebObject.getUrl(): cannot retrieve url because source was not specified when object was created")

        return self._source_.url


class WebObjectProxy(WebObjectBase):

    kChangedProperty = "_changed_"
    kSendOnlyChangedProperty = "_sendOnlyChanged_"
    kNonJsonProperties = WebObjectBase.kNonJsonProperties + [kChangedProperty, kSendOnlyChangedProperty]

    """An element of a tree of json proxy objects that represents an object/dictionary."""

    def __init__(self, _source_=None, **entries):
        super(WebObjectProxy, self).__init__(_source_)
        self._changed_ = []
        self._sendOnlyChanged_ = False
        for key, value in entries.items():
            self.__setattr__(key, _WebObject(value))

    def __repr__(self):
        """Convenience override of repr() method to aid in debugging."""
        return "Object %s: %s" % (hex(id(self)), self)

    def __setattr__(self, propertyName, value):
        """Internal method to keep track of changed properties"""
        super(WebObjectProxy, self).__setattr__(propertyName, value)
        if propertyName not in self.kNonJsonProperties:
            self._changed_.append(propertyName)

    def _setSendOnlyChanged_(self, value):
        for propertyName in self._jsonProperties_:
            propValue = getattr(self, propertyName)
            if isinstance(propValue, WebObjectBase):
                propValue._setSendOnlyChanged_(value)
        self._sendOnlyChanged_ = value

    def _clearChanged_(self):
        self._changed_[:] = []
        for propertyName in self._jsonProperties_:
            propValue = getattr(self, propertyName)
            if isinstance(propValue, WebObjectBase):
                propValue._clearChanged_()

    @property
    def _hasChanged_(self):
        childProperties = self._jsonProperties_
        if set(childProperties.keys()).issubset(self.kAlwaysSend):
            return False
        else:
            return True

    @property
    def _jsonProperties_(self):
        properties = self.__dict__.copy()
        if self._sendOnlyChanged_:
            for propertyName in properties.keys():
                propValue = getattr(self, propertyName)
                if propertyName in self.kNonJsonProperties:
                    del properties[propertyName]
                elif isinstance(propValue, WebObjectBase):
                    if not propValue._hasChanged_:
                        del properties[propertyName]
                elif propertyName not in self._changed_ and propertyName not in self.kAlwaysSend:
                    del properties[propertyName]
        else:
            for propertyName in self.kNonJsonProperties:
                if propertyName in properties:
                    del properties[propertyName]
        return properties

    @property
    def objectType(self):
        """Gets the type of the object. Value is different than 'None' for polymorphic web services. Reads the '$type' json field."""
        try:
            type = getattr(self, "$type")
        except AttributeError:
            return None
        return type

    @objectType.setter
    def objectType(self, value):
        """Set the type of the object. Needs to be specified for polymorphic web services. It will add in json a '$type' field."""
        setattr(self, "$type", value)

    def httpPut(self):
        """Put this object back to it's source.

        Note that this is only valid for WebObjects initialized with a source.
        The get and post methods automatically set these values.
        """
        if not self._source_:
            raise WebException("WebObject.httpPut(): cannot put back to source because source was not specified when object was created")
        result = self._source_.httpPut(self)
        self._clearChanged_()
        return result

    def httpPatch(self):
        """Patch the source of this object.

        Note that this is only valid for WebObjects initialized with a source.
        The get and post methods automatically set these values
        """
        if not self._source_:
            raise WebException("WebObject.httpPatch(): cannot put back to source because source was not specified when object was created")
        self._setSendOnlyChanged_(True)
        try:
            result = self._source_.httpPatch(self)
        finally:
            self._setSendOnlyChanged_(False)
        self._clearChanged_()
        return result

    def httpDelete(self):
        """Delete the source of this object.

        Note that this is only valid for WebObjects initialized with a source.
        The get and post methods automatically set these values
        """
        result = super(WebObjectProxy, self).httpDelete()
        self._source_ = None
        return result

    def httpCallOperation(self, operation, data=""):
        """Invokes an operation defined on this WebObject by doing a httpPost at <object-source>/operations/<operation>
        @param operation: the name of the operation
        @param data: the data to send as the body of the HTTP request
        Note that this is only valid for WebObjects initialized with a source.
        The get and post methods automatically set these values.
        """

        if not self._source_:
            raise WebException("WebObject.httpCallOperation(): cannot call operation because source was not specified when object was created")
        availableOperations = [link for link in self.links if link.rel.endswith(" operation")]
        try:
            desiredOperation = next((link for link in availableOperations if link.rel.split(" ")[0] == operation))
        except StopIteration:
            raise KeyError('operation not supported by object: "%s"' % operation)
        return self._source_.convention.httpPost(url=desiredOperation.href, data=data)

class WebListProxy(WebObjectBase, list):
    """An element of a tree of json proxy objects that represents a list."""

    def __init__(self, entries=[], source=None):
        self._changed_ = False
        for item in entries:
            self.append(_WebObject(item))
        super(WebListProxy, self).__init__(source)

    def _checkArgs_(self, callName, item, kwArgs):
        """Checks the args and returns an item."""
        if item is None and not kwArgs:
            return None
        if item is not None and kwArgs:
            raise WebException("%s: Either a single unnamed parameter or a set of named parameters are allowed, not both." % callName)
        if item is not None:
            item = _WebObject(item)
        if kwArgs:
            item = _WebObject(kwArgs)
        return item

    def __repr__(self):
        """Convenience override of repr() method to aid in debugging."""
        return "List %s: %s" % (hex(id(self)), self)

    def __setitem__(self, idx, item):
        list.__setitem__(self, idx, item)
        self._changed_ = True

    def __setslice__(self, start, end, seq):
        list.__setslice__(self, start, end, seq)
        self._changed_ = True

    def __getitem__(self, nameOrIdx):
        if isinstance(nameOrIdx, (int, long) ):
            return list.__getitem__(self, nameOrIdx)
        else:
            return self.named(nameOrIdx)

    def __delitem__(self, idx):
        list.__delitem__(self, idx)
        self._changed_ = True

    def __delslice__(self, start, end):
        list.__delslice__(self, start, end)
        self._changed_ = True

    def remove(self, item):
        list.remove(self, item)
        self._changed_ = True

    def append(self, item=None, **kwArgs):
        """Append a WebObject to a WebObject list."""
        itemToAppend = self._checkArgs_("WebListProxy.append()", item, kwArgs)
        list.append(self, itemToAppend)
        self._changed_ = True

    def insert(self, idx, item=None, **kwArgs):
        itemToInsert = self._checkArgs_("WebListProxy.insert()", item, kwArgs)
        list.insert(self, idx, itemToInsert)
        self._changed_ = True

    def _setSendOnlyChanged_(self, value):
        for item in self:
            if isinstance(item, WebObjectProxy):
                item._setSendOnlyChanged_(value)

    def _clearChanged_(self):
        self._changed_ = False
        for item in self:
            if isinstance(item, WebObjectProxy):
                item._clearChanged_()

    @property
    def _hasChanged_(self):
        if self._changed_:
            return True
        childProperties = {}
        for item in self:
            if isinstance(item, WebObjectProxy):
                childProperties = item._jsonProperties_
                if not set(childProperties.keys()).issubset(self.kAlwaysSend):
                    break
        if set(childProperties.keys()).issubset(self.kAlwaysSend):
            return False
        else:
            return True

    def _setSource_(self, source):
        super(WebListProxy, self)._setSource_(source)
        if not source:
            return
        for item in self:
            if not hasattr(item, self.kLinksProperty):
                continue
            for link in item.links:
                if link.rel == self.kSelfLink:
                    itemSource = WebObjectLocation(source.convention, link.href)
                    item._setSource_(itemSource)
                    break

    def _update_(self, other):
        super(WebListProxy, self)._update_(other)
        del self[:]
        for item in other:
            self.append(item)

    def named(self, name, ignoreCase=False):
        """
        Returns the first object whose "name" property is equal to name (assuming it has a "name"). The comparison can also be done ignoring case.
        This method only works on lists of objects that have a "name" property, and will raise an AttributeError if used otherwise.

        @param name: the name of the object you want to find in this list.
        """
        try:
            if ignoreCase:
                return next(obj for obj in self if obj.name.lower() == name.lower())
            else:
                return next(obj for obj in self if obj.name == name)
        except StopIteration:
            raise KeyError("No item named '%s' (%s)" % (name, "ignoring case" if ignoreCase else "matching case"))

    def httpPost(self, item):
        """Adds a new item in the list.
        Note that this is only valid if the WebListProxy was initialized with a source.
        The get and post methods automatically set these values.
        """
        if not self._source_:
            raise WebException("WebListProxy.httpPost(): cannot add a new item because source was not specified when the WebListProxy object was created")
        newItem = self._source_.httpPost(item)
        return newItem


def _getSpecificSubclass(webObject):
    if not hasattr(webObject, 'links'):
        return None
    linkNames = set((link.rel[0:link.rel.index(' operation')] if (' operation' in link.rel) else link.rel
                     for link in webObject.links
                     if link.rel != "self"))
    if len(linkNames) == 0:
        return None
    for subclass in WebObjectProxy.__subclasses__():
        if linkNames.issubset(set(subclass.__dict__.keys())):
            return subclass
    return None


def _WebObject(value):
    """Helper factory method for nested objects"""
    if isinstance(value, WebObjectBase):
        result = value
    elif isinstance(value, dict):
        for name, rename in kJsonPropertyRenameMap.items():
            if name in value:
                value[rename] = value[name]
                del value[name]
        result = WebObjectProxy(**value)
        specificSubclass = _getSpecificSubclass(result)
        if specificSubclass is not None:
            result = specificSubclass(**value)
        result._lock_()
    elif isinstance(value, list):
        result = WebListProxy(value)
        result._lock_()
    else:
        # simple types are directly represented as themselves
        result = value
    return result


def WebObject(*args, **kwArgs):
    """Factory method that converts dictionaries and lists into json object proxies.
        This is useful to call on a response that is a known json object, in which case it returns a locked proxy object that
        can conveniently access the json fields using python object/list notation. It is locked to avoid accidentally creating
        new fields. The called can always call unlock on the returned object if adding fields is desired.

        @param args: zero or one positional parameter. If one, then the parameter
                     is a dictionary or list (possibly with nested dictionaries and lists) from which to create an 
                     equivalent python object
                     If no positional parameters are specified, then kwArgs is used to create the object. 
        @param kwArgs: if no positional argument is specified, then named parameters can be used to specify a json object
    """
    numArgs = len(args)
    if numArgs > 1:
        raise WebException("WebObject can accept at most one positional parameter")
    if numArgs == 1:
        if kwArgs:
            raise WebException("WebObject can accept either a value or a set of named parameters, but not both")
        value = args[0]
    if numArgs == 0:
        # note if neither value nor dictionary is specified then the result will be an empty object
        value = kwArgs
    return _WebObject(value)


def WebObjectWithSource(value, source, **kwArgs):
    """Factory method to create a web object and set its source location."""
    result = WebObject(value, **kwArgs)
    result._setSource_(source)
    return result


class WebException(Exception):
    """Exception for nonstandard exceptions thrown by webapi module"""

    def __init__(self, description="", result=None, extra=""):
        super(Exception, self).__init__(description + extra)
        self.result = result

    def getResult(self):
        """Returns the result of the query that resulted in the exception."""
        return self.result


class ErrorNotificationException(WebException):
    """Exception for error notifications reported by the server"""
    pass


class WebApiTimeout(WebException):
    """Specialized exception for timeouts"""
    pass


class StatsTimeoutException(WebException):
    """ Specialized exception for timeouts when getting stats values """
    pass


class SslAdapter(HTTPAdapter):
    """An HTTPS Transport Adapter that uses an arbitrary SSL version."""

    def __init__(self, ssl_version=None, **kwargs):
        self.ssl_version = ssl_version
        super(SslAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize, block=block, ssl_version=self.ssl_version)


class HttpConvention(object):
    """Class for remembering a set of common headers, urlParameters, and cookies used by an HTTP conversation.
        @param url:     the base url. The url passed into the specific methods will be appended to this one 
        @param parentConvention: (optional) an HttpConvention that is extended by this one
        @param params:  (optional) a dictionary of name value pairs to send as URL urlParameters
        @param headers: (optional) a dictionary of name value pairs to send as HTTP headers
    """
    kMethodDelete = "DELETE"
    kMethodGet = "GET"
    kMethodHead = "HEAD"
    kMethodOptions = "OPTIONS"
    kMethodPost = "POST"
    kMethodPut = "PUT"
    kMethodPatch = "PATCH"
    kMethodTrace = "TRACE"

    kStandardStreamingChunkSize = 10240

    def __init__(self, url, parentConvention=None, params={}, headers={}, sslVersion=kDefaultSslProtocol, **kwArgs):
        self.url = url
        self.parentConvention = parentConvention
        self.params = params.copy()
        self.headers = headers.copy()
        self.sslVersion = sslVersion
        self.cookies = CookieJar()
        self.extras = kwArgs
        self.httpSession = None
        self.sslAdapter = None

    def updateHeaders(self, headerDict):
        """Add or change HTTP headers used for all operations by this object."""
        self.headers.update(headerDict)

    def updateParams(self, paramDict):
        """Add or change URL parameters used for all operations by this object."""
        self.params.update(paramDict)

    def getErrorNotifications(self):
        """Returns any notifications for errors.

        This base class method is a hook for subclasses to implement if their supported server(s) can provide
        additional error information via another API. When checking for notifications, the implementing subclass
        must pass false for the checkNotifications parameter in any calls that make HTTP requests (to prevent an infinite
        loop if the call to checkNotifications fails).
        """
        return []

    def _getFormattedErrorNotifications(self):
        """Utility method checks the notifications and throws a WebException or returns a string representation of notifications if no error.

        @return Either an empty string, or a newline-prefixed string representing the list of non-error notifications.
        @raises WebException
        """
        result = ""
        errors = self.getErrorNotifications()
        if errors:
            result = "\nError notification(s): " + str([error.message for error in errors])
        return result

    def check(self, result, method, originalUrl, checkNotifications):
        """Check an HTTP result and throw an exception if there was an error."""
        content = ""
        notifications = ""
        if not result.ok:
            if checkNotifications:
                notifications = self._getFormattedErrorNotifications()
            if result.text:
                content = "\n" + result.text
            raise WebException("%s request to '%s' failed: server returned status %s: %s%s%s" % (method, result.url, result.status_code, result.reason, content, notifications), result)
        if result.url != originalUrl and result.url.endswith("/login"):
            if checkNotifications:
                notifications = self._getFormattedErrorNotifications()
            raise WebException("%s request to '%s' failed: invalid URL or user key.%s" % (method, originalUrl, notifications))

    def _getHttpSession(self):
        if self.httpSession is None:
            self.httpSession = requests.Session()
            self.sslAdapter = SslAdapter(ssl_version=self.sslVersion)
            self.httpSession.mount("https://", self.sslAdapter)
        return self.httpSession

    def httpRequest(self, method, url="", data="", params={}, headers={}, checkNotifications=True, **kwArgs):
        """Utility method to send an HTTP request of any kind to self.url + url (url parameter).

        Throws an exception on any error, or return a Requests library result object.
        @param method: the HTTP method to use
        @param url: the url-relative url to send the request to.
        @param data: the data to send as the body of the HTTP request
        @param params: a dictionary with URL parameters to use for this message only
        @param headers: a dictionary with HTTP headers to use for this message only
        @param checkNotifications: a flag to indicate whether the server notifications should be checked on an HTTP error.
                                    This is normally set to False only when checking notifications to avoid infinite recursion.
        @param kwArgs: a dictionary with any other options to pass to the Requests library request call
        """
        Validators.checkNotNone(method, "method")
        params = self.resolveParams(params)
        headers = self.resolveHeaders(headers)
        absUrl = self.resolveUrl(url)
        # set verify to False to turn off SSL certificate validation
        extras = {"verify": False}
        extras.update(self.resolveExtras(kwArgs))
        result = self._getHttpSession().request(method, absUrl, data=str(data), params=params, headers=headers, cookies=self.cookies, **extras)
        self.check(result, method, absUrl, checkNotifications)
        return result

    def resolveParams(self, params={}):
        # Internal method to merage all the conventions' params together prior to making the final HTTP request
        result = self.parentConvention and self.parentConvention.resolveParams() or {}
        result.update(self.params)
        result.update(params)
        return result

    def resolveHeaders(self, headers={}):
        # Internal method to merage all the conventions' headers together prior to making the final HTTP request
        result = self.parentConvention and self.parentConvention.resolveHeaders() or {}
        result.update(self.headers)
        result.update(headers)
        return result

    def resolveExtras(self, extras={}):
        # Internal method to merage all the conventions' extra Requests.request kwArgs together prior to making the final HTTP request
        result = self.parentConvention and self.parentConvention.resolveExtras() or {}
        result.update(self.extras)
        result.update(extras)
        return result

    def resolveUrl(self, url):
        """Get the absolute URL from the url for self and the specified url parameter.

        @param url: the relative url (even if starting with /) to make absolute.
        """
        Validators.checkString(url, "url")
        result = self.parentConvention and self.parentConvention.resolveUrl(self.url) or self.url
        return HttpConvention.urljoin(result, url)

    def httpDelete(self, url="", data="", params={}, headers={}, checkNotifications=True, **kwArgs):
        """Deletes the resource associated with self.urlBase+url."""
        return self.httpRequest(HttpConvention.kMethodDelete, url, data, params, headers, checkNotifications, **kwArgs)

    def httpGetRaw(self, url="", data="", params={}, headers={}, checkNotifications=True, **kwArgs):
        """Performs an HTTP GET and returns the Requests library result object."""
        kwArgs.setdefault('allow_redirects', True)
        return self.httpRequest(HttpConvention.kMethodGet, url, data, params, headers, checkNotifications, **kwArgs)

    def getWebObjectFromReply(self, reply, url, *urlExts):
        result = None
        if reply.text:
            try:
                result = WebObject(reply.json())
                if result is not None \
                   and url is not None:
                    result._setSource_(WebObjectLocation(self, url, *urlExts))
                    result._clearChanged_()
            except ValueError:
                # allow for rare case of non-json response (e.g. /api/doc)
                result = reply.text
        return result

    def httpGet(self, url="", data="", params={}, headers={}, checkNotifications=True, **kwArgs):
        """Performs an HTTP GET and returns a WebObject representing the returned JSON payload."""
        reply = self.httpGetRaw(url, data, params, headers, checkNotifications, **kwArgs)
        return self.getWebObjectFromReply(reply, url)

    def httpHead(self, url="", data="", params={}, headers={}, checkNotifications=True, **kwArgs):
        """Performs an HTTP HEAD command and returns a Requests library result object.

        Parameters are the same as for HttpConvention.request().
        """
        return self.httpRequest(HttpConvention.kMethodHead, url, data, params, headers, checkNotifications, **kwArgs)

    def httpOptions(self, url="", data="", params={}, headers={}, checkNotifications=True, **kwArgs):
        """Performs an HTTP OPTIONS command and returns a Requests library result object.

        Parameters are the same as for HttpConvention.request().
        """
        kwArgs.setdefault('allow_redirects', True)
        return self.httpRequest(HttpConvention.kMethodOptions, url, data, params, headers, checkNotifications, **kwArgs)

    def _httpPollAsyncOperation(self, reply, timeout=None):
        statusUrl = None
        lastMethod = self.kMethodPost
        startTime = time.time()
        while True:
            if not reply.text:
                raise WebException("Status not returned from query to %s" % reply.url, extra=self._getFormattedErrorNotifications())
            time.sleep(0.1)  # avoid DOS attack
            status = WebObject(reply.json())
            if not statusUrl:
                statusUrl = status.url
            if timeout is not None and time.time() - startTime > timeout:
                raise WebApiTimeout("Async operation polling timeout after %ss!" % str(timeout))
            if status.progress < 100:
                reply = self.httpGetRaw(statusUrl, allow_redirects=False)
                lastMethod = self.kMethodGet
            else:
                if status.state.lower() != "success":
                    raise WebException("%s to '%s' returned error. State: '%s' Message: '%s'"
                                       % (lastMethod, reply.url, status.state, status.message), extra=self._getFormattedErrorNotifications())
                return status

    def _httpGetTextResult(self, originalUrl, resultUrl):
        """ Helper method to get either a web object or text from a result URL."""
        result = None
        reply = self.httpGetRaw(resultUrl)
        if reply.text:
            try:
                result = self.getWebObjectFromReply(reply, originalUrl)
            except ValueError:
                result = reply.text
        return result

    def _httpStreamBinaryResultToFile(self, resultUrl, filehandle):
        """ Helper method to stream binary data from the server to a file."""
        reply = self.httpGetRaw(resultUrl, stream=True)
        for chunk in reply.iter_content(chunk_size=self.kStandardStreamingChunkSize):
            filehandle.write(chunk)
        filehandle.flush()

    def httpPostRaw(self, url="", data="", params={}, headers={}, checkNotifications=True, **kwArgs):
        """Performs an HTTP OPTIONS command and returns a Requests library result object.

        Parameters are the same as for HttpConvention.request().
        """
        return self.httpRequest(HttpConvention.kMethodPost, url, data, params, headers, checkNotifications, **kwArgs)

    def httpPost(self, url="", data="", params={}, headers={}, checkNotifications=True, timeout=None, **kwArgs):
        """Performs an HTTP OPTIONS command and returns a WebObject representing the returned JSON.

        If the URL represents an asyncronous operation (as indicated by a 202 response code) and timeout is None, 
        then this method will block until the method completes.

        Parameters are the same as for HttpConvention.request(), with the following additions:

        @type timeout: float
        @param timeout: optional amount of time in seconds and/or fractions of seconds to poll for the async operation result.
            If the result is not available in the specified time, a L{WebApiTimeout} exception is raised.
            The default value is None, blocking indefinitely.

        @return A WebObject representing the returned JSON or None if no JSON was returned
        """
        result = None
        reply = self.httpPostRaw(url, data, params, headers, checkNotifications, **kwArgs)
        if reply.status_code == httplib.ACCEPTED:
            status = self._httpPollAsyncOperation(reply, timeout=timeout)
            # if the service produces a result, return it (Otherwise just return None)
            if hasattr(status, "resultUrl"):
                result = self._httpGetTextResult(url, status.resultUrl)
        elif reply.text and reply.status_code == httplib.CREATED:
            # Use the json from the reply, but get the new object's real location from the header
            result = self.getWebObjectFromReply(reply, reply.headers.get("location"))
        elif reply.text:
            # If there is no object created on the server, no location header will be available
            result = self.getWebObjectFromReply(reply, None)
        else:
            # Get the object using the location header
            location = reply.headers.get("location")
            result = location and self.httpGet(location) or None
        return result

    def httpPut(self, url="", data="", params={}, headers={}, checkNotifications=True, **kwArgs):
        """Performs an HTTP PUT command and returns a Requests library result object.

        Parameters are the same as for HttpConvention.request().
        """
        return self.httpRequest(HttpConvention.kMethodPut, url, data, params, headers, checkNotifications, **kwArgs)

    def httpPatch(self, url="", data="", params={}, headers={}, checkNotifications=True, **kwArgs):
        """Performs an HTTP PATCH command and returns a Requests library result object.

        Parameters are the same as for HttpConvention.request().
        """
        return self.httpRequest(HttpConvention.kMethodPatch, url, data, params, headers, checkNotifications, **kwArgs)

    def httpTrace(self, url="", data="", params={}, headers={}, checkNotifications=True, **kwArgs):
        """Performs an HTTP TRACE command and returns a Requests library result object.

        Parameters are the same as for HttpConvention.request().
        """
        return self.httpRequest(HttpConvention.kMethodTrace, url, data, params, headers, checkNotifications, **kwArgs)

    @classmethod
    def urljoin(cls, base, end):
        """ Join two URLs. If the second URL is absolute, the base is ignored.

        Use this instead of urlparse.urljoin directly so that we can customize its behavior if necessary.
        Currently differs in that it 
            1. appends a / to base if not present.
            2. casts end to a str as a convenience
        """
        Validators.checkNotNone(base, "base")
        Validators.checkNotNone(end, "end")
        if base and not base.endswith("/"):
            base = base + "/"
        return urljoin(base, str(end))

    #---------------
    # Close support
    #---------------

    def __enter__(self):
        self._getHttpSession()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.httpSession:
            self.httpSession.close()

    #---------------

#-------------------------------------------------------------------------------------------
#
#   Session Services
#
#-------------------------------------------------------------------------------------------


class SessionsData(WebObjectBase):
    """A DAO to represent the parameter(s) necessary to create a session."""

    def __init__(self, sessionType):
        super(SessionsData, self).__init__()
        self.applicationType = sessionType


class SessionState(object):
    """Constants that represent possible values of a Session's state property."""
    kInitial = "Initial"
    kStarting = "Starting"
    kActive = "Active"
    kStopping = "Stopping"
    kStopped = "Stopped"
    kDead = "Dead"


class SessionSubState(object):
    """ These are not valid for all labs and states. """
    kUnconfigured = "Not Configured"
    kConfiguring = "Configuring"
    kConfigured = "Configured"
    kStarting = "Starting"
    kRunning = "Running"
    kStopping = "Stopping"


class TestState(object):
    """The states of a test run."""
    kNotStarted = "NotStarted"
    kStarting = "Starting"
    kRunning = "Running"
    kStopping = "Stopping"
    kStopped = "Stopped"


class Session(HttpConvention):
    """
        A class that represents a test session on the web server.
        A test session includes a configuration which can be executed via startTest
    """
    kOperationStopSession = "operations/stop"
    kOperationStartSession = "operations/start"
    kOperationGetNotificationsFormat = "notifications/sessions/%s"
    kOperationLoadConfigFormat = "config/%s/operations/load"
    kOperationSaveConfigFormat = "config/%s/operations/save"
    kOperationStartTestFormat = "testruns/%d/operations/start"
    kOperationStopTestFormat = "testruns/%s/operations/stop"
    kTestRuns = "testruns"
    kTestRunFormat = "testruns/%s"

    kSessionBase = "sessions"
    _kJoin = "INTERNAL_JOIN"
    applicationType = None

    sessionClassesPerAppType = {}

    class __metaclass__(type):

        # this method is called for Session and all classes that derive from Session
        # at the point when Python detects the class (e.g. when importing)
        def __init__(cls, name, base, attrs):
            # register all the classes that provide a web api
            cls.sessionClassesPerAppType[cls.applicationType] = cls

    def __init__(self, connection, sessionType, sessionId=None, **kwArgs):
        """
            Create a session on the specified connection. Normally done using Connection.createSession
            Use join() to connect to an existing session

            @type connection: Connection
            @param connection: The connection on which to reference or establish a session
            @type sessionType: SessionType constant
            @param sessionType: The type of session to create.
        """
        Validators.checkNotNone(connection, "connection")
        Validators.checkSessionType(sessionType)
        super(Session, self).__init__(Session.kSessionBase, connection, **kwArgs)
        if sessionType == self._kJoin:
            # join the session
            # invoke this code through Session.join()
            Validators.checkInt(sessionId, "sessionId")
            # note that we can't check notifications until the session is up
            self._session = self.httpGet(str(sessionId), checkNotifications=False)
        else:
            # create the session
            # note that we can't check notifications until the session is up
            self._session = self.httpPost(data=SessionsData(sessionType), checkNotifications=False)
            sessionId = self.sessionId
        self.url = HttpConvention.urljoin(self.url, sessionId)
        self.currentTestRun = None
        self._config = None
        self.kBasePrefix = None

    @classmethod
    def join(cls, connection, sessionId, **kwArgs):
        """
            Attach to the specified session.

            @type connection: Connection object
            @param connection: the connection (server) on which to join
            @type sessionId: num
            @param sessionId: The session number to join
            @rtype Session: The joined session
        """
        Validators.checkNotNone(connection, "connection")
        Validators.checkInt(sessionId, "sessionId")
        return cls(connection, cls._kJoin, sessionId, **kwArgs)

    @property
    def sessionId(self):
        return self._session.id

    @property
    def sessionType(self):
        return self._session.applicationType

    @property
    def creationTime(self):
        return self._session.createdOn

    @property
    def startingTime(self):
        return self._session.startedOn

    @property
    def stoppingTime(self):
        return self._session.stoppedOn

    @property
    def state(self):
        return self._session.state

    @property
    def subState(self):
        return self._session.subState

    @property
    def testIsRunning(self):
        """
        Checks if the current test exists and is in one of the running states (TestState.kRunning, TestState.kStarting, or TestState.kStopping).
        """
        testRun = self.getCurrentTestRun()
        if not testRun:
            testRun = self.getTestRun()
        expectedStates = [TestState.kRunning, TestState.kStarting, TestState.kStopping]
        return testRun is not None and checkForPropertyValue(testRun, "testState", expectedStates, refresh=True)

    @property
    def testConfigName(self):
        return self._session.testConfigName

    @property
    def config(self):
        """
        Returns the root node of the configuration tree for this session.
        """
        if self._config:
            return self._config
        tryingDefaultConfigPath = False
        if not self.kBasePrefix:
            tryingDefaultConfigPath = True
            self.kBasePrefix = "config/%s" % self.applicationType
        try:
            self._config = self.httpGet(self.kBasePrefix)
            return self._config
        except WebException as e:
            if e.status_code == httplib.NOT_FOUND and tryingDefaultConfigPath:
                raise NotImplementedError("Can't access the configuration page for this lab type.")
            else:
                raise

    def httpRefresh(self):
        self._session = self.httpGet()

    def runTest(self, trace=False):
        """Runs a test using the current configuration.

        Blocks until the test is done. On success returns an object with
        a testId property set to the id of the test.

        @return test result
        @exception WebException
        """
        result = self.startTest(trace=trace)
        self.waitTestStopped(trace=trace)
        return result

    def startTest(self, trace=False):
        """Start the currently configured test, and wait for it to enter the 'Started' state.

        On success returns an object with a testId property set to the id of the test. 
        That id can be passed to the httpGetStatsCsvToFile API.

        @return testRun
        @exception WebException
        """
        self.httpRefresh()
        if self.testIsRunning:
            raise WebException("Cannot startTest. Test already running")
        self.currentTestRun = self.httpPost("testruns")
        self.httpPost(self.kOperationStartTestFormat % self.currentTestRun.testId)
        return self.currentTestRun

    def stopTest(self, testId=None, graceful=False, trace=False):
        """Stop the currently running test."""
        self.httpPost(self.kOperationStopTestFormat % self.currentTestRun.testId, WebObject(gracefulStop=graceful))
        self.waitTestStopped(testId=testId, trace=trace)

    def getCurrentTestRun(self):
        """Get the WebObject representing the run of the last started test.

        The current test run is started by the last call to startTest.
        WaitTestStopped will delete the current test run when it exits.
        @return the current test run
        """
        return self.currentTestRun

    def getTestRun(self, testId=None):
        """Returns the testRun WebObject for the specified id.

        @param testId: The id of the testRun requested
        @return a testRun WebObject
        """
        if testId:
            return self.httpGet(self.kTestRunFormat % testId)
        else:
            testRuns = self.httpGet(self.kTestRuns)
            if testRuns:
                return testRuns[0]
        return None

    def waitTestStopped(self, testId=None, timeout=None, trace=False):
        """Waits until the currently running test stops.

        @param testId: the id of the test to wait for (e.g. from startTest().testId)
        @param timeout: max number of seconds to wait.
        @param trace: true to print polled value"""
        if testId is not None:
            testRun = self.getTestRun(testId)
        else:
            testRun = self.getCurrentTestRun()
            if not testRun:
                testRun = self.getTestRun()
                if not testRun:
                    raise ValueError("Either testId must be specified, or a current test must have been created using startTest().")
        waitForProperty(testRun, "testState", [TestState.kStopped], timeout=timeout, trace=trace)
        self.checkNotifications()
        self.currentTestRun = None

    def getStatsCsvZipToFile(self, testResult, statFile):
        """Retrieves the entire set of stats from the web server and writes them into the file-like object statFile.

        @param testResult: a test object. Typically obtained by using the archivedResult member of the WebObject returned by runTest.
        @param statFile: a file handle or file-like object to be written to with the CSV-formatted statistics data
        """
        return self.parentConvention.getStatsCsvZipToFile(testResult, statFile)

    def getErrorNotifications(self):
        """Returns only error notifications, if any are in the queue."""
        return [notification for notification in self.getNotifications() if notification.level == "Error"]

    def checkNotifications(self):
        """Checks the notifications for errors and raises a WebException with the errors if any are found."""
        notifications = self.getErrorNotifications()
        if notifications:
            notificationMsgs = [notification.message for notification in notifications]
            raise ErrorNotificationException("The test failed with the following error(s): %s" % notificationMsgs)

    def startSession(self, timeout=None):
        """Start the session. The session must be started before being used.

        @type timeout: float
        @param timeout: optional amount of time in seconds and/or fractions of seconds to wait for the session to start.
            If the session does not start in the specified time, a L{WebApiTimeout} exception is raised.
            The default value is None, blocking indefinitely.
        """
        # The session currently automatically starts on creation, but will not do so in the future
        # For now, for this synchronous call, we just wait for it to finish starting.
        startTime = time.time()
        self.httpPost(self.kOperationStartSession, timeout=timeout)
        remainingTime = time.time() - startTime
        self._waitForProperty("state", [SessionState.kActive], validValues=[SessionState.kInitial, SessionState.kStarting], timeout=remainingTime)

    def stopSession(self, timeout=None):
        """Bring down this session.

        The session was created by calling the Session constructor, and started using the startSession API

        @type timeout: float
        @param timeout: optional amount of time in seconds and/or fractions of seconds to wait for the session to stop.
            If the session does not stop in the specified time, a L{WebApiTimeout} exception is raised.
            The default value is None, blocking indefinitely.
        """
        startTime = time.time()
        self.httpPost(self.kOperationStopSession, timeout=timeout)
        remainingTime = time.time() - startTime
        self._waitForProperty("state", [SessionState.kStopped], validValues=[SessionState.kActive, SessionState.kStopping], timeout=remainingTime)

    def getNotifications(self):
        """Returns a possibly-empty list of currently posted notifications for this session."""
        # session-specific, but resides under api/notifications/sessions/{id}
        return self.parentConvention.httpGet(self.kOperationGetNotificationsFormat % self.sessionId, checkNotifications=False)

    def saveConfiguration(self, configName, description="", overwrite=False):
        """Save the current configuration to the specified configuration name.

        @type configName: string
        @param configName: the configuration name
        """
        Validators.checkConfigName(configName)
        self.httpPost(self.kOperationSaveConfigFormat % self.sessionType, WebObject(name=configName, description=description, overwrite=overwrite))

    def loadConfiguration(self, configName, description=""):
        """Replace the current configuration with the configuration from the specified configuration name.

        @type configName: string
        @param configName: the configuration name
        """
        Validators.checkConfigName(configName)
        self.httpPost(self.kOperationLoadConfigFormat % self.sessionType, WebObject(name=configName))

    def findConfigurationByName(self, configName, raiseException=True):
        """Returns an object describing the named configuration.

        Throws an exception if raiseException is True and no configuration is found.
        @return A WebObject describing the configuration, or None if the configuration is not found (and raiseException is False)
        """
        Validators.checkConfigName(configName)
        return self.parentConvention.findConfigurationByName(self.sessionType, configName, raiseException)

    def exportConfigurationToFile(self, configName, exportFile):
        """Export a configuration, identified by its name, to a file.

        @param configName: the name of the config to export
        @param exportFile: a file-like object to write the configuration to. Must be opened in binary mode.
        """
        config = self.findConfigurationByName(configName)
        self.parentConvention.exportConfigurationToFileById(self.sessionType, config.id, exportFile)

    def importConfigurationFromFile(self, importFile):
        """ imports a configuration from the specified file.

        The file must have been created by a previous export operation.
        @param importFile: a file-like object to read the configuration from
        """
        return self.parentConvention.importConfigurationFromFile(self.sessionType, importFile)

    def getConfigurations(self):
        """Return a list of available configurations.

        Not really session-specific, but available on session for convenience.
        """
        return self.parentConvention.getConfigurations(self.sessionType) or WebListProxy()

    def deleteConfiguration(self, configName):
        """Deletes a configuration, given its sessionType and name

        @param sessionType: a string with the type of session
        @param configName: the name of the configuration to delete
        """
        config = self.findConfigurationByName(configName)
        self.parentConvention.deleteConfigurationById(self.sessionType, config.id)

    def _waitForProperty(self, propertyName, targetValues, validValues=[], invalidValues=[], timeout=None, trace=False):
        """Wait for the session to enter any of the specified targetStates. 

        Caller can also specified a set of valid or invalid states 
        """
        waitForProperty(self, propertyName, targetValues, validValues, invalidValues, timeout, trace)

    def collectDiagnosticsToFile(self, diagFile):
        """Collects debug diagnostics for the session and downloads them to a file

        @param diagFile: a file-like object to send the configuration to. Must be opened in binary mode
        """
        Validators.checkFile(diagFile, "diagFile")
        reply = self.parentConvention._collectSessionDiagnostics(self.sessionId)
        if reply.status_code == httplib.ACCEPTED:
            status = self._httpPollAsyncOperation(reply)
            self._httpStreamBinaryResultToFile(status.resultUrl, diagFile)
        else:
            raise WebException("Unexpected status code from request to collect diagnostics: %s" % reply.status_code)


#-------------------------------------------------------------------------------------------
#
#    User Administration
#
#-------------------------------------------------------------------------------------------


class UserRole(object):
    kUser = "User"
    kAdmin = "Admin"
    kGuest = "Guest"


class UserPermission(object):
    kAll = "*"
    kAllApps = "apps:*"

    @classmethod
    def kSpecificApp(cls, appName):
        """Used to get the constant representing permission to use the specified appName.

        @param appName: A legal application name available on the server.
        """
        return "apps:%s" % appName


class UserAdmin(HttpConvention):
    """A class with User Administration methods. Get an instance using getUserAdmin on a Connection."""

    kUserAdminBase = "auth"
    kRelUsersUrl = "users"
    kRelUserFormat = "users/%s"

    def __init__(self, connection, **kwArgs):
        """
            Create a session on the specified connection. Normally done using Connection.getUserAdmin
            Use join() to connect to an existing session

            @type connection: Connection
            @param connection: The connection on which to reference or establish a session
            @type sessionType: SessionType constant
            @param sessionType: The type of session to create.
        """
        Validators.checkNotNone(connection, "connection")
        super(UserAdmin, self).__init__(self.kUserAdminBase, connection, **kwArgs)

    def getUsers(self):
        """Returns a list of users registered with the connected-to server."""
        return self.httpGet(self.kRelUsersUrl)

    def findUser(self, username=None):
        """Returns an object describing the specified user, or throws an exception if not found.

        @param username: the login name of the user to find. Defaults to the current user
        """
        if username:
            Validators.checkString(username, "username")
        # avoid permission error on server for non-Admins working on their own account
        # (getUsers fails for non-Admins)
        currentUser = self.getCurrentUser()
        if not username or username == currentUser:
            return currentUser
        else:
            for user in self.getUsers():
                if user.username == username:
                    return user
        raise WebException("No such user: %s" % username)

    def getCurrentUser(self):
        """Returns an object describing the current user.

        The object will be the same as the individual list elements returned by findUser.
        """
        # get the current user info from the auth session (api/auth/session is different than api/sessions)
        userInfo = self.httpGet("session")
        # web service doensn't provide id directly, but it is last element of userAccountUrl
        userId = userInfo.userAccountUrl.split("/")[-1]
        # auth/session doesn't provide full user info, so we need to make another round trip
        return self.httpGet(self.kRelUserFormat % userId)

    def createUser(self,
                   username,
                   password,
                   fullname="",
                   email="",
                   roles=[UserRole.kUser],
                   permissions=[UserPermission.kAllApps]):
        """Creates a user with the specified username, password, and other properties.

        @param username: the login name of the user
        @param password: the password for the username
        @param email: the email address of the user
        @param fullname: the real name of the user
        @param roles: A list of UserRole constants that reflect the users use of the web site
        @param permissions: A list of UserPermission constants that reflect the permissions of the user for the web site
        """
        Validators.checkNonEmptyString(username, "username")
        Validators.checkNonEmptyString(password, "password")
        Validators.checkString(email, "email")
        Validators.checkString(fullname, "fullname")
        return self.httpPost(self.kRelUsersUrl, WebObject(username=username,
                                                          password=password,
                                                          email=email,
                                                          fullname=fullname,
                                                          roles=roles,
                                                          permissions=permissions))

    def deleteUser(self, username):
        """Deletes the specified user.

        @param username: the login name of the user
        """
        user = self.findUser(username)
        self.httpDelete(self.kRelUserFormat % user.id)

    def changePassword(self, username, password, oldpassword=None):
        """Changes the password for a given user.

        @param username: the login name of the user
        @param password: the new password for the username
        @param oldpassword: the old password for the user. Only required for non-admins
        """
        if oldpassword:
            Validators.checkString(oldpassword, "oldpassword")
        Validators.checkNonEmptyString(password, "password")
        user = self.findUser(username)
        user._unlock_()  # allow setting of undefined properties
        user.password = password
        if oldpassword:
            # don't even send it unless its provided
            user.oldpassword = oldpassword
        self.httpPut(self.kRelUserFormat % user.id, user)

    def setEmail(self, username, email):
        """Sets a new email address for a given user.

        @param username: the login name of the user
        @param email: the new email for the username
        """
        Validators.checkString(email, "email")
        user = self.findUser(username)
        user.email = email
        self.httpPut(self.kRelUserFormat % user.id, user)

    def setFullname(self, username, fullname):
        """Change a the fullName property of a user.

        There is no special validation of fullName. It is just a string for the admin's convenience
        @param username: the login name of the user
        @param fullname: the new full user name
        """
        Validators.checkString(fullname, "fullname")
        user = self.findUser(username)
        user.fullname = fullname
        self.httpPut(self.kRelUserFormat % user.id, user)

    def getAvailableRoles(self):
        """Returns a list of known Roles."""
        return self.httpGet("roles")

    def setRoles(self, username, roles):
        """Assigns a new list of roles (UserRole constants) to a user.

        @param username: the login name of the user
        @param roles: the list set of roles for the user
        """
        Validators.checkList(roles, "roles")
        user = self.findUser(username)
        user.roles = roles
        self.httpPut(self.kRelUserFormat % user.id, user)

    def getAvailablePermissions(self):
        """Returns a list of known permissions."""
        return self.httpGet("permissions")

    def setPermissions(self, username, permissions):
        """Assigns a new list of permissions (UserPermission constants) to a user.

        @param username: the login name of the user
        @param roles: the new list of roles for the user
        """
        Validators.checkList(permissions, "permissions")
        user = self.findUser(username)
        user.permissions = permissions
        self.httpPut(self.kRelUserFormat % user.id, user)


#-------------------------------------------------------------------------------------------
#
#    Connection to Server
#
#-------------------------------------------------------------------------------------------

class TestResultColumn:
    """Constants that represent possible values of a test result attribute name."""
    kApplicationType = "apptype"
    kConfigurationName = "configname"
    kResult = "result"
    kDuration = "duration"
    kStartTime = "starttime"
    kEndTime = "endtime"
    kUser = "userid"
    kSize = "size"


class TestResultSortOrder:
    """Constants that represent possible values of test result sorting order."""
    kAscending = "ascending"
    kDescending = "descending"


class Connection(HttpConvention):

    kGetSupportedApplicationTypes = "applicationtypes"
    kOperationGetConfigurationsFormat = "configurations/%s"
    kOperationDeleteConfigFormat = "configurations/%s/%s"
    kOperationImportConfigFormat = "configurations/%s/import"
    kOperationExportConfigFormat = "configurations/%s/%s/export"
    kOperationCollectDiags = "diagnostics"
    kHeaderContentType = "content-type"
    kHeaderApiKey = "X-Api-Key"
    kHeaderReferrers = "referers"
    kContentJson = "application/json"
    kImportFormElement = "fileId"
    kOperationsGenerateCsvLinkBundle = "results/%d/zip"

    """ A class that represents a connection to an Ixia web app server and managing sessions there-on """

    def __init__(self, siteUrl, apiVersion, userkey="", username="", password="", params={}, headers={}, sessionClass=None, sslVersion=kDefaultSslProtocol, **kwArgs):
        """
            Construct a Connection instance to use for accessing an Ixia web app server

            Connects to the site specified by siteUrl with the specified apiVersion (currently only "v1" is supported).
            Either userkey or both username and password must be passed in. If username and password are supplied, then
            getuserkey may be called to determine the corresponding user key for later use.

            @type  siteUrl: string
            @param siteUrl: the top URL serving an Ixia web app (may require "IpAddress:portNum")            
            @type  userkey: string
            @param userkey: the key for the registered user running the script.
            @type  username: string
            @param username: this and password may be specified instead of userkey
            @type  password: string
            @param password: this and username may be specified instead of userkey
            @type  params: dictionary 
            @kwarg params: URL parameters to always use for this connection
            @type  headers: dictionary 
            @kwarg headers: HTTP headers to always use for this connection
            @type  kwArgs: dictionary
            @kwarg kwArgs: additional keyword args (future expansion)
            @except Throws a WebException if the connection was not successful
        """
        Validators.checkNonEmptyString(siteUrl, "siteUrl")
        Validators.checkNonEmptyString(apiVersion, "apiVersion")
        # initialize the user key. If not provided, it will be reinitialized from server in _getOrFetchuserkey
        if userkey:
            Validators.checkString(userkey, "userkey")
        self._userkey = userkey
        # default content type is json
        headers.setdefault(self.kHeaderContentType, self.kContentJson)
        super(Connection, self).__init__(HttpConvention.urljoin(siteUrl, "api"), params=params, headers=headers, sslVersion=sslVersion, **kwArgs)
        # we had to initialize our connection first in case we have to fetch user key from server here
        self.checkApiVersion(apiVersion)
        self.url = HttpConvention.urljoin(self.url, apiVersion)
        self.updateHeaders({self.kHeaderApiKey: self._getOrFetchuserkey(username, password)})
        self.checkScriptApiVersion()
        # try one URL that requires authentication to be sure we're connected
        self.httpGet("auth/ping")
        # initialize the session class which will be used to create test sessions
        self._sessionClass = sessionClass

    def _getOrFetchuserkey(self, username=None, password=None):
        # internal method to get the user key. If user key not alreay set, then username and password must be supplied.
        if not self._userkey:
            Validators.checkNonEmptyString(username, "username")
            Validators.checkNonEmptyString(password, "password")
            httpSession = self._getHttpSession()
            httpSession.headers.update(self.headers)
            sessionKeyUrl = self.resolveUrl("auth/session")
            reply = httpSession.post(sessionKeyUrl, str(WebObject({"username": username, "password": password})), verify=False)
            if not reply.ok and reply.status_code == httplib.UNAUTHORIZED:
                raise WebException("Invalid username and/or password.")
            self.check(reply, self.kMethodPost, sessionKeyUrl, checkNotifications=False)
            try:
                keyUrl = self.resolveUrl("auth/session/key")
                reply = httpSession.get(keyUrl)
                self.check(reply, self.kMethodGet, keyUrl, checkNotifications=False)
                if not reply.text:
                    raise WebException("Authorization response not understood")
                response = WebObject(reply.json())
                self._userkey = response.apiKey
            finally:
                # log out of the session
                reply = httpSession.delete(sessionKeyUrl)
                self.check(reply, self.kMethodPost, sessionKeyUrl, checkNotifications=False)
        return self._userkey

    def getUserKey(self):
        """Return the user key, either supplied or determined from the username+password."""
        return self._userkey

    def checkApiVersion(self, apiVersion):
        Validators.checkNotNone(apiVersion, "apiVersion")
        availableVersions = [info.version for info in self.httpGet("versions")]
        if apiVersion not in availableVersions:
            raise WebException("API version %s not in available versions: %s" % (apiVersion, availableVersions))

    def checkScriptApiVersion(self):
        versionInfoList = self.httpGet("scriptapi/versions")
        versions = [versionInfo.version for versionInfo in versionInfoList]
        for version in kSupportedScriptApiVersions:
            if version in versions:
                break
        else:
            raise WebException("None of the script api versions supported by this library %s are supported by the server which supports only %s. Please use a compatible webapi library."
                               % (kSupportedScriptApiVersions, versions))

    def getSessionTypes(self):
        """ Returns a list of available session types."""
        sessionTypes = self.httpGet(self.kGetSupportedApplicationTypes)
        return [session.type for session in sessionTypes]

    def createSession(self, sessionType=None):
        """ Creates a new session.

        @param sessionType: The type of session to create, e.g. storagelab, contactcenter
        """
        # if the sessionType is not provided, then get a default session type
        if not sessionType:
            sessionType = self._getDefaultSessionType()

        Validators.checkSessionType(sessionType)
        return self._getSessionClass(sessionType)(self, sessionType)

    def joinSession(self, sessionId):
        """ Joins a previously created session.

        Note that the session could have been created by a different script or user

        @param sessionId: the session number to join
        """
        Validators.checkInt(sessionId, "sessionId")
        try:
            sessionType = self.httpGet("sessions/%d" % sessionId).applicationType
        except (WebException, AttributeError):
            sessionType = None

        return self._getSessionClass(sessionType).join(self, sessionId)

    def startSession(self, sessionId):
        """Start the specified session.

        Normally this is just done using session.startSession(), but is provided
        for completeness.

        @param sessionId: the session number to start        
        """
        return self.joinSession(sessionId).startSession()

    def stopSession(self, sessionId):
        """Stop the specified session.

        Can also be done using session.stopSession. This API on the connection is
        useful for scripts that didn't start the session

        @param sessionId: the session number to stop
        """
        return self.joinSession(sessionId).stopSession()

    def getSessions(self):
        """Return a list of session IDs."""
        return [session.id for session in self.httpGet("sessions")]

    def getConfigurations(self, sessionType):
        """Return a list of available configurations.

        Configurations may only be loaded into or saved from an active session
        """
        Validators.checkSessionType(sessionType)
        return self.httpGet(self.kOperationGetConfigurationsFormat % sessionType)

    def findConfigurationByName(self, sessionType, configName, raiseException=True):
        """Finds a specific configuration by sessionType and name
        """
        Validators.checkSessionType(sessionType)
        Validators.checkConfigName(configName)
        result = None
        matches = [x for x in self.getConfigurations(sessionType) if x.name == configName]
        if matches:
            result = matches[0]
        elif raiseException:
            raise WebException("No such %s configuration: '%s'." % (sessionType, configName))
        return result

    def exportConfigurationToFileById(self, sessionType, configId, exportFile):
        """Export a configuration of a specific sessionType and identified by its id to a file.

        @param sessionType: a string with the type of session.
        @param configId: the (numeric) id of the config to export.
        @param exportFile: a file-like object to write the configuration to. Must be opened in binary mode.
        """
        Validators.checkSessionType(sessionType)
        Validators.checkInt(configId, "configId")
        Validators.checkFile(exportFile, "exportFile")
        reply = self.httpGetRaw(self.kOperationExportConfigFormat % (sessionType, configId))
        exportFile.write(reply.content)

    def collectSessionDiagnostics(self, sessionId):
        warn("Use Session.collectDiagnosticsToFile instead of Connection.collectSessionDiagnostics", DeprecationWarning, stacklevel=2)
        self._collectSessionDiagnostics(sessionId)

    def _collectSessionDiagnostics(self, sessionId):
        Validators.checkInt(sessionId, "sessionId")
        absUrl = self.resolveUrl(self.kOperationCollectDiags)
        return self.httpPostRaw(absUrl, WebObject(sessionId=sessionId), stream=True)

    def collectSystemDiagnosticsToFile(self, diagFile):
        """Collects system wide debug diagnostics and downloads them to a file

        @param diagFile: a file-like object to send the configuration to. Must be opened in binary mode
        """
        Validators.checkFile(diagFile, "diagFile")
        absUrl = self.resolveUrl(self.kOperationCollectDiags)
        reply = self.httpPostRaw(absUrl, stream=True)

        if reply.status_code == httplib.ACCEPTED:
            status = self._httpPollAsyncOperation(reply)
            self._httpStreamBinaryResultToFile(status.resultUrl, diagFile)
        else:
            raise WebException("Unexpected status code from request to collect system diagnostics: %s" % reply.status_code)

    def importConfigurationFromFile(self, sessionType, importFile):
        """ Import a configration from a client-side file to the server.

        @param sessionType: a string with the type of session
        @param importFile: a file-like object to read the configuration from
        @return a WebObject if the server returns json. Otherwise, just the text value
        """
        Validators.checkSessionType(sessionType)
        Validators.checkFile(importFile, "importFile")
        # requests library does most of the work, but we have to customize the headers
        files = {self.kImportFormElement: importFile}
        headers = self.resolveHeaders()
        # for the upload, the content type is not the default json payload
        del headers[self.kHeaderContentType]
        absUrl = self.resolveUrl(self.kOperationImportConfigFormat % sessionType)
        method = self.kMethodPost
        # create a new HTTP session to avoid content-type mismatch error
        localHttpSession = requests.Session()
        localSslAdapter = SslAdapter(ssl_version=self.sslVersion)
        localHttpSession.mount("https://", localSslAdapter)
        # we also omit the params and extras (that httpRequest would send) as these are not likely to ever be used here
        # but set verify to False to turn off SSL certificate validation
        try:
            reply = localHttpSession.request(method, absUrl, files=files, headers=headers, cookies=self.cookies, verify=False)
        finally:
            localHttpSession.close()
        self.check(reply, method, absUrl, checkNotifications=True)
        return self.getWebObjectFromReply(reply, absUrl)

    def deleteConfigurationById(self, sessionType, configId):
        """Deletes a configuration on the server, given its sessionType and id

        @param sessionType: a string with the type of session
        @param configId: the id of the configuration to delete
        """
        Validators.checkSessionType(sessionType)
        Validators.checkInt(configId, "configId")
        self.httpDelete(self.kOperationDeleteConfigFormat % (sessionType, configId), WebObject(applicationType=sessionType))

    def getTestResults(self, start=0, limit=1, sortColumn=TestResultColumn.kStartTime, sortOrder=TestResultSortOrder.kDescending, filter={}):
        """Retrieves a WebObject describing a set of previous test results.

        @type start: integer
        @param start: skip first start test results

        @type limit: integer
        @param limit: the maximum number of test results to retrieve

        @type sortColumn: string
        @param sortColumn: a member of TestResultColumn which specifies the attribute of the test results used for sorting

        @type sortOrder: string
        @param sortOrder: a member of TestResultSortOrder which specifies the sorting order of the test results

        @type filter: dict
        @param filter: a dictionary with string keys representing test result attributes to filter by (members of TestResultColumn) and
        string values which represent the required values of the specified attributes
        """
        Validators.checkInt(start, "start")
        Validators.checkInt(limit, "limit")
        filterString = ' '.join(filterColumn + ":" + filterValue for filterColumn, filterValue in filter.items())
        response = self.httpGet("results", params={"start": start, "limit": limit, "sortColumn": sortColumn, "sortOrder": sortOrder, "filter": filterString})
        response.testRunInformationList._setSource_(response._source_)
        return response

    def getStatsCsvZipToFile(self, testResult, statFile):
        """Retrieves the entire set of stats from the web server and writes them into the file-like object statFile.

        @param testResult: a test object, or the ID of a test object. Typically obtained by using the archivedResult member of the WebObject returned by runTest.
        @param statFile: a file handle or file-like object to be written to with the CSV-formatted statistics data
        """
        Validators.checkFile(statFile, "statFile")
        try:
            generateCsvLink = next(link.href for link in testResult.archivedResult.links if link.rel == 'generateCsv operation')
        except AttributeError:
            generateCsvLink = self.kOperationsGenerateCsvLinkBundle % testResult
        reply = self.httpPostRaw(generateCsvLink, stream=True)
        if reply.status_code == httplib.ACCEPTED:
            status = self._httpPollAsyncOperation(reply)
            self._httpStreamBinaryResultToFile(status.resultUrl, statFile)
        else:
            raise WebException("Unable to retrieve csv for test/result %s" % testOrResultId)

    def loadTestResult(self, testResultId):
        """Loads a test result into a new session and returns the session object.

        @type testResultId: integer
        @param testResultId: the test result Id. Typically obtained by using the id member of a WebObject returned by getTestResults.
        """
        Validators.checkInt(testResultId, "testResultId")
        reply = self.httpPostRaw("results/%s/operations/load" % testResultId)
        if reply.status_code == httplib.ACCEPTED:
            status = self._httpPollAsyncOperation(reply)
            return self.joinSession(status.sessionId)
        else:
            raise WebException("Unable to load test result %s" % testResultId)

    def getUserAdmin(self):
        """ Returns a UserAdmin object that can be used to create/edit/delete users.

        Note that the username (or corresponding key) used to create the Connection object must have a
        role of kAdmin and permissions of kAll to list or modify the settings for other users.
        """
        return UserAdmin(self)

    def _getDefaultSessionType(self):
        """
        Returns the most specific session type this connection can handle.

        If a session class was explicitly given to this connection at creation time, then that class's session type is the most specific one.
        Otherwise, if the server we are connecting to only has a single session type, then that is the most specific one.
        Finally, we return None.
        """
        if hasattr(self._sessionClass, "applicationType"):
            return self._sessionClass.applicationType
        else:
            try:
                sessionTypes = self.getSessionTypes()
                if len(sessionTypes) == 1:
                    return sessionTypes[0]
            except WebException:
                pass
        return None

    def _getSessionClass(self, sessionType):
        """
        Returns the most specific Session implementation we can find based on the session type.

        If a session class was explicitly given to this connection at creation time, then that is the most specific one.
        Otherwise, we try to see if any external module has registered its own class for this session type.
        Finally, we choose Session.
        """
        if self._sessionClass:
            return self._sessionClass
        if sessionType in Session.sessionClassesPerAppType:
            return Session.sessionClassesPerAppType[sessionType]
        return Session.sessionClassesPerAppType[None]


class webApi(object):
    """A class that represents a connection to an ixia app server"""

    """Either userkey or both username and password must be provided
    @param siteUrl: The URL of the top-level of the site, e.g. http://testServer:8080
    @param siteVersion: The version of the site, e.g. 'v1', 'v2', etc.
    @param userkey: The user key for the user under which this script will run
    @param username: The login name of the user under which this script will run
    """
    @classmethod
    def connect(cls, siteUrl, siteVersion, userkey=None, username=None, password=None, sessionClass=None):
        return Connection(siteUrl, siteVersion, userkey=userkey, username=username, password=password, sessionClass=sessionClass)


class TestResult(WebObjectProxy):

    def __init__(self, source=None, **args):
        super(TestResult, self).__init__(source, **args)

    def generateCsv(self, filePath, timeout=None):
        """
        Generate a CSV with all of the historical values of the stats in the whole test. You can optionally specify a 
        maximum timeout to wait for the stats to become available.

        For each group of stats in this test, for each timestamp when stats were read, there will be one or 
        more lines in the CSV with that timestamp and the following properties:
        - it has a `timestamp` property indicating the number of milliseconds since test start when the data was read
        - if the StatsSource has any `keys`, for each timestamp there will be one row for each unique combination of values of those keys 
          in the current test
        - there will be a header row with a `timestamp` column and the one column for each element of `keys` and `stats`
        - for each timestamp, the rows will be ordered by the first statistic in this StatsSource's `orderBy` property, then by the second etc.
        - for each timestamp, there will only be at most `limit` rows
        - the selected rows will respect the `filter` condition
        - if `distinct` is true, there will never be identical rows for a specific timestamp
        """

        generateCsvLink = next(link.href for link in self.links if link.rel == 'generateCsv operation')
        asyncGenerationReply = self._source_.convention.httpPostRaw(url=generateCsvLink, timeout=timeout, stream=True)
        if not asyncGenerationReply:
            raise ValueError("The server failed to generate a CSV bundle.")
        if asyncGenerationReply.status_code == httplib.ACCEPTED:
            asyncGenerationReply = self._source_.convention._httpPollAsyncOperation(asyncGenerationReply, timeout=timeout).resultUrl
        with open(filePath, "wb+") as statsFile:
            self._source_.convention._httpStreamBinaryResultToFile(asyncGenerationReply, statsFile)

    def exportConfig(self, filePath, timeout=None):
        """
        Exports the configuration used to run this test to a file.
        """

        exportConfigLink = next(link.href for link in self.links if link.rel == 'exportConfig operation')
        asyncGenerationReply = self._source_.convention.httpGetRaw(url=exportConfigLink, timeout=timeout, stream=True)
        if not asyncGenerationReply:
            raise ValueError("The server failed to generate a CSV bundle.")
        if asyncGenerationReply.status_code == httplib.ACCEPTED:
            asyncGenerationReply = self._source_.convention._httpPollAsyncOperation(asyncGenerationReply, timeout=timeout).resultUrl
        with open(filePath, "wb+") as configFile:
            for chunk in asyncGenerationReply.iter_content(chunk_size=self._source_.convention.kStandardStreamingChunkSize):
                configFile.write(chunk)
            configFile.flush()

    def load(self):
        """
        Loads a test result into a new session and returns the session object.
        """
        loadLink = next(link.href for link in self.links if link.rel == 'load operation')
        reply = self._source_.convention.httpPostRaw(loadLink)
        if reply.status_code == httplib.ACCEPTED:
            status = self._source_.convention._httpPollAsyncOperation(reply)
            return self._source_.convention.joinSession(status.sessionId)
        else:
            raise WebException("Unable to load test result %s" % self.id)

    @property
    def failReasons(self):
        return self._source_.convention.httpGet(next(link.href for link in self.links if link.rel == 'failReasons'))


class StatsSource(WebObjectProxy):
    """
    Represents a source of statistics for the current test.
    You can use this class to get the latest values for the statistics it represents, 
    by using the `values` property.
    You can also generate a CSV and download it to the local machine using the `generateCsv` method.

    The snapshot returned by the `values` property is guaranteed to have the following shape:
    - it has a `timestamp` property indicating the number of milliseconds since test start when the data was read
    - if the StatsSource has any `keys`, there will be one row for each unique combination of values of those keys 
      in the current test; you can access a specific row by using the `rowByKeys('ValueOfKey1', 'ValueOfKey2')` method
    - each row (if any) will have one column for each of this StatsSource's `keys` and `stats`; you can access a specific
      column using the `value('StatName')` method
    - the rows will be ordered by the first statistic in this StatsSource's `orderBy` property, then by the second etc.
    - there will only be at most `limit` rows
    - the data will only extend back in time for at most `cacheSize` seconds since the current test time
    - the selected rows will respect the `filter` condition
    - if `distinct` is true, there will never be identical rows
    """

    def __init__(self, source=None, **args):
        super(StatsSource, self).__init__(source, **args)

    def generateCsv(self, filePath, timeout=None):
        """
        Generate a CSV with all of the historical values of the stats in the statGroupName group. You can optionally specify a 
        maximum timeout to wait for the stats to become available.

        For each timestamp when stats were read, there will be one or more lines in the CSV with that timestamp and the following 
        properties:
        - it has a `timestamp` property indicating the number of milliseconds since test start when the data was read
        - if the StatsSource has any `keys`, for each timestamp there will be one row for each unique combination of values of those keys 
          in the current test
        - there will be a header row with a `timestamp` column and the one column for each element of `keys` and `stats`
        - for each timestamp, the rows will be ordered by the first statistic in this StatsSource's `orderBy` property, then by the second etc.
        - for each timestamp, there will only be at most `limit` rows
        - the selected rows will respect the `filter` condition
        - if `distinct` is true, there will never be identical rows for a specific timestamp
        """

        generateCsvLink = next(link.href for link in self.links if link.rel == 'generateCsv operation')
        asyncGenerationReply = self._source_.convention.httpPostRaw(url=generateCsvLink, timeout=timeout, stream=True)
        if not asyncGenerationReply:
            raise ValueError("The server failed to generate a CSV.")
        if asyncGenerationReply.status_code == httplib.ACCEPTED:
            asyncGenerationReply = self._source_.convention._httpPollAsyncOperation(asyncGenerationReply, timeout=timeout).resultUrl
        with open(filePath, "w+") as statsFile:
            for chunk in asyncGenerationReply.iter_content(chunk_size=self._source_.convention.kStandardStreamingChunkSize):
                statsFile.write(chunk)
            statsFile.flush()

    @property
    def values(self):
        """
        Read a snapshot with the latest values of the stats in this group.

        @return A Snapshot object representing the stats returned by the server.

        The returned snapshot is guaranteed to have the following shape:
        - it has a `timestamp` property indicating the number of milliseconds since test start when the data was read
        - if the StatsSource has any `keys`, there will be one row for each unique combination of values of those keys 
          in the current test; you can access a specific row by using the `rowByKeys('ValueOfKey1', 'ValueOfKey2')` method
        - each row (if any) will have one column for each of this StatsSource's `keys` and `stats`; you can access a specific
          column using the `value('StatName')` method
        - the rows will be ordered by the first statistic in this StatsSource's `orderBy` property, then by the second etc.
        - there will only be at most `limit` rows
        - the data will only extend back in time for at most `cacheSize` seconds since the current test time
        - the selected rows will respect the `filter` condition
        - if `distinct` is true, there will never be identical rows
        """
        data = self._source_.convention.httpGet(next(link.href for link in self.links if link.rel == 'values'))
        if data is not None:
            return Snapshot(data, self)
        return None


class Snapshot(object):

    def __init__(self, snapshot, statsRequest):
        self._snapshot = snapshot
        self.statsRequest = statsRequest
        self.columns = {}

        statIndex = 0

        for col in self._emptyIfNone(statsRequest.keys) + self._emptyIfNone(statsRequest.stats):
            self.columns[col.definition] = statIndex
            if None != col.alias:
                self.columns[col.alias] = statIndex
            statIndex += 1

        values = self._emptyIfNone(self._snapshot.values)

        self.rows = [_Row(rowIndex, self._snapshot, self.columns) for rowIndex in range(0, len(values))]

    @classmethod
    def _emptyIfNone(self, coll):
        if coll is None:
            return []
        return coll

    @property
    def isEmpty(self):
        """
        @return True if there are no rows in this Snapshot, False otherwise
        """
        return self._snapshot.timestamp == -1 \
            or len(self._emptyIfNone(self.rows)) == 0

    @property
    def isLast(self):
        """
        @return True if the data in this snapshot was collected after traffic stopped, False otherwise
        """
        return self._snapshot.last

    @property
    def timestamp(self):
        """
        @return the time, in milliseconds, between the start of the test and when the data was collected
        """
        return self._snapshot.timestamp

    def rowByKeys(self, *keyValues):
        """
        Helper method to get a row with a specific combination of key values, assuming that the data has any keys.

        Example: if the Snapshot is created from a StatsSource with `keys: [{alias: 'Traffic' [...]}, {alias: 'Protocol'[...]}]`, 
        then rowByKeys('Traffic1', 'HTTP') will return the values values of the HTTP protocol on the first traffic.

        @param args: the values of each key, in the same order they were specified in the request's `keys`
        """
        if len(keyValues) != len(self.statsRequest.keys):
            raise Exception("Snapshot:rowByKeys(): The number of specified key(s): %s does not match the number keys specified in the stat request %s" % (len(argv), len(self.statsRequest.keys)))

        rowIndex = 0
        for row in self._snapshot.values:
            if self._compare(keyValues, row):
                break
            rowIndex += 1

        if (rowIndex >= len(self.rows)):
            raise Exception("Snapshot:rowByKeys(): Unable to find a row matching the specified key(s)")

        return _Row(rowIndex, self._snapshot, self.columns)

    def _compare(self, keys, values):
        for (i, j) in zip(keys, values):
            if i != j:
                return False

        return True

    def getSummary(self):
        result = "Query Id:%s, TS:%s, %s rows" % (self.statsRequest.id, self.timestamp, len(self.rows))
        return result

    def printAsTable(self):

        result = "Query Id:%s" % (self.statsRequest.id)

        colWrap = [textwrap.wrap(column.alias, 10) for column in
                   self._emptyIfNone(self.statsRequest.keys) + self._emptyIfNone(self.statsRequest.stats)]

        colHeader = ""
        lineIndex = 0
        cont = 1
        while cont == 1:
            if lineIndex == 0:
                curLine = "%12s" % "Timestamp"
            else:
                curLine = "%12s" % ""

            cont = 0
            for col in colWrap:
                if lineIndex < len(col):
                    curLine += ("%12s" % col[lineIndex])
                    cont = 1
                else:
                    curLine += ("%12s" % "")

            colHeader += curLine
            if cont == 1:
                colHeader += "\n"
            lineIndex += 1

        result += "\n" + colHeader + "\n"

        for rowData in self._emptyIfNone(self._snapshot.values):
            rowString = "%12s" % self._snapshot.timestamp
            for cellValue in rowData:
                rowString += "%12s" % str(cellValue)[:11]
            result += rowString + "\n"

        return result

    def __repr__(self):
        return \
            "timestamp:%s\n" % self.timestamp\
            + ",".join(stat.alias for stat in
                       self._emptyIfNone(self.statsRequest.keys)
                       + self._emptyIfNone(self.statsRequest.stats)) \
            + "\n" \
            + "\n".join(str(row) for row in self.rows)


class _Row(object):

    def __init__(self, rowIndex, snapshot, columns):
        self._snapshot = snapshot
        self._rowIndex = rowIndex
        self._columns = columns

    @property
    def timestamp(self):
        """
        @return the time, in milliseconds, between the start of the test and when the data was collected
        """
        return self._snapshot.timestamp

    def value(self, statName):
        """
        Returns the value of the speecified stat on this row.

        @param statName: the alias of the stat to read data for.
        """
        return self._snapshot.values[self._rowIndex][self._columns[statName]]

    def __repr__(self):
        return str(self._snapshot.values[self._rowIndex])
