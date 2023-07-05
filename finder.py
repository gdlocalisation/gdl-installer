import os
import winreg


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
            self.logger.log('GD dir is not exists')
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
        f = open(fp, 'r', encoding='utf-8')
        lines = [x.strip() for x in f.read().split('\n')]
        f.close()
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
