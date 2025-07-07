import pyttsx3
import speech_recognition as sr


from datetime import datetime
from decouple import config
from random import choice
from conv import random_text

engine = pyttsx3.init('sapi5')  # sapi5 is microsoft speech ap for speech recogntion
engine.setProperty('volume',1.0)
engine.setProperty('rate',210)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

USER = config('USER')
HOSTNAME = config('BOT')


def speak(text):
    engine.say(text)
    engine.runAndWait()

def greet_me():
    hour = datetime.now().hour
    if (hour>=6) and (hour < 12):
        speak(f"Good Morning {USER}")
    elif (hour >= 12) and (hour <= 16 ):
        speak(f"Good Afternoon {USER}")
    elif (hour >= 16) and (hour < 24):
        speak(f"Good evening {USER}")
    speak(f" I am {HOSTNAME}, your personal assistant. How may I assist you? {USER}")

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening......")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        queri = r.recognize_google(audio, language= "en-in")
        print(queri)
        if not 'stop' in queri or 'exit'  not in queri:
            speak(choice(random_text))
        else:
            hour = datetime.now().hour
            if hour>= 21 or hour <= 4:
                speak("It's been midnight Shaivi, i hope you had your coffee today? ")
            else:
                speak(" have a good day baby!")
                exit()
    except Exception:
        speak("Sorry baby, i couldn't understand. Can you please repeat that?")
        queri = " None"
    return queri


if __name__ == '__main__':
     greet_me()
     while True:
         query = take_command().lower()
         if "how are you Jarvis" in query:
            speak(" I wasen't , but now i am absolutely amazing, just missing you")
