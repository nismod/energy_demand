"""Setting up the logger
"""
import sys
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

    #logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d } %(levelname)s - %(message)s','%m-%d %H:%M:%S') #%(module)s
    #hdlr.setFormatter(formatter)
    #root.addHandler(hdlr)
    """
    logging.basicConfig(filename=path_log_file)
    log = logging.getLogger()


    out_hdlr = logging.StreamHandler(sys.stdout)
    out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    out_hdlr.setLevel(logging.INFO)
    log.addHandler(out_hdlr)
    log.setLevel(logging.INFO)
    """
    '''
    logging.basicConfig(
        filename=path_log_file,
        filemode='w', #'a, w'
        level=logging.DEBUG, #INFO, DEBUG
        format=('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )


    #logging.getLogger().addHandler(logging.StreamHandler(sys.stderr))
    #logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    
    #root = logging.getLogger()
    #_ch = logging.StreamHandler(sys.stderr) #stdout
    #root.addHandler(_ch)
    #logging.getLogger().addHandler(logging.StreamHandler(sys.stderr))

    # Make that system errors are written to file
    root = logging.getLogger()
    _ch = logging.StreamHandler(sys.stderr) #stdout
    _ch1 = logging.StreamHandler(sys.stdout) #stdout
    _ch2 = logging.StreamHandler(sys) #stdout
    root.addHandler(_ch)
    root.addHandler(_ch1)
    root.addHandler(_ch2)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    hdlr = logging.FileHandler(path_log_file)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    hdlr.setFormatter(formatter)
    root.addHandler(hdlr)
    '''
    '''
        try:
        prnt(".")
        pass
    except Exception as e:
        print("dd")
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.info(exc_type, fname, exc_tb.tb_lineno)
        logging.info("---------")
        logging.warning(e)
        logging.info("---------")
        logging.info(sys.exc_info()[1])
         
        sys.exit()
    '''