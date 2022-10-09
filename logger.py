import os
import sys


class Logger:
    def __init__(self, app: any) -> None:
        self.app = app
        self.log_path = os.path.join(self.app.temp_dir, 'gdl-installer.log')
        if not self.app.is_compiled and True:
            self.f = sys.stdout
        else:
            self.f = open(self.log_path, 'w', encoding=self.app.encoding)
        self.is_opened = True

    def join_data(self, *data) -> str:  # noqa
        return ' '.join([str(_x) for _x in data]).replace('\n', '\n       ')

    def log(self, *data) -> None:
        self.f.write('[LOG]: ' + self.join_data(*data) + '\n')

    def error(self, *data) -> None:
        self.f.write('[ERR]: ' + self.join_data(*data) + '\n')

    def destroy(self) -> None:
        if not self.is_opened:
            return
        self.is_opened = False
        self.f.close()
