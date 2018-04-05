"""Setting up the logger
"""
import os
import logging

def set_up_logger(path_log_file):
    """Create logger
    Arguments
    --------
    path_log_file : str
        Path to logger file
    Info
    -----
    The logging level can be changed depending on mode
    Note
    ----
    logger.debug('debug message')
    logger.warn('warn message')
    logger.error('error message')
    logger.critical('critical message')
    """
    # Create logging file if not existing
    if not os.path.isfile(path_log_file):
        open(path_log_file, 'w').close()

    # Set logger level
    logging.basicConfig(
        filename=path_log_file,
        filemode='w', #'a, w'
        level=logging.DEBUG, #INFO, DEBUG, ERROR, CRITICAL
        format=('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # Necessary to add loggers in visual studio console
    ##logging.getLogger().addHandler(logging.StreamHandler())

    # Turn on/off logger
    #logging.disable = False
    #logging.disable(logging.CRITICAL)
