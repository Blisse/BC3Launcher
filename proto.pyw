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

import re, htmlentitydefs

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


class MyFileDropTarget(wx.FileDropTarget):
	def __init__(self, panel):
		wx.FileDropTarget.__init__(self)
		self.panel = panel

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
		self.panel.prim.listctrl_link_all( os.path.abspath(filenames[0]) )

class file_directory( wx.ListCtrl, ListCtrlAutoWidthMixin):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT, size=(-1,300))
		ListCtrlAutoWidthMixin.__init__(self)

		self.listctrl_create()
		self.listctrl_bind()

		self.listctrl_link_all(".")

	def listctrl_create(self):	
		self.lines = 0
		self.files = []

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
			size = os.path.getsize(file)
			sec = os.path.getmtime(file)
			self.InsertStringItem(self.lines, name)
			self.SetStringItem(self.lines, 1, ex)
			self.SetStringItem(self.lines, 2, str(size) + ' B')
			self.SetStringItem(self.lines, 3, time.strftime('%Y-%m-%d %H:%M', time.localtime(sec)))
			if (self.lines % 2) == 0:
				self.SetItemBackgroundColour(self.lines, '#e6f1f5')
			self.add_line()
	def listctrl_clear(self):
		while ( self.get_line() > 0 ):
			self.DeleteItem(0)
			self.delete_line()

	def listctrl_link_all(self, path):
		self.listctrl_link_backend(os.path.abspath(path))
		self.listctrl_refresh()
	def listctrl_link_backend(self, path):
		self.set_url(path)
		self.set_cwd(path)

	def get_line(self):
		return self.lines
	def add_line(self):
		self.lines += 1
	def delete_line(self):
		self.lines -= 1

	def set_cwd(self, path):
		self.clear_cwd()
		for (dirpath, dirname, filename) in os.walk(self.get_url()):
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
		self.set_url( os.path.abspath( self.get_cwd_index( selected_index ) ) )


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
		self.sec = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(-1,300))
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
		fileexit = filemenu.Append(wx.ID_EXIT,"E&xit","Terminate the program")

		actionmenu = wx.Menu()
		actionlaunchbc3 = filemenu.Append(ID_BUTTON + 1, "&Launch BC3")
		actionloadfiles = filemenu.Append(ID_BUTTON + 2, "Load &Files")
		actionclear = filemenu.Append(ID_BUTTON + 6, "&Clear All")
		actionremone = filemenu.Append(ID_BUTTON + 7, "Remove &One Duplicate")
		actionremall = filemenu.Append(ID_BUTTON + 8, "Remove &All Duplicates")

		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&File")
		menuBar.Append(actionmenu, "&Actions")

		self.SetMenuBar(menuBar)

		self.Bind(wx.EVT_MENU, self.on_exit, fileexit)
		self.Bind(wx.EVT_MENU, self.p1.get_new_file, fileorigchange)
		self.Bind(wx.EVT_MENU, self.p2.get_new_file, filemodichange)

		self.Bind(wx.EVT_MENU, self.launch_BC3, actionlaunchbc3)
		self.Bind(wx.EVT_MENU, self.panels_sec_set_file, actionloadfiles)
		self.Bind(wx.EVT_MENU, self.panels_sec_clear, actionclear)
		self.Bind(wx.EVT_MENU, self.panels_sec_remove_one_duplicate, actionremone)
		self.Bind(wx.EVT_MENU, self.panels_sec_remove_all_duplicates, actionremall)

	def button_create(self):

		self.barsizer = wx.BoxSizer(wx.HORIZONTAL)

		button1 = wx.Button(self, ID_BUTTON + 1, "Launch BC3")
		button2 = wx.Button(self, ID_BUTTON + 2, "Load Files")
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

		self.Bind(wx.EVT_BUTTON, self.launch_BC3, button1)
		self.Bind(wx.EVT_BUTTON, self.panels_sec_set_file, button2)
		self.Bind(wx.EVT_BUTTON, self.panels_sec_clear, button6)
		self.Bind(wx.EVT_BUTTON, self.panels_sec_remove_one_duplicate, button7)
		self.Bind(wx.EVT_BUTTON, self.panels_sec_remove_all_duplicates, button8)


	def on_exit(self,evt):
		self.Close(True)

	def iter_remove_all(self, iter_object, to_remove):
		temp = []
		for item in iter_object:
			if item != to_remove:
				temp.append(item)
		return temp
	def iter_build_per_line(self, iter_object):
		temp = ""
		for item in iter_object:
			temp += item + "\n"
		return temp


	def launch_BC3(self, evt):
		commands = [bc3_path]
		commands.append(self.p1.get_url())
		commands.append(self.p2.get_url())
		subprocess.Popen(commands)

	def panels_sec_set_file(self, e):
		
		commands = [ptt_path]
		commands.append("-layout")
		commands.append("-nopgbrk")
		commands.append(self.p1.get_url())
		self.p1.set_sec( subprocess.Popen(commands, stdout=subprocess.PIPE).communicate()[0] )

		commands = [ptt_path]
		commands.append("-layout")
		commands.append("-nopgbrk")
		commands.append(self.p2.get_url())
		self.p2.set_sec( subprocess.Popen(commands, stdout=subprocess.PIPE).communicate()[0] )

		"""left_url = self.p1.get_url()
		left_type = left_url.split(".")[-1]
		right_url = self.p2.get_url()
		right_type = right_url.split(".")[-1]
		print right_type

		if left_type != "txt" or left_type != "pdf":
			wx.MessageBox('Invalid Left File Type', 'Error', wx.OK | wx.ICON_INFORMATION)
		if right_type != "txt" or right_type != "pdf":
			wx.MessageBox('Invalid Right File Type', 'Error', wx.OK | wx.ICON_INFORMATION)

		if left_type == "txt":
			left = open(left_url)
			self.p2.set_sec( iter_build_per_line(left) )
		elif left_type == "pdf":
			commands = [ptt_path]
			commands.append("-layout")
			commands.append("-nopgbrk")
			commands.append(left_url)
			self.p1.set_sec( subprocess.Popen(commands, stdout=PIPE).communicate()[0] )

		if right_type == "txt":
			right = open(right_url)
			self.p2.set_sec( iter_build_per_line(right) )
		elif right_type == "pdf":
			commands = [ptt_path]
			commands.append("-layout")
			commands.append("-nopgbrk")
			commands.append(right_url)
			self.p2.set_sec( subprocess.Popen(commands, stdout=PIPE).communicate()[0] )
		"""
	def panels_sec_clear(self, evt):
		self.p1.sec.ChangeValue("")
		self.p2.sec.ChangeValue("")

	def	panels_sec_remove_all_duplicates(self, evt):
		left = self.p1.get_sec().splitlines()
		right = self.p2.get_sec().splitlines()

		for i in range(len(left)):
			for j in range(len(right)):
				if left[i].split() == right[j].split() and left[i] != "SETTOBEREMOVEDexa01%44":
					left[i] = "SETTOBEREMOVEDexa01%44"
					right[j] = "SETTOBEREMOVEDexa01%44"
					break

		left = self.iter_remove_all(left, "SETTOBEREMOVEDexa01%44" )
		right = self.iter_remove_all(right, "SETTOBEREMOVEDexa01%44" )
		
		left = iter_build_per_line(left)
		right = iter_build_per_line(right)

		self.p1.set_sec(left)
		self.p2.set_sec(right)
	
	def panels_sec_remove_one_duplicate(self, evt):
		left = self.p1.get_sec().splitlines()
		right = self.p2.get_sec().splitlines()

		removed = 0
		for i in range(len(left)):
			for j in range(len(right)):
				if left[i].split() == right[j].split() and left[i] != "SETTOBEREMOVEDexa01%44":
					left[i] = "SETTOBEREMOVEDexa01%44"
					right[j] = "SETTOBEREMOVEDexa01%44"
					removed = 1
					break
			if removed == 1:
				break

		left = self.iter_remove_all(left, "SETTOBEREMOVEDexa01%44" )
		right = self.iter_remove_all(right, "SETTOBEREMOVEDexa01%44" )
		
		left = iter_build_per_line(left)
		right = iter_build_per_line(right)

		self.p1.set_sec(left)
		self.p2.set_sec(right)
			

app = wx.App(0)
PDFCompare(None, -1, 'BTC')
app.MainLoop()