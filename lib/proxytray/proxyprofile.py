import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import os
from lib.proxytray.proxytrayconfig import ProxyTrayConfig

class ProfileEditor(Gtk.Window):

    def __init__(self, config):
        self.config = config
        self._initUI()
        self.onApplyCommand = None
        self.onSaveCommand = None
        self.onDeleteCommand = None

    def updateFromProfile(self, profileToEdit):
        self.creation = (profileToEdit == None)
        self.profile = {'manual': True, 'auto': True} if self.creation else profileToEdit
        self._updateUI()

    def _initUI(self):
        Gtk.Window.__init__(self)
        self.set_icon_from_file(os.path.abspath(self.config.getPath() + '/icons/proxytray.png'))

        self.set_border_width(10)

        mainbox = Gtk.VBox(spacing=6)
        self.add(mainbox)

        btnbox = Gtk.HBox(spacing=6)

        self.fromCurrentButton = Gtk.Button(label=_("From Current Configuration"))
        self.fromCurrentButton.connect("clicked", self._fromCurrent)
        btnbox.pack_start(self.fromCurrentButton, False, False, 0)

        self.saveButton = Gtk.Button(label=_("Save"))
        self.saveButton.connect("clicked", self._save)
        btnbox.pack_end(self.saveButton, False, False, 0)

        self.applyButton = Gtk.Button(label=_("Save and Apply"))
        self.applyButton.connect("clicked", self._apply)
        btnbox.pack_end(self.applyButton, False, False, 0)

        self.cancelButton = Gtk.Button(label=_("Cancel"))
        self.cancelButton.connect("clicked", self._cancel)
        btnbox.pack_end(self.cancelButton, False, False, 0)

        self.deleteButton = Gtk.Button(label=_("Delete"))
        self.deleteButton.connect("clicked", self._delete)
        btnbox.pack_end(self.deleteButton, False, False, 0)

        mainbox.pack_end(btnbox, False, False, 0)

        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(8)
        mainbox.pack_start(self.grid, False, False, 0)

        self.labels = (Gtk.Label(_("Name: ")),
            Gtk.Label(_("Mode: ")),
            Gtk.Label(_("Leave Unchanged: ")),
            Gtk.Label(_("HTTP Proxy: ")),
            Gtk.Label(_("HTTPS Proxy: ")),
            Gtk.Label(_("FTP Proxy: ")),
            Gtk.Label(_("SOCKS Proxy: ")),
            Gtk.Label(_("Ignored Hosts: ")),
            Gtk.Label(_("Automatic Config URL: ")))

        for label in self.labels:
            label.set_size_request(300, -1)
            label.set_alignment(1, 0.5)
        
        self.grid.attach(self.labels[0], 0, 0, 1, 1)
        self.grid.attach(self.labels[1], 0, 1, 1, 1)

        self.nameText = Gtk.Entry()
        self.nameText.set_size_request(500 , -1)
        self.nameText.connect("changed", self._changeName)
        self.grid.attach(self.nameText, 1, 0, 1, 1)

        modeBox = Gtk.HBox(spacing=6)

        self.mode = 'manual'

        self.modeManualButton = Gtk.RadioButton.new_with_label_from_widget(None, "Manual")
        self.modeManualButton.connect("toggled", self._changeMode, "manual")
        modeBox.pack_start(self.modeManualButton, False, False, 0)

        self.modeAutoButton = Gtk.RadioButton.new_with_label_from_widget(self.modeManualButton, "Automatic")
        self.modeAutoButton.connect("toggled", self._changeMode, "auto")
        modeBox.pack_start(self.modeAutoButton, False, False, 0)

        self.leaveUnchangedManualButton = Gtk.CheckButton()
        self.leaveUnchangedManualButton.connect("toggled", self._updateMode)
        self.leaveUnchangedAutoButton = Gtk.CheckButton()
        self.leaveUnchangedAutoButton.connect("toggled", self._updateMode)

        self.httpHost = ProfileHost(self, "http")
        self.httpsHost = ProfileHost(self, "https")
        self.ftpHost = ProfileHost(self, "ftp")
        self.socksHost = ProfileHost(self, "socks")
        self.ignoredText = Gtk.Entry()
        self.autoConfigUrlText = Gtk.Entry()
        self.autoConfigUrlText.set_size_request(500 , -1)

        self.grid.attach(modeBox, 1, 1, 1, 1)

    def _updateUI(self, forceModeManual = True):
        self.set_title(_("New Profile") if self.creation else _("Edit Profile"))
        self.deleteButton.set_sensitive(not self.creation)
        if not self.creation:
            self.nameText.set_text(self._getProfileValue('name'))
        self.leaveUnchangedManualButton.set_active(not self._getProfileValue('manual'))
        self.leaveUnchangedAutoButton.set_active(not self._getProfileValue('auto'))
        self.httpHost.updateFromProfile()
        self.httpsHost.updateFromProfile()
        self.ftpHost.updateFromProfile()
        self.socksHost.updateFromProfile()
        self.ignoredText.set_text(self._getProfileValue('ignored'))
        self.autoConfigUrlText.set_text(self._getProfileValue('autoConfigUrl'))
        self._updateButtons()
        if forceModeManual:
            self._showModeManual()

    def onApplyCallback(self, command):
        self.onApplyCommand = command

    def onSaveCallback(self, command):
        self.onSaveCommand = command

    def onDeleteCallback(self, command):
        self.onDeleteCommand = command

    def _updateButtons(self):
        self.applyButton.set_sensitive(not not self.nameText.get_text())
        self.saveButton.set_sensitive(not not self.nameText.get_text())
    
    def _getProfileValue(self, k, d = ''):
        val = self.profile.get(k)
        return val if val != None else d
    
    def _updateProfile(self):
        self.profile = {}
        self.profile['name'] = self.nameText.get_text()

        self.profile['manual'] = not self.leaveUnchangedManualButton.get_active()
        if self.profile['manual']:
            if self.httpHost.getHost():
                self.profile['httpHost'] = self.httpHost.getHost()
                self.profile['httpPort'] = int(self.httpHost.getPort())

            if self.httpsHost.getHost():
                self.profile['httpsHost'] = self.httpsHost.getHost()
                self.profile['httpsPort'] = int(self.httpsHost.getPort())

            if self.ftpHost.getHost():
                self.profile['ftpHost'] = self.ftpHost.getHost()
                self.profile['ftpPort'] = int(self.ftpHost.getPort())

            if self.socksHost.getHost():
                self.profile['socksHost'] = self.socksHost.getHost()
                self.profile['socksPort'] = int(self.socksHost.getPort())

            if self.ignoredText.get_text():
                self.profile['ignored'] = self.ignoredText.get_text()
        
        self.profile['auto'] = not self.leaveUnchangedAutoButton.get_active()
        if self.profile['auto']:
            if self.autoConfigUrlText.get_text():
                self.profile['autoConfigUrl'] = self.autoConfigUrlText.get_text()

    def _fromCurrent(self, _):
        self.profile = self.config.generateProfile(self._getProfileValue('name'))
        self._updateUI(False)

    def _cancel(self, _):
        self.hide()

    def _delete(self, _):
        self._save(_)
        ProxyTrayConfig.deleteProfile(self.profile['name'])
        if self.onDeleteCommand:
            self.onDeleteCommand(self.profile['name'])
        self.hide()

    def _apply(self, _):
        self._save(_)
        self.config.applyProfile(self.profile['name'])
        if self.onApplyCommand:
            self.onApplyCommand(self.profile['name'])
        self.hide()

    def _save(self, _):
        self._updateProfile()
        ProxyTrayConfig.saveProfile(self.profile)
        if self.onSaveCommand:
            self.onSaveCommand(self.profile['name'])
        self.hide()

    def _changeName(self, _):
        self._updateButtons()

    def _changeMode(self, _, mode):
        if _.get_active():
            self.mode = mode
            self._updateMode(_)

    def _updateMode(self, _):
            if self.mode == "manual":
                self._showModeManual()
            if self.mode == "auto":
                self._showModeAuto()

    def _hideAllModes(self):
        for idx in range(1, 7):
            self.grid.remove_row(2)

    def _showModeManual(self):
        self._hideAllModes()
        self.grid.attach(self.labels[2], 0, 2, 1, 1)
        self.grid.attach(self.leaveUnchangedManualButton, 1, 2, 1, 1)

        if not self.leaveUnchangedManualButton.get_active():
            self.grid.attach(self.labels[3], 0, 3, 1, 1)
            self.grid.attach(self.labels[4], 0, 4, 1, 1)
            self.grid.attach(self.labels[5], 0, 5, 1, 1)
            self.grid.attach(self.labels[6], 0, 6, 1, 1)
            self.grid.attach(self.labels[7], 0, 7, 1, 1)

            self.grid.attach(self.httpHost.component(), 1, 3, 1, 1)
            self.grid.attach(self.httpsHost.component(), 1, 4, 1, 1)
            self.grid.attach(self.ftpHost.component(), 1, 5, 1, 1)
            self.grid.attach(self.socksHost.component(), 1, 6, 1, 1)
            self.grid.attach(self.ignoredText, 1, 7, 1, 1)

        self.show_all()

    def _showModeAuto(self):
        self._hideAllModes()
        self.grid.attach(self.labels[2], 0, 2, 1, 1)
        self.grid.attach(self.leaveUnchangedAutoButton, 1, 2, 1, 1)

        if not self.leaveUnchangedAutoButton.get_active():
            self.grid.attach(self.labels[8], 0, 3, 1, 1)
            self.grid.attach(self.autoConfigUrlText, 1, 3, 1, 1)

        self.show_all()


