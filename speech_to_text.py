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
