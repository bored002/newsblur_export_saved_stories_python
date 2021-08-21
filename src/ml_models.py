import tensorflow as tf
import pathlib
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class machine_learning(object):
    '''
    Experimenting with machine learnign (tensor flow)
    '''


    def base_case(self,data_frame):
        np.set_printoptions(precision=4)
        tf_convered_df = tf.convert_to_tensor(data_frame)
        # normalizer = tf.keras.layers.Normalization(axis=-1)
        # normalizer.adapt(data_frame)