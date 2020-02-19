# Proxy Tray

## Preamble

This small python utility allows Linux users to quickly switch their proxy settings between none, manual or auto.

This is useful if your move your laptop from home to work every day: you will save some precious clicks ! :-)

I made this little utility because :

- I needed to switch between proxy / no proxy very often
- It allowed me to learn Python

So it might not be made in a fully pythonic way of coding. Please be indulgent :-)

## How to install / run

To install and run, just follow these few steps :

- First, you need Python. It's generally installed by default on every Linux distros.
- Then, you will need to install `gir1.2-appindicator3`.  
  To install it on Ubuntu/Mint/Debian: `sudo apt-get install gir1.2-appindicator3`  
  On Fedora: `sudo dnf install libappindicator-gtk3`  
  For other distributions, just search for any packages containing appindicator.
- Then install pip if not done : `sudo apt install python-pip` in order to execute `pip install pyyaml`
- Then, clone this repo. For example in `~/proxy-tray`
- Finally, execute this command (modified with your real clone path) : `~/proxy-tray/proxy-tray.py` to run it.

If you want it up at startup, run `gnome-session-properties` and configure a new application at startup,
using the previous command line with nohup : `nohup ~/proxy-tray/proxy-tray.py > /dev/null 2>&1 &`.

## Internationalization

French and English are handled. Default is English if detected locale is not handled.

## Settings

You can configure ProxyTray with a file in your home directory : `~/.proxy-tray.yaml`.

For now it allows to configure:

- Language.

File structure: 

---
locale: [fr]  -- If omitted, falls back to en.
---

## Future

This is a very small and quick-made app.
It will evolve to add more features (like proxy profiles, icons, more settings, etc ...)
