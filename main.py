import os
import sys
import platform
import wintheme
import installer
from logger import Logger
from PyQt5 import QtCore, QtGui, QtWidgets


class App:
    def __init__(self) -> None:
        self.encoding = sys.getdefaultencoding()
        self.cwd = os.path.dirname(__file__) or os.getcwd()
        os.chdir(self.cwd)
        self.files_dir = os.path.join(self.cwd, 'files')
        self.exec_fn = os.path.basename(sys.executable)
        self.is_compiled = not self.exec_fn.lower().split('.')[0] == 'python'
        self.spawn_args = [sys.executable] if self.is_compiled else [sys.executable, __file__]
        self.exec_script = self.spawn_args[-1]
        self.theme = wintheme.get_apps_theme()
        if False:
            self.theme = wintheme.THEME_LIGHT  # noqa
        self.logger = Logger(self)
        self.logger.log('GDL Log')
        self.logger.log('CWD', self.cwd)
        self.logger.log('Python', sys.version)
        self.logger.log('Version', sys.version_info)
        self.logger.log('Platform', platform.platform())
        self.logger.log('Theme', wintheme.theme_to_string.get(self.theme))
        self.child_app = None
        self.run_installer()

    def round_point(self, number: float, count: int = 2) -> None:  # noqa
        count_10 = 10 ** count
        return round(number * count_10) / count_10

    def show_error(self, window: any, caption: str, text: str, cb: any) -> QtWidgets.QMessageBox:  # noqa
        box = QtWidgets.QMessageBox(window)
        if self.theme == wintheme.THEME_DARK:
            wintheme.set_window_theme(int(box.winId()), wintheme.THEME_DARK)
        box.setIcon(box.Icon.Critical)
        box.setWindowTitle(caption)
        box.setText(text)
        box.addButton('  OK  ', box.ActionRole).clicked.connect(cb)
        box.show()
        return box

    def show_question(
            self, window: any, caption: str, text: str, yes_cb: any, no_cb: any = None
    ) -> QtWidgets.QMessageBox:  # noqa
        box = QtWidgets.QMessageBox(window)
        if self.theme == wintheme.THEME_DARK:
            wintheme.set_window_theme(int(box.winId()), wintheme.THEME_DARK)
        box.setIcon(box.Icon.Question)
        box.setWindowTitle(caption)
        box.setText(text)
        box.addButton('  Да  ', box.ActionRole).clicked.connect(yes_cb)
        box.addButton('  Нет ', box.ActionRole).clicked.connect(no_cb or box.hide)
        box.show()
        return box

    def run_installer(self) -> None:
        self.child_app = installer.Installer(self)
        sys.exit(self.child_app.exit_code)


if __name__ == '__main__':
    App()
