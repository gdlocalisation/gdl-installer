import requests
from PyQt5 import QtCore


class Downloader(QtCore.QObject):
    url = ''
    encoding = 'utf-8'
    progress = QtCore.pyqtSignal(int, bytes)
    chunk_size = 1024

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
