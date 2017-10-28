# coding=utf-8

"""
Collect given directories stats.

"""

import os

from getpass import getuser
from stat import S_ISDIR, S_ISREG
from time import time

try:
    import Queue as queue
except ImportError:
    import queue

import diamond.collector

DAY = 86400
MB = 1048576
USER = getuser()


class Directory(object):
    """
    Directory object.
    """
    def __init__(self, path):

        self.path = path
        self.size = 0
        self.m_date = 0
        self.files = 0
        self.skipped = set()

    def log_skipped(self, os_error):
        """
        Log skipped path.
        """
        self.skipped.add(
            os_error.strerror + ': ' + \
            os_error.filename + ' User: ' + USER)

    def get_stats(self):
        """
        Calculate directory size and number of days since last update.
        """
        dirs_queue = queue.Queue()
        dirs_queue.put(self.path)

        while not dirs_queue.empty():

            try:

                path = dirs_queue.get()
                entities = os.listdir(path)

            except OSError as os_error:
                self.log_skipped(os_error)
                continue

            for entity in entities:
                fullpath = os.path.join(path, entity)

                try:

                    mode = os.stat(fullpath).st_mode

                    if S_ISDIR(mode):

                        dirs_queue.put(fullpath)

                    elif S_ISREG(mode):

                        self.files += 1
                        self.size += os.stat(fullpath).st_size
                        last_modified = os.stat(fullpath).st_mtime
                        if last_modified > self.m_date:
                            self.m_date = last_modified

                except OSError as os_error:
                    self.log_skipped(os_error)
                    continue


class DirStatsCollector(diamond.collector.Collector):

    def get_default_config_help(self):
        """
        Returns the help text for the configuration options for this collector.
        """
        config_help = super(DirStatsCollector, self).get_default_config_help()
        config_help.update({
            'dirs': 'directories to collect stats on'})

        return config_help

    def get_default_config(self):
        """
        Returns default configuration options.
        """
        config = super(DirStatsCollector, self).get_default_config()
        config['dirs'] = {}

        return config

    def collect(self):
        """
        Collect and publish directories stats.
        """
        metrics = {}

        for dir_name in self.config['dirs']:

            directory = Directory(self.config['dirs'][dir_name])
            directory.get_stats()

            if directory.skipped:
                for message in directory.skipped:
                    self.log.error(message)

            metrics.update({
                dir_name + '.current_size': int(directory.size/MB),
                dir_name + '.days_unmodified': int((time()-directory.m_date)/DAY),
                dir_name + '.files_total': directory.files})

        for metric in metrics:
            self.publish(metric, metrics[metric])
