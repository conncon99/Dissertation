import numpy as np


def decode_single_selection(output, options):
    index = np.argmax(output[:len(options)])
    return options[index]


def two_step_selection(output):
    # TODO: Useful for things like _handle_movement, where the from and two clearings are picked first and then the number of units - maybe should split those up
    pass


def decode_multiple_selection(output, options, k):
    indices = np.argsort(output[:len(options)])[-k:]
    return [options[i] for i in indices]


def decode_binary_choice(output):
    return output[0] > 0.5


def decode_numerical_selection(output, min_val, max_val):
    scaled_value = min_val + (max_val - min_val) * output[0]
    return round(scaled_value)
