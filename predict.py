from __future__ import absolute_import, division, print_function
import os
import tensorflow as tf
from tensorflow import keras
from sys import platform as sys_pf
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg") # This prevents program failing on mac
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

model_dir = os.path.join("./saved_models")

model = keras.models.load_model(os.path.join(model_dir, 'model1'))

model.summary()


