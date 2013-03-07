#!/usr/bin/env python
#-*- coding: UTF-8 -*-

#import GObject
#import Gtk
#import os
#import gio
import urllib
#import GConf
#import rb,rhythmdb
#import treefilebrowser
#import logging,logging.handlers

from gi.repository import GObject, Peas, RB, Gtk, Gio

#log=logging.getLogger('FolderView')
LAST_PATH_KEY = '/rhythmbox.plugin.FolderView.lastpath'

class FolderViewSource(RB.BrowserSource):
    #__gproperties__ = {'plugin': (RB.Plugin, 'plugin', 'plugin', GObject.PARAM_WRITABLE|GObject.PARAM_CONSTRUCT_ONLY),}
    
    def __init__(self):
        RB.BrowserSource.__init__(self)

        self.shell = None
        
        library = Gio.Settings("org.gnome.rhythmbox.rhythmdb")
        library_location = library['locations'][0]

    def do_impl_activate(self):
        #log.info('Activate')
        if self.shell == None:
            self.shell      = self.get_property('shell')
            self.db         = self.shell.get_property('db')
            self.entry_type = self.get_property('entry-type')
            self.entry_view = self.get_entry_view()
            self.filebrowser.set_active_dir(GConf.client_get_default().get_without_default(LAST_PATH_KEY).get_string())

        ui_browse=self.shell.get_ui_manager().get_widget('/ToolBar/Browse')
        #ui_browse.set_sensitive(False)
        ui_browse.hide()
        #GConf.client_get_default().set_string(LAST_PATH_KEY,userName)
        RB.BrowserSource.do_impl_activate(self)

    def do_impl_deactivate(self):
        #log.info('Deactivate')
        ui_browse=self.shell.get_ui_manager().get_widget('/ToolBar/Browse')
        ui_browse.show()
        RB.BrowserSource.do_impl_deactivate(self)
        #uim.get_widget('/ToolBar/Browse').set_sensitive(False)

    #def set_entry(self, uri):
    #    entry = self.db.entry_lookup_by_location(uri)
    #    if entry != None:
    #        if self.db.entry_get(entry, rhythmdb.PROP_DURATION) != 0:
    #            #self.props.query_model.add_entry(entry, 0)
    #            self.db.query_append(self.query, (rhythmdb.QUERY_PROP_SUFFIX, rhythmdb.PROP_LOCATION, self.db.entry_get(entry, rhythmdb.PROP_LOCATION)))

    def on_treeview_cursor_changed(self, widget):
        for row in self.props.query_model:
            entry = row[0]
            self.props.query_model.remove_entry(entry)

        self.query = self.db.query_new()
        song_type = self.db.entry_type_get_by_name('song')
        path = self.filebrowser.get_selected()
        GConf.client_get_default().set_string(LAST_PATH_KEY,path)
        #for item in os.listdir(path):
        #    filename = os.path.join(path, item)
        #    if os.path.isfile(filename):
        #        tmp = str(path_to_uri(filename))
                #self.set_entry(path_to_uri(filename))
        self.db.query_append(self.query, (rhythmdb.QUERY_PROP_EQUALS, rhythmdb.PROP_TYPE, song_type))
        self.db.query_append(self.query, (rhythmdb.QUERY_PROP_PREFIX, rhythmdb.PROP_LOCATION, path_to_uri(path)))
        self.db.do_full_query_parsed(self.props.query_model, self.query)

        if self.shell.props.shell_player.props.playing:
            pass
        else:
            self.shell.props.shell_player.stop()

    def do_impl_pack_paned (self, paned):
        self.__paned_box = Gtk.HPaned()
        self.filebrowser = treefilebrowser.TreeFileBrowser(self.library_location[7:])
        self.scrolled = self.filebrowser.get_scrolled()
        self.scrolled.set_size_request(200,-1)
        self.treeview = self.filebrowser.get_view()
        self.treeview.connect('cursor-changed', self.on_treeview_cursor_changed)
        self.pack_start(self.__paned_box)
        self.__paned_box.add1(self.scrolled)
        self.__paned_box.add2(paned)
        

def path_to_uri(path):
    gfile = gio.File(path)
    return gfile.get_uri()

#GObject.type_register(FolderViewSource)
