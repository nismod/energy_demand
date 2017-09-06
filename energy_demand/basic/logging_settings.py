import logging

def create_logger(path_log_file):
    """Create logger
    """
    print("path_log_file: " + str(path_log_file))
    # create logger
    logging.basicConfig(
        filename=path_log_file,
        filemode='w'
        )
    logger = logging.getLogger('Main Logger')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    #
    logger.error('error message')
    '''
    logging.basicConfig(
        filename=path_log_file,
        filemode='a',
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG
        )

    logger = logging.getLogger('logger_ed')
    '''
    return logger
