import random
import json
import numpy as np
import pickle

import nltk
from nltk.stem import WordNetLemmatizer

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.optimizers import SGD

lemmatizer = WordNetLemmatizer()

# treats json file as a dictionary
intents = json.loads(open('./intents.json').read())

words = []
classes = []
documents = []

# create training data
training = []

# disregard punctuation
ignore_chars = ['?', '!', '.', ',']

# compare to patterns defined in dict
for intent in intents['intents']:
    for pattern in intent['patterns']:
        #tokenize to individual words
        word = nltk.word_tokenize(pattern)
        words.extend(word)
        # adds associated words + tag to dictionary
        documents.append((word, intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

# lemmaztize words
words = [lemmatizer.lemmatize(word.lower()) for word in words if word not in ignore_chars]
words = sorted(set(words))
classes = sorted(set(classes))

pickle.dump(words,open('./words.pkl','wb'))
pickle.dump(classes,open('./classes.pkl','wb'))

output = [0] * len(classes)
for doc in documents:
    word_bank = []
    pattern_words = doc[0] #tokenized words belonging to pattern
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
    for word in words:
        word_bank.append(1) if word in pattern_words else word_bank.append(0)

    # output is '1' for current tag
    output_row = list(output)
    output_row[classes.index(doc[1])] = 1
    training.append([word_bank, output_row])

# randomize into np array
random.shuffle(training)
training = np.array(training)

# create lists
train_patt = list(training[:,0])
train_int = list(training[:,1])
print("Checkpoint: Training Data Creation")

# Create 3 layer model - 128->64->num intents to meet softmax
model = Sequential()
# rectified linear unit defined activation
model.add(Dense(128, input_shape=(len(train_patt[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_int[0]), activation='softmax'))

# Compile model using Stochastic gradient descent with Nesterov accelerated gradient
sgd = SGD(learning_rate=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

#fitting and saving the model
hist = model.fit(np.array(train_patt), np.array(train_int), epochs=200, batch_size=5, verbose=1)
model.save('chatbot_model.h5', hist)

print("Success: model created")
