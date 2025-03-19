import builtins

VERBOSE = False
LOG = False


RESET = "\033[0m"
current_colour = ""

original_print = builtins.print

if LOG:
    with open("print.log", "w") as f:
        pass
    log_file = open("print.log", "a")


def colored_print(*args, **kwargs):
    global current_colour, log_file
    if VERBOSE:
        # Prepend the colour code to all arguments
        colored_args = [f"{current_colour}{arg}{RESET}" for arg in args]
        original_print(*colored_args, **kwargs)
    if LOG:
        message = " ".join(map(str, args))
        colored_message = f"{current_colour}{message}{RESET}"
        log_file.write(colored_message + "\n")
        log_file.flush()


def set_print_colour(colour):
    global current_colour
    current_colour = colour


def set_log(val):
    global LOG, log_file
    LOG = val
    if LOG:
        # Reset the log file
        with open("print.log", "w") as f:
            pass
        log_file = open("print.log", "a")
    else:
        if log_file:
            log_file.close()
            log_file = None
