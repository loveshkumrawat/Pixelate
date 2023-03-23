import logging
from supporting import env

#:: Logging
log_format = '%(name)s %(levelname)s: %(asctime)s %(filename)s:%(funcName)s on line %(lineno)s, %(message)s'
logging.basicConfig(
	filename = ".logrecord",
	datefmt = '%d-%m-%Y %H:%M:%S',
	format = log_format
)

logger = logging.getLogger('API')
logger.setLevel(env.LOG_LEVEL)
console = logging.StreamHandler()
console.setLevel(env.LOG_LEVEL)
console.setFormatter(logging.Formatter(log_format))
logger.addHandler(console)
