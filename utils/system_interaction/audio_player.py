import soundfile as sf
import sounddevice as sd
import numpy as np
from ..vfs_runtime import extract_temp, vfs_exists

# TODO play mp3 from yt

try:
    from winsound import PlaySound, SND_FILENAME, SND_ASYNC
except ImportError:
    PlaySound = lambda *args:args
    SND_ASYNC = SND_FILENAME = None

from urllib.request import urlretrieve
from os import remove

def wav_to_ogg(filename: str, rmold: bool=False) -> str:
    data, samplerate = sf.read(filename)
    new_filepath = filename.replace(".wav", ".ogg")
    sf.write(new_filepath, data, samplerate, format="OGG", subtype="OPUS")
    if rmold:
        remove(filename)
    return new_filepath

def ogg_to_wav(filename: str, rmold: bool=False) -> str:
    data, sr = sf.read(filename) 
    new_filepath = filename.replace(".ogg", ".wav")
    sf.write(new_filepath, data, sr)
    if rmold:
        remove(filename)
    return new_filepath

class AudioPlayer:
    def __init__(self):
        self.stream: sd.OutputStream|None = None
    
    @staticmethod
    def play_wav(audio: str, separate_thread: bool = True) -> None:
        if vfs_exists(audio):
            tmp_path = extract_temp(audio)
            PlaySound(tmp_path, SND_FILENAME | (SND_ASYNC if separate_thread else 0))
        else:
            PlaySound(audio, SND_FILENAME | (SND_ASYNC if separate_thread else 0))

    def stopallsounds(self):
        if isinstance(sd.OutputStream, self.stream):
            sd.stop()

    def play_random_noise(self, duration, samplerate=44100, volume=0.3):
        samples = int(duration * samplerate)
        noise = np.random.uniform(-1.0, 1.0, samples).astype(np.float32) * volume

        chunk_size = 1024  # number of samples per chunk

        with sd.OutputStream(
            samplerate=samplerate,
            channels=1,
            dtype='float32'
        ) as self.stream:
            for start in range(0, samples, chunk_size):
                end = min(start + chunk_size, samples)
                self.stream.write(noise[start:end])

    def play_mp3(self, path: str, blocking: bool = True):
        data, sr = sf.read(path, dtype='float32', always_2d=True)

        with sd.OutputStream(
            samplerate=sr,
            channels=data.shape[1],
            dtype='float32',
            latency='low'
        ) as self.stream:
            self.stream.write(data)
            if blocking:
                self.stream.stop()

    def play_from_url(self, url: str, filename: str="out.mp3", delete_after_playing: bool=True) -> None:
        filename = url.split("/")[-1]
        extension = filename.split(".")[-1]
        urlretrieve(url, filename=filename)
        if extension == "mp3":
            self.play_mp3(filename)
        elif extension == "wav":
            self.play_wav(filename)
        elif extension == "ogg":
            new_filename = ogg_to_wav(filename, rmold=True)
            self.play_wav(new_filename)

        if delete_after_playing:
            try:
                remove(filename)
            except:...