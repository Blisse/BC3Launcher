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

current_file = "proto.pyw"
bc3_path = "C:\Program Files (x86)\Beyond Compare 3\BComp.exe"
ptt_path = os.path.abspath("ptt.exe")

ID_BUTTON=100
ID_OPENL=001
ID_OPENR=002
ID_RDALL=021
ID_RDONE=022

ID_COPY=031
ID_CUT=032
ID_PASTE=033
ID_SELA=034

weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december", "janvier", "fevrier", "mars", "avril", "mai", "juin", "juillet", "aout", "septembre", "octobre", "novembre", "decembre"]
days = [ str(i) for i in range(1,32) ]

def remove_all(iter_object, to_remove):
	temp = []
	for item in iter_object:
		if item != to_remove:
			temp.append(item)
	return temp

class MyFileDropTarget(wx.FileDropTarget):
	def __init__(self, panel):
		wx.FileDropTarget.__init__(self)
		self.panel = panel

	def OnDropFiles(self, x, y, filenames):        
		self.panel.set_url( os.path.abspath(filenames[0]) )
		self.panel.prim.listctrl_link_all( self.panel.get_url() )

class file_directory( wx.ListCtrl, ListCtrlAutoWidthMixin):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT, size=(-1,200))
		ListCtrlAutoWidthMixin.__init__(self)
		self.SetFont( wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL ) )

		self.listctrl_create()
		self.listctrl_bind()

		self.listctrl_link_all(".")

	def listctrl_create(self):	
		self.lines = 0
		self.files = []
		self.dir = "\\".join(os.path.abspath(".").split("\\")[:-1])

		self.InsertColumn(0, 'Name')
		self.InsertColumn(1, 'Ext')
		self.InsertColumn(2, 'Size', wx.LIST_FORMAT_RIGHT)
		self.InsertColumn(3, 'Last Modified')
		self.SetColumnWidth(0, 200)
		self.SetColumnWidth(1, 70)
		self.SetColumnWidth(2, 100)
		self.SetColumnWidth(3, 100)
	def listctrl_bind(self):
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_double_click, self)

	def listctrl_refresh(self):
		self.listctrl_clear()
		self.InsertStringItem(self.get_line(), "..")
		self.add_line()
		for file in self.files:
			(name, ext) = os.path.splitext(file)
			ex = ext[1:]
			try:
				size = os.path.getsize(file)
			except:
				size = 0
			try:
				sec = os.path.getmtime(file)
			except:
				sec = 0
			self.InsertStringItem(self.lines, name)
			self.SetStringItem(self.lines, 1, ex)
			self.SetStringItem(self.lines, 2, str(size) + ' B')
			self.SetStringItem(self.lines, 3, ( "-" if sec == 0 else time.strftime('%Y-%m-%d %H:%M', time.localtime(sec) ) ) )
			if (self.lines % 2) == 0:
				self.SetItemBackgroundColour(self.lines, '#e6f1f5')
			self.add_line()
	def listctrl_clear(self):
		while ( self.get_line() > 0 ):
			self.DeleteItem(0)
			self.delete_line()

	def listctrl_link_all(self, path):
		self.listctrl_link_backend(path)
		self.listctrl_refresh()
	def listctrl_link_backend(self, path):
		self.set_url(path)
		self.set_cwd(path)

	def set_dir(self, path):
		self.dir = "\\".join(os.path.abspath(path).split("\\")[:-1])
		print self.dir
	def get_dir(self):
		return self.dir
	
	def get_line(self):
		return self.lines
	def add_line(self):
		self.lines += 1
	def delete_line(self):
		self.lines -= 1

	def set_cwd(self, path):
		self.clear_cwd()
		self.set_dir( path )
		if path == ".":
			for (dirpath, dirname, filename) in os.walk("."):
				self.files.extend(dirname)
				self.files.extend(filename)
				break
		else:
			for (dirpath, dirname, filename) in os.walk("\\".join(os.path.abspath(path).split("\\")[:-1])):
				self.files.extend(dirname)
				self.files.extend(filename)
				break
	def clear_cwd(self):
		self.files = []
	def get_cwd_index(self, index):
		return self.get_cwd()[index]
	def get_cwd(self):
		return self.files

	def get_url(self):
		return self.GetParent().url.GetValue()
	def set_url(self, path):
		self.GetParent().url.ChangeValue(path)

	def on_double_click(self, event):
		selected_index = self.GetFirstSelected()-1	
		if selected_index == -1:
			return
		self.set_url( self.get_dir() + "\\" + self.get_cwd_index( selected_index ) )


