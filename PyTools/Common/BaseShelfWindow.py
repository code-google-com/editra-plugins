# -*- coding: utf-8 -*-
# Name: BaseShelfWindow.py
# Purpose: Base shelf window
# Author: Mike Rans
# Copyright: (c) 2010 Mike Rans
# License: wxWindows License
###############################################################################

"""Editra Base Shelf display window"""

__author__ = "Mike Rans"
__svnid__ = "$Id $"
__revision__ = "$Revision $"

#-----------------------------------------------------------------------------#
# Imports
import os
import wx

# Editra Libraries
import ed_glob
import util
import eclib
import ed_msg
import syntax.synglob as synglob

# Local imports
from Common import ToolConfig
from Common.PythonDirectoryVariables import PythonDirectoryVariables

# Globals
_ = wx.GetTranslation
#-----------------------------------------------------------------------------#

class BaseShelfWindow(eclib.ControlBox):
    __directoryVariables = {
        synglob.ID_LANG_PYTHON: PythonDirectoryVariables
    }
    
    def __init__(self, parent):
        """Initialize the window"""
        super(BaseShelfWindow, self).__init__(parent)

        # Attributes
        # Parent is ed_shelf.EdShelfBook
        self._mw = self.__FindMainWindow()
        self._log = wx.GetApp().GetLog()
        
    def setup(self, listCtrl):
        self._listCtrl = listCtrl
        self._curfile = u""

        # Setup
        self._listCtrl.set_mainwindow(self._mw)
        self.ctrlbar = eclib.ControlBar(self, style=eclib.CTRLBAR_STYLE_GRADIENT)
        self.ctrlbar.SetVMargin(2, 2)
        if wx.Platform == '__WXGTK__':
            self.ctrlbar.SetWindowStyle(eclib.CTRLBAR_STYLE_DEFAULT)
        rbmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_PREF), wx.ART_MENU)
        if rbmp.IsNull() or not rbmp.IsOk():
            rbmp = None
        self.cfgbtn = eclib.PlateButton(self.ctrlbar, wx.ID_ANY, bmp=rbmp,
                                        style=eclib.PB_STYLE_NOBG)
        self.cfgbtn.SetToolTipString(_("Configure"))
        self.ctrlbar.AddControl(self.cfgbtn, wx.ALIGN_LEFT)
        return self.ctrlbar
        
    def layout(self, taskbtndesc, taskfn):
        rbmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_BIN_FILE), wx.ART_MENU)
        if rbmp.IsNull() or not rbmp.IsOk():
            rbmp = None
        self.taskbtn = eclib.PlateButton(self.ctrlbar, wx.ID_ANY, _(taskbtndesc), rbmp,
                                        style=eclib.PB_STYLE_NOBG)
        self.ctrlbar.AddControl(self.taskbtn, wx.ALIGN_RIGHT)

        # Layout
        self.SetWindow(self._listCtrl)
        self.SetControlBar(self.ctrlbar, wx.TOP)

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnShowConfig, self.cfgbtn)
        self.Bind(wx.EVT_BUTTON, taskfn, self.taskbtn)

        # Editra Message Handlers
        ed_msg.Subscribe(self.OnThemeChanged, ed_msg.EDMSG_THEME_CHANGED)
        
    def __del__(self):
        ed_msg.Unsubscribe(self.OnThemeChanged)

    def GetMainWindow(self):
        return self._mw

    def __FindMainWindow(self):
        """Find the mainwindow of this control
        @return: MainWindow or None
        """
        def IsMainWin(win):
            """Check if the given window is a main window"""
            return getattr(tlw, '__name__', '') == 'MainWindow'

        tlw = self.GetTopLevelParent()
        if IsMainWin(tlw):
            return tlw
        elif hasattr(tlw, 'GetParent'):
            tlw = tlw.GetParent()
            if IsMainWin(tlw):
                return tlw

        return None

    def OnThemeChanged(self, msg):
        """Icon theme has changed so update button"""
        rbmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_BIN_FILE), wx.ART_MENU)
        if rbmp.IsNull() or not rbmp.IsOk():
            return
        else:
            self.taskbtn.SetBitmap(rbmp)
            self.taskbtn.Refresh()
            
    def OnShowConfig(self, event):
        """Show the configuration dialog"""
        mw = self.GetMainWindow()
        dlg = ToolConfig.ToolConfigDialog(mw)
        dlg.CenterOnParent()
        dlg.ShowModal()

    def get_directory_variables(self, filetype):
        try:
            return self.__directoryVariables[filetype]()
        except Exception:
            pass
        return None
