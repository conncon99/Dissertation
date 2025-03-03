import builtins

RESET = "\033[0m"
current_colour = ""

original_print = builtins.print

with open("print.log", "w") as f:
    pass

log_file = open("print.log", "a")


def colored_print(*args, **kwargs):
    # Prepend the colour code to all arguments
    colored_args = [f"{current_colour}{arg}{RESET}" for arg in args]
    original_print(*colored_args, **kwargs)

    message = " ".join(map(str, args))
    log_file.write(message + "\n")
    log_file.flush()


def set_print_colour(colour):
    global current_colour
    current_colour = colour
