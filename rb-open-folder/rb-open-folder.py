# -*- coding: utf8 -*-
#
# Copyright (C) 2007, 2008 Adolfo González Blázquez <code@infinicode.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA.

import rhythmdb, rb
import gobject, gtk
from subprocess import Popen

ui_str = """
<ui>
  <popup name="BrowserSourceViewPopup">
    <placeholder name="PluginPlaceholder">
      <menuitem name="OpenFolderPopup" action="OpenFolder"/>
    </placeholder>
  </popup>

  <popup name="PlaylistViewPopup">
    <placeholder name="PluginPlaceholder">
      <menuitem name="OpenFolderPopup" action="OpenFolder"/>
    </placeholder>
  </popup>

  <popup name="QueuePlaylistViewPopup">
    <placeholder name="PluginPlaceholder">
      <menuitem name="OpenFolderPopup" action="OpenFolder"/>
    </placeholder>
  </popup>

  <popup name="PodcastViewPopup">
    <placeholder name="PluginPlaceholder">
      <menuitem name="OpenFolderPopup" action="OpenFolder"/>
    </placeholder>
  </popup>
</ui>
"""

class OpenFolder(rb.Plugin):

	def __init__(self):
		rb.Plugin.__init__(self)
			
	def activate(self, shell):
		self.action = gtk.Action('OpenFolder', _('Open containing folder'),
					 _('Open the folder that contains the selected song'),
					 'rb-open-folder')
		self.activate_id = self.action.connect('activate', self.open_folder, shell)
		
		self.action_group = gtk.ActionGroup('OpenFolderPluginActions')
		self.action_group.add_action(self.action)
		
		uim = shell.get_ui_manager ()
		uim.insert_action_group(self.action_group, 0)
		self.ui_id = uim.add_ui_from_string(ui_str)
		uim.ensure_update()
	
	def open_folder(self, action, shell):
		source = shell.get_property("selected_source")
		entry = rb.Source.get_entry_view(source)
		selected = entry.get_selected_entries()
		if selected != []:
			uri = selected[0].get_playback_uri()
			dirpath = uri.rpartition('/')[0]
			if dirpath == "": dirpath = "/"
			Popen(["xdg-open", dirpath])
	
	def deactivate(self, shell):
		uim = shell.get_ui_manager()
		uim.remove_ui (self.ui_id)
		uim.remove_action_group (self.action_group)

		self.action_group = None
		self.action = None
