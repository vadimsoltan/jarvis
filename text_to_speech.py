import speech_recognition as sr
import pyaudio
import wave
import sys

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
WAVE_OUTPUT_FILENAME = "output.wav"

SHORT_NORMALIZE = (1.0/32768.0)
THRESHOLD = 0.015

audio = pyaudio.PyAudio()

'''
Using Speech Recognition and CMU Sphinx listen
for incoming sound returning the text translation
'''
def speech_to_text(audio):
    recognizer = sr.Recognizer();
    try:
        result = r.recognize_sphinx(audio)
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
    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)
    print "recording..."
    frames = []
    silent_frames_count = 0;
    
    while silent_frames_count < 5:
        data = stream.read(CHUNK)
        if(is_silent(data)):
            silent_frames_count += 1
        else:
            frames.append(data)

    print "finished recording"
    speech_to_text(frames)
    stream.stop_stream()
    stream.close()
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
    return amplitude < THRESHHOLD