import numpy as np


motion = raw_input('motion to read: ')
file_name = 'data/{}.txt'.format(motion)
data = np.loadtxt(file_name)
data.reshape(data.shape[0], -1, 6)
print(data.shape)