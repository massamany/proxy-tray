import os
from lib.proxytray.proxytrayconfig import ProxyTrayConfig
from lib.proxytray.proxysettings import ProxyMode
from lib.proxytray.proxyprofile import ProfileEditor

try:
    from PIL import Image, ImageDraw
    from pystray import Icon, Menu, MenuItem
    FOUND_PYSTRAY = True
except ImportError:
    FOUND_PYSTRAY = False

def pystrayAvailable():
    return FOUND_PYSTRAY

class PysTrayProxyTrayMenu:

    def __init__(self, config):
        self.config = config
        self.proxySettings = config.proxySettings
        self.proxySettings.onChangedMode(self._changedProxyMode)

        self.iconNoProxy = Image.open(os.path.abspath(self.config.path + '/icons/no_proxy.png'))
        self.iconProxyMan = Image.open(os.path.abspath(self.config.path + '/icons/proxy_man.png'))
        self.iconProxyAuto = Image.open(os.path.abspath(self.config.path + '/icons/proxy_auto.png'))

        self.menu = Menu(lambda: (
            MenuItem(self.modeLabel, None, enabled=False),
            Menu.SEPARATOR,
            MenuItem(_('Deactivate Proxy'), self._redirectTo(self._noProxy), enabled=not self.mode.isNone()),
            MenuItem(_('Activate Manual Proxy'), self._redirectTo(self._proxyMan), enabled=not self.mode.isManual()),
            MenuItem(_('Activate Automatic Proxy'), self._redirectTo(self._proxyAuto), enabled=not self.mode.isAuto()),
            Menu.SEPARATOR,
            MenuItem(_('Proxy Profiles'), Menu(lambda: self.generateProfilesMenu())),
            Menu.SEPARATOR,
            MenuItem(_('Exit Tray'), self._redirectTo(self.quit))
        ))

        self.profileEditor = ProfileEditor(self.config)
        self.profileEditor.onSaveCallback(self.update_menu)
        self.profileEditor.onDeleteCallback(self.update_menu)

        self.pystray = Icon('ProxyTray', self.iconProxyMan, menu=self.menu)
        self._refreshProxyMode()

        self.pystray.run()
    
    def generateProfilesMenu(self):
        result = [MenuItem(_('New Profile'), self._redirectTo(self._newProfile))]
        for profile in ProxyTrayConfig.getProfiles():
            result.append(
                MenuItem(profile['name'], Menu(lambda: (
                    MenuItem(_('Apply'), self._redirectTo(self._applyProfile, profile['name'])),
                    MenuItem(_('Edit'), self._redirectTo(self._modifyProfile, profile['name']))
                )))
            )
        return result

    def update_menu(self, _):
        self.pystray.update_menu()
    
    def _redirectTo(self, method, arg = None):
        def inner():
            if arg == None:
                method()
            else:
                method(arg)
        return inner

    def _changedProxyMode(self, _, __):
        self._refreshProxyMode()

    def _refreshProxyMode(self):
        self.mode = self.proxySettings.getMode()
        self.modeLabel = ""
        if self.mode == ProxyMode.none:
            self.modeLabel = _('Deactivated')
            self.pystray.icon = self.iconNoProxy
        if self.mode == ProxyMode.manual:
            self.modeLabel = _('Manual')
            self.pystray.icon = self.iconProxyMan
        if self.mode == ProxyMode.auto:
            self.modeLabel = _('Automatic')
            self.pystray.icon = self.iconProxyAuto
    
    def _noProxy(self):
        self.proxySettings.setMode(ProxyMode.none)

    def _proxyMan(self):
        self.proxySettings.setMode(ProxyMode.manual)

    def _proxyAuto(self):
        self.proxySettings.setMode(ProxyMode.auto)

    def _newProfile(self):
        self.profileEditor.updateFromProfile(None)

    def _applyProfile(self, name):
        self.config.applyProfile(name)

    def _modifyProfile(self, name):
        self.profileEditor.updateFromProfile(ProxyTrayConfig.getProfile(name))

    def quit(self):
        self.pystray.stop()

