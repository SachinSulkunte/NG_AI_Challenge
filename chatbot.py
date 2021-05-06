import random
import json
import pickle
import numpy as np
import time
import sys

import nltk
from nltk.stem import WordNetLemmatizer

import speech_recognition as sr

from tensorflow.keras.models import load_model

# scraping
import requests
import bs4

model = load_model('./chatbot_model.h5')

# set-up
lemmatizer = WordNetLemmatizer()
intents = json.loads(open('./intents.json').read())

# for web scraping
headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
(KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}

# generated from training model
words = pickle.load(open('./words.pkl','rb'))
classes = pickle.load(open('./classes.pkl','rb'))

def define_sentence(phrase):
    # split phrase into array of words
    phrase_words = nltk.word_tokenize(phrase)
    # lemmatize every word
    phrase_words = [lemmatizer.lemmatize(word) for word in phrase_words]
    return phrase_words


# return array indicating word presence in sentence
def list_of_words(sentence):
    sentence_words = define_sentence(sentence)
    word_list = [0] * len(words)
    for current_word in sentence_words:
        for i, word in enumerate(words):
            if word == current_word:
                word_list[i] = 1
    return(np.array(word_list))

def predict_class(sentence):
    low = list_of_words(sentence)
    temp_result = model.predict(np.array([low]))[0]

    # decrease for more precise results assuming plenty of training data
    ERROR_THRESHOLD = 0.25

    result = [[i, r] for i, r in enumerate(temp_result) if r > ERROR_THRESHOLD]
    result.sort(key=lambda x: x[1], reverse=True)
    return_list = []

    # determine probability of the tagged class for the user input
    for r in result:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})

    return return_list

def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            # picks random response from intents.json
            result = random.choice(i['responses'])

            # more specific data if user input is a particular category
            if tag == "testing_site":
                result += find_test()
            elif tag == "masks":
                result += masks()
            elif tag == "covid":
                result += covidInfo()
                result += moreInfo()
            elif tag == "goodbyes":
                print("Program exit")
                quit()
            break
    return result

def find_test():
    str = "Now searching for test locations: \n"

    # url of the website
    text= "covid testing sites near me"
    doc = 'https://google.com/search?q=' + text

    # getting response object
    res = requests.get(doc)

    # Initialize the object
    soup = bs4.BeautifulSoup(res.content, "html.parser")

    # all major headings of search result
    heading_obj=soup.find_all( 'h3' )

    # Iterate through the object and grab headings
    for info in heading_obj:
        str += info.getText()
        str += "\n"

    return str

def masks():
    str = "\nThis is what I was able to find: \n"

    # scraping query
    text= "umd mask policy"
    doc = 'https://google.com/search?q=' + text

    source=requests.get(doc,headers=headers).text

    soup=bs4.BeautifulSoup(source,"html.parser")
    answer=soup.find('span',class_="hgKElc")
    str += answer.text # scraping result

    return str

def covidInfo():
    str = "According to the CDC, the Coronavirus disease (COVID-19) is an infectious disease caused by a newly discovered coronavirus."
    str += " Most people infected with the COVID-19 virus will experience mild to moderate respiratory illness and"
    str += " recover without requiring special treatment.  Older people, and those with underlying medical problems"
    str += " like cardiovascular disease, diabetes, chronic respiratory disease, and cancer are more likely to"
    str += " develop serious illness. \n\n"

    return str

def moreInfo():
    nextStr = "The CDC recommends protecting yourself and others from"
    nextStr += " by washing your hands or using an alcohol based rub "
    nextStr += "frequently and not touching your face. Additionally, social"
    nextStr += " distancing and wearing a mask is recommended to further "
    nextStr += "protect against transmission"

    return nextStr

def speech():
    r = sr.Recognizer()
    # gives 3 seconds to ask question
    # print("Starting: 3 seconds")
    with sr.Microphone() as source:
        # read audio from default microphone (usb mic) - otherwise manually
        # configure microphone on jetson nano with mic = #### (name of mic)
        audio_data = r.record(source, duration=5)
        # print("Processing")

        # convert voice to text
        try:
            text = r.recognize_google(audio_data)
        except (sr.UnknownValueError) as err:
            # print(err)
            text = ""

        return text

print("Bot is live: ")

#Creating tkinter GUI
import tkinter
from tkinter import *

def send():
    cam = sys.stdin.readline()
    while cam == 1:
        ChatBox.insert(END, "Bot: " + "Please put on a mask" + '\n')
        cam = sys.stdin.readline()
        if cam == 0:
            ChatBox.insert(END, "Bot: " + "Thanks!" + '\n')
            break

    msg = speech()
    EntryBox.delete("0.0",END)

    if msg != '':
        ChatBox.config(state=NORMAL)
        ChatBox.insert(END, "You: " + msg + '\n\n')
        ChatBox.config(foreground="#B82505", font=("Verdana", 16 ))

        ints = predict_class(msg)
        res = get_response(ints, intents)

        ChatBox.insert(END, "Bot: " + res + '\n\n')

        ChatBox.config(state=DISABLED)
        ChatBox.yview(END)


root = Tk()
root.title("Neural-19 Chatbot")
root.geometry("400x500")
root.resizable(width=FALSE, height=FALSE)

#Create Chat window
ChatBox = Text(root, bd=0, bg="white", height="8", width="50", font="Arial")

ChatBox.config(state=DISABLED)

#Bind scrollbar to Chat window
scrollbar = Scrollbar(root, command=ChatBox.yview, cursor="heart")
ChatBox['yscrollcommand'] = scrollbar.set

#Create Button to send message
SendButton = Button(root, font=("Verdana",12,'bold'), text="Send", width="12", height=5,
                    bd=0, bg="#f9a602", activebackground="#3c9d9b",fg='#000000',
                    command= send )

#Create the box to enter message
EntryBox = Text(root, bd=0, bg="white",width="29", height="5", font="Arial")
#EntryBox.bind("<Return>", send)


#Place components on the screen
scrollbar.place(x=376,y=6, height=386)
ChatBox.place(x=6,y=6, height=386, width=370)
EntryBox.place(x=128, y=401, height=90, width=265)
SendButton.place(x=6, y=401, height=90)

root.mainloop()


#while True:
#    message = speech()
#    ints = predict_class(message)
#    print(ints)
#    get_response(ints, intents)
