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

        self._initLang()

        self.proxySetting = gio.Settings.new("org.gnome.system.proxy")
        self.proxySettingHttp = gio.Settings.new("org.gnome.system.proxy.http")
        self.proxySettingHttps = gio.Settings.new("org.gnome.system.proxy.https")
        self.proxySettingFtp = gio.Settings.new("org.gnome.system.proxy.ftp")
        self.proxySettingSocks = gio.Settings.new("org.gnome.system.proxy.socks")

        self.commandCurrent = gtk.MenuItem(label='')
        self.commandNoProxy = gtk.MenuItem(label=_('Deactivate Proxy'))
        self.commandProxyMan = gtk.MenuItem(label=_('Activate Manual Proxy'))
        self.commandProxyAuto = gtk.MenuItem(label=_('Activate Automatic Proxy'))

        self.indicator = appindicator.Indicator.new("ProxyTray", "", appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.menu = gtk.Menu()

        self.profilesMenuItem = gtk.MenuItem(label=_('Proxy Profiles'))
        self.profilesMenu = gtk.Menu()
        self.commandNewProfile = gtk.MenuItem(label=_('New Profile'))

        self._initMenu()

    def _initLang(self):
        locale = ProxyTrayConfig.getLocale()
        try:
            if locale.startswith('en') == False:
                trs = gettext.translation('proxytray', localedir=self.path + '/i18n', languages=[locale])
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

    def _initMenu(self):
        self.proxySetting.connect("changed::mode", self._refresh)
        self.refresh()

        self.commandCurrent.set_sensitive(False)
        self.menu.append(self.commandCurrent)

        self.menu.append(gtk.SeparatorMenuItem())

        self.commandNoProxy.connect('activate', self._noProxy)
        self.menu.append(self.commandNoProxy)

        self.commandProxyMan.connect('activate', self._proxyMan)
        self.menu.append(self.commandProxyMan)

        self.commandProxyAuto.connect('activate', self._proxyAuto)
        self.menu.append(self.commandProxyAuto)

        self.menu.append(gtk.SeparatorMenuItem())

        self.profilesMenuItem.set_submenu(self.profilesMenu)
        self.menu.append(self.profilesMenuItem)
        self.commandNewProfile.connect('activate', self._newProfile)
        self.updateProfilesMenu()

        self.menu.append(gtk.SeparatorMenuItem())

        exittray = gtk.MenuItem(label=_('Exit Tray'))
        exittray.connect('activate', self.quit)
        self.menu.append(exittray)

        self.menu.show_all()

        self.menu.connect('scroll-event', self._refresh)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.menu)

        #self.newProfile(None)

    def _refresh(self, _, __):
        self.refresh()

    def refresh(self):
        mode = self.proxySetting.get_string("mode")
        modeLib = ""
        self.commandNoProxy.set_sensitive(mode != "none")
        self.commandProxyMan.set_sensitive(mode != "manual")
        self.commandProxyAuto.set_sensitive(mode != "auto")
        if mode == "none":
            modeLib = _('Deactivated')
            self.indicator.set_icon_full(os.path.abspath(self.path + '/icons/no_proxy.png'), modeLib)
        if mode == "auto":
            modeLib = _('Automatic')
            self.indicator.set_icon_full(os.path.abspath(self.path + '/icons/proxy_auto.png'), modeLib)
        if mode == "manual":
            self.indicator.set_icon_full(os.path.abspath(self.path + '/icons/proxy_man.png'), modeLib)

        self.commandCurrent.set_label(_('Proxy: ') + modeLib)
    
    def _noProxy(self, _):
        self.proxySetting.set_string("mode", "none")

    def _proxyMan(self, _):
        self.proxySetting.set_string("mode", "manual")

    def _proxyAuto(self, _):
        self.proxySetting.set_string("mode", "auto")

    def _newProfile(self, _):
        profile.ProfileEditor(self, None)

    def updateProfilesMenu(self):
        for oldItem in self.profilesMenu.get_children():
            self.profilesMenu.remove(oldItem)
        self.profilesMenu.append(self.commandNewProfile)
        for profile in ProxyTrayConfig.getProfiles():
            profileMenuItem = gtk.MenuItem(label=profile['name'])
            self.profilesMenu.append(profileMenuItem)
            profileSubMenu = gtk.Menu()
            profileMenuItem.set_submenu(profileSubMenu)
            profileSubMenuItem = gtk.MenuItem(label=_('Apply'))
            profileSubMenuItem.connect('activate', self._applyProfile, profile['name'])
            profileSubMenu.append(profileSubMenuItem)
            profileSubMenuItem = gtk.MenuItem(label=_('Edit'))
            profileSubMenuItem.connect('activate', self._modifyProfile, profile['name'])
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

    def _applyProfile(self, _, name):
        self.applyProfile(name)

    def applyProfile(self, name):
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

    def _modifyProfile(self, _, name):
        self.modifyProfile(name)

    def modifyProfile(self, name):
        profile.ProfileEditor(self, ProxyTrayConfig.getProfile(name))

    def _deleteProfile(self, _, name):
        self.deleteProfile(name)

    def deleteProfile(self, name):
        ProxyTrayConfig.deleteProfile(name)
        self.updateProfilesMenu()


    def quit(self, _):
        gtk.main_quit()

def main():
    a = ProxyTray()
    gtk.main()


if __name__ == "__main__":
    main()