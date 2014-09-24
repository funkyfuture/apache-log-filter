#!/usr/bin/env python3

import logging

LOG_LEVEL = logging.INFO
# LOG_LEVEL = logging.DEBUG

from os.path import abspath, dirname, join
import sys
sys.path.append(abspath(join(dirname(sys.argv[0]), '..', '..')))

import apache_log_filter.bots
import apache_log_filter.tools.valids
from importlib import reload
from signal import sigwait, SIGINT, SIGTERM
from time import time
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer

SAMPLE_FILE = abspath(join(dirname(sys.argv[0]), 'sample.txt'))
BOTS_FILE = apache_log_filter.bots.__file__
VALIDS_FILE = apache_log_filter.tools.valids.__file__

##


# noinspection PyShadowingNames,PyBroadException
def find_unknown(path):
    if not path or path == BOTS_FILE:
        try:
            reload(apache_log_filter.bots)
        except:
            return
    if not path or path == VALIDS_FILE:
        try:
            reload(apache_log_filter.tools.valids)
        except:
            return
    _found_one = False
    with open(SAMPLE_FILE, 'rt') as f:
        for line in f.readlines():
            is_valid = apache_log_filter.tools.valids.valids.search(line)
            is_bot = apache_log_filter.bots.BOTS.search(line)
            if is_valid:
                if is_bot:
                    print("This is recognized as non-bot's and as bot's user agents:\n{}".format(line))
                    _found_one = True
                    break
                for token in ['bot', 'crawler', 'spider']:
                    if token in line.lower():
                        print("This line contains the token '{}':\n{}".format(token, line))
                        _found_one = True
                        break
            if not is_valid and not is_bot:
                print("Here's a new one:\n{}".format(line))
                _found_one = True
                break
    if not _found_one:
        print("There's nothing new.")
    return time()


##


class EventHandler(PatternMatchingEventHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_handle_time = 0

    def handle_or_not(self, event):
        if time() > self.last_handle_time + 1:
            self.last_handle_time = time()
            find_unknown(event.src_path)

    def on_modified(self, event):
        self.handle_or_not(event)

    def on_moved(self, event):
        self.handle_or_not(event)


if __name__ == "__main__":
    paths = {dirname(SAMPLE_FILE), dirname(BOTS_FILE), dirname(VALIDS_FILE)}
    patterns = [SAMPLE_FILE, BOTS_FILE, VALIDS_FILE]
    observer = Observer()

    if LOG_LEVEL == logging.DEBUG:
        from watchdog.events import LoggingEventHandler

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        event_logger = LoggingEventHandler()
        for path in paths:
            observer.schedule(event_logger, path)
            logging.debug('Started watching {} for {}'.format(path, event_logger))

    event_handler = EventHandler(patterns)
    for path in paths:
        observer.schedule(event_handler, path)
        logging.debug('Started watching {} for {}'.format(path, event_handler))

    find_unknown(None)
    observer.start()

    rec_signal = sigwait((SIGINT, SIGTERM))  # FIXME
    logging.info("Received signal {}".format(rec_signal))

    observer.join()  # TODO funktion recherchieren
