import numpy as np


def decode_single_selection(output, options):
    return options[np.argmax(output[:len(options)])]


def decode_binary_choice(output):
    # True if index 0 is max, False if index 1 is max
    return np.argmax(output[:2]) == 0


def decode_numerical_selection(output, min_val, max_val):
    # One hot encoded - index 0 = 0, index 1 = 1, etc
    return np.argmax(output[min_val:max_val + 1])
