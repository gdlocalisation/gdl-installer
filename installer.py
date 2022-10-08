import os
import sys
import time
import requests
import wintheme
from PyQt5 import QtCore, QtGui, QtWidgets
from installer_ui import Ui_MainWindow


class Installer:
    def __init__(self, app: any) -> None:
        self.app = app
        self.logger = self.app.logger
        self.application = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QtWidgets.QMainWindow()
        self.hwnd = int(self.MainWindow.winId())
        if self.app.theme == wintheme.THEME_DARK:
            wintheme.set_window_theme(self.hwnd, wintheme.THEME_DARK)
            self.set_stylesheet('Darkeum')
        else:
            self.set_stylesheet('Ubuntu')
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)
        self.bind_events()
        self.MainWindow.show()
        self.json_data = {}
        self.load_json()
        self.exit_code = self.application.exec_()

    def bind_events(self) -> None:
        self.ui.cancelButton.clicked.connect(lambda: self.app.show_question(
            self.MainWindow, 'Выход из установки', 'Вы уверены, что хотите выйти?', self.MainWindow.close
        ))

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
                self.MainWindow,
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
        self.MainWindow.setStyleSheet(content)
