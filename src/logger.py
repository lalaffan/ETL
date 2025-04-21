import os
import logging
from datetime import datetime

class Logger:
    def __init__(self, log_dir="logs"):
        """Initializes the logger with custom settings.

        Args:
            log_dir (str): Directory to save log files (default is "logs").
        """
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)


        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"{log_dir}/{timestamp}_gdtc.log"

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        """Returns the logger instance."""
        return self.loggers