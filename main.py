import yaml
import logging
import logging.config
from logging import getLogger

from src.app import App


with open("logger.yaml") as f:
    loggerConfig = yaml.safe_load(f.read())
    logging.config.dictConfig(loggerConfig)

logger = getLogger(__name__)


if __name__ == "__main__":
    logger.info("Starting Circuit Stash")
    app = App()
    app.init()
    app.mainloop()
    logger.info("Closing Circuit Stash\n"+ 96* "-")
