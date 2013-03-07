#!/usr/bin/env python
#-*- coding: UTF-8 -*-

#import GObject
#import Gtk
#import rb
#import RB
#import logging,logging.handlers

from FolderViewSource import FolderViewSource

from gi.repository import GObject, Peas, RB, Gtk

class FolderViewEntryType(RB.RhythmDBEntryType):
    def __init__(self):
        RB.RhythmDBEntryType.__init__(self, name = 'FolderViewEntryType')

class FolderView (GObject.Object, Peas.Activatable):
    __gtype_name = 'FolderView'
    object = GObject.property(type=GObject.GObject)

    def __init__(self):
        GObject.Object.__init__(self)

        #log.setLevel(logging.DEBUG)
        #console_handler = logging.StreamHandler()
        #console_handler.setLevel(logging.DEBUG)
        #console_handler.setFormatter(logging.Formatter('%(name)s %(levelname)-8s %(module)s::%(funcName)s - %(message)s'))
        #log.addHandler(console_handler)
        
    def do_activate(self):
        shell = self.object

        #group = RB.rb_source_group_get_by_name ("library")
        self.db = shell.get_property("db")
        try:
            self.entry_type = FolderViewEntryType()
            self.db.register_entry_type(self.entry_type)
        except NotImplementedError:
            self.entry_type = self.db.entry_register_type("FolderViewEntryType")
        self.entry_type.can_sync_metadata = True
        self.entry_type.save_to_disk = True
        self.entry_type.category = RB.RhythmDBEntryCategory.STREAM
        self.source = GObject.new (FolderViewSource,
                                    shell=shell,
                                    name="Folder View",
                                    entry_type=self.entry_type,
                                    plugin=self,
                                    #source_group=group
                                    )
        #self.source.set_property( "icon", self.get_folder_closed_icon()) 
        shell.append_display_page(self.source, None)
        shell.register_entry_type_for_source(self.source, self.entry_type)
        
    def do_deactivate(self):
        #log.info("deactivate")
        self.db.entry_delete_by_type(self.entry_type)
        #self.db.commit()
        self.db = None
        self.entry_type = None
        self.source.delete_thyself()
        self.source = None

    def get_folder_closed_icon(self):
        """ Returns a pixbuf with the current theme closed folder icon """

        icon_theme = Gtk.IconTheme.get_default()
        try:
            icon = icon_theme.load_icon("gnome-fs-directory", 24, 0)
            return icon
        except GObject.GError, exc:
            #print "Can't load icon", exc
            try:
                icon = icon_theme.load_icon("Gtk-directory", 24, 0)
                return icon
            except:
                #print "Can't load default icon"
                return None
