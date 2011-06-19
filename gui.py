#!/usr/bin/python

import os
import os.path as osp
import math

import wx

import lib


class ImageBox(wx.Window):
	def __init__(self, parent, filename, name):
		wx.Window.__init__(self, parent, name=name)

		self.load_image(filename)
		#cursor = wx.StockCursor(wx.CURSOR_MAGNIFIER)
		#self.SetCursor(cursor)

		self.Bind(wx.EVT_SIZE, self.resize_space)
		self.Bind(wx.EVT_PAINT, self.on_paint)

	def on_paint(self, event):
		dc = wx.PaintDC(self)
		w, h = self.bitmap.GetSize()
		win_w, win_h = dc.GetSize()
		off_w = (win_w - w) / 2
		off_h = (win_h - h) / 2
		dc.DrawBitmap(self.bitmap, off_w, off_h, useMask=False)

	def resize_space(self, event):
		w, h = self.get_best_size()
		self.s_image = self.image.Scale(w, h)
		self.bitmap = wx.BitmapFromImage(self.s_image)
		self.Refresh()

	def load_image(self, filename):
		if not filename:
			self.image = wx.EmptyImage(200, 200)
		else:
			self.image = wx.Image(filename, wx.BITMAP_TYPE_JPEG)
		self.bitmap = wx.BitmapFromImage(self.image)

	def set_image(self, image):
		self.image = image
		self.resize_space(None)

	def get_best_size(self):
		win_w, win_h = self.GetSizeTuple()
		w, h = self.image.GetSize()
		ratio = w * 1.0 / h

		new_w = win_w
		new_h = win_w * 1.0 / ratio

		if new_h > win_h:
			new_h = win_h
			new_w = win_h * ratio

		return (new_w, new_h)