class file_panel(wx.Panel):
	def __init__(self, parent, title):
		super(file_panel, self).__init__(parent, title)

		vbox = wx.BoxSizer(wx.VERTICAL)
		hbox = wx.BoxSizer(wx.HORIZONTAL)

		self.panel_url_create()
		self.panel_newdir_create()
		
		hbox.Add(self.url, 1, wx.RIGHT, border=5)
		hbox.Add(self.newdir, 0, flag=wx.RIGHT, border=3)

		vbox.Add(hbox, 0, flag=wx.TOP|wx.EXPAND, border=5)

		self.panel_prim_create()
		self.panel_sec_create()
		self.panel_sec_bind()

		vbox.Add(self.prim, 1, flag=wx.TOP|wx.EXPAND, border=5)
		vbox.Add(self.sec, 0, flag=wx.TOP|wx.EXPAND, border=5)

		self.SetSizer(vbox)

	def panel_url_create(self):
		self.url = wx.TextCtrl(self)
		self.set_url(current_file)
	def panel_newdir_create(self):
		self.newdir = wx.Button(self, label="File")
		self.newdir.Bind(wx.EVT_BUTTON, self.get_new_file)

	def panel_prim_create(self):
		self.prim = file_directory(self)
	def panel_sec_create(self):
		self.sec = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.HSCROLL, size=(-1,400))
		self.sec.SetFont( wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL ) )
	def panel_sec_bind(self):
		self.sec.Bind(wx.EVT_MENU, self.select_sec_all_text, id=060)
		accel_sec = wx.AcceleratorTable([(wx.ACCEL_CTRL,ord('A'),060)])
		self.sec.SetAcceleratorTable(accel_sec)

	def get_url(self):
		return self.url.GetValue()
	def set_url(self, path):
		return self.url.ChangeValue(os.path.abspath(path))

	def select_sec_all_text(self, e):
		self.sec.SetFocus()
		self.sec.SetSelection(-1,-1)
	def get_sec(self):
		return self.sec.GetValue()
	def set_sec(self, value):
		self.sec.ChangeValue(value)

	def get_new_file(self, e):
		dlg = wx.FileDialog( None, message="Choose a file", defaultFile="", style=wx.FD_OPEN|wx.FD_CHANGE_DIR)
		if dlg.ShowModal() == wx.ID_OK:
			self.prim.listctrl_link_all(dlg.GetPath())
		dlg.Destroy()


