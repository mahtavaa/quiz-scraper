import logging

def create_logger(name=__name__):

	logger = logging.getLogger(name)
	logger.setLevel(logging.DEBUG)

	file_logger = logging.FileHandler('-quizarchief-.log')
	file_logger.setLevel(logging.DEBUG)

	console_logger = logging.StreamHandler()
	console_logger.setLevel(logging.DEBUG)

	formatter = logging.Formatter('%(asctime)s::%(module)s::%(funcName)s::%(lineno)s::%(levelname)s::%(message)s')

	console_logger.setFormatter(formatter)
	file_logger.setFormatter(formatter)

	logger.addHandler(console_logger)
	logger.addHandler(file_logger)

	return logger