from gi.repository import Gio as gio
from enum import Enum

class ProxyMode(Enum):
    none = 'none'
    manual = 'manual'
    auto = 'auto'

    def isNone(self):
        return self == ProxyMode.none

    def isManual(self):
        return self == ProxyMode.manual

    def isAuto(self):
        return self == ProxyMode.auto

class AbstractProxySettings:
    def __init__(self):
        pass
    
    def onChangedMode(self, listener):
        raise Exception("NotImplementedException")

    def setMode(self, mode):
        raise Exception("NotImplementedException")

    def getMode(self):
        raise Exception("NotImplementedException")
    
    def getHttpHost(self):
        raise Exception("NotImplementedException")
    
    def setHttpHost(self, value):
        raise Exception("NotImplementedException")

    def getHttpPort(self):
        raise Exception("NotImplementedException")

    def setHttpPort(self, value):
        raise Exception("NotImplementedException")

    def getHttpsHost(self):
        raise Exception("NotImplementedException")

    def setHttpsHost(self, value):
        raise Exception("NotImplementedException")

    def getHttpsPort(self):
        raise Exception("NotImplementedException")

    def setHttpsPort(self, value):
        raise Exception("NotImplementedException")

    def getFtpHost(self):
        raise Exception("NotImplementedException")

    def setFtpHost(self, value):
        raise Exception("NotImplementedException")

    def getFtpPort(self):
        raise Exception("NotImplementedException")

    def setFtpPort(self, value):
        raise Exception("NotImplementedException")

    def getSocksHost(self):
        raise Exception("NotImplementedException")

    def setSocksHost(self, value):
        raise Exception("NotImplementedException")

    def getSocksPort(self):
        raise Exception("NotImplementedException")

    def setSocksPort(self, value):
        raise Exception("NotImplementedException")
    
    def getAutoconfigUrl(self):
        raise Exception("NotImplementedException")
    
    def setAutoconfigUrl(self, value):
        raise Exception("NotImplementedException")
        
    def getIgnoredHosts(self):
        raise Exception("NotImplementedException")
        
    def setIgnoredHosts(self, value):
        raise Exception("NotImplementedException")


class GSettingsProxySettings(AbstractProxySettings):
    def __init__(self):
        self.proxySetting = gio.Settings.new("org.gnome.system.proxy")
        self.proxySettingHttp = gio.Settings.new("org.gnome.system.proxy.http")
        self.proxySettingHttps = gio.Settings.new("org.gnome.system.proxy.https")
        self.proxySettingFtp = gio.Settings.new("org.gnome.system.proxy.ftp")
        self.proxySettingSocks = gio.Settings.new("org.gnome.system.proxy.socks")
    
    def onChangedMode(self, listener):
        self.proxySetting.connect("changed::mode", listener)

    def setMode(self, mode):
        self.proxySetting.set_string("mode", mode.name)

    def getMode(self):
        mode = self.proxySetting.get_string("mode")
        if mode == ProxyMode.none.name:
            return ProxyMode.none
        if mode == ProxyMode.manual.name:
            return ProxyMode.manual
        if mode == ProxyMode.auto.name:
            return ProxyMode.auto
    
    def getHttpHost(self):
        return self.proxySettingHttp.get_string('host')
    
    def setHttpHost(self, value):
        self._setStr(self.proxySettingHttp, 'host', value)

    def getHttpPort(self):
        return self.proxySettingHttp.get_int('port')

    def setHttpPort(self, value):
        self._setInt(self.proxySettingHttp, 'port', value)

    def getHttpsHost(self):
        return self.proxySettingHttps.get_string('host')

    def setHttpsHost(self, value):
        self._setStr(self.proxySettingHttps, 'host', value)

    def getHttpsPort(self):
        return self.proxySettingHttps.get_int('port')

    def setHttpsPort(self, value):
        self._setInt(self.proxySettingHttps, 'port', value)

    def getFtpHost(self):
        return self.proxySettingFtp.get_string("host")

    def setFtpHost(self, value):
        self._setStr(self.proxySettingFtp, 'host', value)

    def getFtpPort(self):
        return self.proxySettingFtp.get_int("port")

    def setFtpPort(self, value):
        self._setInt(self.proxySettingFtp, 'port', value)

    def getSocksHost(self):
        return self.proxySettingSocks.get_string("host")

    def setSocksHost(self, value):
        self._setStr(self.proxySettingSocks, 'host', value)

    def getSocksPort(self):
        return self.proxySettingSocks.get_int("port")

    def setSocksPort(self, value):
        self._setInt(self.proxySettingSocks, 'port', value)
    
    def getAutoconfigUrl(self):
        return self.proxySetting.get_string("autoconfig-url")
    
    def setAutoconfigUrl(self, value):
        self._setStr(self.proxySetting, "autoconfig-url", value)
        
    def getIgnoredHosts(self):
        return ', '.join(self.proxySetting.get_strv("ignore-hosts"))
        
    def setIgnoredHosts(self, value):
        if value:
            tmp = value.replace(' ', '').split(',')
            if tmp != self.proxySetting.get_default_value("ignore-hosts").get_strv():
                self.proxySetting.set_strv("ignore-hosts", tmp)
            else:
                self.proxySetting.reset('ignore-hosts')
        else:
            self.proxySetting.reset('ignore-hosts')
        
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


