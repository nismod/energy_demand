"""Setting up the logger
"""
import logging

def set_up_logger(path_log_file):
    """Create logger

    Argument
    --------
    path_log_file : str
        Path to logger file

    Info
    -----
    The logging level can be changed depending on mode
    
    Note
    ----
    logger.debug('debug message')
    print('info message')
    logger.warn('warn message')
    logger.error('error message')
    logger.critical('critical message')
    """
    # Set logger level
    logging.basicConfig(
        filename=path_log_file,
        filemode='w', #'a, w'
        level=logging.DEBUG, #INFO, DEBUG
        format=('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )

    # Necessary to add loggers in visual studio console
    logging.getLogger().addHandler(logging.StreamHandler())