class ProfileHost(Gtk.Window):

    def __init__(self, profileEditor, name):
        self.profileEditor = profileEditor
        self.name = name
        self.hostText = Gtk.Entry()
        self.hostText.set_size_request(300, -1)
        self.hostText.connect("changed", self._hostChanged)
        self.portText = Gtk.SpinButton()
        self.portText.set_size_request(50 , -1)
        self.portText.set_range(1, 65535)
        self.portText.set_increments(1, 100)
        self.portText.set_update_policy(Gtk.SpinButtonUpdatePolicy.IF_VALID)
        self.mainbox = Gtk.HBox(spacing=6)
        self.mainbox = Gtk.HBox(spacing=6)
        self.mainbox.pack_start(self.hostText, True, True, 0)
        self.mainbox.pack_start(self.portText, False, False, 0)
    
    def updateFromProfile(self):
        self.hostText.set_text(self.profileEditor._getProfileValue(self.name + 'Host'))
        port = int(self.profileEditor._getProfileValue(self.name + 'Port', '1'))
        if port < 1:
            port = 1
        self.portText.set_text(str(port))
        self._hostChanged(None)

    def component(self):
        return self.mainbox
    
    def getHost(self):
        return self.hostText.get_text()
    
    def getPort(self):
        return self.portText.get_text()
    
    def setHost(self, host):
        self.hostText.set_text(host)
        self._hostChanged(None)
    
    def setPort(self, port):
        self.portText.set_text(port)
    
    def _hostChanged(self, _):
        if self.getHost():
            self.portText.set_sensitive(True)
            if not self.getPort():
                self.setPort('1')
        else:
            self.portText.set_sensitive(False)
            self.setPort('')
