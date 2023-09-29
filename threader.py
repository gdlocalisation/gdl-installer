import os
import shutil
import requests
from PyQt5 import QtCore


class Downloader(QtCore.QThread):
    url = ''
    encoding = 'utf-8'
    chunk_size = 4096
    progress = QtCore.pyqtSignal(int, bytes)

    def run(self) -> None:
        try:
            stream = requests.get(self.url, stream=True)
            stream.raise_for_status()
            for chunk in stream.iter_content(self.chunk_size):
                self.progress.emit(0, chunk)
                QtCore.QThread.msleep(5)
            self.progress.emit(1, b'OK!')
        except Exception as err:
            self.progress.emit(2, str(err).encode(self.encoding))


class Unzipper(QtCore.QThread):
    encoding = 'utf-8'
    base_dir = ''
    json_data = {}
    bin_data = b''
    progress = QtCore.pyqtSignal(int, str)

    def run(self) -> None:
        try:
            dst_dir = os.path.join(self.base_dir, 'Resources')
            backup_dir = os.path.join(self.base_dir, 'gdl-backup')
            for data in self.json_data:
                f_size = data['size']
                dst_fn = os.path.join(dst_dir, data['fn'])
                backup_fn = os.path.join(backup_dir, data['fn'])
                if not os.path.isfile(backup_fn) and os.path.isfile(dst_fn):
                    shutil.copy(dst_fn, backup_fn)
                content = self.bin_data[:f_size]
                self.bin_data = self.bin_data[f_size:]
                f = open(dst_fn, 'wb')
                f.write(content)
                f.close()
                QtCore.QThread.msleep(20)
                self.progress.emit(0, str(len(self.bin_data)))
            self.progress.emit(1, 'OK!')
        except Exception as err:
            self.progress.emit(2, str(err))
