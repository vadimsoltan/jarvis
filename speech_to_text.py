import speech_recognition as sr
AUDIO_FILE = 'output.wav'

'''
Using Speech Recognition and CMU Sphinx listen
for incoming sound returning the text translation
'''
def speech_to_text():
    recognizer = sr.Recognizer()
    result = ''
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = recognizer.record(source)  # read the entire audio file
    try:
        result = recognizer.recognize_sphinx(audio)
        print("Sphinx thinks you said " + result)
    except sr.UnknownValueError:
        print("Sphinx could not understand audio")
    except sr.RequestError as e:
        print("Sphinx error; {0}".format(e))

    return result
