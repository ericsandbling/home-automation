#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Greger Update Agent module for the Greger Client Module
"""

__author__ = "Eric Sandbling"
__license__ = 'MIT'
__status__ = 'Development'

# System modules
import os
import logging
import subprocess
from threading import Event
from threading import Thread

# Local Modules
from cfg import getLocalConfig

class UpdateAgent(Thread):
    """
    Main class which holds the main sequence of the application.
    """
    def __init__(self, settings):
        '''
        Initialize the main class
        '''
        Thread.__init__(self)

        # Setup logging
        self.logPath = "root.GUA"
        self.log = logging.getLogger(self.logPath)
        localLog = logging.getLogger(self.logPath + ".__init__")
        localLog.debug("Initiating Greger Update Agent...")

        # Get setting
        self.settings = settings

        # Stop execution handler
        self.stopExecution = Event()

        # Get local path
        self._location = os.path.abspath(__file__)
        self._location = self._location[:-15] # Trim gcm/__main__.py from path to get at location of application
        localLog.debug("Local path: " + self._location)

        self.log.info("Greger Update Agent initiated successfully!")
        # self._main()

    def updateLocalRevisionRecord(self, serverRevision):
        '''
        Update local revision record (.gcm)
        '''
        # Logging
        localLog = logging.getLogger(self.logPath + ".updateLocalRevisionRecord")
        localLog.debug("Updating local revision record (.gcm)...")

        # Local parameters
        revisionRecord = self._location + "/.gcm"

        localLog.debug("Attemption to write \"" + str(serverRevision) + "\" to file...")
        with open(revisionRecord,"w") as f:
            f.write(str(serverRevision))
        localLog.debug("Revision record updated!")

        with open(revisionRecord,"r") as f:
            localRevision = f.read()
        localLog.debug("Local Revision: " + str(localRevision))

        return localRevision

    def getServerRevision(self):
        '''
        Retrieve latest revision available on server.
        '''
        # Logging
        localLog = logging.getLogger(self.logPath + ".getServerRevision")
        localLog.debug("Attempting to retrieve latest revision stored on the server...")

        # Locally relevant parameters
        guaSWServerURI = self.settings['guaSWSource']['value']

        # Get server revision info
        localLog.debug("Attempting to retrieve info from server... " + guaSWServerURI)
        try:
            p = subprocess.Popen(
                "svn info " + guaSWServerURI + " | grep \"Last Changed Rev\" | awk '{print $4}'",
                stdout=subprocess.PIPE,
                shell=True)
            (serverRevision, err) = p.communicate()
            serverRevision = int(serverRevision)
            localLog.debug("Server revision = " + str(serverRevision))
            if err is not None:
                localLog.debug("Error message: " + str(err))
        except Exception as e:
            self.log.error("Oops! Something went wrong - " + str(e))

        self.localRevision = self.updateLocalRevisionRecord(serverRevision)

    def run(self):
        '''
        Run Greger Update Agent.
        '''
        # Logging
        localLog = logging.getLogger(self.logPath + ".run")
        localLog.debug("Starting Greger Update Agent main method...")

        while not self.stopExecution.is_set():

            # Get server revision...
            self.getServerRevision()

            self.stopExecution.wait(self.settings['guaCheckUpdateDelay']['value'])