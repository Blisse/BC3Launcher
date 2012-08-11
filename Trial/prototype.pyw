#!/usr/bin/python

import sys
import wx
import os
import time
import wx.grid as gridlib
import subprocess
from time import sleep

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
ID_FANCY=042


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


class primPanel(wx.Panel):
	def __init__(self, parent, title):
		super(primPanel, self).__init__(parent, title)

		self.originalfile = ""

		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)

		self.url = wx.TextCtrl(self)
		self.newdir = wx.Button(self, label="File")
		self.newdir.Bind(wx.EVT_BUTTON, self.getNewFile)

		#self.prim = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.HSCROLL|wx.TE_READONLY|wx.TE_RICH2, size=(-1,300))
		self.prim = wx.ListCtrl(self, style=wx.LC_REPORT|wx.LC_NO_HEADER|wx.LC_HRULES, size=(-1,300))
		self.prim.Bind(wx.EVT_MENU, self.onPrimSELA, id=050)
		accel_prim = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('A'), 050)])
		self.prim.SetAcceleratorTable(accel_prim)
		self.prim.InsertColumn(0,"")

		self.sec = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.HSCROLL, size=(-1,200))
		self.sec.Bind(wx.EVT_MENU, self.onSecSELA, id=060)
		accel_sec = wx.AcceleratorTable([(wx.ACCEL_CTRL,ord('A'),060)])
		self.sec.SetAcceleratorTable(accel_sec)

		hbox.Add(self.url, 1, wx.RIGHT, border=5)
		hbox.Add(self.newdir, 0, flag=wx.RIGHT, border=5)
		
		vbox.Add(hbox, 0, flag=wx.TOP|wx.EXPAND, border=5)
		vbox.Add(self.prim, 1, flag=wx.TOP|wx.EXPAND, border=5)
		vbox.Add(self.sec, 0, flag=wx.TOP|wx.EXPAND, border=5)

		self.SetSizer(vbox)

	def SetValue(self, s):
		s = s.splitlines()
		for line in s:
			self.prim.InsertStringItem(0,line)
	
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
		filters = "Portable Document Format (*.pdf)|*.pdf|Text Files (*.txt)|*.txt|All supported files|*.txt;*.pdf"	
		dlg = wx.FileDialog( None, message="Choose a file", defaultFile="", wildcard=filters, style=wx.OPEN|wx.CHANGE_DIR)
		if dlg.ShowModal() == wx.ID_OK:
			self.modifiedfile = dlg.GetPath()
		dlg.Destroy()
		self.url.ChangeValue(self.modifiedfile)
		self.displayFile(self)

	def displayFile(self, evt):
		filetype = self.url.GetValue().split("\\")[-1].split(".")[-1].lower()
		if filetype == "txt":
			self.displayTextFile()
		elif filetype == "pdf":
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
		self.prim.ChangeValue(s)
	
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

		self.formatText()

	def formatText(self):
		s = ""
		temp = self.getText()
		for i in range( len(temp) ):
			if ( len( temp[i] ) == 0 ):
				s += "\n"
			else:
				s += temp[i].strip() + "\n" 
		temp = open( self.url.GetValue()[:-4] + ".txt" , 'w' )
		temp.write(s)

	def justifyText(self, max_len):	
		temp = self.getText()
		i = k = 0
		oneword = 1
		s = ""
		for line in temp:
			oneword = 1
			line_len = len(line)
			offset = max_len - line_len
			for i in range( line_len ):
				if line[i] == ' ':
					oneword = 0

			if offset == 0:
				s += line + "\n"
			else:
				if oneword != 0:
					s += line
					while offset != 0:
						s += " "
						offset -= 1
					s += '\n'
				else:
					n = 0
					while offset > 0:
						if k > (line_len-1):
							k = 0
						if line[k] == ' ':
							line = insertText(line, ' ', k)
							k += 1
							while line[k] == ' ':
								k += 1
							line_len += 1
							offset -= 1
						k += 1
					k = 0
					s += line + "\n"
		temp = open( self.url.GetValue()[:-4] + ".txt" , 'w' )
		temp.write(s)


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
		actioncrude = actionmenu.Append(ID_CRUDE,"Run &Crude Report")
		actionfancy = actionmenu.Append(ID_FANCY,"Run &Fancy Report")

		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&File")
		menuBar.Append(actionmenu, "&Actions")

		self.SetMenuBar(menuBar)

		self.Bind(wx.EVT_MENU, self.OnExit, fileexit)
		self.Bind(wx.EVT_MENU, self.p1.getNewFile, fileorigchange)
		self.Bind(wx.EVT_MENU, self.p2.getNewFile, filemodichange)
		self.Bind(wx.EVT_MENU, self.runCrudeReport, actioncrude )
		self.Bind(wx.EVT_MENU, self.runFancyReport, actionfancy )

		self.barsizer = wx.BoxSizer(wx.HORIZONTAL)

		button1 = wx.Button(self, ID_BUTTON + 1, "Crude Report")
		button2 = wx.Button(self, ID_BUTTON + 2, "Fancy Report")
		button3 = wx.Button(self, ID_BUTTON + 3, "3")
		button4 = wx.Button(self, ID_BUTTON + 4, "4")
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

		self.Bind(wx.EVT_BUTTON, self.runCrudeReport, button1)
		self.Bind(wx.EVT_BUTTON, self.runFancyReport, button2)
		self.Bind(wx.EVT_BUTTON, self.secRemoveDuplicates, button7)
		self.Bind(wx.EVT_BUTTON, self.secRemoveFirstDuplicate, button8)

		self.sizer = wx.BoxSizer(wx.VERTICAL)

		self.panesizer = wx.BoxSizer(wx.HORIZONTAL)
		self.panesizer.Add(self.p1,proportion=1,flag=wx.EXPAND|wx.ALL)
		self.panesizer.Add(self.p2,proportion=1,flag=wx.EXPAND|wx.ALL)
		self.sizer.Add(self.panesizer,proportion=1,flag=wx.EXPAND)
		self.sizer.Add(self.barsizer,proportion=0,flag=wx.EXPAND)

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
			
	def runCrudeReport(self, evt):
		try:
			file1 = open( self.p1.url.GetValue()[:-4] + ".txt" ).readlines()
		except:
			dlg = wx.MessageDialog(self, "Original File not loaded", "OK", wx.OK|wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return
		try:
			file2 = open( self.p2.url.GetValue()[:-4] + ".txt" ).readlines()
		except:
			dlg = wx.MessageDialog(self, "Modified File not loaded", "OK", wx.OK|wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return

		for i in range(len(file1)):
			for j in range(len(file2)):
				if file1[i] == file2[j] and file2[j] != "SETTOBEREMOVEDexa01%44":
					file1[i] = "SETTOBEREMOVEDexa01%44"
					file2[j] = "SETTOBEREMOVEDexa01%44"
					continue

		file1 = self.removeAll( file1, "SETTOBEREMOVEDexa01%44" )
		file2 = self.removeAll( file2, "SETTOBEREMOVEDexa01%44" )
		
		s1 = ""
		s2 = ""
		for line in file1:
			s1 += line + "\n"
		for line in file2:
			s2 += line + "\n"

		self.p1.prim.ChangeValue(s1)
		self.p2.prim.ChangeValue(s2)

	def runFancyReport(self, evt):

		self.p1.prim.Clear()
		self.p2.prim.Clear()
		try:
			file1 = open( self.p1.url.GetValue()[:-4] + ".txt" ).readlines()
		except:
			dlg = wx.MessageDialog(self, "Original File not loaded", "OK", wx.OK|wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return
		try:
			file2 = open( self.p2.url.GetValue()[:-4] + ".txt" ).readlines()
		except:
			dlg = wx.MessageDialog(self, "Modified File not loaded", "OK", wx.OK|wx.ICON_WARNING)
			dlg.ShowModal()
			dlg.Destroy()
			return
		
		f1 = f2 = []

		for line in file1:
			f1.append( ["-1","A",line] )
		for line in file2:
			f2.append( ["-1","A",line] )
		
		for i in range( len(f1) ):
			for j in range( len(f2) ):
				if f1[i][2] == f2[j][2]:
					f1[i][0] = j
					f2[j][0] = i
					if i == j:
						f1[i][1] = "S"
						f2[j][1] = "S"
					else:
						f1[i][1] = "M"
						f2[j][1] = "M"
					continue

		s = 0
		for line in f1:
			self.p1.prim.AppendText(line[2])
			if line[1] == "A":
				self.p1.prim.SetStyle(s,s+len(line[2]),wx.TextAttr("BLACK","RED"))
			elif line[1] == "S":
				self.p1.prim.SetStyle(s,s+len(line[2]),wx.TextAttr("BLACK","CYAN"))
			elif line[1] == "M":
				self.p1.prim.SetStyle(s,s+len(line[2]),wx.TextAttr("BLACK","WHITE"))
			s += len(line[2])

		s = 0
		for line in f2:
			self.p2.prim.AppendText(line[2])
			if line[1] == "A":
				self.p2.prim.SetStyle(s,s+len(line[2]),wx.TextAttr("BLACK","RED"))
			elif line[1] == "S":
				self.p2.prim.SetStyle(s,s+len(line[2]),wx.TextAttr("BLACK","CYAN"))
			elif line[1] == "M":
				self.p2.prim.SetStyle(s,s+len(line[2]),wx.TextAttr("BLACK","WHITE"))
			s += len(line[2])









app = wx.App(0)
PDFCompare(None, -1, 'File Hunter')
app.MainLoop()