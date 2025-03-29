import logging
import sys
import traceback
from colorama import Fore, Style, init


init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA + Style.BRIGHT
    }

    def format(self, record):
        log_message = super().format(record)
        return f"{self.COLORS.get(record.levelname, '')}{log_message}{Style.RESET_ALL}"

def configure_logging():
    colored_formatter = ColoredFormatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create a file handler (without colors)
    file_handler = logging.FileHandler('app.log')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    # Create a stream handler (with colors)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(colored_formatter)

    # Configure the root logger with both handlers
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=[file_handler, stream_handler]
    )

    logger = logging.getLogger()
    for level in ('debug', 'info', 'warning', 'error', 'exception', 'fatal', 'critical'):
        setattr(logger, level, getattr(logger, level))

    # Set up an exception hook to log uncaught exceptions
    def exception_handler(exc_type, exc_value, exc_traceback):
        formatted_exception = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        # Print the exception in red to the console
        print(Fore.RED + formatted_exception + Style.RESET_ALL)
        # Append the exception details to the log file
        with open('app.log', 'a') as log_file:
            log_file.write(formatted_exception)

    sys.excepthook = exception_handler
