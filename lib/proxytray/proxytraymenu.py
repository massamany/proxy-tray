import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk as gtk, Gio as gio, AppIndicator3 as appindicator, Gdk, GdkPixbuf
from lib.proxytray.proxytrayconfig import ProxyTrayConfig
from lib.proxytray.proxysettings import ProxyMode
from lib.proxytray.proxyprofile import ProfileEditor

class AppIndicatorProxyTrayMenu:

    def __init__(self, config):
        self.config = config
        self.proxySettings = config.proxySettings
        self.commandCurrent = gtk.MenuItem(label='')
        self.commandNoProxy = gtk.MenuItem(label=_('Deactivate Proxy'))
        self.commandProxyMan = gtk.MenuItem(label=_('Activate Manual Proxy'))
        self.commandProxyAuto = gtk.MenuItem(label=_('Activate Automatic Proxy'))

        self.indicator = appindicator.Indicator.new("ProxyTray", "", appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.menu = gtk.Menu()

        self.profilesMenuItem = gtk.MenuItem(label=_('Proxy Profiles'))
        self.profilesMenu = gtk.Menu()
        self.commandNewProfile = gtk.MenuItem(label=_('New Profile'))

        self.profileEditor = ProfileEditor(self.config)
        self.profileEditor.onSaveCallback(self._profilesUpdated)
        self.profileEditor.onDeleteCallback(self._profilesUpdated)

        self._initMenu()
        gtk.main()

    def _initMenu(self):
        self.proxySettings.onChangedMode(self._changedProxyMode)
        self._refreshProxyMode()

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
        self._refreshProfilesMenu()

        self.menu.append(gtk.SeparatorMenuItem())

        exittray = gtk.MenuItem(label=_('Exit Tray'))
        exittray.connect('activate', self.quit)
        self.menu.append(exittray)

        self.menu.show_all()

        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.menu)

    def _changedProxyMode(self, _, __):
        self._refreshProxyMode()

    def _refreshProxyMode(self):
        mode = self.proxySettings.getMode()
        modeLib = ""
        self.commandNoProxy.set_sensitive(mode != ProxyMode.none)
        self.commandProxyMan.set_sensitive(mode != ProxyMode.manual)
        self.commandProxyAuto.set_sensitive(mode != ProxyMode.auto)
        if mode == ProxyMode.none:
            modeLib = _('Deactivated')
            self.indicator.set_icon_full(os.path.abspath(self.config.path + '/icons/no_proxy.png'), modeLib)
        if mode == ProxyMode.manual:
            modeLib = _('Manual')
            self.indicator.set_icon_full(os.path.abspath(self.config.path + '/icons/proxy_man.png'), modeLib)
        if mode == ProxyMode.auto:
            modeLib = _('Automatic')
            self.indicator.set_icon_full(os.path.abspath(self.config.path + '/icons/proxy_auto.png'), modeLib)

        self.commandCurrent.set_label(_('Proxy: ') + modeLib)

    def _refreshProfilesMenu(self):
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
    
    def _noProxy(self, _):
        self.proxySettings.setMode(ProxyMode.none)

    def _proxyMan(self, _):
        self.proxySettings.setMode(ProxyMode.manual)

    def _proxyAuto(self, _):
        self.proxySettings.setMode(ProxyMode.auto)

    def _newProfile(self, _):
        self.profileEditor.updateFromProfile(None)

    def _applyProfile(self, _, name):
        self.config.applyProfile(name)

    def _modifyProfile(self, _, name):
        self.profileEditor.updateFromProfile(ProxyTrayConfig.getProfile(name))
    
    def _profilesUpdated(self, name):
        self._refreshProfilesMenu()

    def quit(self, _):
        gtk.main_quit()

