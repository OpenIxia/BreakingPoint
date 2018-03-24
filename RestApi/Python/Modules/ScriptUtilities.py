#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division

#
#   scriptuyil.py
#
#   Utilities shared by the webapi samples and scripts.
#
#   Note: Backwards compatibility for these utilities is not guaranteed.
#
#   (c) Copyright 2013 Ixia
#

import getopt
import sys

from webApi import *

DEFAULT_PORT = 80
DEFAULT_SECURE_PORT = 443
PORT_SEPARATOR = ":"
kWebServerSecureFormat = "https://%s:%s"
kWebServerNonsecureFormat = "http://%s:%s"
params = None   # global


class FlexObject(object):
    """A class to hold arbitrary properties. Like a dict but with object syntax.

    You can pass in key=value pairs to set the properties on the object, or just
    set them directly after constructing.
    """

    def __init__(self, **kwArgs):
        self.__dict__.update(kwArgs)


def standardArgsHelp(extraMsg=""):
    global params
    if extraMsg:
        print("Error: " + extraMsg)
    optionalArgs = ""
    if params.requireClientPort:
        optionalArgs += "-c chassis/card/port "
    if params.requireServerPort:
        optionalArgs += "-s chassis/card/port "
    if params.webServerAsOption:
        optionalArgs += "[-w server-ip[:port]] "
    optionalArgs += "[-e ssl] "
    if not params.webServerAsOption:
        optionalArgs += "[server-ip[:port]] "
    print("Usage: %s [-u userkey] [-n username -p password] %s" % (sys.argv[0], optionalArgs))
    print("Note that server-ip must come after any other flags used.")
    print("Default port is port 80 or port 443 if -e ssl is used.")
    sys.exit(2)


def parseStandardArgs(argv,
                      helpFunc=standardArgsHelp,
                      requireClientPort=True,
                      requireServerPort=True,
                      webServerAsOption=False):
    """Returns an object with clientPort, serverPort, and webServerAddr properties.

    @param argv: The command line parameters array (usually called with sys.argv)
    @param helpFunc: A method that takes a single parameter and is called if there is a syntax problem
    @param requireClientPort: pass in False to skip requirement for -c option
    @param requireServerPort: pass in False to skip requirement for -s option
    @param webServerAsOption: accept the web server address as the -w option (defaults to localhost)
    """
    global params
    params = FlexObject(argv=argv,
                        requireClientPort=requireClientPort,
                        requireServerPort=requireServerPort,
                        webServerAsOption=False)

    userkey = ""
    clientPort = None
    serverPort = None
    username = ""
    password = ""
    serverString = ""
    encryption = False

    try:
        optionString = "hu:n:p:c:s:e:"
        if webServerAsOption:
            optionString += "w:"
        opts, args = getopt.getopt(argv[1:], optionString)
    except getopt.GetoptError:
        helpFunc()

    for opt, arg in opts:
        if opt == '-h':
            helpFunc()
        elif opt == "-u":
            userkey = arg
        elif opt == "-n":
            username = arg
        elif opt == "-p":
            password = arg
        elif opt == '-c':
            clientPort = parsePort(arg, helpFunc)
        elif opt == '-s':
            serverPort = parsePort(arg, helpFunc)
        elif opt == "-w":
            serverString = arg
        elif opt == "-e":
            if arg.lower() != "ssl":
                helpFunc("Only SSL encryption is supported (usage: '-e ssl').")
            encryption = True
        else:
            helpFunc("Unrecognized option %s." % opt)

    if not webServerAsOption:
        if len(args) > 2:
            helpFunc()
        if len(args) > 0:
            serverString = args[0]

    # default components of base url
    serverIp = "localhost"
    if encryption:
        serverFormat = kWebServerSecureFormat
        serverTcpPort = DEFAULT_SECURE_PORT
    else:
        serverFormat = kWebServerNonsecureFormat
        serverTcpPort = DEFAULT_PORT

    if serverString:
        serverSplit = serverString.split(PORT_SEPARATOR)
        if len(serverSplit) == 1:
            serverIp = serverSplit[0]
        elif len(serverSplit) == 2:
            serverIp = serverSplit[0]
            serverTcpPort = serverSplit[1]
        else:
            helpFunc("Invalid server or 'server:port': %s" % serverString)

    serverAddr = serverFormat % (serverIp, serverTcpPort)

    if not userkey and not (username and password):
        helpFunc("either userkey or both username and password are required")

    if requireClientPort and not clientPort:
        helpFunc("missing client port.")

    if requireServerPort and not serverPort:
        helpFunc("missing server port.")

    # Note: userkey published under userKey for backwards compatibility with older scripts
    return FlexObject(args=args,
                      userkey=userkey,
                      userKey=userkey,
                      username=username,
                      password=password,
                      clientPort=clientPort,
                      serverPort=serverPort,
                      webServerAddr=serverAddr)


