import os
import sys
import ctypes
import platform
import json
import winapi
import installer
import uninstaller
import logger
from PyQt5 import QtWidgets
if sys.platform == 'win32':
    from ctypes import wintypes


class App:
    def __init__(self) -> None:
        self.encoding = sys.getdefaultencoding()
        self.cwd = os.path.dirname(__file__) or os.getcwd()
        os.chdir(self.cwd)
        self.files_dir = os.path.join(self.cwd, 'files')
        self.temp_dir = os.getenv('temp')
        self.exec_fn = os.path.basename(sys.executable)
        self.is_compiled = not self.exec_fn.lower().split('.')[0] == 'python'
        self.spawn_args = [sys.executable] if self.is_compiled else [sys.executable, __file__]
        self.spawn_str = '"' + '"'.join(self.spawn_args) + '"'
        self.exec_script = self.spawn_args[-1]
        if sys.platform == 'win32':
            try:
                self.ux_theme = ctypes.windll.uxtheme
                try:
                    self.should_use_dark_mode = self.ux_theme.__getitem__(132)
                    self.should_use_dark_mode.argtypes = ()
                    self.should_use_dark_mode.restype = ctypes.c_byte
                    print(self.should_use_dark_mode())
                except AttributeError:
                    self.should_use_dark_mode = None
            except FileNotFoundError:
                self.ux_theme = None
                self.should_use_dark_mode = None
            try:
                self.dwm_api = ctypes.windll.dwmapi
                try:
                    self.dwm_set_attribute = self.dwm_api.DwmSetWindowAttribute
                    self.dwm_set_attribute.argtypes = (
                        wintypes.HWND,
                        wintypes.DWORD,
                        wintypes.LPCVOID,
                        wintypes.DWORD
                    )
                    self.dwm_set_attribute.restype = wintypes.LONG
                except AttributeError:
                    self.dwm_set_attribute = None
            except FileNotFoundError:
                self.dwm_api = None
                self.dwm_set_attribute = None
        else:
            self.ux_theme = None
            self.dwm_api = None
            self.should_use_dark_mode = None
            self.dwm_set_attribute = None
        self.is_dark = False
        self.reg_path = 'Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\GDLocalisation'
        self.logger = logger.Logger(self)
        self.logger.log('GDL Log')
        self.logger.log('CWD', self.cwd)
        self.logger.log('Executable', sys.executable)
        self.logger.log('Python', sys.version)
        self.logger.log('Version', sys.version_info)
        self.logger.log('Encoding', self.encoding)
        self.logger.log('Platform', platform.platform())
        self.logger.log('Files dir', self.files_dir)
        self.logger.log('Temp dir', self.temp_dir)
        self.logger.log('REG Path', self.reg_path)
        self.logger.log('Spawn args', self.spawn_args)
        self.logger.log('Dark Theme', self.is_dark)
        self.child_app = None
        self.main()

    def check_dark_theme(self) -> None:
        if not sys.platform == 'win32':
            return
        if os.getenv('GDL_ENABLE_DARK_THEME'):
            self.is_dark = os.environ['GDL_ENABLE_DARK_THEME'] == '1'
        if not self.ux_theme or not self.should_use_dark_mode:
            return self.check_dark_theme_reg()
        self.is_dark = bool(self.should_use_dark_mode())

    def check_dark_theme_reg(self) -> None:
        if not sys.platform == 'win32':
            return

    def apply_dark(self, hwnd: int) -> None:
        if not hwnd or not self.dwm_api or not self.dwm_set_attribute:
            return
        self.logger.log(f'Dark Theme for {hwnd}', not self.dwm_set_attribute(hwnd, 20, ctypes.c_buffer(b'\0\0\0\1'), 4))
        self.logger.log(f'Dark Theme for {hwnd}', not self.dwm_set_attribute(hwnd, 20, ctypes.c_buffer(b'\0\0\0\1'), 4))

    def read_binary(self, fn: str) -> bytes:
        self.logger.log('Reading file', fn)
        f = open(fn, 'rb')
        result = f.read()
        f.close()
        return result

    def write_binary(self, fn: str, content: bytes) -> int:
        self.logger.log('Writing file', fn)
        f = open(fn, 'wb')
        result = f.write(content)
        f.close()
        return result

    def round_point(self, number: float, count: int = 2) -> None:
        self.logger.log('Rounding point', number, count)
        count_10 = 10 ** count
        return round(number * count_10) / count_10

    def show_error(self, window: any, caption: str, text: str, cb: any = None) -> QtWidgets.QMessageBox:
        self.logger.log('Showing error', caption, text)
        box = QtWidgets.QMessageBox(window)
        self.apply_dark(int(box.winId()))
        box.setIcon(box.Icon.Critical)
        box.setWindowTitle(caption)
        box.setText(text)
        box.addButton('  OK  ', box.ActionRole).clicked.connect(cb or box.hide)
        box.show()
        return box

    def show_question(
            self, window: any, caption: str, text: str, yes_cb: any, no_cb: any = None
    ) -> QtWidgets.QMessageBox:
        self.logger.log('Showing question', caption, text)
        box = QtWidgets.QMessageBox(window)
        self.apply_dark(int(box.winId()))
        box.setIcon(box.Icon.Question)
        box.setWindowTitle(caption)
        box.setText(text)
        box.addButton('  Да  ', box.ActionRole).clicked.connect(yes_cb)
        box.addButton('  Нет ', box.ActionRole).clicked.connect(no_cb or box.hide)
        box.show()
        return box

    def run_installer(self, json_data: dict = None) -> None:
        self.logger.log('Running installer')
        self.child_app = installer.Installer(self, json_data)
        self.logger.destroy()
        sys.exit(self.child_app.exit_code)

    def run_uninstaller(self, json_data: dict = None) -> None:
        self.logger.log('Running uninstaller')
        self.child_app = uninstaller.Uninstaller(self, json_data)
        self.logger.destroy()
        sys.exit(self.child_app.exit_code)

    def main(self) -> None:
        settings_path = os.path.join(os.path.dirname(self.spawn_args[-1]), 'gdl-installer.json')
        self.logger.log('Settings path', settings_path)
        if not os.path.isfile(settings_path):
            return self.run_installer()
        f = open(settings_path, 'r', encoding=self.encoding)
        json_data = json.loads(f.read())
        f.close()
        if sys.argv[-1] == '--modify':
            return self.run_installer(json_data)
        if sys.argv[-1] == '--remove':
            return self.run_uninstaller(json_data)
        self.logger.log('Showing msg about install')
        msg_result = winapi.MessageBoxW(
            0,
            'Да - Обновить GDL.\nНет - Удалить GDL.\nОтмена - Выйти.',
            'Изменение GDL',
            0x00000003 | 0x00000020
        )
        if msg_result == 6:
            return self.run_installer(json_data)
        if msg_result == 7:
            return self.run_uninstaller(json_data)


if __name__ == '__main__':
    App()
