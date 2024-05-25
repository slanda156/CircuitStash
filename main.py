import yaml
import logging
import logging.config
from logging import getLogger
from traceback import format_exc

from src.app import App


with open("logger.yaml") as f:
    loggerConfig = yaml.safe_load(f.read())
    logging.config.dictConfig(loggerConfig)

logger = getLogger(__name__)

def main() -> None:
    logger.info("Starting Circuit Stash")
    app = App()
    app.init()
    app.mainloop()
    logger.info("Closing Circuit Stash\n"+ 96* "-")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(format_exc())
        raise e
