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
