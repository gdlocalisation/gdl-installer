import os
import sys
import shutil
import subprocess
import json
import zlib
import winreg
import requests
import time
import finder
import threader
import winapi
from PyQt5 import QtCore, QtWidgets
from installer_ui import Ui_MainWindow


class Installer:
    def __init__(self, app: any, installer_data: dict = None) -> None:
        self.app = app
        self.installer_data = installer_data or {}
        self.logger = self.app.logger
        self.application = QtWidgets.QApplication(sys.argv)
        self.window = QtWidgets.QMainWindow()
        self.hwnd = int(self.window.winId())
        self.app.check_dark_theme()
        self.logger.log('Dark Theme', self.app.is_dark)
        if self.app.is_dark:
            self.app.apply_dark(self.hwnd)
            self.set_stylesheet('Darkeum')
        else:
            self.set_stylesheet('Ubuntu')
        self.install_game_path = ''
        self.install_path = ''
        self.locale = {}
        self.locale_str = self.installer_data.get('locale')
        self.locale_split = [self.locale_str] if self.locale_str else QtCore.QLocale().name().lower().strip().split('_')
        self.logger.log('System Locale', self.locale_split)
        self.binary_data = b''
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.after_setup_ui()
        if 'ru' in self.locale_split:
            self.locale_str = 'ru'
            self.ui.langBox.setCurrentIndex(1)
        else:
            self.locale_str = 'ru'  # TODO
            self.ui.langBox.setCurrentIndex(0)
        self.load_locale(self.locale_str)
        self.window.show()
        self.json_data = {}
        self.exit_code = self.application.exec_()

    def load_locale(self, locale_str: str) -> None:
        self.locale = json.loads(self.app.read_text(os.path.join(self.app.files_dir, f'locale_{locale_str}.json')))
        _translate = QtCore.QCoreApplication.translate
        ld = self.locale['data']
        self.window.setWindowTitle(ld[0])
        self.ui.hellomainLabel.setText(ld[1])
        self.ui.helloLabel1.setText(ld[2])
        self.ui.helloLabel2.setText(ld[3])
        self.ui.langLabel.setText(ld[4])
        self.ui.tabs.setTabText(self.ui.tabs.indexOf(self.ui.helloTab), ld[5])
        self.ui.folderLabel.setText(ld[6])
        self.ui.folderpathButton.setText(ld[7])
        self.ui.regappBox.setText(ld[8])
        self.ui.tabs.setTabText(self.ui.tabs.indexOf(self.ui.folderselectTab), ld[9])
        self.ui.defaultType.setText(ld[10])
        self.ui.loaderType.setText(ld[11])
        self.ui.modType.setText(ld[12])
        self.ui.hackType.setText(ld[13])
        self.ui.typeLabel.setText(ld[14])
        self.ui.gdhmType.setText(ld[15])
        self.ui.tabs.setTabText(self.ui.tabs.indexOf(self.ui.typeselectTab), ld[16])
        self.ui.downloadLabel.setText(ld[17])
        self.ui.unpackLabel.setText(ld[18])
        self.ui.tabs.setTabText(self.ui.tabs.indexOf(self.ui.installTab), ld[19])
        self.ui.ok1Label.setText(ld[20])
        self.ui.ok2Label.setText(ld[21])
        self.ui.githubBox.setText(ld[22])
        self.ui.discordBox.setText(ld[23])
        self.ui.siteBox.setText(ld[24])
        self.ui.tabs.setTabText(self.ui.tabs.indexOf(self.ui.okTab), ld[25])
        self.ui.cancelButton.setText(ld[26])
        self.ui.goForwardButton.setText(ld[27])
        self.ui.goBackButton.setText(ld[28])

    def after_setup_ui(self) -> None:
        self.window.setWindowFlag(QtCore.Qt.WindowType.CustomizeWindowHint, True)
        self.window.setWindowFlags(
            # QtCore.Qt.WindowType.WindowCloseButtonHint |
            QtCore.Qt.WindowType.WindowMinimizeButtonHint
        )
        self.ui.tabs.setCurrentIndex(0)
        self.ui.tabs.tabBar().setEnabled(not self.app.is_compiled)
        if self.installer_data:
            self.ui.folderpathEdit.setText(self.installer_data['game_path'])
            self.ui.regappBox.setChecked(self.installer_data['is_registered'])
            self.ui.folderpathEdit.setEnabled(False)
            self.ui.folderpathButton.setEnabled(False)
            self.ui.regappBox.setEnabled(False)
        else:
            self.ui.folderpathEdit.setText(
                finder.ProcessFinder(self.app).game_dir or finder.SteamFinder(self.app).game_dir
            )
        if not self.app.is_compiled:
            self.ui.folderpathEdit.setText('e:/games/gd_test')
        self.bind_events()

    def bind_events(self) -> None:
        self.ui.cancelButton.clicked.connect(lambda: self.app.show_question(
            self.window, self.locale['data'][29], self.locale['data'][30], self.window.close
        ))
        self.ui.goForwardButton.clicked.connect(self.go_forward)
        self.ui.goBackButton.clicked.connect(self.go_back)
        self.ui.folderpathButton.clicked.connect(self.select_install_dir)
        self.ui.folderpathEdit.textChanged.connect(self.check_install_dir)
        self.ui.adafpathEdit.textChanged.connect(self.check_radio_buttons)
        self.ui.loaderType.changeEvent = self.check_radio_buttons
        self.logger.log('Events bound')

    def run_game_installer_and_exit(self) -> None:
        subprocess.Popen(os.path.join(self.ui.folderpathEdit.text(), 'GDL_Installer.exe'))
        sys.exit(0)

    def tab_changed(self, to_change: int = -1) -> None:
        if to_change >= 0:
            self.ui.tabs.setCurrentIndex(to_change)
            tab_id = to_change
        else:
            tab_id = self.ui.tabs.currentIndex()
        self.logger.log('Tab id', tab_id)
        if tab_id == 0:
            self.ui.goBackButton.setEnabled(False)
            self.ui.goForwardButton.setEnabled(True)
        elif tab_id == 1:
            self.load_json()
            self.ui.goBackButton.setEnabled(True)
            self.ui.goForwardButton.setText('Далее')
            self.check_install_dir()
        elif tab_id == 2:
            if not self.installer_data:
                check_fn = os.path.join(self.ui.folderpathEdit.text(), 'gdl-installer.json')
                if os.path.isfile(check_fn):
                    self.tab_changed(1)
                    self.app.show_question(
                        self.window,
                        self.locale['data'][31],
                        self.locale['data'][32],
                        self.run_game_installer_and_exit
                    )
            self.ui.goBackButton.setEnabled(True)
            self.ui.goForwardButton.setText(self.locale['data'][33])
            default_path = os.path.join(self.ui.folderpathEdit.text(), 'adaf-dll')
            self.ui.defaultType.setEnabled(not (os.path.isdir(default_path) and os.listdir(default_path)))
            self.ui.modType.setEnabled(os.path.isdir(os.path.join(self.ui.folderpathEdit.text(), 'mods')))
            self.ui.hackType.setEnabled(os.path.isdir(os.path.join(self.ui.folderpathEdit.text(), 'extensions')))
            self.ui.gdhmType.setEnabled(os.path.isdir(os.path.join(self.ui.folderpathEdit.text(), '.GDHM', 'dll')))
            self.check_radio_buttons()
            if not self.installer_data:
                return
            self.ui.defaultType.setEnabled(False)
            self.ui.modType.setEnabled(False)
            self.ui.hackType.setEnabled(False)
            self.ui.gdhmType.setEnabled(False)
            self.ui.loaderType.setEnabled(False)
            self.ui.adafpathEdit.setEnabled(False)
        elif tab_id == 3:
            self.ui.goForwardButton.setEnabled(False)
            self.ui.goBackButton.setEnabled(False)
            self.ui.cancelButton.setEnabled(False)
            target_dir = 'adaf-dll'
            if self.ui.modType.isChecked():
                target_dir = 'mods'
            elif self.ui.hackType.isChecked():
                target_dir = 'extensions'
            elif self.ui.gdhmType.isChecked():
                target_dir = os.path.join('.GDHM', 'dll')
            self.install_game_path = self.ui.folderpathEdit.text()
            self.install_path = os.path.join(self.install_game_path, target_dir)
            if self.installer_data:
                self.install_path = self.installer_data['dll_path']
            if not os.path.isdir(self.install_path):
                os.mkdir(self.install_path)
            self.ui.downloadBar.setMaximum(self.json_data['size'])
            self.ui.unpackBar.setMaximum(self.json_data['gdl-assets-size'])
            self.logger.log('Installing to', self.install_path)
            self.window.download_thread = loader = threader.Downloader()
            self.window.binary_data = b''
            loader.url = self.locale['binaries_url']
            loader.encoding = self.app.encoding
            loader.chunk_size = 1024 * 32 if self.app.is_compiled else 1024 * 128
            loader.progress.connect(self.download_progress)
            loader.start()
        elif tab_id == 4:
            self.ui.goForwardButton.setEnabled(True)
            self.ui.goBackButton.setEnabled(False)
            self.ui.cancelButton.setEnabled(False)
            self.ui.goForwardButton.setText(self.locale['data'][34])

    def register_app(self) -> None:
        self.logger.log('Registering app')
        reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        try:
            winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, self.app.reg_path)
        except Exception as err:
            self.logger.error('Failed to create reg key', err)
            return
        try:
            key = winreg.OpenKey(reg, self.app.reg_path, 0, winreg.KEY_WRITE)
        except Exception as err:
            self.logger.error('Failed to open reg key', err)
            return
        winreg.SetValueEx(key, 'DisplayIcon', 0, winreg.REG_SZ, os.path.join(self.install_game_path, 'gdl-icon.ico'))
        winreg.SetValueEx(key, 'DisplayName', 0, winreg.REG_SZ, 'Geometry Dash Localisation')
        winreg.SetValueEx(key, 'DisplayVersion', 0, winreg.REG_SZ, '1.0.0')
        winreg.SetValueEx(key, 'URLInfoAbout', 0, winreg.REG_SZ, 'https://www.gdlocalisation.uk/')
        installer_path = '"' + os.path.join(self.install_game_path, os.path.basename(self.app.exec_script)) + '"'
        if not self.app.is_compiled:
            installer_path = '"' + sys.executable + '" ' + installer_path
        self.logger.log('Installer path', installer_path)
        winreg.SetValueEx(
            key,
            'ModifyPath',
            0,
            winreg.REG_SZ,
            installer_path.replace('/', '\\') + ' --modify'
        )
        winreg.SetValueEx(
            key,
            'UninstallString',
            0,
            winreg.REG_SZ,
            installer_path.replace('/', '\\') + ' --remove'
        )
        winreg.SetValueEx(key, 'Publisher', 0, winreg.REG_SZ, 'The GDL Community')
        winreg.SetValueEx(key, 'NoModify', 0, winreg.REG_DWORD, 0)
        winreg.SetValueEx(key, 'NoRepair', 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)

    def save_settings(self) -> None:
        try:
            shutil.copy(
                self.app.exec_script,
                os.path.join(self.install_game_path, os.path.basename(self.app.exec_script))
            )
        except Exception as err:
            self.logger.error('Failed to copy installer', err)
        shutil.copy(
            os.path.join(self.app.files_dir, 'gdl_icon.ico'),
            os.path.join(self.install_game_path, 'gdl-icon.ico')
        )
        if self.installer_data:
            is_default = self.installer_data['is_default']
            is_registered = self.installer_data['is_registered']
        else:
            is_default = self.ui.defaultType.isChecked()
            is_registered = self.ui.regappBox.isChecked()
        json_result = {
            'locale': self.locale_str,
            'is_default': is_default,
            'is_registered': is_registered,
            'dll_path': self.install_path,
            'game_path': self.install_game_path,
            'json_data': self.json_data
        }
        self.app.write_text(os.path.join(self.install_game_path, 'gdl-installer.json'), json.dumps(json_result))
        self.logger.log('Installer json wrote')
        if self.ui.regappBox.isChecked():
            self.register_app()
        self.tab_changed(4)

    def unzip_gdl(self) -> None:
        self.logger.log('Unzipping gdl into memory')
        files = {}
        for data in self.json_data['gdl-binaries']:
            files[data['fn']] = self.binary_data[:data['size']]
            self.binary_data = self.binary_data[data['size']:]
        self.logger.log('Other size 0 is', len(self.binary_data))
        for fn in ('gdl_patches.json', 'ru_ru.json', 'ru_ru_locations.json', 'minhook.x32.dll'):
            self.app.write_binary(os.path.join(self.install_game_path, fn), files[fn])
        if not self.installer_data and self.ui.defaultType.isChecked():  # Please work
            try:
                self.app.write_binary(os.path.join(self.install_game_path, 'xinput9_1_0.dll'), files['xinput9_1_0.dll'])
            except Exception as err:
                self.logger.error('Failed to write xinput', err)
        dll_path = os.path.join(self.install_path, 'GDLocalisation.dll')
        dll_bak_path = dll_path + '.bak'
        if os.path.isfile(dll_bak_path):
            try:
                os.remove(dll_bak_path)
            except Exception as err:
                self.logger.error('Failed to remove dll backup', err)
        if os.path.isfile(dll_path):
            os.rename(dll_path, dll_bak_path)
        self.app.write_binary(
            dll_path,
            files['GDLocalisation.dll']
        )
        self.logger.log('Binaries are unzipped')
        self.save_settings()

    def unzip_progress(self, status: int, content: str) -> None:
        if status == 0:
            self.ui.unpackBar.setValue(len(self.binary_data) - int(content))
            return
        if status == 1:
            self.binary_data = self.binary_data[self.json_data['gdl-assets-size']:]
            self.logger.log('Data Unzipped')
            self.unzip_gdl()
            return
        self.logger.error('Failed to unzip assets', content)
        self.app.show_error(
            self.window,
            self.locale['data'][31],
            self.locale['data'][35],
            lambda: self.tab_changed(2)
        )

    def download_progress(self, status: int, chunk: bytes) -> None:
        if status == 0:
            self.window.binary_data += chunk  # noqa
            self.ui.downloadBar.setValue(len(self.window.binary_data))  # noqa
            return
        if status == 1:
            self.binary_data = zlib.decompress(self.window.binary_data, 0xF | 0x20) # noqa
            del self.window.binary_data  # noqa
            self.logger.log('Bin downloaded', len(self.binary_data))  # noqa
            backup_path = os.path.join(self.install_game_path, 'gdl-backup')
            if not os.path.isdir(backup_path):
                os.mkdir(backup_path)
                self.logger.log('Backup dir created')
            self.logger.log('Unzipping to', self.install_game_path)
            self.window.unzip_thread = unzipper = threader.Unzipper()
            unzipper.encoding = self.app.encoding
            unzipper.base_dir = self.install_game_path
            unzipper.json_data = self.json_data['gdl-assets']
            unzipper.bin_data = self.binary_data
            unzipper.progress.connect(self.unzip_progress)
            unzipper.start()
            return
        del self.window.binary_data  # noqa
        self.logger.error('Failed to download bin', chunk.decode(self.app.encoding))
        self.app.show_error(
            self.window,
            self.locale['data'][31],
            self.locale['data'][36],
            lambda: self.tab_changed(2)
        )

    def go_forward(self) -> None:
        self.logger.log('Go forward')
        if self.ui.tabs.currentIndex() == 2:
            if self.ui.loaderType.isChecked():
                if not os.path.isdir(os.path.join(self.ui.folderpathEdit.text(), self.ui.adafpathEdit.text())):
                    self.app.show_error(
                        self.window,
                        self.locale['data'][31],
                        self.locale['data'][37] + self.ui.adafpathEdit.text()
                    )
                    return
        if self.ui.tabs.currentIndex() == 4:
            if self.ui.siteBox.isChecked():
                winapi.ShellExecuteW(
                    self.hwnd,
                    None,
                    'https://www.gdlocalisation.uk/',
                    None,
                    None,
                    0x05
                )
            if self.ui.githubBox.isChecked():
                winapi.ShellExecuteW(
                    self.hwnd,
                    None,
                    'https://github.com/gdlocalisation',
                    None,
                    None,
                    0x05
                )
            if self.ui.discordBox.isChecked():
                winapi.ShellExecuteW(
                    self.hwnd,
                    None,
                    'https://discord.gg/CScsGU3N6M',
                    None,
                    None,
                    0x05
                )
            self.window.close()
            return
        self.ui.tabs.setCurrentIndex(self.ui.tabs.currentIndex() + 1)
        self.tab_changed()

    def go_back(self) -> None:
        self.logger.log('Go back')
        self.ui.tabs.setCurrentIndex(self.ui.tabs.currentIndex() - 1)
        self.tab_changed()

    def check_radio_buttons(self, *args: any) -> None:
        self.logger.log('Checking radio buttons', *args)
        self.ui.goForwardButton.setEnabled(True)
        if not self.ui.defaultType.isEnabled() and self.ui.defaultType.isChecked():
            self.ui.defaultType.setChecked(False)
            self.ui.loaderType.setChecked(True)

    def check_install_dir(self) -> None:
        install_dir = self.ui.folderpathEdit.text().strip()
        self.logger.log('Checking install dir', install_dir)
        if not os.path.isdir(install_dir):
            self.logger.log('Install dir check failed')
            return self.ui.goForwardButton.setEnabled(False)
        is_gd = self.app.is_gd_path(install_dir)
        self.logger.log('Install dir check', is_gd)
        self.ui.goForwardButton.setEnabled(is_gd)

    def select_install_dir(self) -> None:
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self.window, self.locale['data'][38], self.ui.folderpathEdit.text()
        )
        self.logger.log('Selected install dir', path)
        self.ui.folderpathEdit.setText(path)
        self.check_install_dir()

    def load_json(self) -> None:
        self.logger.log('Downloading JSON')
        url = self.locale['json_url']
        start_time = time.time()
        try:
            resp = requests.get(url)
            if not resp.status_code == 200:
                raise RuntimeError('Failed to download code 200 != ' + str(resp.status_code))
        except Exception as err:
            self.logger.error('Failed to download JSON', err)
            return self.app.show_error(
                self.window,
                self.locale['data'][31],
                self.locale['data'][36],
                lambda: self.tab_changed(0)
            )
        self.json_data = resp.json()
        end_time = time.time()
        self.logger.log(f'JSON downloaded [{self.app.round_point(end_time - start_time, 3)}s]')

    def set_stylesheet(self, style_name: str) -> None:
        self.logger.log('Setting stylesheet', style_name)
        self.window.setStyleSheet(self.app.read_text(os.path.join(self.app.files_dir, style_name + '.qss')))
