# Echo server program
import socket
import numpy as np
import sys

# Set up model
from helper import preprocessing
from keras.models import load_model
import tensorflow as tf

motions = ['nothing', 'unarmed-attack-r3', '2Hand-Axe-Attack1']
model = load_model('model/keras/model_{}motions.h5'.format(len(
    motions)))
graph = tf.get_default_graph()

HOST = ''                # Symbolic name meaning all available interfaces
PORT = 6672          # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
try:
    while True:
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            data = ''.encode()
            while True:
                new_data = conn.recv(4096)
                data += new_data
                if sys.getsizeof(data) >= 3093:
                    break
            motion_data = np.fromstring(data, dtype='float64').reshape(1, -1, 6)
            print("shape: {}".format(motion_data.shape))

            # recognize motion
            with graph.as_default():
                pred = model.predict(motion_data).argmax(axis=-1)[0]
            motion = motions[pred]
            print('prediction: {}'.format(motion))
            conn.send(motion.encode())
except KeyboardInterrupt:
    pass
s.close()
