import ctypes
import os
import winreg
import winapi
from ctypes import wintypes


class ProcessFinder:
    def __init__(self, app: any) -> None:
        self.app = app
        self.logger = app.logger
        self.game_dir = ''
        self.main()

    def check_for_gd(self, pid: int) -> bool:
        if not pid:
            return False
        proc = winapi.OpenProcess(0x0400 | 0x0010, False, pid)  # Query Info, Read VM
        if not proc:
            return False
        is_gd_dir = False
        try:
            buf = (wintypes.WCHAR * 4096)()
            if winapi.GetModuleFileNameExW(proc, None, buf, 4095):
                proc_dir = os.path.dirname(buf.value)
                if not os.path.isdir(proc_dir):
                    self.logger.error('Inaccessible folder for process with pid', pid)
                elif self.app.is_gd_path(proc_dir):
                    is_gd_dir = True
                    self.game_dir = proc_dir
                    self.logger.log('Process dir found', self.game_dir)
            else:
                self.logger.error('Failed to get process path with pid', pid)
        except Exception as _err:
            self.logger.error(f'Failed to get path for process with pid {pid} ({_err})')
        if not winapi.CloseHandle or not winapi.CloseHandle(proc):
            self.logger.error('Failed to close process handle')
        return is_gd_dir

    def main(self) -> None:
        if not winapi.CreateToolhelp32Snapshot or not winapi.Process32FirstW or not winapi.Process32NextW or\
                not winapi.OpenProcess or not winapi.GetModuleFileNameExW:
            self.logger.log('Failed to import process enumeration functions')
            return
        snap = winapi.CreateToolhelp32Snapshot(0x00000002, 0)  # For Process
        if not snap or snap == -1:
            self.logger.error('Failed to create process snapshot')
            return
        pe32 = winapi.PROCESSENTRY32W()
        pe32.dwSize = ctypes.sizeof(pe32)
        if winapi.Process32FirstW(snap, pe32):
            if not self.check_for_gd(pe32.th32ProcessID):
                while winapi.Process32NextW(snap, pe32):
                    if self.check_for_gd(pe32.th32ProcessID):
                        break
                if not winapi.GetLastError() == 18:  # No More Files
                    self.logger.error('Failed to enumerate process')
        elif not winapi.GetLastError() == 18:
            self.logger.error('Failed to enumerate the first process')
        if not self.game_dir:
            self.logger.log('Failed to find geometry dash process')
        if not winapi.CloseHandle or not winapi.CloseHandle(snap):
            self.logger.error('Failed to close process snapshot')


class SteamFinder:
    def __init__(self, app: any) -> None:
        self.app = app
        self.logger = self.app.logger
        self.game_id = 322170
        self.game_dir = ''
        self.main()
    
    def main(self) -> int:
        steam_path = self.search_steam(r'SOFTWARE\Wow6432Node\Valve\Steam') or\
                     self.search_steam(r'SOFTWARE\Valve\Steam')
        if not steam_path:
            self.logger.log('Steam not found')
            return 1
        config_path = os.path.join(steam_path, 'config', 'libraryfolders.vdf')
        if not os.path.isfile(config_path):
            self.logger.log(f'Could not find config at "{config_path}"')
            return 1
        library_dir = self.parse_folders(config_path)
        game_dir = os.path.join(library_dir, 'steamapps', 'common', 'Geometry Dash')
        if not os.path.isdir(game_dir):
            self.logger.log('GD dir does not exist')
            return 1
        self.game_dir = game_dir

    def search_steam(self, reg_path: str) -> str:  # noqa
        try:
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ)
        except FileNotFoundError:
            return ''
        try:
            value = winreg.QueryValueEx(reg_key, 'InstallPath')[0]
        except (FileNotFoundError, TypeError, IndexError, AttributeError):
            value = ''
        winreg.CloseKey(reg_key)
        return value.strip()

    def parse_folders(self, fp: str) -> str:
        lines = [x.strip() for x in self.app.read_text(fp).split('\n')]
        brackets_level = 0
        last_path = ''
        is_apps = False
        for line in lines:
            if line == '{':
                brackets_level += 1
                continue
            elif line == '}':
                brackets_level -= 1
                continue
            if brackets_level == 2:
                is_apps = is_apps and len(line) == 0
                if line.startswith('"path"'):
                    last_path = line.split('"')[-2]
                    continue
                if line.startswith('"apps"'):
                    is_apps = True
                    continue
                continue
            if brackets_level == 3 and is_apps:
                if line.startswith(f'"{self.game_id}"'):
                    return last_path
                continue
        return ''
