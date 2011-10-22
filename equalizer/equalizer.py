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

import gst
from ConfDialog import ConfDialog
import Conf

from gi.repository import GObject, Peas
from gi.repository import RB

class EqualizerPlugin(GObject.Object, Peas.Activatable):
	__gtype_name__ = 'EqualizerPlugin'
	object = GObject.property(type = GObject.Object)

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
		self.shell = self.object
		self.conf = Conf.Config()
		#eq = gst.element_factory_make("equalizer-10bands")
		#self.eq = eq
		#self.conf.apply_settings(eq)
		#glade_f = rb.Plugin.find_file("equalizer-prefs.glade")
		#dialog = ConfDialog(glade_f, self.conf, eq)
		#dialog.add_ui(self, self.shell)
		#self.dialog = dialog
		
		sp = self.shell.props.shell_player
		self.psc_id = sp.connect('playing-song-changed', self.playing_song_changed)

		#if (sp.get_playing()):
			#sp.stop()
			#sp.props.player.add_filter(eq)
			#sp.play()
		#else:
			#sp.props.player.add_filter(eq)

	def do_deactivate(self):
	
		sp = self.shell.props.shell_player
		sp.disconnect(self.psc_id)
			
		#if (sp.get_playing()):
			#sp.stop()
			#sp.props.player.remove_filter(self.eq)
			#sp.play()
		#else:
			#sp.props.player.remove_filter(self.eq)
		
		del self.shell
		del self.conf
		del self.dialog
		#del self.eq

	def playing_song_changed(self, sp, entry):
		if entry == None:
			return
			
		genre = entry.get_string(RB.RhythmDBPropType.GENRE)
		#if self.conf.preset_exists(genre):
		#	self.conf.change_preset(genre, self.eq)

	#def create_configure_dialog(self, dialog=None):
		#dialog = self.dialog.get_dialog()
		#dialog.present()
		#return dialog
