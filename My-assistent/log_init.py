# -*- coding: utf-8 -*-
import logging
import os
from logging.handlers import RotatingFileHandler


class CustomRotatingFileHandler(RotatingFileHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # noinspection PyTypeChecker
    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                """
                Method modification: changing filename adding _n to the "body" of the name without changing file type
                Before: logfile.log.n ()
                After: logfile_n.log
                """
                sfn = self.rotation_filename(f"{self.baseFilename.split('.log')[0]}_{i}.log")
                dfn = self.rotation_filename(f"{self.baseFilename.split('.log')[0]}_{i + 1}.log")
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            dfn = self.rotation_filename(f"{self.baseFilename.split('.log')[0]}_1.log")
            # END modification
            if os.path.exists(dfn):
                os.remove(dfn)
            self.rotate(self.baseFilename, dfn)
        if not self.delay:
            self.stream = self._open()


def init_logger():
    logger = logging.getLogger()
    FORMAT = u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s'
    logger.setLevel(logging.INFO)
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(FORMAT))
    sh.setLevel(logging.INFO)
    fh = CustomRotatingFileHandler("C:\\My-assistent\\log_files\\logfile.log", maxBytes=2560000, backupCount=5, encoding='utf-8')
    fh.setFormatter(logging.Formatter(FORMAT))
    fh.setLevel(logging.INFO)
    logger.addHandler(sh)
    logger.addHandler(fh)

    # Setting loglevel for SeleniumWire
    sw_logger = logging.getLogger('seleniumwire')
    sw_logger.setLevel(logging.ERROR)

    logger.debug('Logger was initialized')
