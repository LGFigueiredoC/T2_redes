import pyaudio
#import keyboard
import wave
import asyncio
from threading import Thread

class Recorder ():
    def __init__(self):
        self.channels = 1
        self.frames_p_buffer = 1024
        self.format = pyaudio.paInt16
        self.rate = self.frames_p_buffer*5
        self.done = False
        self.rec = pyaudio.PyAudio()
        self.frames = []

    def start_recording (self):
        stream = self.rec.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.frames_p_buffer
        )

        print("Now Recording.")

        th = Thread(target=self.input_reading)
        th.start()
        while True:
        #for i in range (int(self.rate/self.frames_p_buffer*0.1)):
            chunk = stream.read(self.frames_p_buffer)
            self.frames.append(chunk)
            #print("rodando")
            if self.done:
                break

        stream.stop_stream()
        stream.close()
        self.rec.terminate()
    
    def save_audio (self):
        obj = wave.open("teste.wav", "wb")
        obj.setnchannels(self.channels)
        obj.setsampwidth(self.rec.get_sample_size(self.format))
        obj.setframerate(self.rate)
        obj.writeframes(b"".join(self.frames))
        


    def input_reading (self):
        input("Input any button to stop recording.")
        #print("eu hein")
        self.done = True