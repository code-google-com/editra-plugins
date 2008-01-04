#!/usr/bin/python
# -*- coding: utf-8 -*-
###############################################################################
#Name: cbrowser.py                                                           #
#Purpose: UI portion of the CommentBrowser Plugin                            #
#Author: DR0ID <dr0iddr0id@googlemail.com>                                   #
#Copyright: (c) 2008 DR0ID                                                   #
#Licence: wxWindows Licence                                                  #
###############################################################################

"""
Provides a comment browser panel and other UI components for Editra's
CommentBrowser Plugin.

"""

__author__ = 'DR0ID <dr0iddr0id@googlemail.com>'
__svnid__ = '$Id: browser.py 50827 2007-12-19 08:48:03Z CJP $'
__revision__ = '$Revision$'

#-----------------------------------------------------------------------------#
#Imports
import os.path
import wx

#Editra Library Modules
import ed_glob
#import ed_menu
from extern import flatnotebook as FNB

#Local
from cbrowserlistctrl import TestListCtrl

#--------------------------------------------------------------------------#
#Globals
_ = wx.GetTranslation

PANE_NAME = u'CommentBrowser'
CAPTION = _(u'Comment Browser')
ID_CBROWSERPANE = wx.NewId()
ID_COMMENTBROWSE = wx.NewId()
ID_TIMER = wx.NewId()

#--------------------------------------------------------------------------#
#TODO: todos list for all opened files 
    #TODO: update if gets focus?
    #TODO: update every second?
    #TODO: update when tab changes (should every tab have its own todo list??)
# [14:15]	cprecord: current_txt_ctrl.Bind(wx.EVT_CHAR, self.OnListenToKeys)
# [14:15]	cprecord: def OnListenToKeys(self, evt):
# [14:15]	cprecord:     e_key = event.GetKeyCode()
# # [14:16]	cprecord:     charval = unichar(e_key)
# [14:17]	DR0ID_: lets say 0.5 seconds after the last key hit -> update the todo's list
# [14:19]	cprecord: you could make a timer and listen for wx.EVT_TIMER, when starting the timer object give it an agrument of 500 milliseconds
# [14:19]	cprecord: wx.Timer(self)
# [14:19]	DR0ID_: oh, that simple :-D
# [14:19]	cprecord: yea pretty easy
# [14:19]	cprecord: just make sure that you override __del__ and make sure the timer is stopped when the windows is deleted
# [14:20]	DR0ID_: ok, thx, as you know, I have little experience with wxpython 
# [14:20]	cprecord: or there will likely be PyDeadObjectErrors when closing the editor
#TODO: two tabs, one for current file, one for all opened files??

#columns: (priority, tasktype, comment, file, linenr)

#TODO: better comments
#TODO: code clean up (self._log()!!!)



class CBrowserPane(wx.Panel):

    """Creates a Commentbrowser panel"""

    def __init__(
        self,
        parent,
        id,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.NO_BORDER,
        ):
        """ Initializes the CBrowserPane class"""

        wx.Panel.__init__(
            self,
            parent,
            id,
            pos,
            size,
            style,
            )

        #---- private attr ----#
        self._mainwin = parent
        self.__log = wx.GetApp().GetLog()
        
        self._timerenabled = False
        self._timer = wx.Timer(self, ID_TIMER)
        self._intervall = 3000; #  milli seconds
        
        #TODO: datastructure for todos caching
        # {key:(page, fullname, (prio, task, desr, file, line)), filename2:{key:(),...},...}
