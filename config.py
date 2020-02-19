import locale
import os
import yaml

def _read():
    try:
        with open(os.getenv("HOME") + '/.proxy-tray.yaml') as config_file:
            return yaml.load(config_file)
    except:
        return {}

class ProxyTrayConfig:

    _conf = _read()

    @staticmethod
    def _save():
        with open('~/.proxy-tray.yaml', 'w') as outfile:
            yaml.dump(ProxyTrayConfig._conf, outfile)

    @staticmethod
    def getLocale():
        if 'locale' in ProxyTrayConfig._conf:
            return ProxyTrayConfig._conf['locale']
        return locale.getlocale()[0][:2]
