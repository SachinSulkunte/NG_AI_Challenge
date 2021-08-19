from keras.optimizers import RMSprop
from keras.preprocessing.image import ImageDataGenerator
import cv2

from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from sklearn.utils import shuffle

from keras.models import Sequential
from keras.layers import Conv2D, Input, ZeroPadding2D, BatchNormalization, Activation, MaxPooling2D, Flatten, Dense,Dropout
from keras.models import Model, load_model
from keras.callbacks import TensorBoard, ModelCheckpoint

import imutils
import numpy as np

# Extract features from the dataset - Two pairs of Conv and MaxPool layers
# To convert data in 1D - Flatten and Dropout layer
# Classification - Two Dense layers
model =Sequential([
    Conv2D(100, (3,3), activation='relu', input_shape=(150, 150, 3)),
    MaxPooling2D(2,2),

    Conv2D(100, (3,3), activation='relu'),
    MaxPooling2D(2,2),

    Flatten(),
    Dropout(0.5),
    Dense(50, activation='relu'),
    Dense(2, activation='softmax')
])

# adam - adaptive learning rate optimization algorithm
# good replacement for stochastic gradient descent
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['acc'])

# Dataset containing images classified "with_mask" or "without_mask"
# Future program extensibility - add "improper_mask" data to check improper
# mask usage
TRAINING_DIR = "./train"
train_datagen = ImageDataGenerator(rescale=1.0/255,
                                   rotation_range=40,
                                   width_shift_range=0.2,
                                   height_shift_range=0.2,
                                   shear_range=0.2,
                                   zoom_range=0.2,
                                   horizontal_flip=True,
                                   fill_mode='nearest')

# training data coming from directory
train_generator = train_datagen.flow_from_directory(TRAINING_DIR,
                                                    batch_size=10,
                                                    target_size=(150, 150))

# second dataset of test data
VALIDATION_DIR = "./test"
validation_datagen = ImageDataGenerator(rescale=1.0/255)

validation_generator = validation_datagen.flow_from_directory(VALIDATION_DIR,
                                                         batch_size=10,
                                                         target_size=(150, 150))
# checkpoint to save best model after each epoch
checkpoint = ModelCheckpoint('model2-{epoch:03d}.model',monitor='val_loss',
                                    verbose=0,save_best_only=True,mode='auto')

# train 10 epochs
history = model.fit_generator(train_generator,
                              epochs=10,
                              validation_data=validation_generator,
                              callbacks=[checkpoint])
model.save('model-010.h5', history)