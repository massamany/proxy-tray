#!/usr/bin/python
# coding=UTF-8  
import os
import subprocess
from gi.repository import Gtk as gtk, Gio as gio, AppIndicator3 as appindicator
from inspect import currentframe, getframeinfo

class ProxyTray:

    def __init__(self):
        print 'init Proxytray'

        filename = getframeinfo(currentframe()).filename
        self.path = os.path.dirname(os.path.abspath(filename))
        print 'Proxytray installed in ' + self.path

        self.proxySetting = gio.Settings.new("org.gnome.system.proxy")

        self.command_no_proxy = gtk.MenuItem('Deactivate Proxy')
        self.command_proxy_man = gtk.MenuItem('Activate Manual Proxy')
        self.command_proxy_auto = gtk.MenuItem('Activate Auto Proxy')

        self.indicator = appindicator.Indicator.new("ProxyTray", "", appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.menu = gtk.Menu()
        self.command_current = gtk.MenuItem('')

        self.initMenu()

    def initMenu(self):
        self.proxySetting.connect("changed::mode", self.refresh)
        self.doRefresh()

        self.command_current.set_sensitive(False)
        self.command_current.connect('activate', self.refresh)
        self.menu.append(self.command_current)

        self.menu.append(gtk.SeparatorMenuItem())

        self.command_no_proxy.connect('activate', self.no_proxy)
        self.menu.append(self.command_no_proxy)

        self.command_proxy_man.connect('activate', self.proxy_man)
        self.menu.append(self.command_proxy_man)

        self.command_proxy_auto.connect('activate', self.proxy_auto)
        self.menu.append(self.command_proxy_auto)

        exittray = gtk.MenuItem('Exit Tray')
        exittray.connect('activate', self.quit)
        self.menu.append(exittray)

        self.menu.show_all()

        self.menu.connect('scroll-event', self.refresh)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.menu)

    def refresh(self, _, __):
        self.doRefresh()

    def doRefresh(self):
        mode = self.proxySetting.get_string("mode")
        print 'refresh - mode: ' + mode
        self.command_current.set_label('Proxy: ' + mode)
        self.command_no_proxy.set_sensitive(mode != "none")
        self.command_proxy_man.set_sensitive(mode != "manual")
        self.command_proxy_auto.set_sensitive(mode != "auto")
        if mode == "none":
            self.indicator.set_icon(os.path.abspath(self.path + '/icons/no_proxy.png'))
        if mode == "auto":
            self.indicator.set_icon(os.path.abspath(self.path + '/icons/proxy_auto.png'))
        if mode == "manual":
            self.indicator.set_icon(os.path.abspath(self.path + '/icons/proxy_man.png'))

    def no_proxy(self, _):
        self.proxySetting.set_string("mode", "none")
        self.doRefresh()

    def proxy_man(self, _):
        self.proxySetting.set_string("mode", "manual")
        self.doRefresh()

    def proxy_auto(self, _):
        self.proxySetting.set_string("mode", "auto")
        self.doRefresh()

    def quit(self, _):
        gtk.main_quit()

def main():
    a = ProxyTray()
    gtk.main()


if __name__ == "__main__":
    main()