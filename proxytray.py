#!/usr/bin/python3
# coding=UTF-8  
import os
from inspect import currentframe, getframeinfo
import gettext
from lib.proxytray.proxytrayconfig import ProxyTrayConfig
from lib.proxytray.proxysettings import GSettingsProxySettings, ProxyMode
from lib.proxytray.proxytraymenu import AppIndicatorProxyTrayMenu

class ProxyTray:

    def __init__(self):
        print('init ProxyTray')

        filename = getframeinfo(currentframe()).filename
        self.path = os.path.dirname(os.path.abspath(filename))
        print('ProxyTray installed in ' + self.path)

        self._initLang()

        self.proxySettings = GSettingsProxySettings()
        self.config = ProxyTrayConfig(self.path, self.proxySettings)
        self.menu = AppIndicatorProxyTrayMenu(self.config)

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

def main():
    ProxyTray()


if __name__ == "__main__":
    main()