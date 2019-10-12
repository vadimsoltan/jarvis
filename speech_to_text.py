import speech_recognition as sr
import pyaudio
import wave
import sys
import os
import struct
import math

sys.path.append(os.path.join(os.path.dirname(__file__), './binding/python'))
from porcupine import Porcupine

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
WAVE_OUTPUT_FILENAME = "output.wav"

SHORT_NORMALIZE = (1.0/32768.0)
THRESHOLD = 0.005

audio = pyaudio.PyAudio()

'''
Using Speech Recognition and CMU Sphinx listen
for incoming sound returning the text translation
'''
def speech_to_text(audio):
    recognizer = sr.Recognizer()
    try:
        result = recognizer.recognize_sphinx(audio)
        print("Sphinx thinks you said " + result)
    except sr.UnknownValueError:
        print("Sphinx could not understand audio")
    except sr.RequestError as e:
        print("Sphinx error; {0}".format(e))

    return result
'''
Start speech to text (triggerd by hotword from picovoice)
Keep doing speech to text untill there is a long enough pause
'''
def trigger_conversion():
    library_path = './lib/mac/x86_64/libpv_porcupine.dylib'
    model_file_path ='./lib/common/porcupine_params.pv' 
    keyword_file_paths = ['./keyword_files/mac/alexa_mac.ppn']
    sensitivities = [0.2]
    porcupine = Porcupine(
                library_path=library_path,
                model_file_path=model_file_path,
                keyword_file_paths=keyword_file_paths,
                sensitivities=sensitivities)
    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)

    try :
        print("recording...")
        frames = []
        silent_frames_count = 0
        
        while True:
            # read chunk of audio
            data = stream.read(CHUNK)
            # check if the chunk is silent
            if(is_silent(data)):
                if(silent_frames_count > 5):
                    break
            else:
                # setup object for porcupine and check for keyword
                pcm = struct.unpack_from("h" * porcupine.frame_length, data)
                result = porcupine.process(pcm)
                # if we got the keyword then we add the frames to data
                if result:
                    frames.append(data)
                    print('detected keyword')
        return frames
    except KeyboardInterrupt:
            print('stopping ...')
    finally:
        if porcupine is not None:
            porcupine.delete()

        if stream is not None:
            stream.close()

        if audio is not None:
            audio.terminate()

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
