import random
import json
import pickle
import numpy as np

import nltk
from nltk.stem import WordNetLemmatizer

import speech_recognition as sr

from tensorflow.keras.models import load_model
model = load_model('./chatbot_model.h5')

lemmatizer = WordNetLemmatizer()
intents = json.loads(open('./intents.json').read())
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

    ERROR_THRESHOLD = 0.25

    result = [[i, r] for i, r in enumerate(temp_result) if r > ERROR_THRESHOLD]
    result.sort(key=lambda x: x[1], reverse=True)
    return_list = []

    for r in result:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})

    return return_list

def get_response(intents_list, intents_json):
    tag = intents_list[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            if tag == "testing_site":
                find_test()
            elif tag == "masks":
                masks()
            elif tag == "goodbyes":
                # call to the camera detection which pauses until new person detected
            break
    return result

def find_test():
    print("Now searching for test locations: ")
    location_dict = ["CVS", "Walgreens", "Walmart"]
    for s in location_dict:
        print(s)

def masks():
    print("In Maryland, Masks are still required in all outdoor public areas \
    whenever it is not possible to maintain physical distancing. Please ensure \
    that you are wearing your mask whenever within close proximity to others \
    whether indoors or outdoors. If you would like to read some studies regarding \
    the efficacy of masks, here is what I found: ")
    #run web API crawl to grab google search results

def search(name):
    #web crawl to grab google data results for that pharmacy name

def speech():
    r = sr.Recognizer()
    print("Starting: 5 seconds")
    with sr.Microphone() as source:
        # read audio from default microphone
        audio_data = r.record(source, duration=5)
        print("Processing")
        # convert voice to text
        text = r.recognize_google(audio_data)
        return text

print("Bot is live: ")

while True:
    message = speech()
    ints = predict_class(message)
    print(ints)
    res = get_response(ints, intents)
    print(res)