class PDFCompare(wx.Frame):
	def __init__(self, parent, id, title):
		wx.Frame.__init__(self, None, id, title)

		self.p1 = file_panel(self, -1)
		targ1 = MyFileDropTarget(self.p1)
		self.p1.SetDropTarget(targ1)

		self.p2 = file_panel(self, -1)
		targ2 = MyFileDropTarget(self.p2)
		self.p2.SetDropTarget(targ2)

		self.menu_create()
		self.button_create()

		self.sizer = wx.BoxSizer(wx.VERTICAL)

		self.panesizer = wx.BoxSizer(wx.HORIZONTAL)
		self.sizer.Add(self.barsizer,proportion=0,flag=wx.EXPAND)
		self.panesizer.Add(self.p1,proportion=1,flag=wx.EXPAND|wx.ALL)
		self.panesizer.Add(self.p2,proportion=1,flag=wx.EXPAND|wx.ALL)
		self.sizer.Add(self.panesizer,proportion=1,flag=wx.EXPAND)

		self.SetSizerAndFit(self.sizer)

		size = wx.DisplaySize()
		self.SetSize((1280,800))

		self.statusbar = self.CreateStatusBar()
		self.statusbar.SetStatusText(os.getcwd())
		self.Center()
		self.Show(True)


	def menu_create(self):
		filemenu = wx.Menu()
		fileorigchange = filemenu.Append(ID_OPENL,"Change &Left File")
		filemodichange = filemenu.Append(ID_OPENR,"Change &Right File")
		filebc3path = filemenu.Append(ID_BUTTON - 1,"Set BC3 Path")
		filepttpath = filemenu.Append(ID_BUTTON - 2,"Set PTT Path")
		fileexit = filemenu.Append(wx.ID_EXIT,"E&xit","Terminate the program")

		actionmenu = wx.Menu()
		actionlaunchbc3 = actionmenu.Append(ID_BUTTON + 1, "&Launch BC3")
		actionloadfiles = actionmenu.Append(ID_BUTTON + 2, "Load &Files")
		actioninline = actionmenu.Append(ID_BUTTON + 3, "&Inline BC3")
		actionnewlines = actionmenu.Append(ID_BUTTON + 4, "Remove &Newlines")
		actiondate = actionmenu.Append(ID_BUTTON + 5, "Remove &Dates")
		actionclear = actionmenu.Append(ID_BUTTON + 6, "&Clear All")
		actionremone = actionmenu.Append(ID_BUTTON + 7, "Remove &One Duplicate")
		actionremall = actionmenu.Append(ID_BUTTON + 8, "Remove &All Duplicates")

		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&File")
		menuBar.Append(actionmenu, "&Actions")

		self.SetMenuBar(menuBar)

		self.Bind(wx.EVT_MENU, self.on_exit, fileexit)
		self.Bind(wx.EVT_MENU, self.set_bc3_path, filebc3path)
		self.Bind(wx.EVT_MENU, self.set_ptt_path, filepttpath)
		self.Bind(wx.EVT_MENU, self.p1.get_new_file, fileorigchange)
		self.Bind(wx.EVT_MENU, self.p2.get_new_file, filemodichange)

		self.Bind(wx.EVT_MENU, self.launch_BC3, actionlaunchbc3)
		self.Bind(wx.EVT_MENU, self.panels_sec_set_file, actionloadfiles)
		self.Bind(wx.EVT_MENU, self.panels_sec_launch_BC3, actioninline)
		self.Bind(wx.EVT_MENU, self.panels_sec_remove_newline, actionnewlines)
		self.Bind(wx.EVT_MENU, self.panels_sec_remove_dates, actiondate)
		self.Bind(wx.EVT_MENU, self.panels_sec_clear, actionclear)
		self.Bind(wx.EVT_MENU, self.panels_sec_remove_one_duplicate, actionremone)
		self.Bind(wx.EVT_MENU, self.panels_sec_remove_all_duplicates, actionremall)

	def button_create(self):

		self.barsizer = wx.BoxSizer(wx.HORIZONTAL)

		button1 = wx.Button(self, ID_BUTTON + 1, "Launch BC3")
		button2 = wx.Button(self, ID_BUTTON + 2, "Load Files")
		button3 = wx.Button(self, ID_BUTTON + 3, "In-line BC3")
		button4 = wx.Button(self, ID_BUTTON + 4, "Remove Newlines")
		button5 = wx.Button(self, ID_BUTTON + 5, "Remove Dates")
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

		self.Bind(wx.EVT_BUTTON, self.launch_BC3, button1)
		self.Bind(wx.EVT_BUTTON, self.panels_sec_set_file, button2)
		self.Bind(wx.EVT_BUTTON, self.panels_sec_launch_BC3, button3)
		self.Bind(wx.EVT_BUTTON, self.panels_sec_remove_newline, button4)
		self.Bind(wx.EVT_BUTTON, self.panels_sec_remove_dates, button5)
		self.Bind(wx.EVT_BUTTON, self.panels_sec_clear, button6)
		self.Bind(wx.EVT_BUTTON, self.panels_sec_remove_one_duplicate, button7)
		self.Bind(wx.EVT_BUTTON, self.panels_sec_remove_all_duplicates, button8)

	def set_bc3_path(self, e):
		dlg = wx.FileDialog( None, message="Choose select your BComp.exe file", defaultFile="", wildcard = "EXECUTABLES (*.exe)|*.exe", style=wx.FD_OPEN|wx.FD_CHANGE_DIR)
		if dlg.ShowModal() == wx.ID_OK:
			bc3_path = dlg.GetPath()
		dlg.Destroy()	

	def set_ptt_path(self, e):
		dlg = wx.FileDialog( None, message="Choose select your ptt.exe file", defaultFile="", wildcard = "EXECUTABLES (*.exe)|*.exe", style=wx.FD_OPEN|wx.FD_CHANGE_DIR)
		if dlg.ShowModal() == wx.ID_OK:
			ptt_path = dlg.GetPath()
		dlg.Destroy()

	def on_exit(self,evt):
		self.Close(True)

	def launch_BC3(self, evt):
		commands = [bc3_path]
		commands.append(self.p1.get_url())
		commands.append(self.p2.get_url())
		subprocess.Popen(commands, shell=False)

	def panels_sec_set_file(self, e):
		try:
			type = self.p1.get_url().split(".")[-1]
			if type == "pdf":
				commands = [ptt_path]
				commands.append("-layout")
				commands.append("-nopgbrk")
				commands.append(self.p1.get_url())
				commands.append("exa01left.txt")
				subprocess.call(commands)
				s = "".join( open("exa01left.txt").readlines() )
				self.p1.set_sec( s )
			else:
				s = "".join( open(self.p1.get_url()).readlines() )
				self.p1.set_sec( s )
		except:
			s = "".join( open(self.p1.get_url()).readlines() )
			self.p1.set_sec( s )

		try:
			type = self.p1.get_url().split(".")[-1]
			if type == "pdf":
				commands = [ptt_path]
				commands.append("-layout")
				commands.append("-nopgbrk")
				commands.append(self.p2.get_url())
				commands.append("exa01right.txt")
				subprocess.call(commands)
				s = "".join( open("exa01right.txt").readlines() )
				self.p2.set_sec( s )
			else:
				s = "".join( open(self.p2.get_url()).readlines() )
				self.p2.set_sec( s )
		except:
			s = "".join( open(self.p2.get_url()).readlines() )
			self.p2.set_sec( s )

	def panels_sec_clear(self, evt):
		self.p1.sec.ChangeValue("")
		self.p2.sec.ChangeValue("")

	def	panels_sec_remove_all_duplicates(self, evt):
		left = self.p1.get_sec().splitlines()
		right = self.p2.get_sec().splitlines()

		for i in range(len(left)):
			if left[i] == "xxcver213:nOne":
				continue
			for j in range(len(right)):
				if right[j] == "xxcver213:nOne":
					continue
				if left[i].split() == right[j].split():
					left[i] = "xxcver213:nOne"
					right[j] = "xxcver213:nOne"
					break

		left = remove_all(left, "xxcver213:nOne" )
		right = remove_all(right, "xxcver213:nOne" )

		self.p1.set_sec("\n".join(left))
		self.p2.set_sec("\n".join(right))

	def panels_sec_remove_one_duplicate(self, evt):
		left = self.p1.get_sec().splitlines()
		right = self.p2.get_sec().splitlines()

		removed = 0
		for i in range(len(left)):
			if left[i] == "xxcver213:nOne":
				continue
			for j in range(len(right)):
				if right[j] == "xxcver213:nOne":
					continue
				if left[i].split() == right[j].split():
					left[i] = "xxcver213:nOne"
					right[j] = "xxcver213:nOne"
					removed = 1
					break
			if removed == 1:
				break

		left = remove_all(left, "xxcver213:nOne" )
		right = remove_all(right, "xxcver213:nOne" )

		self.p1.set_sec("\n".join(left))
		self.p2.set_sec("\n".join(right))
	
	def panels_sec_remove_dates(self, e):
		
		left = self.p1.get_sec().splitlines()
		right = self.p2.get_sec().splitlines()

		for line in range(len(left)):		
			try: 
				weekday = left[line].split()[0].rstrip(",").lower()
				if weekday in weekdays:
					month = left[line].split()[1].lower()
					if month in months:
						day = left[line].split()[2].rstrip(",")
						if day in days:
							left[line] = "xxcver213:nOne"
			except: 
				pass

		for line in range(len(right)):	
			try:
				weekday = right[line].split()[0].rstrip(",").lower()
				if weekday in weekdays:
					month = right[line].split()[1].lower()
					if month in months:
						day = right[line].split()[2].rstrip(",")
						if day in days:
							right[line] = "xxcver213:nOne"
			except:
				pass

		left = remove_all(left, "xxcver213:nOne" )
		right = remove_all(right, "xxcver213:nOne" )

		self.p1.set_sec("\n".join(left))
		self.p2.set_sec("\n".join(right))

	def panels_sec_remove_newline(self, e):

		left = self.p1.get_sec().splitlines()
		right = self.p2.get_sec().splitlines()

		new_left = []
		new_right = []

		for line in left:
			if not line.strip():
				continue
			else:
				new_left.append(line)
				
		for line in right:
			if not line.strip():
				continue
			else:
				new_right.append(line)

		self.p1.set_sec("\n".join(new_left))
		self.p2.set_sec("\n".join(new_right))

	def panels_sec_launch_BC3(self, e):

		left = "\n".join( self.p1.get_sec().splitlines() ).encode('utf-8')
		right = "\n".join( self.p2.get_sec().splitlines() ).encode('utf-8')

		lfile = "newlfile.txt"
		rfile = "newrfile.txt"

		l = open(lfile, "w")
		r = open(rfile, "w")

		l.write(left)
		r.write(right)

		commands = [bc3_path]
		commands.append(lfile)
		commands.append(rfile)
		subprocess.Popen(commands, shell=False)

app = wx.App(0)
PDFCompare(None, -1, 'BTC')
app.MainLoop()