def parsePort(chassisCardPortString, helpFunc):
    """Parse a string in chassis/card/port format and return an equivalent JSON proxy.

    The JSON proxy will have chassis, cardId, and portId properties, with chassis as a string,
    and cardId and portId as integers.

    @param chassisCardPortString: The chassis/card/port string
    """
    chassisCardPortString = chassisCardPortString.strip('"')
    portParts = chassisCardPortString.split("/")
    if len(portParts) != 3:
        helpFunc("Need 3 elements separated by two slashes")
    try:
        cardId = int(portParts[1])
    except:
        helpFunc("Second element not an integer: %s" % portParts[1])
    try:
        portId = int(portParts[2])
    except:
        helpFunc("Third element not an integer: %s" % portParts[2])
    return WebObject(chassis=portParts[0], cardId=cardId, portId=portId)


class ScriptBase(object):
    """Base class for script dispatcher classes.

    To use subclass this class, and create methods with the format a_b_Cmd
    """

    kCmd = "_cmd"
    kPrefix = "prefix"

    def __init__(self, scriptName):
        super(ScriptBase, self).__init__()
        self.scriptName = scriptName

    @classmethod
    def findCommandMethodNames(cls, partFilter=None, minParts=0, maxParts=0, **kwArgs):
        # finds the list of method names of command dispatchers
        # accepts optional kwArgs:
        #     partFilter = a lambda expression
        #     minParts = the min number of words in a command.
        #     maxParts = the max number of words in a command.
        #
        #   so for example help_detail_cmd (to dispatch "help detail") has 2 parts.
        #
        result = [method for method in dir(cls) if method.endswith(ScriptBase.kCmd)]
        if partFilter:
            result = list(filter(partFilter, result))
        if maxParts:
            # note that the split will have count +1 because of _cmd
            result = [x for x in result if len(x.split("_")) <= maxParts + 1]
        if minParts:
            # note that the split will have count +1 because of _cmd
            result = [x for x in result if len(x.split("_")) >= minParts + 1]
        return result

    @classmethod
    def getMethodName(cls, cmdAndParamsList, **kwArgs):
        # returns the method specified by argument after converting it to lowercase
        # finds the longest matching substring
        #
        # cmdAndParamsList is an argv-like list but just the non-keyword parameters (and no script name)
        commands = cls.findCommandMethodNames(**kwArgs)
        commands = [x.replace(ScriptBase.kCmd, "") for x in commands]
        commands.sort(lambda x, y: len(y) - len(x))
        searchName = "_".join([x.lower() for x in cmdAndParamsList])
        for command in commands:
            if searchName.startswith(command):
                return command + ScriptBase.kCmd
        raise ValueError("No command found in %s" % cmdAndParamsList)

    def execute(self, cmdAndParamsList, **kwArgs):
        # cmdAndParamsList is an argv-like list but just the non-keyword parameters (and no script name)
        if not cmdAndParamsList:
            raise ValueError("Missing command.")
        modargs = [arg.strip('"') for arg in cmdAndParamsList]
        try:
            methodName = self.getMethodName(modargs)
            method = getattr(self.__class__, methodName)
        except ValueError as e:
            raise Exception("Invalid command: %s" % " ".join(cmdAndParamsList))
        lastMethodArg = len(methodName.split("_")) - 1
        return method(self, *modargs[lastMethodArg:], **kwArgs)

    def runAllCommands(self, **kwArgs):
        prefix = kwArgs.pop(self.kPrefix, "")
        startsWith = kwArgs.pop("startsWith", "")
        sort = kwArgs.pop("sort", "")
        kwArgs[self.kPrefix] = prefix + "  "
        commandMethods = self.findCommandMethodNames(partFilter=lambda x: x.startswith(startsWith), **kwArgs)
        if sort:
            commandMethods.sort()
        for method in commandMethods:
            self.execute([method], **kwArgs)

    @classmethod
    def output(cls, format="", *args, **kwArgs):
        prefix = kwArgs.pop(cls.kPrefix, "")
        if args:
            print((prefix + format) % args)
        else:
            print(prefix + format)
