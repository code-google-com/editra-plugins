# -*- coding: utf-8 -*-
# Name: RpdbStateManager.py
# Purpose: Debug State
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
##############################################################################
""" RpdbStateManager functions """

__version__ = "0.2"
__author__ = "Mike Rans"
__svnid__ = "$Id$"
__revision__ = "$Revision$"

#-----------------------------------------------------------------------------#
# Imports
from time import sleep
import wx

# Local Imports
import rpdb2
from PyTools.Common.PyToolsUtils import RunProcInThread
#----------------------------------------------------------------------------#

class RpdbStateManager(object):
    def __init__(self, rpdb2debugger):
        super(RpdbStateManager, self).__init__()
        self.m_state = rpdb2.STATE_DETACHED
        self.rpdb2debugger = rpdb2debugger
        state = self.rpdb2debugger.sessionmanager.get_state()
        self.update_state(rpdb2.CEventState(state))
        
        event_type_dict = {rpdb2.CEventConflictingModules: {}}
        self.rpdb2debugger.register_callback(self.update_conflicting_modules, event_type_dict)
        
        event_type_dict = {rpdb2.CEventState: {}}
        self.rpdb2debugger.register_callback(self.update_state, event_type_dict)

    def update_conflicting_modules(self, event):
        modulesstr = ', '.join(event.m_modules_list)
        wx.CallAfter(self.conflictingmodules, modulesstr)
        
    def update_state(self, event):
        wx.CallAfter(self.callback_state, event.m_state)

    def finalmessage(self):
        sleep(1)
        self.rpdb2debugger.debuggeroutput("\nDebugger detached.")
        sleep(1)
        self.rpdb2debugger.debuggeroutput = lambda x:None
    
    def callback_state(self, state):
        old_state = self.m_state
        self.m_state = state

        # change menu or toolbar items displayed according to state eg. running, paused etc.
        if self.m_state == rpdb2.STATE_DETACHED:
            self.rpdb2debugger.attached = False
            self.rpdb2debugger.analyzing = False
            if self.rpdb2debugger.breakpoints_installed:
                # clear all debugging stuff as we have finished
                self.rpdb2debugger.clear_all()
                worker = RunProcInThread("Detach", None, self.finalmessage)
                worker.start()
        elif (old_state in [rpdb2.STATE_DETACHED, rpdb2.STATE_DETACHING, rpdb2.STATE_SPAWNING, rpdb2.STATE_ATTACHING]) and (self.m_state not in [rpdb2.STATE_DETACHED, rpdb2.STATE_DETACHING, rpdb2.STATE_SPAWNING, rpdb2.STATE_ATTACHING]):
            self.rpdb2debugger.attached = True

        if self.m_state == rpdb2.STATE_BROKEN:
            # we hit a breakpoint
            # show the stack viewer, threads viewer, namespace viewer
            self.rpdb2debugger.analyzing = False
            pass
            
        elif self.m_state == rpdb2.STATE_ANALYZE:
            # we are analyzing an exception
            # show the stack viewer and namespace viewer
            self.rpdb2debugger.analyzing = True
            pass
        else:
            # any other state
            # don't show any viewers
            self.rpdb2debugger.analyzing = False
            pass
        self.rpdb2debugger.updateanalyze()
        self.rpdb2debugger.debugbuttonsupdate()