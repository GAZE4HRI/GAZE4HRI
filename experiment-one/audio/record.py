from array import array
from struct import pack
from sys import byteorder

import pyaudio
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"


def record(duration):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    print("* recording")
    r = array('h')
    # frames = []
    for i in range(0, int(RATE / CHUNK * duration)):
        snd_data = array('h', stream.read(CHUNK))
        if byteorder == 'big':
            snd_data.byteswap()
        r.extend(snd_data)
        # data = stream.read(CHUNK)
        # frames.append(data)
    print("* done recording")
    stream.stop_stream()
    stream.close()
    p.terminate()
    return normalize(r), p.get_sample_size(FORMAT)

def normalize(snd_data):
    "Average the volume out"
    MAXIMUM = 16384
    times = float(MAXIMUM)/max(abs(i) for i in snd_data)

    r = array('h')
    for i in snd_data:
        r.append(int(i*times))
    return r

def record_to_file(path, frames, sample_size):

    data = pack('<' + ('h'*len(frames)), *frames)

    wf = wave.open(path, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(sample_size)
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()

def make_record(name, time):
    frames, sample_size = record(time)
    record_to_file(name, frames, sample_size)



if __name__ == "__main__":
    make_record(WAVE_OUTPUT_FILENAME, RECORD_SECONDS)
