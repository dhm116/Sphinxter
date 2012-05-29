import logging
import os, sys
import time
import subprocess
from optparse import OptionParser
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import *

__all__ = ['Sphinxter']

class Sphinxter(Thread, FileSystemEventHandler):
	"""
	"""

	def __init__(self, watched_folders=None, make_path='.', **kwargs):
		super(Sphinxter, self).__init__(**kwargs)

		self.daemon = True
		self.logger = logging.getLogger('{}.{}'.format(self.__module__, self.__class__.__name__))
		"""A standard :class:`logging.Logger` available to sub-classes.
		
		Will dynamically name the logger based on the module and class name."""

		self.watch = watched_folders or []
		"""A :class:`list` of directories to monitor for changes."""

		self.make_path = make_path
		"""A :class:`string` containing the full or relative path to the sphinx make command."""

		self.make_formats = ['html']
		"""A :class:`list` of output types to have sphinx generate when changes are detected."""

		self.observers = []
		"""A :class:`list` of :class:`watchdog.observer.Observer` for monitoring file system events."""

	def watch(self, folder):
		"""Adds a new folder to the list of watched folders. If this thread is
		currently running, a new :class:`watchdog.observers.Observer` is created
		and started.

		:param folder: The relative or full path to the directory to monitor for changes.
		:type folder: string
		"""

		if os.path.isdir(folder):
			self.watch.append(folder)

			if self.is_alive():
				self.__observe_folder(folder)
		else:
			self.logger.warn('{} is not a directory'.format(folder))

	def run(self):
		for folder in self.watch:
			self.__observe_folder(folder)

	def on_created(self, event):
		"""Triggered any time a new file/directory is created in a watched folder."""

		self.__initiate_rebuild(event)

	def on_deleted(self, event):
		"""Triggered any time a file/directory is deleted in a watched folder."""

		self.__initiate_rebuild(event)

	def on_modified(self, event):
		"""Triggered any time a file/directory is modified in a watched folder."""

		self.__initiate_rebuild(event)

	def __observe_folder(self, folder):
		"""Helper method for creating the :class:`watchdog.observers.Observer` instances
		and starting them."""

		if os.path.isdir(folder):
			self.logger.info('Creating observer for folder "{}"'.format(folder))
			o = Observer()

			o.schedule(self, path=folder, recursive=True)

			self.observers.append(o)

			o.start()
		else:
			self.logger.warn('{} is not a directory'.format(folder))

	def __initiate_rebuild(self, event):
		if 'build' not in event.src_path and '.pyc' not in event.src_path:
			self.logger.debug('{} was {}'.format(event.src_path, event.event_type))
			self.logger.info('Rebuilding sphinx documentation')
			for type in self.make_formats:
				self.logger.debug('Rebuilding documentation for "{}"'.format(type))
				#self.logger.debug('{}/make {}'.format(os.getcwd(), type))

				#os.chdir(os.getcwd())

				subprocess.call('{}\\make {}'.format(self.make_path, type), shell=True, stderr=subprocess.STDOUT)

	def __initiate_clean(self):
		pass

if __name__ == '__main__':
	usage = "Usage: %prog [options] DIR"
	optp = OptionParser(usage=usage)

	optp.add_option('-D', '--debug', help='Enables DEBUG logging level',
					action='store_true', dest='loglevel')
	
	opts, args = optp.parse_args()
	
	console_level = logging.INFO
	
	if opts.loglevel:
		console_level = logging.DEBUG
	
	logging.basicConfig(level=console_level)

	'''
	Remove the root logging handler to use the new one
	'''
	root_logger = logging.getLogger('')
	root_logger.removeHandler(root_logger.handlers[0])

	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	handler = logging.StreamHandler(sys.stdout)
	handler.setFormatter(formatter)

	logger = logging.getLogger('MAIN')
	logger.addHandler(handler)

	builder = Sphinxter(watched_folders=args)
	builder.logger.addHandler(handler)

	try:
		logger.info('Starting Sphinx monitor')

		builder.start()

		while True:
			time.sleep(1)
	except Exception as ex:
		logger.exception('An error has occurred')
	except KeyboardInterrupt:
		logger.info('CTRL-C pressed, exiting application...')