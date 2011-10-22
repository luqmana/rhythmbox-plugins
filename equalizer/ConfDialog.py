# ConfDialog.py
#
# Copyright (C) 2008 - Teemu Kallio <teemu.kallio@cs.helsinki.fi>
#				2009-2010 - Floreal Morandat <morandat AT lirmm DOT fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from gi.repository import Gtk, Gio
import Conf

STOCK_IMAGE = "stock-equalizer-button"

class ConfDialog(object):
	def __init__(self, glade_file, conf, eq):
		self.eq = eq
		self.conf = conf
		#gladexml = Gtk.glade.XML(glade_file)
		gladexml = Gtk.Builder()
		gladexml.add_from_file(glade_file)
	
		self.dialog = gladexml.get_widget('preferences_dialog')
		self.dialog.connect("response", self.dialog_response)

		box = gladexml.get_widget("presetchooser")
		self.box = box
		self.read_presets()
		#box.connect("changed", self.preset_change)
		box.child.connect("changed", self.preset_change)

		self.bands = []
		for i in range(0,10):
			self.bands.append(gladexml.get_widget("b" + `i`))
			self.bands[i].connect("value_changed", self.slider_changed)
		self.update_bands()
			#gc.set_float(path, default)
		conf.apply_settings(eq)

	def read_presets(self):
		box = self.box
		conf = self.conf
		box.get_model().clear()
		i = 0
		current = conf.demangle(conf.preset)
		for str in conf.list_preset():
			preset_entry = conf.demangle(str.rsplit('/',1)[1])
			box.append_text(preset_entry)
			if preset_entry == current:
				box.set_active(i)
			i += 1

	def update_bands(self):
		for i in range(0, 10):
			self.bands[i].set_value(self.conf.config[i])

	def get_dialog(self):
		return self.dialog

	def dialog_response(self, dialog, response):
		if(response == -6):
			for i in range(0, 10):
				self.conf.config[i] = 0.0
			self.update_bands()

		if(response == -4 or response == -7):
			self.conf.write_settings()
			dialog.hide()

	def preset_change(self, entry):
		new_preset = entry.get_text()
		if new_preset != '':
			self.conf.change_preset(entry.get_text(), self.eq)
			self.update_bands()

	def slider_changed(self, hscale):
		eq = self.eq
		if eq == None:
			return
		i = self.bands.index(hscale)
		val = self.bands[i].get_value()
		self.conf.config[i] = val
		eq.set_property('band' + `i`, val)
		
	def add_ui(self, plugin, shell):
		icon_factory = Gtk.IconFactory()
		icon_factory.add(STOCK_IMAGE, Gtk.IconSet(Gtk.gdk.pixbuf_new_from_file(plugin.find_file("equalizer.svg"))))
		icon_factory.add_default()

		action = Gtk.Action ('Equalize', 
				_('_Equalizer'), 
				_('10 Band Equalizer'),
				STOCK_IMAGE)
		action.connect ('activate', self.show_ui, shell)
		action_group = Gtk.ActionGroup ('EqualizerActionGroup')
		action_group.add_action (action)
		shell.get_ui_manager().insert_action_group (action_group, -1)
		ui_manager = shell.get_ui_manager()
		ui_manager.add_ui_from_file(plugin.find_file("equalizer-ui.xml"))

	def show_ui(self, shell, state):
		self.read_presets()
		self.get_dialog().present()
