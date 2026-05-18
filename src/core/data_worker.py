import numpy as np
from PySide6.QtCore import QThread, Signal


class DataWorker(QThread):
    """
    A QThread subclass that continuously emits chunks of data from a DataSource.
    It handles the timing to ensure that data is emitted at the correct intervals
    based on the specified sample rate and chunk size.
    """

    data_chunk_signal = Signal(np.ndarray)

    def __init__(self, data_source):
        super().__init__()
        self.data_source = data_source
        self.sample_rate = self.data_source.sampling_rate
        self.chunk_size = self.data_source.chunk_size

        # Calculate the interval in milliseconds between emitting data chunks
        self.interval = (self.chunk_size / self.sample_rate) * 1000  # Convert to milliseconds
        self._is_running = False
        self._is_paused = False

    def run(self):
        self._is_running = True
        self._is_paused = False

        while self._is_running:
            if self._is_paused:
                self.msleep(100)
                continue

            chunk = self.data_source.get_chunk()
            self.data_chunk_signal.emit(chunk)
            self.msleep(int(self.interval))

    def pause(self):
        self._is_paused = True

    def resume(self):
        self._is_paused = False

    def stop(self):
        self._is_running = False
        self._is_paused = False