#         self._entryDict = dict()

        #---- Add Menu Items ----#
        viewm = self._mainwin.GetMenuBar().GetMenuByName('view')
        self._mi = viewm.InsertAlpha(ID_COMMENTBROWSE, CAPTION,
                _('Open Comment Browser Sidepanel'), wx.ITEM_CHECK,
                after=ed_glob.ID_PRE_MARK)

        #---- Gui ----#
        self._listctrl = TestListCtrl(self)
        
        self._taskChoices = ['ALL', 'TODO', 'HACK', 'XXX', 'FIXME']
        self._taskFilter = wx.Choice(self, choices=self._taskChoices)
        self._taskFilter.SetStringSelection(self._taskChoices[0])
        self._checkBoxAllFiles = wx.CheckBox(self, label=_("All opened files"), style=wx.ALIGN_LEFT)
        
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        tasklbl = wx.StaticText(self, label=_("Taskfilter: "))
        hsizer.Add((5, 5))
        hsizer.Add(tasklbl, 0, wx.ALIGN_CENTER_VERTICAL)
        hsizer.Add((5, 5))
        hsizer.Add(self._taskFilter, 0, wx.ALIGN_CENTER_VERTICAL)
        hsizer.Add((-1, 5), 1, wx.EXPAND)
        hsizer.Add(self._checkBoxAllFiles, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        hsizer.Add((5, 5))
        
        #TODO: update button: remove or not?
        btn = wx.Button(self, label=_("Update"))
        hsizer.Add(btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
        hsizer.Add((5, 5))

        # Use small version of controls on osx as they are more suitable in this
        # use case.
        if wx.Platform == '__WXMAC__':
            for win in [self._taskFilter, tasklbl, btn, self._checkBoxAllFiles]:
                win.SetWindowVariant(wx.WINDOW_VARIANT_SMALL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(hsizer, 0, wx.EXPAND)
        sizer.Add(self._listctrl, 1, wx.EXPAND)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Layout()
        
        #---- Bind events ----#
        
        self._mainwin.Bind(wx.EVT_ACTIVATE, self.OnActivate)
        
        self.Bind(wx.EVT_TIMER, self.OnListUpdate, self._timer)
        if self._timerenabled:
            self._timer.Start(self._intervall)
        
        btn.Bind(wx.EVT_BUTTON, self.OnListUpdate, btn)
        self._taskFilter.Bind(wx.EVT_CHOICE, self.OnListUpdate, self._taskFilter)
        
# FIXME: if this are uncommented the list is not drawn proberly, I dont know why
#        self._mainwin.GetNotebook().Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CLOSED, self.OnPageClose, self._mainwin.GetNotebood())
#        self._mainwin.GetNotebook().Bind(FNB.EVT_FLATNOTEBOOK_PAGE_CHANGED, self.OnPageChange, self._mainwin.GetNotebook())
        self._log("-----------------------binding page change event done<<<<<<<<<<<<")

    def _log(self, msg):
        """writes a log message to the app log"""
        self.__log('[commentbrowser] ' + str(msg))

    def __del__(self):
        self._log("__del__(): stopping timer")
        self._timer.Stop()
        super(CBrowserPane, self).__del__()

    #---- Methods ----#
    
    def UpdateCurrent(self, textctrl=None):
        """
        Updates the entries of the current page in the todo list.
        If textctrl is None then it trys to use the current page,
        otherwise it trys to 
        """
        if textctrl is None:
            textctrl = self._mainwin.GetNotebook().GetCurrentCtrl()

        if textctrl is not None:
#             self._log(help(self._mainwin.GetNotebook()))
            try:
                fullname = textctrl.GetFileName()
                filename = os.path.split(fullname)[1]

                textlines = textctrl.GetText().splitlines()
            except Exception, e:
                self._log("[error]:" + str(e.message))
                self._log(type(e))
                return
            tasklist = []
            filterVal = self._taskFilter.GetStringSelection()
            choice = self._taskChoices.index(filterVal)
            for idx, line in enumerate(textlines):
                prio = 1
                descr = ''
                #TODO: use regex to match anything we are looking for
                
                # the TODO
                for tasknr in range(1, len(self._taskChoices)):
                    # tasknr: meaning is the order of the self._taskChoices list
                    prio = 1
                    if (choice==0 or choice==tasknr) and line.find(self._taskChoices[tasknr]) != -1:
                        descr = line
                        prio += tasknr # prio is higher if further in the list
                        tasklist.append( (prio,self._taskChoices[tasknr], descr, filename, idx+1))
                    
            # TODO: only clear the entries for the current page (cache it)
            # TODO: prevent flickering of list redraw
            self._listctrl.Clear(refresh=False)
            keys = self._listctrl.AddEntries(tasklist)
            self._listctrl.SortListItems(0, 0) # TODO: should be same sort order that the list is already sorted (if possible?)

    def OnListUpdate(self, event):
        self._log("OnListUpdate"+str(event))
        if event.GetId() == ID_TIMER:
            self._log("timer update")
        self._log("timer running: "+str(self._timer.IsRunning()))
        self.UpdateCurrent()

    def OnPageClose(self, event):
        self._log("OnPaneClose")
        
    def OnPageChange(self, event):
        self._log("OnPageChange")

    def OnActivate(self, event):
        self._log("OnActivate")
        if event.GetActive():
            # awake, reastart timer
            if self._timerenabled:
                self._timer.Start(self._intervall)
            self.UpdateCurrent() # XXX: <-- really needed here? because during sleep the file cant be changed ;-)
            self._log("[timer] OnActivate: restarting timer")
        else:
            # going to sleep, stop timer
            self._timer.Stop()
            self._log("[timer] OnActivate: stopoing timer")


    #---- Eventhandler ----#
    def OnShow(self, evt):
        """Shows the Comment Browser"""

        self._log('OnShow')
        if evt.GetId() == ID_COMMENTBROWSE:
            mgr = self._mainwin.GetFrameManager()
            pane = mgr.GetPane(PANE_NAME)
            if pane.IsShown():
                pane.Hide()
                self._mi.Check(False)
            else:
#               Profile_Set('SHOW_FB', False)
                pane.Show()
                self._mi.Check(True)
#               Profile_Set('SHOW_FB', True)
            mgr.Update()
        else:
            evt.Skip()

    def OnClose(self, evt):
        """Clean up settings when Comment Browser is closed"""

        evt_caption = evt.GetPane().caption
        if CAPTION == evt_caption:
            self._log('OnClose ')
            self._mi.Check(False)
            evt.Skip()



#---------------------------------------------------------------------------- #