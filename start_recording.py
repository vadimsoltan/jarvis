import sys
import os
import pyaudio
import struct
from datetime import datetime
import speech_recognition as sr
import wave
import math


sys.path.append(os.path.join(os.path.dirname(__file__), './binding/python'))

import porcupine

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
WAVE_OUTPUT_FILENAME = "output.wav"

SHORT_NORMALIZE = (1.0/32768.0)
THRESHOLD = 0.005


audio_stream = None
handle = None
pa = None


def start_recording():
    try:
        library_path = './lib/mac/x86_64/libpv_porcupine.dylib'
        model_file_path = './lib/common/porcupine_params.pv'
        keyword_file_paths = ['./keyword_files/mac/alexa_mac.ppn']
        sensitivities = [0.2]
        handle = porcupine.Porcupine(library_path,
                                    model_file_path,
                                    keyword_file_paths=keyword_file_paths,
                                    sensitivities=sensitivities)

        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
                rate=handle.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=handle.frame_length)

        print('Listening for keyword alexa...')
        silent_frames = 0
        while True:
            sample_size = pa.get_sample_size(FORMAT)
            data = audio_stream.read(handle.frame_length)
            pcm = struct.unpack_from("h" * handle.frame_length, data)
            result = handle.process(pcm)
            if result:
                while(silent_frames < 5):
                    frame = audio_stream.read(CHUNK)
                    if(is_silent(frame)):
                        silent_frames += 1
                    save_wav(sample_size, frame)
                print('[%s] detected keyword' % str(datetime.now()))

    except KeyboardInterrupt:
        print('stopping ...')
    finally:
        if handle is not None:
            handle.delete()

        if audio_stream is not None:
            audio_stream.close()

        if pa is not None:
            pa.terminate()

def save_wav(audio, frames):
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio)
    waveFile.setframerate(RATE)
    waveFile.writeframes(frames)
    waveFile.close()

'''
RMS amplitude is defined as the square root of the 
mean over time of the square of the amplitude.
so we need to convert this string of bytes into 
a string of 16-bit samples...

we will get one short out for each 
two chars in the string.
'''
def get_rms(block):
    count = len(block)/2
    format = "%dh"%(count)
    shorts = struct.unpack(format, block)

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
        # sample is a signed short in +/- 32768. 
        # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n

    return math.sqrt( sum_squares / count )

def is_silent(block):
    amplitude = get_rms(block)
    print(amplitude)
    return amplitude < THRESHOLD


if __name__ == '__main__':
    start_recording()