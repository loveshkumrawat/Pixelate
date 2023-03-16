import logging

logging.basicConfig(filename='log_file.log', filemode='w', format="%(name)s %(asctime)s-->%(message)s %(lineno)s",
                    level=logging.DEBUG)
logger = logging.getLogger()


