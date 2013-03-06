#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import gobject
import gtk
import rb
import rhythmdb
import logging,logging.handlers
from FolderViewSource import FolderViewSource

log=logging.getLogger('FolderView')

class FolderViewEntryType(rhythmdb.EntryType):
    def __init__(self):
        rhythmdb.EntryType.__init__(self, name = 'FolderViewEntryType')

class FolderView (rb.Plugin):
    def __init__(self):
        rb.Plugin.__init__(self)

        log.setLevel(logging.DEBUG)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logging.Formatter('%(name)s %(levelname)-8s %(module)s::%(funcName)s - %(message)s'))
        log.addHandler(console_handler)
        
    def activate(self, shell):
        self.shell = shell

        group = rb.rb_source_group_get_by_name ("library")
        self.db = shell.get_property("db")
        try:
            self.entry_type = FolderViewEntryType()
            self.db.register_entry_type(self.entry_type)
        except NotImplementedError:
            self.entry_type = self.db.entry_register_type("FolderViewEntryType")
        self.entry_type.can_sync_metadata = True
        self.entry_type.save_to_disk = True
        self.entry_type.category = rhythmdb.ENTRY_STREAM
        self.source = gobject.new (FolderViewSource,
                                    shell=self.shell,
                                    name="Folder View",
                                    entry_type=self.entry_type,
                                    plugin=self,
                                    source_group=group
                                    )
        self.source.set_property( "icon", self.get_folder_closed_icon()) 
        shell.append_source(self.source, None)
        shell.register_entry_type_for_source(self.source, self.entry_type)
        
    def deactivate(self, shell):
        log.info("deactivate")
        self.db.entry_delete_by_type(self.entry_type)
        #self.db.commit()
        self.db = None
        self.entry_type = None
        self.source.delete_thyself()
        self.source = None

    def get_folder_closed_icon(self):
        """ Returns a pixbuf with the current theme closed folder icon """

        icon_theme = gtk.icon_theme_get_default()
        try:
            icon = icon_theme.load_icon("gnome-fs-directory", 24, 0)
            return icon
        except gobject.GError, exc:
            #print "Can't load icon", exc
            try:
                icon = icon_theme.load_icon("gtk-directory", 24, 0)
                return icon
            except:
                #print "Can't load default icon"
                return None
