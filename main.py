import speech_to_text
import resolve_command
import executor


if __name__=='__main__':
    data = speech_to_text.trigger_conversion()
    print(data)