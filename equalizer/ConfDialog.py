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

from gi.repository import Gtk, Gio, Gdk, GdkPixbuf, Gst
import Conf

STOCK_IMAGE = "stock-equalizer-button"

class ConfDialog(object):
	def __init__(self, glade_file, conf, eq, plugin):
		self.plugin = plugin
		self.eq = eq
		self.conf = conf
		gladexml = Gtk.Builder()
		gladexml.add_from_file(glade_file)

		self.dialog = gladexml.get_object('preferences_dialog')
		self.dialog.connect("response", self.dialog_response)
		self.dialog.connect("destroy", self.on_destroy)
		self.dialog.connect("close", self.on_destroy)

		box = gladexml.get_object("presetchooser")
		self.box = box

		# workarounds
		# see https://bugzilla.gnome.org/show_bug.cgi?id=650369#c4
		self.box.set_entry_text_column(0)
		self.box.set_id_column(1)

		self.read_presets()
		box.connect("changed", self.preset_change)

		self.bands = []
		for i in range(0,10):
			self.bands.append(gladexml.get_object("b" + `i`))
			self.bands[i].connect("value_changed", self.slider_changed)
		self.update_bands()
		conf.apply_settings(eq)

	def cleanup(self):
		self.plugin.shell.props.ui_manager.remove_action_group(self.action_group)
		self.plugin.shell.props.ui_manager.remove_ui(self.ui)

	def on_destroy(self, dialog):
		dialog.hide()
		self.__init__(self.plugin.glade_f, self.conf, self.eq, self.plugin)
		return True

	def read_presets(self):
		box = self.box
		conf = self.conf
		if box:
			box.get_model().clear()

		current = conf.demangle(conf.preset)
		s_presets = sorted(Gst.Preset.get_preset_names(self.eq))
		i = 1
		box.append_text("default")
		box.set_active(0)
		for preset in s_presets:
			box.append_text(preset)
			if (preset == current):
				box.set_active(i)
			i += 1

	def update_bands(self):
		for i in range(0, 10):
			self.bands[i].set_value(self.conf.config[i])

	def get_dialog(self):
		return self.dialog

	def dialog_response(self, dialog, response):
		if (response == -4):
			self.conf.write_settings()
			dialog.hide()

		if (response == -6):
			self.conf.reset_all()
			self.box.set_active(0)

		if (response == -8 or response == -6):
			if self.box.get_active_text() == "default":
				self.conf.config = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
			else:
				Gst.Preset.load_preset(self.eq, self.box.get_active_text())
				self.conf.config = list(self.eq.get_property('band' + str(i)) for i in range(0,10))

			self.update_bands()

	def preset_change(self, entry):
		new_preset = entry.get_active_text()
		if new_preset != '':
			self.conf.change_preset(entry.get_active_text(), self.eq)
			self.update_bands()

	def slider_changed(self, hscale):
		eq = self.eq
		if eq == None:
			return
		i = self.bands.index(hscale)
		val = self.bands[i].get_value()
		self.conf.config[i] = val
		eq.set_property('band' + `i`, val)
		self.conf.write_settings()

	def add_ui(self, shell):
		plugin = self.plugin
		action = Gtk.Action ('Equalize',
				_('_Equalizer'),
				_('10 Band Equalizer'),
				STOCK_IMAGE)
		action.connect ('activate', self.show_ui, shell)
		self.action_group = Gtk.ActionGroup ('EqualizerActionGroup')
		self.action_group.add_action (action)
		shell.props.ui_manager.insert_action_group(self.action_group, -1)
		ui_manager = shell.props.ui_manager
		self.ui = ui_manager.add_ui_from_file(plugin.find_file("equalizer-ui.xml"))

	def show_ui(self, shell, state):
		self.read_presets()
		self.get_dialog().present()
