# Proxy Tray

## Preamble

This small python utility allows Linux GNome users to quickly switch their proxy settings between none, manual or auto.

This is useful if your move your laptop from home to work every day: you will save some precious clicks ! :-)

I made this little utility because :

- I needed to switch between proxy / no proxy very often
- It allowed me to learn Python

So it might not be made in a fully pythonic way of coding. Please be indulgent :-)

## How to install / run

To install and run, just follow these few steps :

- First, you need Python. It's generally installed by default on every Linux distros.
- Then, you will need to install `gir1.2-appindicator3` OR `pystray`.  
  - To install appindicator on Ubuntu/Mint/Debian: `sudo apt-get install gir1.2-appindicator3`.  
    On Fedora: `sudo dnf install libappindicator-gtk3`.  
  - If you choose pystray, just install it from the sources : https://github.com/moses-palmer/pystray.
  For other distributions, just search for any packages containing appindicator.
- Then install pip if not done : `sudo apt install python-pip` in order to execute `pip install pyyaml`
- Then, clone this repo. For example in `~/proxytray`
- Finally, execute this command (modified with your real clone path) : `~/proxytray/proxytray.py` to run it.

If you want it up at startup, run `gnome-session-properties` and configure a new application at startup,
using the previous command line with nohup : `nohup ~/proxytray/proxytray.py > /dev/null 2>&1 &`.

## Internationalization

French and English are handled. Default is English if detected locale is not handled.

## Settings

You can configure ProxyTray with a file in your home directory : `~/.proxytray.yaml`.

For now it allows to configure:

- Language (only via preference file edition).
- Proxy profiles that you can apply to configure you system. Useful if you switch seats between several companies. The profiles are editable via a GUI.

File structure: 

---
locale: [fr]  -- If omitted, falls back to en.
profiles:  -- name, manual and auto are mandatory
- name: ProfileName
  manual: [true|false]  -- If false, leaves manual proxy configuration untouched
  httpHost: http proxy host
  httpPort: http proxy port
  httpsHost: https proxy host
  httpsPort: https proxy port
  ftpHost: ftp proxy host
  ftpPort: ftp proxy port
  socksHost: socks proxy host
  socksPort: socks proxy port
  ignored: non proxy hosts
  auto: [true|false]  -- If false, leaves auto proxy configuration untouched
  autoConfigUrl: url for automatic proxy configuration
---

## Future

This is a very small and quick-made app.
It will evolve to add more features (like adding other OS support, nice icons, more settings, etc ...)
