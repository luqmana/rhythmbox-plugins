# __init__.py
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

import rb, rhythmdb
import gst
from ConfDialog import ConfDialog
import Conf

class EqualizerPlugin(rb.Plugin):

	def __init__(self):
		rb.Plugin.__init__(self)

	def activate(self, shell):	
		self.shell = shell
		self.conf = Conf.Config()
		eq = gst.element_factory_make("equalizer-10bands")
		self.eq = eq
		self.conf.apply_settings(eq)
		glade_f = self.find_file("equalizer-prefs.glade")
		dialog = ConfDialog(glade_f, self.conf, eq)
		dialog.add_ui(self, shell)
		self.dialog = dialog
		sp = shell.get_player()
		sp.connect ('playing-song-changed', self.playing_entry_changed)

		if(shell.props.shell_player.get_playing()):
			sp.stop()
			sp.props.player.add_filter(eq)
			sp.play()
		else:
			sp.props.player.add_filter(eq)

	def deactivate(self, shell):
		if(shell.props.shell_player.get_playing()):
			shell.props.shell_player.stop()
			shell.get_player().props.player.remove_filter(self.eq)
			shell.props.shell_player.play()
		else:
			shell.get_player().props.player.remove_filter(self.eq)
		del self.shell
		del self.conf
		del self.dialog
		del self.eq

	def playing_entry_changed (self, sp, entry):
		if entry == None:
			return
		genre = self.shell.props.db.entry_get(entry, rhythmdb.PROP_GENRE)
		if self.conf.preset_exists(genre):
			self.conf.change_preset(genre, self.eq)

	def create_configure_dialog(self, dialog=None):
		dialog = self.dialog.get_dialog()
		dialog.present()
		return dialog
