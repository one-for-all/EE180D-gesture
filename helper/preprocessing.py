import numpy as np
import math


def regularize_shape(data, num_samples):
    '''
    return num_samples of entries in data,
    (Note: data are groups of 6dof measurements)
    '''
    data = data.reshape(data.shape[0], -1, 6)
    length = data.shape[1]
    assert(num_samples <= length)
    # step = math.ceil(data.shape[1]//num_samples)
    result = []
    for data_instance in data:
        result_instance = []
        for i in range(num_samples):
            result_instance.append(data_instance[int(math.ceil(i*length/num_samples))])
        result.append(np.asarray(result_instance))
    return np.asarray(result)


def flatten(X):
    return X.reshape(X.shape[0], -1)