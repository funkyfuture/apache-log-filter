import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import logging
LOG_LEVEL = logging.DEBUG
log_filename = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs', os.path.basename(__file__)[:-3] + '.log'))
if os.path.isfile(log_filename):
    os.truncate(log_filename, 0)
logging.basicConfig(filename=log_filename, level=LOG_LEVEL, style='{',
                    format='[{name}] {levelname}: {message}')
logger = logging.getLogger(__name__)

import tempfile
import random
import re
import unittest

from apache_log_filter import ApacheLogFilter
from apache_log_filter.filters import DictFilter, DictFilterSet, RegExFilterSet


# noinspection PyClassHasNoInit,PyPep8Naming
class SimpleLogFile():
    def setUp(self):
        number_of_test_log_files = 4
        number_of_lines_per_file = 12

        self.format_string = '%h <<%P>> %t %Dus \"%r\" %>s %b  \"%{Referer}i\" \"%{User-Agent}i\" %l %u'
        self.valid_logline = '127.0.0.1 <<6113>> [16/Aug/2013:15:45:34 +0000] 1966093us "GET / HTTP/1.1" 200 3478  "https://example.com/" "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.18)" - -'
        self.invalid_loglines = [ '127.0.0.1 <<6113>> [16/Aug/2013:15:45:34 +0000] 1966093us "GET /login HTTP/1.1" 200 3478  "https://example.com/" "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.18)" - -',
                                 '127.0.0.1 <<6113>> [16/Aug/2013:15:45:34 +0000] 1966093us "GET /login?redirect=no HTTP/1.1" 200 3478  "https://example.com/" "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.18)" - -',
                                  '127.0.0.1 <<6113>> [16/Aug/2013:15:45:34 +0000] 1966093us "GET / HTTP/1.1" 200 3478  "https://example.com/" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" - -' ]


        self.files = []
        # noinspection PyUnusedLocal
        for i in range(0, number_of_test_log_files):
            self.files.append(tempfile.mkstemp(suffix='.log',
                                            prefix='apache_log_filter_')[1])

        self.valid_lines = 0
        for file in self.files:
            vl = random.randrange(0, number_of_lines_per_file)
            sample = [self.valid_logline] * vl
            sample.extend(self.invalid_loglines *
              ( (number_of_lines_per_file - vl) // len(self.invalid_loglines)) )
            random.shuffle(sample)
            self.valid_lines += vl
            with open(file, 'tw') as f:
                f.writelines('\n'.join(sample))

    def tearDown(self):
        for file in self.files:
            os.remove(file)


class SimpleDictFilterTest(SimpleLogFile, unittest.TestCase):
    #@unittest.skip("")
    def test_dictfilter(self):
        test_dict = DictFilter( { 'status': '200', 'pid': '6113',
                      'request_first_line': 'GET / HTTP/1.1',
                      'request_method': 'GET', 'request_url': '/',
                      'request_header_referer': 'https://example.com/',
                      'request_header_user_agent': re.escape('Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.18)'),
                      'request_header_user_agent__os__family': 'Linux' } )

        test_dictfilters = DictFilterSet()
        for key, value in test_dict.items():
            test_dictfilters.append((True, DictFilter({ key: value })))
        test_dictfilters.append((True, test_dict))
        test_dictfilters.append((False, DictFilter({'request_url': re.compile('/login')})))
        #TODO test gt_, lt_
        random.shuffle(test_dictfilters)

        test_filter = ApacheLogFilter(files = self.files,
                                  format_string = self.format_string,
                                  dictFilters = test_dictfilters,
                                  ignoreBots = True,
                                  returnType=str)

        counter = 0
        for result in test_filter:
            self.assertEqual(self.valid_logline, result.rstrip())
            counter += 1
        self.assertEqual(self.valid_lines, counter)


class SimplePreFilterTest(SimpleLogFile, unittest.TestCase):
    #@unittest.skip("")
    def test_prefilter(self):
        test_prefilters = RegExFilterSet()
        test_prefilters.append((True, "Linux"))
        test_prefilters.append((False, "login"))

        test_filter = ApacheLogFilter(files = self.files,
                                  format_string = self.format_string,
                                  preFilters = test_prefilters,
                                  returnType=str)

        counter = 0
        for result in test_filter:
            self.assertEqual(self.valid_logline, result.rstrip())
            counter += 1
        self.assertEqual(self.valid_lines, counter)


# noinspection PyPep8Naming
class SimpleIgnoreBotFilter(SimpleLogFile, unittest.TestCase):
    #@unittest.skip("")
    def test_ignorebots(self):
        test_preFilters = RegExFilterSet([(False, 'login')])
        test_filter = ApacheLogFilter(files = self.files,
                          format_string = self.format_string,
                          preFilters = test_preFilters,
                          ignoreBots = True,
                          returnType = str)

        counter = 0
        for result in test_filter:
            self.assertEqual(self.valid_logline, result.rstrip())
            counter += 1
        self.assertEqual(self.valid_lines, counter)

if __name__ == '__main__':
    logger.info("*"*5 + "Starting tests..." + 5*"*")
    unittest.main()
