import os
import sys
import time
import requests
import wintheme
import finder
from PyQt5 import QtCore, QtGui, QtWidgets
from installer_ui import Ui_MainWindow


class Installer:
    def __init__(self, app: any) -> None:
        self.app = app
        self.logger = self.app.logger
        self.application = QtWidgets.QApplication(sys.argv)
        self.window = QtWidgets.QMainWindow()
        self.hwnd = int(self.window.winId())
        if self.app.theme & wintheme.THEME_DARK:
            wintheme.set_window_theme(self.hwnd, wintheme.THEME_DARK)
            self.set_stylesheet('Darkeum')
        else:
            self.set_stylesheet('Ubuntu')
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.window)
        self.after_setup_ui()
        self.window.show()
        self.json_data = {}
        self.load_json()
        self.exit_code = self.application.exec_()

    def after_setup_ui(self) -> None:
        self.window.setWindowFlags(
            QtCore.Qt.WindowType.WindowCloseButtonHint | QtCore.Qt.WindowType.WindowMinimizeButtonHint
        )
        self.ui.tabs.setCurrentIndex(0)
        self.ui.tabs.tabBar().setEnabled(not self.app.is_compiled)
        self.ui.folderpathEdit.setText(finder.SteamFinder(self.app).game_dir)
        self.bind_events()

    def bind_events(self) -> None:
        self.ui.cancelButton.clicked.connect(lambda: self.app.show_question(
            self.window, 'Выход из установки', 'Вы уверены, что хотите выйти?', self.window.close
        ))
        self.ui.goForwardButton.clicked.connect(self.go_forward)
        self.ui.goBackButton.clicked.connect(self.go_back)
        self.ui.folderpathButton.clicked.connect(self.select_install_dir)
        self.ui.folderpathEdit.textChanged.connect(self.check_install_dir)
        self.ui.adafpathEdit.textChanged.connect(self.check_radio_buttons)
        self.ui.loaderType.changeEvent = self.check_radio_buttons
        self.logger.log('Events bound')

    def tab_changed(self) -> None:
        tab_id = self.ui.tabs.currentIndex()
        self.logger.log('Tab id', tab_id)
        if tab_id == 0:
            self.ui.goBackButton.setEnabled(False)
            self.ui.goForwardButton.setEnabled(True)
        elif tab_id == 1:
            self.ui.goBackButton.setEnabled(True)
            self.ui.goForwardButton.setText('Далее')
            self.check_install_dir()
        elif tab_id == 2:
            self.ui.goBackButton.setEnabled(True)
            self.ui.goForwardButton.setText('Установить')
            self.ui.defaultType.setEnabled(not os.path.isdir(os.path.join(self.ui.folderpathEdit.text(), 'adaf-dll')))
            self.ui.modType.setEnabled(os.path.isdir(os.path.join(self.ui.folderpathEdit.text(), 'mods')))
            self.ui.hackType.setEnabled(os.path.isdir(os.path.join(self.ui.folderpathEdit.text(), 'extensions')))
            self.ui.gdhmType.setEnabled(os.path.isdir(os.path.join(self.ui.folderpathEdit.text(), '.GDHM', 'dll')))
            self.check_radio_buttons()

    def go_forward(self) -> None:
        if self.ui.tabs.currentIndex() == 2:
            if self.ui.loaderType.isChecked():
                if not os.path.isdir(os.path.join(self.ui.folderpathEdit.text(), self.ui.adafpathEdit.text())):
                    self.app.show_error(
                        self.window,
                        'Ошибка',
                        'Не удалось найти папку: ' + self.ui.adafpathEdit.text()
                    )
                    return
        self.ui.tabs.setCurrentIndex(self.ui.tabs.currentIndex() + 1)
        self.tab_changed()

    def go_back(self) -> None:
        self.ui.tabs.setCurrentIndex(self.ui.tabs.currentIndex() - 1)
        self.tab_changed()

    def check_radio_buttons(self, *args) -> None:
        self.ui.goForwardButton.setEnabled(True)
        if not self.ui.defaultType.isEnabled() and self.ui.defaultType.isChecked():
            self.ui.defaultType.setChecked(False)
            self.ui.loaderType.setChecked(True)

    def check_install_dir(self) -> None:
        install_dir = self.ui.folderpathEdit.text()
        self.logger.log('Install dir check', install_dir)
        if not os.path.isdir(install_dir):
            self.logger.log('Install dir check failed')
            return self.ui.goForwardButton.setEnabled(False)
        counter = 0
        for fn in os.listdir(install_dir):
            if fn.lower() in ('fmod.dll', 'libcocos2d.dll', 'libextensions.dll', 'sqlite3.dll', 'glew32.dll'):
                counter += 1
        self.logger.log('Install dir check', counter, counter > 3)
        self.ui.goForwardButton.setEnabled(counter > 3)

    def select_install_dir(self) -> None:
        path = QtWidgets.QFileDialog.getExistingDirectory(
            self.window, 'Выбор папки с игрой', self.ui.folderpathEdit.text()
        )
        self.ui.folderpathEdit.setText(path)
        self.check_install_dir()

    def load_json(self) -> None:
        url = 'https://github.com/gdlocalisation/gdl-binaries/releases/latest/download/gdl-binaries.json'
        start_time = time.time()
        try:
            resp = requests.get(url)
            if not resp.status_code == 200:
                raise RuntimeError('Failed to download')
        except Exception as err:
            self.logger.error('Failed to download JSON', err)
            return self.app.show_error(
                self.window,
                'Ошибка!',
                'Не удалось скачать информацию.\nПовторите попытку позже.',
                lambda: sys.exit(1)
            )
        self.json_data = resp.json()
        end_time = time.time()
        self.logger.log(f'JSON downloaded [{self.app.round_point(end_time - start_time, 3)}s]')

    def set_stylesheet(self, style_name: str) -> None:
        f = open(os.path.join(self.app.files_dir, style_name + '.qss'), 'r', encoding=self.app.encoding)
        content = f.read()
        f.close()
        self.window.setStyleSheet(content)
