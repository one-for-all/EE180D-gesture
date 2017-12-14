import sys

sys.path.append('.')
import RTIMU
import os.path
import time
import numpy as np
import socket


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
# if sys.version_info[0] < 3:
#     count_down_seconds = int(raw_input('Count down seconds: '))
# else:
#     count_down_seconds = int(input('Count down seconds: '))
print("Motion duration: {}".format(motion_duration))


# helper functions
def count_down(count_down_secs):
    for i in range(count_down_secs):
        print(count_down_secs-i)
        time.sleep(1)
    print('start')

# Remote Host for Recognition
GAME_HOST = raw_input("Game Host ip: ")
print("Game Host ip is: {}".format(GAME_HOST))
GAME_PORT = 6672

in_gesture_mode = False

try:
    while True:
        if in_gesture_mode:
            motion_data = []
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
            motion_data = preprocessing.regularize_shape(motion_data, 64)
            motion_data = preprocessing.flatten(motion_data)
            size = sys.getsizeof(motion_data.tostring())
            print('size: {}'.format(size))

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((GAME_HOST, GAME_PORT))
            sock.sendall(motion_data.tostring())
            motion = sock.recv(1024)
            sock.close()
            print('detection: {}'.format(motion))

            # Send to communication module
            HOST = ''  # The remote host
            PORT = 6666
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((HOST, PORT))
            sock.sendall('gesture: {}'.format(motion).encode())
            sock.close()

        # raw_input('next')
except KeyboardInterrupt:
    print('exiting')
