import os
import sys
import winapi


class Uninstaller:
    def __init__(self, app: any, json_data: dict):
        self.app = app
        self.json_data = json_data
        self.logger = self.app.logger
        self.exit_code = 0
        self.logger.log('Asking about uninstall')
        if not self.ask_processing():
            return
        self.logger.log('Uninstalling GDL')

    def ask_processing(self) -> bool:
        msg_result = winapi.MessageBoxW(
            0,
            'Вы уверены, что хотите удалить GDL?',
            'Удаление GDL',
            0x00000004 | 0x00000020 | 0x00000100
        )
        return msg_result == 6
