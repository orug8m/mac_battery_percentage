import logging
from datetime import datetime

class Logger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO, encoding="utf-8", filename="./log/development.log"
        )
        self.current_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    def info(self, message):
        self.logger.info("{}, {}".format(self.current_time, message))

    def error(self, message):
        self.logger.error("{}, {}".format(self.current_time, message))
