import sys, getopt

sys.path.append('.')
import RTIMU
import os.path
import time
import math
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

poll_interval = imu.IMUGetPollInterval()
print("Recommended Poll Interval: %dmS\n" % poll_interval)

poll_interval = 0.001 # seconds
sample_seconds = int(raw_input('Sample seconds: '))
count_down_seconds = int(raw_input('Count down seconds: '))
motion_name = raw_input('Motion name: ')
print('Sample seconds: {}'.format(sample_seconds))
print('Polling interval: {}'.format(poll_interval))
print('Count down seconds: {}'.format(count_down_seconds))
file_name = 'data/{}.txt'.format(motion_name)


# helper functions
def count_down(count_down_secs):
    for i in range(count_down_secs):
        print(count_down_secs-i)
        time.sleep(1)
    print('start')


def save_data(data_matrix, file_name):
    try:
        existing_data = np.loadtxt(file_name)
    except IOError:
        existing_data = None
    if existing_data is not None and existing_data.size > 0:
        max_length = max(existing_data.shape[1], data_matrix.shape[1])
        data_matrix = np.pad(data_matrix,
                             ((0, 0), (0, max_length-data_matrix.shape[1])),
                             mode='constant', constant_values=0)
        existing_data = np.pad(existing_data,
                               ((0, 0), (0, max_length-existing_data.shape[1])),
                               mode='constant', constant_values=0)
        data_matrix = np.concatenate((data_matrix, existing_data), axis=0)
    with open(file_name, 'w+') as f:
        np.savetxt(f, data_matrix)

all_motion_data = []
max_length = 0
try:
    sample_n = 1
    while True:
        print('Record #{}'.format(sample_n))
        motion_data = []
        count_down(count_down_seconds)
        for i in range(int(sample_seconds/poll_interval)):
            if imu.IMURead():
                data = imu.getIMUData()
                data_vec = data['accel'] + data['gyro']
                motion_data.append(data_vec)
            time.sleep(poll_interval)
        sample_n += 1
        all_motion_data.append(motion_data)
        print('Finished recording')
        print('Recorded: {}'.format([["{:.5f}".format(x) for x in data] for
                                     data in motion_data]))
        print('length: {}'.format(len(motion_data)))
        max_length = max(max_length, len(motion_data))
        # try:
        #     for i in range(sample_seconds/poll_interval):
        #         if imu.IMURead():
        #             data = imu.getIMUData()
        #             data_vec = data['accel'] + data['gyro']
        #             motion_data.append(data_vec)
        #             time.sleep(poll_interval)
        #             # time.sleep(poll_interval*1.0*10/1000.0)
        # except KeyboardInterrupt:
        #     i += 1
        #     print('Finished recording')
        #     print('Collected {}'.format(motion_data))
        #     print('length: {}'.format(len(motion_data)))
except KeyboardInterrupt:
    print('Saving data')

    for data_entry in all_motion_data:
        num_missing = max_length - len(data_entry)
        for i in range(num_missing):
            data_entry.append((0,)*6)
    data_matrix = np.asarray(all_motion_data)
    print('data matrix shape: {}'.format(data_matrix.shape))
    data_matrix_reshaped = data_matrix.reshape(data_matrix.shape[0], -1)
    print('data matrix new shape (for saving as txt): {}'.format(
        data_matrix_reshaped.shape))
    save_data(data_matrix_reshaped, file_name)
    print('Finished saving')