#!/usr/bin/python

import sys
import wx
import os
import time
import wx.grid as gridlib
import subprocess
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
import wx.lib.mixins.listctrl as listmix
from time import sleep
from BeautifulSoup import BeautifulSoup

import re, htmlentitydefs

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)


def removeAll(obj, item):
	r = []
	for i in obj:
		if i !=  item:
			r.append(i)
	return r

path = "C:\Program Files (x86)\Beyond Compare 3\BComp.exe"

files = os.listdir(".")

ID_BUTTON=100
ID_OPEN1=001
ID_OPEN2=002
ID_RDALL=021
ID_RDONE=022

ID_COPY=031
ID_CUT=032
ID_PASTE=033
ID_SELA=034

def insertText(original, new, pos):
	return original[:pos] + new + original[pos:] 

class MyFileDropTarget(wx.FileDropTarget):
	def __init__(self, window):
		wx.FileDropTarget.__init__(self)
		self.window = window
	def OnDropFiles(self, x, y, filenames):        
		for name in filenames:
			try:
				file = open(name, 'r')
				text = file.read()
				file.close()
			except IOError, error:
				dlg = wx.MessageDialog(None, 'Error opening file\n' + str(error))
				dlg.ShowModal()
			except UnicodeDecodeError, error:
				dlg = wx.MessageDialog(None, 'Cannot open non ascii files\n' + str(error))
				dlg.ShowModal()
		self.window.url.ChangeValue(filenames[0])
		self.window.displayFile(self)

class fileDir( wx.ListCtrl, ListCtrlAutoWidthMixin):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT, size=(-1,300))
		ListCtrlAutoWidthMixin.__init__(self)

		self.InsertColumn(0, 'Name')
		self.InsertColumn(1, 'Ext')
		self.InsertColumn(2, 'Size', wx.LIST_FORMAT_RIGHT)
		self.InsertColumn(3, 'Last Modified')

		self.SetColumnWidth(0, 220)
		self.SetColumnWidth(1, 70)
		self.SetColumnWidth(2, 100)
		self.SetColumnWidth(3, 320)

		self.refreshList(".")

		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnClick, self)

	def OnClick(self, event):
		ix_selected = self.GetFirstSelected()-1
		selected = os.path.abspath(files[ix_selected])
		self.GetParent().url.ChangeValue(selected)
		
	def refreshList(self, dir):
		self.InsertStringItem(0, '..')
		j = 1
		for i in files:
			(name, ext) = os.path.splitext(i)
			ex = ext[1:]
			size = os.path.getsize(i)
			sec = os.path.getmtime(i)
			self.InsertStringItem(j, name)
			self.SetStringItem(j, 1, ex)
			self.SetStringItem(j, 2, str(size) + ' B')
			self.SetStringItem(j, 3, time.strftime('%Y-%m-%d %H:%M', time.localtime(sec)))

			if (j % 2) == 0:
				self.SetItemBackgroundColour(j, '#e6f1f5')
			j = j + 1

	def onSelect(self, event):
		state = states[ix_selected][0]

class primPanel(wx.Panel):
	def __init__(self, parent, title):
		super(primPanel, self).__init__(parent, title)

		self.url = wx.TextCtrl(self)
		self.newdir = wx.Button(self, label="File")
		self.newdir.Bind(wx.EVT_BUTTON, self.getNewFile)

		self.prim = fileDir(self)

		self.sec = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(-1,200))
		self.sec.Bind(wx.EVT_MENU, self.selectAllSecText, id=060)
		accel_sec = wx.AcceleratorTable([(wx.ACCEL_CTRL,ord('A'),060)])
		self.sec.SetAcceleratorTable(accel_sec)

		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)

		hbox.Add(self.url, 1, wx.RIGHT, border=5)
		hbox.Add(self.newdir, 0, flag=wx.RIGHT, border=5)

		vbox.Add(hbox, 0, flag=wx.TOP|wx.EXPAND, border=5)
		vbox.Add(self.prim, 1, flag=wx.TOP|wx.EXPAND, border=5)
		vbox.Add(self.sec, 0, flag=wx.TOP|wx.EXPAND, border=5)

		self.SetSizer(vbox)

	def selectAllSecText(self, evt):
		self.sec.SetFocus()
		self.sec.SetSelection(-1,-1)
	
	def getNewFile(self, evt):
		dlg = wx.FileDialog( None, message="Choose a file", defaultFile="", style=wx.FD_OPEN|wx.FD_CHANGE_DIR)
		if dlg.ShowModal() == wx.ID_OK:
			self.url.ChangeValue(dlg.GetPath())
		dlg.Destroy()
	
