#!/usr/bin/env python2
from gi.repository import Gtk, Gdk, GObject
from Xlib import X, display
import subprocess
import sys
import warnings
warnings.filterwarnings("ignore", message="(.*)was not found when attempting to remove it(.*)")

def system(cmd):
	return subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True).communicate()[0].rstrip()

def previousWorkspace():
	current = int(system("wmctrl -d | sed -n 's/^\([0-9]\+\) *\*.*/\\1/p'"))
	total = int(system("wmctrl -d | wc -l"))
	target = current-1
	if target == -1:
		target = -1 #total-1 for no bounds
	return target

def nextWorkspace():
	current = int(system("wmctrl -d | sed -n 's/^\([0-9]\+\) *\*.*/\\1/p'"))
	total = int(system("wmctrl -d | wc -l"))
	target = current+1
	if target == total:
		target = -1 #0 for no bounds
	return target

def getActiveWindows(n):
	return int(system("wmctrl -l | grep '  %d ultrabook' | wc -l" %(n)))

def gotoWorkspace(n):
	if n != -1:
		system("wmctrl -s %d" %(n))

class MyWindow(Gtk.Window):

    def __init__(self, instance, x, y):
	self.instance = instance
	self.x = x
	self.y = y
	self.goto = -1 #will be set by handler

        Gtk.Window.__init__(self, Gtk.WindowType.POPUP)

	self.set_keep_above(1)
	self.set_skip_taskbar_hint(1)
	self.set_decorated(0)
	self.modify_bg(Gtk.StateType.NORMAL, Gdk.Color.parse("black")[1])
        #self.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(1.0,1.0,1.0,0.0))

	self.eventbox = Gtk.EventBox()
	self.add(self.eventbox)

        self.label = Gtk.Label()
	self.label.set_margin_bottom(0) #was 5
        self.eventbox.add(self.label)
	self.updateLabel()

	self.show_all()
	self.updateSize()

    def updateSize(self):
	x_size, y_size = self.get_size()
	if self.instance == 1:
		self.move(self.x, self.y-y_size)
	elif self.instance == 2:
		self.move(self.x-x_size, self.y-y_size)

    def updateLabel(self):
	activeWindows = getActiveWindows(self.goto)
	if activeWindows == 0:
		self.label.set_markup("<span size='x-large'>  </span>")
	else:
		self.label.set_markup("<span color='white' size='x-large'><b>%d</b></span>" %(activeWindows))

class Handler(object):

    def __init__(self, win1, win2):
	self.win1 = win1
	self.win2 = win2
	win1.goto = previousWorkspace()
	win2.goto = nextWorkspace()
	win1.updateLabel()
	win2.updateLabel()
	win1.eventbox.connect("enter-notify-event", self.on_mouse_over, win1)
	win2.eventbox.connect("enter-notify-event", self.on_mouse_over, win2)
	win1.eventbox.connect("leave-notify-event", self.on_mouse_out, win1)
	win2.eventbox.connect("leave-notify-event", self.on_mouse_out, win2)

    def on_mouse_over(self, self2, self3, window):
	timeout = 300
	self._timeout_id = GObject.timeout_add(timeout, self.on_button_clicked, window)

    def on_mouse_out(self, self2, self3, window):
	GObject.source_remove(self._timeout_id)
	self._timeout_id = 0

    def on_button_clicked(self, window):
	gotoWorkspace(window.goto)
	win1.goto = previousWorkspace()
	win2.goto = nextWorkspace()
	win1.updateLabel()
	win2.updateLabel()
        win1.updateSize()
        win2.updateSize()

screen = Gdk.Screen.get_default()
win1 = MyWindow(1, -1, screen.get_height())
win2 = MyWindow(2, screen.get_width(), screen.get_height())
handler = Handler(win1, win2)

Gtk.main()

