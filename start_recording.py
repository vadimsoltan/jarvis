import sys
import os
import pyaudio
import struct
from datetime import datetime
import wave
import math
sys.path.append(os.path.join(os.path.dirname(__file__), './binding/python'))
import porcupine
import speech_to_text

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 512
WAVE_OUTPUT_FILENAME = "output.wav"

SHORT_NORMALIZE = (1.0/32768.0)
THRESHOLD = 0.005

audio_stream = None
handle = None
pa = None

def start_recording():
    try:
        library_path = './lib/linux/x86_64/libpv_porcupine.so'
        model_file_path = './lib/common/porcupine_params.pv'
        keyword_file_paths = ['./keyword_files/linux/jarvis_linux.ppn']
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

        print('Listening for keyword jarvis...')
        silent_frames = 0
        while True:
            data = audio_stream.read(handle.frame_length, exception_on_overflow = False)
            pcm = struct.unpack_from("h" * handle.frame_length, data)
            sample_size = pa.get_sample_size(FORMAT)
            result = handle.process(pcm)
            if result:
                executed = False
                frames = []
                print('Keep Speaking...')
                while(silent_frames < 20):
                    frame = audio_stream.read(CHUNK, exception_on_overflow = False)
                    if(is_silent(frame)):
                        silent_frames += 1
                    frames.append(frame)
                    save_wav(sample_size, b''.join(frames))
                print('[%s] detected keyword' % str(datetime.now()))
                if(not(executed)):
                    speech_to_text.speech_to_text()
                    executed = True
            silent_frames = 0

    except KeyboardInterrupt:
        print('stopping ...')
    finally:
        if handle is not None:
            handle.delete()

        if audio_stream is not None:
            audio_stream.close()

        if pa is not None:
            pa.terminate()

'''
Write the recorded audio after the hotword to an outfile
for speech recognition to read from later
'''
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

'''
Check if the amplitude for the current chunk of audio is lower than the threshold
'''
def is_silent(block):
    amplitude = get_rms(block)
    return amplitude < THRESHOLD

if __name__ == '__main__':
    start_recording()