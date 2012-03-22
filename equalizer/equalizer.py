# equalizer.py
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

from ConfDialog import ConfDialog
import Conf

import os

from gi.repository import GObject, Gst, Peas
from gi.repository import RB

class EqualizerPlugin(GObject.Object, Peas.Activatable):
	__gtype_name__ = 'EqualizerPlugin'
	object = GObject.property(type = GObject.Object)

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
		self.shell = self.object
		self.sp = self.shell.props.shell_player
		
		self.conf = Conf.Config()
		self.eq = Gst.ElementFactory.make('equalizer-10bands', None)
		self.conf.apply_settings(self.eq)
		
		self.glade_f = self.find_file("equalizer-prefs.ui")
		
		self.dialog = ConfDialog(self.glade_f, self.conf, self.eq, self)
		self.dialog.add_ui(self.shell)
				
		self.psc_id = self.sp.connect('playing-song-changed',
		                              self.playing_song_changed)

		if (self.sp.get_playing()):
			self.sp.stop()
			self.sp.props.player.add_filter(self.eq)
			self.sp.play()
		else:
			self.sp.props.player.add_filter(self.eq)

	def do_deactivate(self):
	
		self.sp.disconnect(self.psc_id)
		
		self.dialog.cleanup()
		
		try:
		
			if (self.sp.get_playing()):
				self.sp.stop()
				self.sp.props.player.remove_filter(self.eq)
				self.sp.play()
			else:
				self.sp.props.player.remove_filter(self.eq)
				
		except:
			pass
					
		del self.sp
		del self.glade_f
		del self.shell
		del self.conf
		del self.dialog
		del self.eq

	def playing_song_changed(self, sp, entry):
		if entry == None:
			return
			
		genre = entry.get_string(RB.RhythmDBPropType.GENRE)
		if self.conf.preset_exists(genre):
			self.conf.change_preset(genre, self.eq)
			
	def create_configure_dialog(self, dialog=None):
		dialog = self.dialog.get_dialog()
		dialog.present()
		return dialog

	def find_file(self, filename):
		info = self.plugin_info
		data_dir = info.get_data_dir()
		path = os.path.join(data_dir, filename)
		
		if os.path.exists(path):
			return path

		return RB.file(filename)
