def decode_single_selection(output, options):
    return options[output]


def decode_binary_choice(output):
    return output == 0


def decode_numerical_selection(output):
    return output
