#!/usr/bin/python

import sys
import wx
import os
import time
import wx.grid as gridlib
import subprocess
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
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

path = "C:\Program Files (x86)\Beyond Compare 3\BComp.exe"

ID_BUTTON=100
ID_OPEN1=001
ID_OPEN2=002
ID_RDALL=021
ID_RDONE=022

ID_COPY=031
ID_CUT=032
ID_PASTE=033
ID_SELA=034

ID_CRUDE=041
ID_INPL=042
ID_BCTEXT=043
ID_BCREP=044

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

class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT|wx.LC_NO_HEADER, size=(-1,300))
        ListCtrlAutoWidthMixin.__init__(self)

class primPanel(wx.Panel):
	def __init__(self, parent, title):
		super(primPanel, self).__init__(parent, title)

		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)

		self.url = wx.TextCtrl(self)
		self.newdir = wx.Button(self, label="File")
		self.newdir.Bind(wx.EVT_BUTTON, self.getNewFile)

		self.prim = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.HSCROLL|wx.TE_READONLY, size=(-1,300))
		self.prim.Bind(wx.EVT_MENU, self.onPrimSELA, id=050)
		accel_prim = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('A'), 050)])
		self.prim.SetAcceleratorTable(accel_prim)

		self.sec = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(-1,150))
		self.sec.Bind(wx.EVT_MENU, self.onSecSELA, id=060)
		accel_sec = wx.AcceleratorTable([(wx.ACCEL_CTRL,ord('A'),060)])
		self.sec.SetAcceleratorTable(accel_sec)

		hbox.Add(self.url, 1, wx.RIGHT, border=5)
		hbox.Add(self.newdir, 0, flag=wx.RIGHT, border=5)
		
		vbox.Add(hbox, 0, flag=wx.TOP|wx.EXPAND, border=5)
		vbox.Add(self.prim, 1, flag=wx.TOP|wx.EXPAND, border=5)
		vbox.Add(self.sec, 0, flag=wx.TOP|wx.EXPAND, border=5)

		self.SetSizer(vbox)

	def primChangeValue(self, s):
		self.prim.ChangeValue(s)
	
	def onPrimSELA(self, evt):
		self.prim.SetFocus()
		self.prim.SetSelection(-1,-1)

	def onSecSELA(self, evt):
		self.sec.SetFocus()
		self.sec.SetSelection(-1,-1)

	def selectAllPrimText(self, evt):
		self.prim.SetFocus()
		self.prim.SetSelection(-1,-1)

	def selectAllSecText(self, evt):
		self.sec.SetFocus()
		self.sec.SetSelection(-1,-1)
	
	def getNewFile(self, evt):
		filters = "Portable Document Format (*.pdf)|*.pdf|All supported files|*.txt;*.pdf"	
		dlg = wx.FileDialog( None, message="Choose a file", defaultFile="", wildcard=filters, style=wx.OPEN|wx.CHANGE_DIR)
		if dlg.ShowModal() == wx.ID_OK:
			self.modifiedfile = dlg.GetPath()
		dlg.Destroy()
		self.url.ChangeValue(self.modifiedfile)
		self.displayFile(self)

	def displayFile(self, evt):
		filetype = self.url.GetValue().split("\\")[-1].split(".")[-1].lower()
		if filetype == "pdf":
			self.callPTTF()
			self.displayTextFile()
		else:
			dlg = wx.MessageDialog(parent, "Invalid file type", "OK", wx.OK|wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()

	def displayTextFile(self):
		file = self.getText()
		s = ""
		for line in file:
			s += line
		self.primChangeValue(s)

	def callPTTF(self):
		pdf = self.url.GetValue()
		newCall = []
		newCall.append( "pttf" )
		newCall.append( "-layout" )
		newCall.append( "-nopgbrk" )
		newCall.append( pdf )
		newCall.append( pdf[:-4] + ".txt" )
		subprocess.call( newCall )
		
		while ( os.path.exists( pdf[:-4] + ".txt" ) == False ):
			sleep(1)

	def getText(self):
		return open( self.url.GetValue()[:-4] + ".txt" ).readlines()

	
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
		actioncrude = actionmenu.Append(ID_CRUDE,"Run &Simple Report")
		actioninplace = actionmenu.Append(ID_INPL,"Run &Simple Report")
		actionbctext = actionmenu.Append(ID_BCTEXT,"Run &BC Text")
		actionbcrep = actionmenu.Append(ID_BCREP,"Run BC &Report")

		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&File")
		menuBar.Append(actionmenu, "&Actions")

		self.SetMenuBar(menuBar)

		self.Bind(wx.EVT_MENU, self.OnExit, fileexit)
		self.Bind(wx.EVT_MENU, self.p1.getNewFile, fileorigchange)
		self.Bind(wx.EVT_MENU, self.p2.getNewFile, filemodichange)
		self.Bind(wx.EVT_MENU, self.runSimpleReport, actioncrude )
		self.Bind(wx.EVT_MENU, self.runInPlaceReport, actioninplace )
		self.Bind(wx.EVT_MENU, self.runBCText, actionbctext )
		self.Bind(wx.EVT_MENU, self.runBCReport, actionbcrep )

		self.barsizer = wx.BoxSizer(wx.HORIZONTAL)

		button1 = wx.Button(self, ID_CRUDE, "Simple Report")
		button2 = wx.Button(self, ID_INPL, "In Place Report")
		button3 = wx.Button(self, ID_BCTEXT, "BC Text")
		button4 = wx.Button(self, ID_BCREP, "BC Report")
		button5 = wx.Button(self, ID_BUTTON + 5, "5")
		button6 = wx.Button(self, ID_BUTTON + 6, "6")

		button7 = wx.Button(self, ID_RDALL, "All Duplicates")
		button8 = wx.Button(self, ID_RDONE, "One Duplicate")

		self.barsizer.Add(button1, 1, wx.EXPAND)
		self.barsizer.Add(button2, 1, wx.EXPAND)
		self.barsizer.Add(button3, 1, wx.EXPAND)
		self.barsizer.Add(button4, 1, wx.EXPAND)
		self.barsizer.Add(button5, 1, wx.EXPAND)
		self.barsizer.Add(button6, 1, wx.EXPAND)

		self.barsizer.Add(button7, 1, wx.EXPAND)
		self.barsizer.Add(button8, 1, wx.EXPAND)

		self.Bind(wx.EVT_BUTTON, self.runSimpleReport, button1)
		self.Bind(wx.EVT_BUTTON, self.runInPlaceReport, button2)
		self.Bind(wx.EVT_BUTTON, self.runBCText, button3)
		self.Bind(wx.EVT_BUTTON, self.runBCReport, button4)

		self.Bind(wx.EVT_BUTTON, self.secRemoveDuplicates, button7)
		self.Bind(wx.EVT_BUTTON, self.secRemoveFirstDuplicate, button8)

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

	def compareFiles(self, evt):
		s1 = self.p1.prim.GetValue().splitlines()
		s2 = self.p2.prim.GetValue().splitlines()

	def removeAll(self, obj, item):
		r = []
		for i in obj:
			if i !=  item:
				r.append(i)
		return r

	def	secRemoveDuplicates(self, evt):
		sec1 = self.p1.sec.GetValue().splitlines()
		sec2 = self.p2.sec.GetValue().splitlines()

		for i in range(len(sec1)):
			for j in range(len(sec2)):
				if sec1[i] == sec2[j] and sec1[i] != "SETTOBEREMOVEDexa01%44":
					sec1[i] = "SETTOBEREMOVEDexa01%44"
					sec2[j] = "SETTOBEREMOVEDexa01%44"
					continue

		sec1 = self.removeAll( sec1, "SETTOBEREMOVEDexa01%44" )
		sec2 = self.removeAll( sec2, "SETTOBEREMOVEDexa01%44" )
		
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

		sec1 = self.removeAll( sec1, "SETTOBEREMOVEDexa01%44" )
		sec2 = self.removeAll( sec2, "SETTOBEREMOVEDexa01%44" )
		
		s1 = ""
		s2 = ""
		for line in sec1:
			s1 += line + "\n"
		for line in sec2:
			s2 += line + "\n"

		self.p1.sec.ChangeValue(s1)
		self.p2.sec.ChangeValue(s2)

	def maxLineLength(self):
		maxLength = 0
		checkfile1 = open( self.p1.url.GetValue()[:-4] + ".txt" ).readlines()
		checkfile2 = open( self.p2.url.GetValue()[:-4] + ".txt" ).readlines()
		for line in checkfile1:
			x = len( line )
			if ( maxLength < x ):
				maxLength = x
		for line in checkfile2:
			x = len( line )
			if ( maxLength < x ):
				maxLength = x
		return maxLength
			
	def runSimpleReport(self, evt):
		try:
			file1 = open( self.p1.url.GetValue()[:-4] + ".txt" ).readlines()
			self.p1.displayTextFile()
		except:
			dlg = wx.MessageDialog(self, "Original File not loaded", "OK", wx.OK|wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return
		try:
			file2 = open( self.p2.url.GetValue()[:-4] + ".txt" ).readlines()
			self.p1.displayTextFile()
		except:
			dlg = wx.MessageDialog(self, "Modified File not loaded", "OK", wx.OK|wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return

		for i in range(len(file1)):
			for j in range(len(file2)):
				if file2[j] != "SETTOBEREMOVEDexa01%44" and file1[i].split() == file2[j].split():
					file1[i] = "SETTOBEREMOVEDexa01%44"
					file2[j] = "SETTOBEREMOVEDexa01%44"
					continue

		file1 = self.removeAll( file1, "SETTOBEREMOVEDexa01%44" )
		file2 = self.removeAll( file2, "SETTOBEREMOVEDexa01%44" )
		
		s1 = ""
		s2 = ""
		for line in file1:
			s1 += line 
		for line in file2:
			s2 += line 
		
		self.p1.primChangeValue(s1)
		self.p2.primChangeValue(s2)

	def runInPlaceReport(self, evt):

		file1 = self.p1.prim.GetValue().splitlines()
		file2 = self.p1.prim.GetValue().splitlines()

		for i in range(len(file1)):
			for j in range(len(file2)):
				if file1[i].split() == file2[j].split() and file2[j] != "SETTOBEREMOVEDexa01%44":
					file1[i] = "SETTOBEREMOVEDexa01%44"
					file2[j] = "SETTOBEREMOVEDexa01%44"
					continue

		file1 = self.removeAll( file1, "SETTOBEREMOVEDexa01%44" )
		file2 = self.removeAll( file2, "SETTOBEREMOVEDexa01%44" )
		
		s1 = ""
		s2 = ""
		for line in file1:
			s1 += line 
		for line in file2:
			s2 += line 
		
		self.p1.primChangeValue(s1)
		self.p2.primChangeValue(s2)


	def runBCText(self, evt):
		pass

	def runBCReport(self, evt):
		pass


app = wx.App(0)
PDFCompare(None, -1, 'PDF Compare')
app.MainLoop()