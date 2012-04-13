import logging
import os
import time
from optparse import OptionParser
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import *

__all__ = ['']

class Sphinxter(Thread, FileSystemEventHandler):
	"""
	"""

	def __init__(self, **kwargs):
		super(Sphinxter, self).__init__(**kwargs)

		self.daemon = True
		self.logger = logging.getLogger('{}.{}'.format(self.__module__, self.__class__.__name__))

	def run(self):
		pass

if __name__ == '__main__':
    optp = OptionParser()

    optp.add_option('-D', '--debug', help='Enables DEBUG logging level',
                    action='store_true', dest='loglevel')
    
    opts, args = optp.parse_args()
    
    console_level = logging.INFO
    
    if opts.loglevel:
        console_level = logging.DEBUG
	
	logging.basicConfig(level=console_level)
	
    logger = logging.getLogger('MAIN')

	monitor = Sphinxter()

    try:
    	logger.info('Starting Sphinx monitor')

    	monitor.start()

        while True:
            time.sleep(1)
    except Exception as ex:
        logger.exception('An error has occurred')
    except KeyboardInterrupt:
        logger.info('CTRL-C pressed, exiting application...')