class MainWindow(wx.Frame):
	def __init__(self, parent=None, id=wx.ID_ANY, pos=wx.DefaultPosition):

		wx.Frame.__init__(self, parent, id, pos=pos, size=(700, 400))

		# Store the image import (working) directory
		self.filename = ''
		self.dirname = os.getcwd()

		# Update the title
		self.title = 'Wavedec'

		# Set up the menu
		self.setup_menu()

		# Main layout
		self.main_panel = wx.Panel(self, wx.ID_ANY)
		self.main_panel.SetBackgroundColour(wx.Colour(191,197,229))
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		self.main_panel.SetSizer(self.main_sizer)

		self.image_panel = wx.Panel(self.main_panel, wx.ID_ANY, style=wx.SIMPLE_BORDER)
		#self.image_panel.SetBackgroundColour(wx.Colour(255, 255, 0))
		self.image_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.image_panel.SetSizer(self.image_sizer)

		# Image boxes
		self.imgbox_orig = ImageBox(self.image_panel, None, 'img_orig')
		self.imgbox_work = ImageBox(self.image_panel, None, 'img_work')
		self.process_level = 0

		# Link the sizers
		self.image_sizer.Add(self.imgbox_orig, 1, wx.GROW | wx.ALIGN_LEFT | wx.ALL, 20)
		self.image_sizer.Add(self.imgbox_work, 1, wx.GROW | wx.ALIGN_RIGHT | wx.ALL, 20)
		self.main_sizer.Add(self.image_panel, 1, wx.GROW | wx.ALIGN_CENTER | wx.ALL, 25)

		# Create a StatusBar
		self.CreateStatusBar()

		self.status = 'No image loaded'
		self.CenterOnScreen()

	# Menu items and bindings
	def setup_menu(self):
		# File menu
		file_menu = wx.Menu()
		self.menu_open = file_menu.Append(wx.ID_OPEN, "&Open", "Open a file to edit")
		self.menu_next = file_menu.Append(wx.ID_FORWARD, "&Next Level\tSHIFT+RIGHT", "Next level of image decomposition")
		self.menu_prev = file_menu.Append(wx.ID_BACKWARD, "&Previous Level\tSHIFT+LEFT", "Previous level of image decomposition")
		self.menu_reset= file_menu.Append(wx.ID_REFRESH, "&Reset\tSPACE", "Reset to the original image")
		self.menu_save = file_menu.Append(wx.ID_SAVE, "&Save", "Save the file to disk")
		self.menu_exit = file_menu.Append(wx.ID_EXIT, "E&xit", "Terminate the program")

		# Wavelet menu
		self.wave_menu = wave_menu = wx.Menu()
		self.wavelet = 'haar'
		opt_haar = wave_menu.AppendRadioItem(-1, "haar")
		opt_db3  = wave_menu.AppendRadioItem(-1, "db3")
		opt_db5  = wave_menu.AppendRadioItem(-1, "db5")
		opt_bior22  = wave_menu.AppendRadioItem(-1, "bior 2.2")
		opt_bior44  = wave_menu.AppendRadioItem(-1, "bior 4.4")

		wave_menu.AppendSeparator()
		opt_haar2 = wave_menu.AppendRadioItem(-1, "haar *")
		opt_cdf97  = wave_menu.AppendRadioItem(-1, "cdf 9/7")

		# Help menu
		help_menu = wx.Menu()
		menu_about = help_menu.Append(wx.ID_ABOUT, "&About"," Information about this program")

		# Create the menubar
		menu_bar = wx.MenuBar()
		menu_bar.Append(file_menu, "&File")
		menu_bar.Append(wave_menu, "&Wavelet")
		menu_bar.Append(help_menu, "&Help")
		self.SetMenuBar(menu_bar)  # Adding the MenuBar to the Frame content

		# Events
		self.Bind(wx.EVT_MENU, self.on_open, self.menu_open)
		self.Bind(wx.EVT_MENU, self.on_next, self.menu_next)
		self.Bind(wx.EVT_MENU, self.on_prev, self.menu_prev)
		self.Bind(wx.EVT_MENU, self.on_reset, self.menu_reset)
		self.Bind(wx.EVT_MENU, self.on_save, self.menu_save)
		self.Bind(wx.EVT_MENU, self.on_exit, self.menu_exit)
		self.Bind(wx.EVT_MENU, self.on_about, menu_about)

		self.Bind(wx.EVT_MENU, self.option_builder('haar'), opt_haar)
		self.Bind(wx.EVT_MENU, self.option_builder('db3'), opt_db3)
		self.Bind(wx.EVT_MENU, self.option_builder('db5'), opt_db5)
		self.Bind(wx.EVT_MENU, self.option_builder('bior2.2'), opt_bior22)
		self.Bind(wx.EVT_MENU, self.option_builder('bior4.4'), opt_bior44)

		self.Bind(wx.EVT_MENU, self.option_builder('haar*'), opt_haar2)
		self.Bind(wx.EVT_MENU, self.option_builder('cdf9/7'), opt_cdf97)


	# Status property (and triggers)
	def get_status(self):
		return self._status

	def set_status(self, value):
		self._status = value

		# Update status bar contents
		suffix = ' - %s [%s level %s]' % (osp.join(self.dirname, self.filename),
				self.wavelet, self.process_level) if self.filename else ''
		self.SetStatusText('%s%s' % (value, suffix))

		# Update window title
		suffix = ' - %s' % self.filename if self.filename else ''
		self.SetTitle('%s%s' % (self.title, suffix))

		# Enable/disable menus
		self.check_state()

	status = property(get_status, set_status)


	def check_state(self):
		""" Enable or disable actions based on the current state """
		if not self.filename:
			for m in self.wave_menu.GetMenuItems():
				m.Enable(False)
			self.menu_reset.Enable(False)
			self.menu_save.Enable(False)
			self.menu_next.Enable(False)
			self.menu_prev.Enable(False)
		else:
			for m in self.wave_menu.GetMenuItems():
				m.Enable(True)
			self.menu_reset.Enable(True)
			self.menu_save.Enable(True)

			max_level = math.log(max(self.img_work.GetWidth(), self.img_work.GetHeight()), 2)
			self.menu_prev.Enable(self.process_level > 0)
			self.menu_next.Enable(self.process_level < max_level)


	@staticmethod
	def dialog_filters(data, add_all=True, add_wildcard=True):
		""" Create a wx.FileDialog compatible wildcard list """
		fmt_ext = lambda name, exts: '{0} ({1})|{1}'.format(name, ';'.join(exts))

		res, all = [], []
		for name, value in data.items():
			if type(value) is str:
				value = (value,)
			value = map(lambda ext: '*.%s' % ext, value)

			all.extend(value)
			res.append(fmt_ext(name, value))

		if add_all:
			if type(add_all) is not str:
				add_all = 'All special files'
			res = [fmt_ext(add_all, all)] + res

		if add_wildcard:
			res.append(fmt_ext('All files', ['*.*']))

		return '|'.join(res)

	def filters(self):
		return self.dialog_filters({
			'Bitmap files': 'bmp',
			'GIF files': 'gif',
			'JPEG files': ('jpg', 'jpeg', 'jpe'),
			'PNG files': 'png',
			}, add_all='All Image files')

	# Generic event handlers for the RadioItem menu (Wavelet selection)
	def option_builder(self, name):
		def on_opt_change(e):
			if self.wavelet != name:
				self.wavelet = name
				self.image_reset('Image reset successfully')
				if self.filename:
					self.image_process()
		return on_opt_change


	# Event handlers
	def on_open(self, e):
		""" Open action dialog """
		dlg = wx.FileDialog(self, message='Choose a file', defaultDir=self.dirname,
				defaultFile='', wildcard=self.filters(), style=wx.OPEN)

		if dlg.ShowModal() == wx.ID_OK:
			self.open_image(dlg.GetPath())
		dlg.Destroy()


	def on_prev(self, event):
		self.process_level -= 1
		self.image_process()


	def on_next(self, event):
		self.process_level += 1
		self.image_process()


	def on_reset(self, e):
		self.image_reset('Image reset successfully')

	def on_save(self, e):
		""" Save action dialog """
		dlg = wx.FileDialog(self, message="Choose a destination", defaultDir=self.dirname,
				wildcard=self.filters(), style=wx.SAVE | wx.OVERWRITE_PROMPT)

		# Show the dialog and get user input
		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			lib.save(self.img_work, path)
		dlg.Destroy()


	def on_exit(self, e):
		""" Exit action """
		self.Close(True)


	def on_about(self, e):
		""" About action """
		license = osp.join(osp.dirname(__file__), 'license.txt')

		info = wx.AboutDialogInfo()
		info.SetName('wavedec')
		info.SetVersion('0.1')
		info.SetLicense(open(license).read())
		info.SetWebSite('alex.cepoi@gmail.com')
		info.AddDeveloper('Alexandru Cepoi')
		wx.AboutBox(info)

	def open_image(self, path):
		# Save path data for the current image
		self.dirname, self.filename = osp.split(path)

		# Load the image original (auto-detect file type)
		self.img_orig = wx.Image(path, wx.BITMAP_TYPE_ANY, -1)
		self.img_orig = self.img_orig.ConvertToGreyscale()
		self.imgbox_orig.set_image(self.img_orig)

		# Reset the processing status
		self.image_reset('Image loaded successfully')


	def image_reset(self, message='Image reset'):
		self.img_work = self.img_orig.Copy()
		self.imgbox_work.set_image(self.img_work)
		self.process_level = 0

		# If successfully loaded, change status
		self.status = message


	def image_process(self):
		self.img_work = lib.transform(image=self.img_orig,
				level=self.process_level, wavelet=self.wavelet)
		self.imgbox_work.set_image(self.img_work)

		self.status = 'Image transformed successfully'


class Application(wx.App):
	def OnInit(self):
		main = MainWindow()
		main.Show()
		self.SetTopWindow(main)
		return True


app = Application(False, None)
app.MainLoop()
