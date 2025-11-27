import logging

logging.basicConfig(
    filename="app.log",
    filemode="a",
    format='{ "asctime": "%(asctime)s", "levelname": "%(levelname)s", "msg": "%(message)s" }',
)

log = logging.getLogger(__name__)
