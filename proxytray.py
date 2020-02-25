#!/usr/bin/python
# coding=UTF-8  
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
import os
import subprocess
from gi.repository import Gtk as gtk, Gio as gio, AppIndicator3 as appindicator, Gdk, GdkPixbuf
from inspect import currentframe, getframeinfo
import gettext
from config import ProxyTrayConfig
import profile

class ProxyTray:

    def __init__(self):
        print('init ProxyTray')

        filename = getframeinfo(currentframe()).filename
        self.path = os.path.dirname(os.path.abspath(filename))
        print('ProxyTray installed in ' + self.path)

        self.initLang()

        self.proxySetting = gio.Settings.new("org.gnome.system.proxy")
        self.proxySettingHttp = gio.Settings.new("org.gnome.system.proxy.http")
        self.proxySettingHttps = gio.Settings.new("org.gnome.system.proxy.https")
        self.proxySettingFtp = gio.Settings.new("org.gnome.system.proxy.ftp")
        self.proxySettingSocks = gio.Settings.new("org.gnome.system.proxy.socks")

        self.command_current = gtk.MenuItem(label='')
        self.command_no_proxy = gtk.MenuItem(label=_('Deactivate Proxy'))
        self.command_proxy_man = gtk.MenuItem(label=_('Activate Manual Proxy'))
        self.command_proxy_auto = gtk.MenuItem(label=_('Activate Automatic Proxy'))

        self.indicator = appindicator.Indicator.new("ProxyTray", "", appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.menu = gtk.Menu()

        self.profilesMenuItem = gtk.MenuItem(label=_('Proxy Profiles'))
        self.profilesMenu = gtk.Menu()
        self.command_new_profile = gtk.MenuItem(label=_('New Profile'))

        self.initMenu()

    def initLang(self):
        locale = ProxyTrayConfig.getLocale()
        try:
            if locale.startswith('en') == False:
                trs = gettext.translation('proxytray', localedir='i18n', languages=[locale])
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

        self.menu.append(gtk.SeparatorMenuItem())

        self.profilesMenuItem.set_submenu(self.profilesMenu)
        self.menu.append(self.profilesMenuItem)
        self.command_new_profile.connect('activate', self.newProfile)
        self.updateProfilesMenu()

        self.menu.append(gtk.SeparatorMenuItem())

        exittray = gtk.MenuItem(label=_('Exit Tray'))
        exittray.connect('activate', self.quit)
        self.menu.append(exittray)

        self.menu.show_all()

        self.menu.connect('scroll-event', self.refresh)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.menu)

        #self.newProfile(None)

    def refresh(self, _, __):
        self.doRefresh()

    def doRefresh(self):
        mode = self.proxySetting.get_string("mode")
        modeLib = ""
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

    def proxy_man(self, _):
        self.proxySetting.set_string("mode", "manual")

    def proxy_auto(self, _):
        self.proxySetting.set_string("mode", "auto")

    def newProfile(self, _):
        profile.EditProfileWindow(self, None)

    def updateProfilesMenu(self):
        for oldItem in self.profilesMenu.get_children():
            self.profilesMenu.remove(oldItem)
        self.profilesMenu.append(self.command_new_profile)
        for profile in ProxyTrayConfig.getProfiles():
            profileMenuItem = gtk.MenuItem(label=profile['name'])
            self.profilesMenu.append(profileMenuItem)
            profileSubMenu = gtk.Menu()
            profileMenuItem.set_submenu(profileSubMenu)
            profileSubMenuItem = gtk.MenuItem(label=_('Apply'))
            profileSubMenuItem.connect('activate', self.applyProfile, profile['name'])
            profileSubMenu.append(profileSubMenuItem)
            profileSubMenuItem = gtk.MenuItem(label=_('Edit'))
            profileSubMenuItem.connect('activate', self.modifyProfile, profile['name'])
            profileSubMenu.append(profileSubMenuItem)
        
        self.profilesMenu.show_all()

    def generateProfile(self, name):
        return {
            'name': name,
            'manual': True,
            'auto': True,

            'httpHost': self.proxySettingHttp.get_string('host'),
            'httpPort': self.proxySettingHttp.get_int('port'),

            'httpsHost': self.proxySettingHttps.get_string("host"),
            'httpsPort': self.proxySettingHttps.get_int("port"),

            'ftpHost': self.proxySettingFtp.get_string("host"),
            'ftpPort': self.proxySettingFtp.get_int("port"),

            'socksHost': self.proxySettingSocks.get_string("host"),
            'socksPort': self.proxySettingSocks.get_int("port"),

            'ignored': ', '.join(self.proxySetting.get_strv("ignore-hosts")),

            'autoConfigUrl': self.proxySetting.get_string("autoconfig-url")
        }

    def applyProfile(self, _, name):
        profile = ProxyTrayConfig.getProfile(name)

        if profile.get('manual'):
            self._setStr(self.proxySettingHttp, 'host', profile.get('httpHost'))
            self._setInt(self.proxySettingHttp, 'port', profile.get('httpPort'))

            self._setStr(self.proxySettingHttps, 'host', profile.get('httpsHost'))
            self._setInt(self.proxySettingHttps, 'port', profile.get('httpsPort'))

            self._setStr(self.proxySettingFtp, 'host', profile.get('ftpHost'))
            self._setInt(self.proxySettingFtp, 'port', profile.get('ftpPort'))

            self._setStr(self.proxySettingSocks, 'host', profile.get('socksHost'))
            self._setInt(self.proxySettingSocks, 'port', profile.get('socksPort'))

            if profile.get('ignored'):
                tmp = profile.get('ignored').replace(' ', '').split(',')
                if tmp != self.proxySetting.get_default_value("ignore-hosts").get_strv():
                    self.proxySetting.set_strv("ignore-hosts", tmp)
                else:
                    self.proxySetting.reset('ignore-hosts')
            else:
                self.proxySetting.reset('ignore-hosts')

        if profile.get('auto'):
            self._setStr(self.proxySetting, "autoconfig-url", profile.get('autoConfigUrl'))
    
    def _setStr(self, settings, k, v):
        if v and v != settings.get_default_value(k).get_string():
            settings.set_string(k, v)
        else:
            settings.reset(k)
    
    def _setInt(self, settings, k, v):
        if v and v != settings.get_default_value(k).get_int32():
            settings.set_int(k, v)
        else:
            settings.reset(k)

    def modifyProfile(self, _, name):
        profile.EditProfileWindow(self, ProxyTrayConfig.getProfile(name))

    def deleteProfile(self, _, name):
        ProxyTrayConfig.deleteProfile(name)
        self.updateProfilesMenu()


    def quit(self, _):
        gtk.main_quit()

def main():
    a = ProxyTray()
    gtk.main()


if __name__ == "__main__":
    main()