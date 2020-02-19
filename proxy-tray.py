#!/usr/bin/python
# coding=UTF-8  
import os
import subprocess
from gi.repository import Gtk as gtk, Gio as gio, AppIndicator3 as appindicator
from inspect import currentframe, getframeinfo
import gettext
from config import ProxyTrayConfig

class ProxyTray:

    def __init__(self):
        print('init ProxyTray')

        filename = getframeinfo(currentframe()).filename
        self.path = os.path.dirname(os.path.abspath(filename))
        print('ProxyTray installed in ' + self.path)

        self.initLang()

        self.proxySetting = gio.Settings.new("org.gnome.system.proxy")

        self.command_no_proxy = gtk.MenuItem(label=_('Deactivate Proxy'))
        self.command_proxy_man = gtk.MenuItem(label=_('Activate Manual Proxy'))
        self.command_proxy_auto = gtk.MenuItem(label=_('Activate Automatic Proxy'))

        self.indicator = appindicator.Indicator.new("ProxyTray", "", appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.menu = gtk.Menu()
        self.command_current = gtk.MenuItem(label='')

        self.initMenu()

    def initLang(self):
        locale = ProxyTrayConfig.getLocale()
        try:
            if locale.startswith('en') == False:
                trs = gettext.translation('proxy-tray', localedir='i18n', languages=[locale])
                trs.install()
                gettext.bindtextdomain('ProxyTray', self.path + '/i18n/')
                gettext.textdomain('ProxyTray')
            else:
                gettext.install("")

            print("Loaded language: " + locale)
        except Exception as e:
            print(e)
            print("Failed to load language: " + locale + ". Using default.")
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

        exittray = gtk.MenuItem(label=_('Exit Tray'))
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
            modeLib = _('Deactivated')
            self.indicator.set_icon_full(os.path.abspath(self.path + '/icons/no_proxy.png'), modeLib)
        if mode == "auto":
            modeLib = _('Automatic')
            self.indicator.set_icon_full(os.path.abspath(self.path + '/icons/proxy_auto.png'), modeLib)
        if mode == "manual":
            self.indicator.set_icon_full(os.path.abspath(self.path + '/icons/proxy_man.png'), modeLib)

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