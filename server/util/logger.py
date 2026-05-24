import logging
from server import config
from datetime import datetime

config.set_config()

file_name = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

logger : logging.Logger = logging.getLogger(__name__)

print(config.CONFIG)
if config.CONFIG:
    logging.basicConfig(
        filename=config.CONFIG.logfile + f"/{file_name}.log",
        encoding="utf-8",
        filemode="a",
        format="{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
        level=logging.INFO,
    )