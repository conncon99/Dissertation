import numpy as np


# TODO: Rework so that

def decode_single_selection(output, options):
    index = np.argmax(output[:len(options)])
    return options[index]


def decode_multiple_selection(output, options, k):
    indices = np.argsort(output[:len(options)])[-k:]
    return [options[i] for i in indices]


def decode_binary_choice(output):
    return output[0] > 0.5


def decode_numerical_selection(output, min_val, max_val):
    # TODO: maybe return highest one hot encoded values from min to max (e.g index 2 is the highest meaning 3 items (start from 0))
    scaled_value = min_val + (max_val - min_val) * output[0]
    return round(scaled_value)
