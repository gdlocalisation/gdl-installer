import os
import json
import subprocess
import shutil
import winreg
import winapi


class Uninstaller:
    def __init__(self, app: any, json_data: dict):
        self.app = app
        self.json_data = json_data
        self.logger = self.app.logger
        self.exit_code = 0
        if not self.ask_processing():
            return
        self.logger.log('Uninstalling GDL')
        self.remove_assets()

    def remove_assets(self) -> None:
        self.logger.log('Removing assets')
        for data in self.json_data['json_data']['gdl-assets']:
            fn = data['fn']
            backup_fp = os.path.join(self.json_data['game_path'], 'gdl-backup', fn)
            res_fp = os.path.join(self.json_data['game_path'], 'Resources', fn)
            self.logger.log('Processing', fn)
            if fn.lower().startswith('gdl'):
                if os.path.isfile(res_fp):
                    os.remove(res_fp)
                if os.path.isfile(backup_fp):
                    os.remove(backup_fp)
                    continue
                continue
            if not os.path.isfile(backup_fp):
                continue
            if os.path.isfile(res_fp):
                os.remove(res_fp)
            os.rename(backup_fp, res_fp)
        shutil.rmtree(os.path.join(self.json_data['game_path'], 'gdl-backup'))
        dll_fp = os.path.join(self.json_data['dll_path'], 'GDLocalisation.dll')
        files_to_remove = [
            'gdl_patches.json', 'gdl-icon.ico', 'gdl-installer.json',
            'ru_ru.json', 'ru_ru_locations.json', 'minhook.x32.dll'
        ]
        self.logger.log('Deleting other shit')
        if os.path.isfile(dll_fp):
            os.remove(dll_fp)
        if os.path.isfile(dll_fp + '.bak'):
            os.remove(dll_fp + '.bak')
        if self.json_data['is_default']:
            files_to_remove.append('xinput9_1_0.dll')
            shutil.rmtree(self.json_data['dll_path'])
        if self.json_data['is_registered']:
            self.logger.log('Cleaning reg')
            try:
                winreg.DeleteKeyEx(winreg.HKEY_LOCAL_MACHINE, self.app.reg_path)
            except Exception as err:
                self.logger.error('Failed to clean reg', err)
        for fn in files_to_remove:
            fp = os.path.join(self.json_data['game_path'], fn)
            if not os.path.isfile(fp):
                continue
            os.remove(fp)
        self.finish_uninstall()

    def finish_uninstall(self) -> None:
        self.logger.log('Uninstallation done!')
        winapi.MessageBoxW(
            0,
            self.app.locale['data'][39],
            self.app.locale['data'][40],
            0x00000040
        )
        self.delete_installer()

    def delete_installer(self) -> None:
        self.logger.log('Deleting self after 5 seconds')
        subprocess.Popen(f'sleep 5 && del "{self.app.exec_script}"', shell=True)
        self.exit_code = 0

    def ask_processing(self) -> bool:
        self.logger.log('Asking about uninstall')
        msg_result = winapi.MessageBoxW(
            0,
            self.app.locale['data'][41],
            self.app.locale['data'][40],
            0x00000004 | 0x00000020 | 0x00000100
        )
        self.logger.log('User selected', msg_result)
        return msg_result == 6
