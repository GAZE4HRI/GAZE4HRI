from Queue import Queue, Empty
import numpy as np

from analyser.AudioSource.audioSource import AudioSource


class AvatarAudioSource(AudioSource):
    def __init__(self):
        self.isProcessingDone = False
        self.queue = Queue()
        # self.file = open("test.pcm","w")

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.isProcessingDone = True
        self.queue.put(None)
        # self.file.close()

    def put_audio(self, data):
        self.queue.put(data)
        # self.file.write(np.fromstring(data, np.dtype('<i2')))

    def generator(self):
        while not self.isProcessingDone:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self.queue.get()
            if chunk is None:
                return
            data = np.fromstring(chunk, np.dtype('<i2'))
            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self.queue.get(block=False)
                    if chunk is None:
                        return
                    data = np.concatenate((data, np.fromstring(chunk, np.dtype('<i2'))), axis=None)
                except Empty:
                    break

            yield data