class PDFCompare(wx.Frame):
	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, None, id, title)

		self.p1 = primPanel(self, -1)
		targ1 = MyFileDropTarget(self.p1)
		self.p1.SetDropTarget(targ1)

		self.p2 = primPanel(self, -1)
		targ2 = MyFileDropTarget(self.p2)
		self.p2.SetDropTarget(targ2)

		filemenu = wx.Menu()
		fileorigchange = filemenu.Append(ID_OPEN1,"Change Original File")
		filemodichange = filemenu.Append(ID_OPEN2,"Change Modified File")
		fileexit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

		actionmenu = wx.Menu()
		actionclear = filemenu.Append(ID_BUTTON + 6, "Clear All")
		actionremone = filemenu.Append(ID_BUTTON + 7, "Remove One Duplicate")
		actionremall = filemenu.Append(ID_BUTTON + 8, "Remove All Duplicates")

		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&File")
		menuBar.Append(actionmenu, "&Actions")

		self.SetMenuBar(menuBar)

		self.Bind(wx.EVT_MENU, self.OnExit, fileexit)
		self.Bind(wx.EVT_MENU, self.p1.getNewFile, fileorigchange)
		self.Bind(wx.EVT_MENU, self.p2.getNewFile, filemodichange)

		self.Bind(wx.EVT_MENU, self.secClearAll, filemodichange)
		self.Bind(wx.EVT_MENU, self.secRemoveDuplicates, filemodichange)
		self.Bind(wx.EVT_MENU, self.secRemoveFirstDuplicate, filemodichange)


		self.barsizer = wx.BoxSizer(wx.HORIZONTAL)

		button1 = wx.Button(self, ID_BUTTON + 1, "1")
		button2 = wx.Button(self, ID_BUTTON + 2, "2")
		button3 = wx.Button(self, ID_BUTTON + 3, "3")
		button4 = wx.Button(self, ID_BUTTON + 4, "4")
		button5 = wx.Button(self, ID_BUTTON + 5, "5")
		button6 = wx.Button(self, ID_BUTTON + 6, "Clear")
		button7 = wx.Button(self, ID_BUTTON + 7, "One Duplicate")
		button8 = wx.Button(self, ID_BUTTON + 8, "All Duplicates")

		self.barsizer.Add(button1, 1, wx.EXPAND)
		self.barsizer.Add(button2, 1, wx.EXPAND)
		self.barsizer.Add(button3, 1, wx.EXPAND)
		self.barsizer.Add(button4, 1, wx.EXPAND)
		self.barsizer.Add(button5, 1, wx.EXPAND)
		self.barsizer.Add(button6, 1, wx.EXPAND)
		self.barsizer.Add(button7, 1, wx.EXPAND)
		self.barsizer.Add(button8, 1, wx.EXPAND)

		self.Bind(wx.EVT_BUTTON, self.secClearAll, button6)
		self.Bind(wx.EVT_BUTTON, self.secRemoveFirstDuplicate, button7)
		self.Bind(wx.EVT_BUTTON, self.secRemoveDuplicates, button8)

		self.sizer = wx.BoxSizer(wx.VERTICAL)

		self.panesizer = wx.BoxSizer(wx.HORIZONTAL)
		self.sizer.Add(self.barsizer,proportion=0,flag=wx.EXPAND)
		self.panesizer.Add(self.p1,proportion=1,flag=wx.EXPAND|wx.ALL)
		self.panesizer.Add(self.p2,proportion=1,flag=wx.EXPAND|wx.ALL)
		self.sizer.Add(self.panesizer,proportion=1,flag=wx.EXPAND)

		self.SetSizerAndFit(self.sizer)

		size = wx.DisplaySize()
		self.SetSize((800,600))

		self.statusbar = self.CreateStatusBar()
		self.statusbar.SetStatusText(os.getcwd())
		self.Center()
		self.Show(True)

	def OnExit(self,e):
		self.Close(True)

	def secClearAll(self, evt):
		self.p1.sec.ChangeValue("")
		self.p2.sec.ChangeValue("")

	def	secRemoveDuplicates(self, evt):
		sec1 = self.p1.sec.GetValue().splitlines()
		sec2 = self.p2.sec.GetValue().splitlines()

		for i in range(len(sec1)):
			for j in range(len(sec2)):
				if sec1[i] == sec2[j] and sec1[i] != "SETTOBEREMOVEDexa01%44":
					sec1[i] = "SETTOBEREMOVEDexa01%44"
					sec2[j] = "SETTOBEREMOVEDexa01%44"
					continue

		sec1 = removeAll( sec1, "SETTOBEREMOVEDexa01%44" )
		sec2 = removeAll( sec2, "SETTOBEREMOVEDexa01%44" )
		
		s1 = ""
		s2 = ""
		for line in sec1:
			s1 += line + "\n"
		for line in sec2:
			s2 += line + "\n"

		self.p1.sec.ChangeValue(s1)
		self.p2.sec.ChangeValue(s2)
	
	def secRemoveFirstDuplicate(self, evt):
		sec1 = self.p1.sec.GetValue().splitlines()
		sec2 = self.p2.sec.GetValue().splitlines()

		removed = 0
		for i in range(len(sec1)):
			for j in range(len(sec2)):
				if sec1[i] == sec2[j] and sec1[i] != "SETTOBEREMOVEDexa01%44":
					sec1[i] = "SETTOBEREMOVEDexa01%44"
					sec2[j] = "SETTOBEREMOVEDexa01%44"
					removed = 1
					break
			if removed == 1:
				break

		sec1 = removeAll( sec1, "SETTOBEREMOVEDexa01%44" )
		sec2 = removeAll( sec2, "SETTOBEREMOVEDexa01%44" )
		
		s1 = ""
		s2 = ""
		for line in sec1:
			s1 += line + "\n"
		for line in sec2:
			s2 += line + "\n"

		self.p1.sec.ChangeValue(s1)
		self.p2.sec.ChangeValue(s2)
			

app = wx.App(0)
PDFCompare(None, -1, 'Mismatched Text Compare')
app.MainLoop()