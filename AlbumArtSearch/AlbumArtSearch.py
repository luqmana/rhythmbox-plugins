import rb, re, os, urllib2, glib, unicodedata
from gi.repository import GObject, Gtk, Pango, Peas, RB, WebKit
from mako.template import Template

albumart_search_ui = """
<ui>
    <toolbar name="ToolBar">
        <toolitem name="AlbumArtSearch" action="ToggleAlbumArtSearch" />
    </toolbar>
</ui>
"""

class AlbumArtSearchPlugin(GObject.Object, Peas.Activatable):
	__gtype_name__ = 'AlbumArtSearchPlugin'
	object = GObject.property(type = GObject.Object)
	
	MODE_PICTURES  = 1
	MODE_RHYTHM = 2
        MODE_FOLDER = 3

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
	
		self.shell = self.object
		self.sp = self.shell.props.shell_player
		self.db = self.shell.get_property('db')

		self.file = ""
		self.basepath = 'file://' + os.path.split(rb.find_plugin_file(self, "AlbumArtSearch.py"))[0]
		self.load_templates()

		self.current_artist = None
		self.current_album = None
		self.current_song = None
		self.current_location = None
		self.visible = False
		
		self.mode = self.MODE_FOLDER

		self.init_gui()
		self.connect_signals()

		self.action = ('ToggleAlbumArtSearch', Gtk.STOCK_DND_MULTIPLE, _('Album Art'),
						None, _('Change the visibility of album art search pane'),
						self.toggle_visibility, False)
		self.action_group = Gtk.ActionGroup('AlbumArtSearchActions')
		self.action_group.add_toggle_actions([self.action])
		uim = self.shell.props.ui_manager
		uim.insert_action_group (self.action_group, -1)
		self.ui_id = uim.add_ui_from_string(albumart_search_ui)
		uim.ensure_update()
		
	def do_deactivate(self):
	
		self.sp.disconnect(self.player_cb_ids[0])
		self.sp.disconnect(self.player_cb_ids[1])
		
		self.shell.remove_widget (self.vbox, RB.ShellUILocation.RIGHT_SIDEBAR)

		self.shell.props.ui_manager.remove_action_group(self.action_group)
		self.shell.props.ui_manager.remove_ui(self.ui_id)
		
		del self.ui_id
		del self.action_group
		del self.sp
		del self.db
		del self.shell

	def connect_signals(self) :
		self.player_cb_ids = ( self.sp.connect ('playing-changed', self.playing_changed_cb), self.sp.connect ('playing-song-changed', self.playing_changed_cb))
		self.albumartbutton.connect('clicked', self.set_album_art)

	def playing_changed_cb (self, playing, user_data) :
		playing_entry = None
		if self.sp:
			playing_entry = self.sp.get_playing_entry ()
		if playing_entry is None :
			return

		playing_artist = playing_entry.get_string(RB.RhythmDBPropType.ARTIST)
		playing_album = playing_entry.get_string(RB.RhythmDBPropType.ALBUM)
		playing_title = playing_entry.get_string(RB.RhythmDBPropType.TITLE)
		playing_location = playing_entry.get_string(RB.RhythmDBPropType.LOCATION)
        	self.current_location = playing_location 

		if playing_album.upper() == "UNKNOWN":
			self.current_album = ""
		if playing_artist.upper() == "UNKNOWN":
			self.current_artist = ""
		if not(self.current_album == "" and self.current_artist == ""):
			self.current_artist = playing_artist.replace ('&', '&amp;')
			self.current_album = playing_album.replace ('&', '&amp;')
			self.current_title = playing_title.replace ('&', '&amp;')
			self.render_album_art_search(self.current_artist, self.current_album, self.current_title)

	def set_album_art(self, button) :
		tburl = self.webview.get_main_frame().get_title()
                
		if not tburl:
			return
		print "Url: " + tburl
		filep = tburl.split('/')
		filepath = filep[len(filep)-1]
		(filen, filextn) = os.path.splitext(filepath)
		request = urllib2.Request(tburl)
		opener = urllib2.build_opener()
		image = None
		try:
			image = opener.open(request).read()
		except:
			print "Failed to download image"
		
		save_filename=self.current_artist + " - " + self.current_album + ".jpg"

                if(self.mode == self.MODE_PICTURES):
			covers_folder = glib.get_user_special_dir(glib.USER_DIRECTORY_PICTURES)
			filename = covers_folder + "/" + save_filename

		if(self.mode == self.MODE_RHYTHM):
                        covers_folder=os.environ['HOME']+"/.cache/rhythmbox/covers/"
			filename = covers_folder + save_filename
                        if (os.path.isdir(covers_folder) == False):
                           os.mkdir(covers_folder)

                if(self.mode == self.MODE_FOLDER):
			location_path_improper = urllib2.url2pathname(self.current_location)
			location_path_arr = location_path_improper.split("//")
			location_path = location_path_arr[1]
			filename = location_path.rsplit("/",1)[0] + "/cover" #+ save_filename

		output = open(filename, 'w')
		output.write(image)
		output.close()

	def render_album_art_search(self, artistname, albumname, currenttitle):
                stripartistname=unicodedata.normalize('NFKD', unicode(artistname, errors='replace')).encode('ascii','ignore')
		stripalbumname=unicodedata.normalize('NFKD', unicode(albumname, errors='replace')).encode('ascii','ignore')
		stripcurrenttitle=unicodedata.normalize('NFKD', unicode(currenttitle, errors='replace')).encode('ascii','ignore')
		self.file = self.template.render (artist = stripartistname, album = stripalbumname, title = stripcurrenttitle, stylesheet = self.styles )
		self.webview.load_string (self.file, 'text/html', 'utf-8', self.basepath)

	def toggle_visibility (self, action) :
		if not self.visible:
			self.shell.add_widget (self.vbox, RB.ShellUILocation.RIGHT_SIDEBAR, expand=True, fill=True)#, padding=4)
			self.visible = True
		else:
			self.shell.remove_widget (self.vbox, RB.ShellUILocation.RIGHT_SIDEBAR)
			self.visible = False

	def load_templates(self):
		self.path = rb.find_plugin_file(self, 'tmpl/albumartsearch-tmpl.html')
		self.template = Template (filename = self.path, module_directory = '/tmp/')
		self.styles = self.basepath + '/tmpl/main.css'
		
	def toggled_rhythm_radio(self, extra):
		if(self.rhythmlocradio.get_active()):
	    		self.mode = self.MODE_RHYTHM

    	def toggled_folder_radio(self, extra):
    		if(self.folderlocradio.get_active()):
	    		self.mode = self.MODE_FOLDER 

    	def toggled_pictures_radio(self, extra):
    		if(self.pictureslocradio.get_active()):
	    		self.mode = self.MODE_PICTURES

	def init_gui(self) :
		self.vbox = Gtk.VBox()

		#---- set up webkit pane -----#
		self.webview = WebKit.WebView()
		self.scroll = Gtk.ScrolledWindow()
		self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
		self.scroll.set_shadow_type(Gtk.ShadowType.IN)
		self.scroll.add( self.webview )
		self.albumartbutton = Gtk.Button (_("Save Album Art"))

		self.selectlabel = Gtk.Label()
		self.selectlabel.set_markup("<u>Choose save location</u>")
     
		self.rhythmlocradio = Gtk.RadioButton.new_with_label_from_widget(None, "Rhythmbox Location")
		self.folderlocradio = Gtk.RadioButton.new_from_widget(self.rhythmlocradio)
                self.folderlocradio.set_label("Song Folder")
		self.pictureslocradio = Gtk.RadioButton.new_from_widget(self.folderlocradio)
                self.pictureslocradio.set_label("Pictures Folder")

		self.folderlocradio.set_active(True)
	
		self.rhythmlocradio.connect("toggled", self.toggled_rhythm_radio)
		self.folderlocradio.connect("toggled", self.toggled_folder_radio)
		self.pictureslocradio.connect("toggled", self.toggled_pictures_radio)

		self.hboxlabel = Gtk.HBox();
		
		self.vbox.pack_start(self.scroll, expand = True, fill = True, padding = 0)
		self.vbox.pack_start(self.scroll, expand = True, fill = True, padding = 0)
		self.vbox.pack_start(self.hboxlabel, expand = False, fill = True, padding = 0)
		self.hboxlabel.pack_start(self.selectlabel, expand = False, fill = True, padding = 0)
        	self.vbox.pack_start(self.rhythmlocradio, expand = False, fill = True, padding = 0)
        	self.vbox.pack_start(self.folderlocradio, expand = False, fill = True, padding = 0)
        	self.vbox.pack_start(self.pictureslocradio, expand = False, fill = True, padding = 0)
        	self.vbox.pack_start(self.albumartbutton, expand = False, fill = True, padding = 0)

		#---- pack everything into side panel ----#
		self.vbox.show_all()
		self.vbox.set_size_request(200, -1)
		#self.shell.add_widget (self.vbox, RB.ShellUILocation.RIGHT_SIDEBAR, True, True)

