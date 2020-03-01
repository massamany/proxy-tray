import locale
import os
import yaml

def _read():
    try:
        with open(os.getenv("HOME") + '/.proxytray.yaml') as config_file:
            return yaml.load(config_file)
    except:
        return {}

class ProxyTrayConfig:

    _conf = _read()

    def __init__(self, path, proxySettings):
        self.path = path
        self.proxySettings = proxySettings

    def getPath(self):
        return self.path

    def generateProfile(self, name):
        return {
            'name': name,
            'manual': True,
            'auto': True,

            'httpHost': self.proxySettings.getHttpHost(),
            'httpPort': self.proxySettings.getHttpPort(),

            'httpsHost': self.proxySettings.getHttpsHost(),
            'httpsPort': self.proxySettings.getHttpsPort(),

            'ftpHost': self.proxySettings.getFtpHost(),
            'ftpPort': self.proxySettings.getFtpPort(),

            'socksHost': self.proxySettings.getSocksHost(),
            'socksPort': self.proxySettings.getSocksPort(),

            'ignored': self.proxySettings.getIgnoredHosts(),

            'autoConfigUrl': self.proxySettings.getAutoconfigUrl(),
        }

    def applyProfile(self, name):
        profile = ProxyTrayConfig.getProfile(name)

        if profile.get('manual'):
            self.proxySettings.setHttpHost(profile.get('httpHost'))
            self.proxySettings.setHttpPort(profile.get('httpPort'))

            self.proxySettings.setHttpsHost(profile.get('httpsHost'))
            self.proxySettings.setHttpsPort(profile.get('httpsPort'))

            self.proxySettings.setFtpHost(profile.get('ftpHost'))
            self.proxySettings.setFtpPort(profile.get('ftpPort'))

            self.proxySettings.setSocksHost(profile.get('socksHost'))
            self.proxySettings.setSocksPort(profile.get('socksPort'))

            self.proxySettings.setIgnoredHosts(profile.get('ignored'))

        if profile.get('auto'):
            self.proxySettings.setAutoconfigUrl(profile.get('autoConfigUrl'))

    @staticmethod
    def _save():
        with open(os.getenv("HOME") + '/.proxytray.yaml', 'w+') as outfile:
            yaml.dump(ProxyTrayConfig._conf, outfile)

    @staticmethod
    def getLocale():
        if 'locale' in ProxyTrayConfig._conf:
            return ProxyTrayConfig._conf['locale']
        return locale.getlocale()[0][:2]

    @staticmethod
    def getProfiles():
        if 'profiles' in ProxyTrayConfig._conf:
            return ProxyTrayConfig._conf['profiles']
        return []

    @staticmethod
    def getProfile(name):
        profiles = ProxyTrayConfig.getProfiles()
        for i in range(0, len(profiles)):
            if profiles[i]['name'] == name:
                return profiles[i]
        return None

    @staticmethod
    def deleteProfile(name):
        profiles = ProxyTrayConfig.getProfiles()
        for i in range(0, len(profiles)):
            if profiles[i]['name'] == name:
                del profiles[i]
                ProxyTrayConfig._conf['profiles'] = profiles
                ProxyTrayConfig._save()

    @staticmethod
    def saveProfile(profile):
        profiles = ProxyTrayConfig.getProfiles()
        for i in range(0, len(profiles)):
            if profiles[i]['name'] == profile['name']:
                profiles[i] = profile
                ProxyTrayConfig._conf['profiles'] = profiles
                ProxyTrayConfig._save()
                return

        profiles.append(profile)
        ProxyTrayConfig._conf['profiles'] = profiles
        ProxyTrayConfig._save()
