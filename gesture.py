import sys

sys.path.append('.')
import RTIMU
import os.path
import time
import numpy as np


SETTINGS_FILE = "RTIMULib"

print("Using settings file " + SETTINGS_FILE + ".ini")
if not os.path.exists(SETTINGS_FILE + ".ini"):
    print("Settings file does not exist, will be created")

s = RTIMU.Settings(SETTINGS_FILE)
imu = RTIMU.RTIMU(s)

print("IMU Name: " + imu.IMUName())

if (not imu.IMUInit()):
    print("IMU Init Failed")
    sys.exit(1)
else:
    print("IMU Init Succeeded")

# this is a good time to set any fusion parameters

imu.setSlerpPower(0.02)
imu.setGyroEnable(True)
imu.setAccelEnable(True)
imu.setCompassEnable(True)


# Set up recording params
motion_duration = 1.0 # seconds
poll_interval = 0.001 # seconds
if sys.version_info[0] < 3:
    count_down_seconds = int(raw_input('Count down seconds: '))
else:
    count_down_seconds = int(input('Count down seconds: '))
print("Motion duration: {}".format(motion_duration))


# helper functions
def count_down(count_down_secs):
    for i in range(count_down_secs):
        print(count_down_secs-i)
        time.sleep(1)
    print('start')

try:
    while True:
        print('start recording')
        motion_data = []
        count_down(count_down_seconds)
        for i in range(int(motion_duration / poll_interval)):
            if imu.IMURead():
                data = imu.getIMUData()
                data_vec = data['accel'] + data['gyro']
                motion_data.append(data_vec)
            time.sleep(poll_interval)
        print('finished recording')
        motion_data = np.asarray(motion_data).reshape(1, -1)

        # Test recognition
        from helper import preprocessing
        from keras.models import load_model
        import tensorflow as tf

        motions = ['stationary', 'slash']
        model = load_model('model/keras/model_{}motions.h5'.format(len(
            motions)))
        graph = tf.get_default_graph()
        X = preprocessing.regularize_shape(motion_data, 64)
        X = preprocessing.flatten(X)
        with graph.as_default():
            pred = model.predict(X).argmax(axis=-1)[0]
        motion = motions[pred]
        print('prediction: {}'.format(motion))
        input('next')
except KeyboardInterrupt:
    print('exiting')
