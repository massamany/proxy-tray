#!/usr/bin/python
# coding=UTF-8  
import os
import subprocess
from gi.repository import Gtk as gtk, Gio as gio, AppIndicator3 as appindicator
from inspect import currentframe, getframeinfo
import gettext
import locale

class ProxyTray:

    def __init__(self):
        print('init ProxyTray')

        filename = getframeinfo(currentframe()).filename
        self.path = os.path.dirname(os.path.abspath(filename))
        print('ProxyTray installed in ' + self.path)

        self.initLang()

        self.proxySetting = gio.Settings.new("org.gnome.system.proxy")

        self.command_no_proxy = gtk.MenuItem(_('Deactivate Proxy'))
        self.command_proxy_man = gtk.MenuItem(_('Activate Manual Proxy'))
        self.command_proxy_auto = gtk.MenuItem(_('Activate Automatic Proxy'))

        self.indicator = appindicator.Indicator.new("ProxyTray", "", appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.menu = gtk.Menu()
        self.command_current = gtk.MenuItem('')

        self.initMenu()

    def initLang(self):
        loc = locale.getlocale()[0][:2]
        try:
            if loc.startswith('en') == False:
                trs = gettext.translation('proxy-tray', localedir='i18n', languages=[loc])
                trs.install()
                gettext.bindtextdomain('ProxyTray', self.path + '/i18n/')
                gettext.textdomain('ProxyTray')
            else:
                gettext.install("")

            print("Loaded language: " + loc)
        except Exception as e:
            print("Failed to load language: " + loc + ". Using default.")
            gettext.install("")

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

        exittray = gtk.MenuItem(_('Exit Tray'))
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
        modeLib = ""
        print('refresh - mode: ' + mode)
        self.command_no_proxy.set_sensitive(mode != "none")
        self.command_proxy_man.set_sensitive(mode != "manual")
        self.command_proxy_auto.set_sensitive(mode != "auto")
        if mode == "none":
            self.indicator.set_icon(os.path.abspath(self.path + '/icons/no_proxy.png'))
            modeLib = _('Deactivated')
        if mode == "auto":
            self.indicator.set_icon(os.path.abspath(self.path + '/icons/proxy_auto.png'))
            modeLib = _('Automatic')
        if mode == "manual":
            self.indicator.set_icon(os.path.abspath(self.path + '/icons/proxy_man.png'))
            modeLib = _('Manual')

        self.command_current.set_label(_('Proxy: ') + modeLib)
    
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