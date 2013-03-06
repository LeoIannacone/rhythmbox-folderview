#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import gobject
import gtk
import os
import gio
import urllib
import gconf
import rb,rhythmdb
import treefilebrowser
import logging,logging.handlers

log=logging.getLogger('FolderView')
LAST_PATH_KEY = '/rhythmbox.plugin.FolderView.lastpath'

class FolderViewSource(rb.BrowserSource):
    #__gproperties__ = {'plugin': (rb.Plugin, 'plugin', 'plugin', gobject.PARAM_WRITABLE|gobject.PARAM_CONSTRUCT_ONLY),}
    
    def __init__(self):
        rb.BrowserSource.__init__(self)

        self.shell = None
        
        self.g_client = gconf.client_get_default()
        self.library_location = urllib.unquote(self.g_client.get_list('/apps/rhythmbox/library_locations', gconf.VALUE_STRING)[0])

    def do_impl_activate(self):
        log.info('Activate')
        if self.shell == None:
            self.shell      = self.get_property('shell')
            self.db         = self.shell.get_property('db')
            self.entry_type = self.get_property('entry-type')
            self.entry_view = self.get_entry_view()
            self.filebrowser.set_active_dir(gconf.client_get_default().get_without_default(LAST_PATH_KEY).get_string())

        ui_browse=self.shell.get_ui_manager().get_widget('/ToolBar/Browse')
        #ui_browse.set_sensitive(False)
        ui_browse.hide()
        #gconf.client_get_default().set_string(LAST_PATH_KEY,userName)
        rb.BrowserSource.do_impl_activate(self)

    def do_impl_deactivate(self):
        log.info('Deactivate')
        ui_browse=self.shell.get_ui_manager().get_widget('/ToolBar/Browse')
        ui_browse.show()
        rb.BrowserSource.do_impl_deactivate(self)
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
        gconf.client_get_default().set_string(LAST_PATH_KEY,path)
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
        self.__paned_box = gtk.HPaned()
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

gobject.type_register(FolderViewSource)
