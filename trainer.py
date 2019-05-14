from __future__ import absolute_import, division, print_function

import os
import time

import tensorflow as tf
from tensorflow import keras
print("TensorFlow version is ", tf.__version__)

import numpy as np

from sys import platform as sys_pf
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg") # This prevents program failing on mac
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

base_dir = os.path.join("./data")
train_dir = os.path.join(base_dir, "trainingData")
validation_dir = os.path.join(base_dir, "validationData")
save_dir = os.path.join("./saved_models")

model_name = "model1"

# Create image generators with image augmentation

image_size = 160
batch_size = 16 #32

# Rescale all images by 1./255
train_datagen = keras.preprocessing.image.ImageDataGenerator(rescale=1./255)
validation_datagen = keras.preprocessing.image.ImageDataGenerator(rescale=1./255)

# Flow training images
train_data = train_datagen.flow_from_directory(
    train_dir,
    target_size=(image_size, image_size),
    batch_size=batch_size
)
validation_data = validation_datagen.flow_from_directory(
    validation_dir,
    target_size=(image_size, image_size),
    batch_size=batch_size
)

# Print shapes of raw images (this will be changed by the generator)
for image_batch,label_batch in train_data:
    print("Image batch shape: ", image_batch.shape)
    print("Label batch shape: ", label_batch.shape)
    break
    

# Create base model from pre-trained model
IMG_SHAPE = (image_size, image_size, 3)
# base_model = tf.keras.applications.MobileNetV2(
#                 input_shape=IMG_SHAPE,
#                 include_top=False, 
#                 weights='imagenet')

base_model = tf.keras.applications.InceptionV3(
    input_shape=IMG_SHAPE,
    include_top=False
)

# freeze the base model so that it does not get trained.
base_model.trainable = False

# Add new classifier layers
model = tf.keras.Sequential([
    base_model,
    keras.layers.GlobalAveragePooling2D(), # use average pooling to lose less information
    keras.layers.Dense(label_batch.shape[1], activation='softmax') # output in 24 categories
])

# initialize RMSprop optimizer
opt = keras.optimizers.RMSprop(lr=0.0001)

# Compile the model
model.compile(
    loss='categorical_crossentropy',
    optimizer=opt,
    metrics=['accuracy']
)

model.summary()

# Tensorboard for evaluation
tensorboard = keras.callbacks.TensorBoard(log_dir="logs/{}".format(time.time()))

# Training:
epochs = 2
steps_per_epoch = train_data.n # batch size
validation_steps = validation_data.n # batch size

history = model.fit_generator(
    train_data,
    steps_per_epoch = steps_per_epoch,
    epochs=epochs, 
    workers=4,
    validation_data=validation_data, 
    validation_steps=validation_steps,
    callbacks=[tensorboard]
)

# Save model and weights
if not os.path.isdir(save_dir):
    os.makedirs(save_dir)
model_path = os.path.join(save_dir, model_name)
model.save(model_path)
print('Saved trained model at %s ' % model_path)

# Score trained model.
scores = model.evaluate(validation_data, verbose=1)
print('Test loss:', scores[0])
print('Test accuracy:', scores[1])

# Plot the learning curves:
acc = history.history['acc']
val_acc = history.history['val_acc']

loss = history.history['loss']
val_loss = history.history['val_loss']

plt.figure(figsize=(8, 8))
plt.subplot(2, 1, 1)
plt.plot(acc, label='Training Accuracy')
plt.plot(val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.ylabel('Accuracy')
plt.ylim([min(plt.ylim()),1])
plt.title('Training and Validation Accuracy')

plt.subplot(2, 1, 2)
plt.plot(loss, label='Training Loss')
plt.plot(val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.ylabel('Cross Entropy')
plt.ylim([0,max(plt.ylim())])
plt.title('Training and Validation Loss')
plt.show()






