from apache_log_parser import LineDoesntMatchException, Parser
from .bots import BOTS #FIXME
from .filters import DictFilter #FIXME
import logging
import re
from urllib.parse import unquote as ul_unquote

APACHE_DEFAULT_LOG_FORMAT = '%h %l %u %t "%r" %>s %b'

logger = logging.getLogger(__name__)
logger.info("Importing {}".format(__name__))

class ApacheLogFilter:
    """Iterator over Apache log files applying some filters.
       Returns the parsed fields as a dictionary, see apache_log_parser

    Args:
        files (str or list): path(s) of logfiles
        preFilter (RegFilterSet): set of regex-filters that are matched against
                                  the unparsed log-lines.
                                  Use this raw filtering to reduce the parsing
                                  before filters on a field-level are applied.
        ignore_query (bool): dismiss the query-string in an URL when parsing
        dictFilters (DictFilterSet): set of filters that are matched against
                                     specific log-fields
        ignoreBots (bool): skip User Agents that match bots in cls.BOTS
    """

    def __init__(self, files=[], format_string=APACHE_DEFAULT_LOG_FORMAT,
                 preFilters=[], ignoreQuery=True, unquote=True, dictFilters=[],
                 ignoreBots=False, returnType=str):
        #TODO handle directories and compressed files
        #TODO implement prefiltered caches (disk or ram)
        #using StringIO and a WeakrefDict with hashed parameters as key
        self.files = files
        self.current_stream = None
        self.format_string = format_string
        if not (returnType == str or returnType == dict):
            raise ValueError("{} is not a supported returnType".format(returnType))

        self.filters = []
        self.returnType = returnType
        self.returnHandlers = []

        if preFilters:
            if not preFilters.type == type(re.compile('')):
                raise ValueError("Filter must be a regular expression.")
            else:
                self.preFilters = preFilters
                self.filters.append(self.preFilters)

        self.log_parser = Parser(self.format_string)
        self.filters.append(self.log_parser.parse)
        self.returnHandlers.append(self.log_parser.parse)
        self.fieldnames = self.log_parser.names

        if ignoreBots:
            self.filters.append(self.ignore_bots)

        if ignoreQuery:
            self.filters.append(self.ignore_query)
            self.returnHandlers.append(self.ignore_query)

        if unquote:
            self.filters.append(self.unquote_url)
            self.returnHandlers.append(self.unquote_url)

        if dictFilters:
            if dictFilters.type != DictFilter:
                raise ValueError("dictFilter must be a DictFilterSet.")
            else:
                self.dictFilters = dictFilters
                self.filters.append(self.dictFilters)

    def __iter__(self):
        return self

    def __next__(self):
        if not self.current_stream:
            logger.debug("There's no self.current_stream.")
            self.__get_next_stream()
        while True:
            line = self.current_stream.readline()
            if not line:
                logger.debug("EOF reached in {}.".format(self.current_stream))
                self.__get_next_stream()
                line = self.current_stream.readline()
            if self.validate(line):
                if self.returnType == dict:
                    for handler in self.returnHandlers:
                        logger.debug("pre-filter line: {}".format(line))
                        line = handler(line)
                        logger.debug("pst-filter line: {}".format(line))
                logger.debug("Iterator returns({}): {}".format(self.returnType, line))
                return line

    def __get_next_stream(self):
        if self.current_stream:
            logger.debug("Closing input stream: {}".format(self.current_stream))
            self.current_stream.close()
        try:
            logger.debug("Popping next stream from: {}".format(self.files))
            self.current_stream = self.files.pop()
        except IndexError:
            logger.debug("Couldn't obtain a next stream; will now raise StopIteration")
            raise StopIteration
        except:
            raise
        else:
            self.current_stream = open(self.current_stream, 'rt')
            logger.info("Reading data from '{}'".format(self.current_stream))

    def validate(self, line):
        if not line or line == '':
            logger.debug("Skipping, empty input.")
            return False
        _current_line = line.rstrip()
        logger.debug("Processing {}: '{}'".format(type(_current_line), _current_line))
        for _filter in self.filters:
            try:
                result = _filter(_current_line)  # evaluate filter
            except LineDoesntMatchException:
                logger.debug("Skipped, not matching the format_string({}).".format(self.format_string))
                return False
            if result == False:
                logger.debug("Line skipped.")
                return False                # skip if filter doesn't match
            if type(result) == dict:
                logger.debug("Replacing with {}".format(result))
                _current_line = result
        logger.debug("Line matched.")
        return True # TODO return the last state of line here and get rid of the returnHandlers all over

    def ignore_bots(self, line):
        """Returns False if User Agent is identified as a bot."""
        logger.debug("Checking for bots: {}".format(BOTS.__str__))
        logger.debug("against: {}".format(line['request_header_user_agent']))
        logger.debug("Returns: {}".format(bool(BOTS.search(line['request_header_user_agent']))))
        return not bool(BOTS.search(line['request_header_user_agent']))

    def ignore_query(self, line):
        """Returns the URL without any query string."""
        result = line
        result.update({ 'request_url' : line['request_url'].split('?')[0] })
        return result

    def unquote_url(self, line):
        """Returns a normalized URL"""
        result = line
        result.update({'request_url': ul_unquote(line['request_url']
                                                .replace('\\x', '%'))})
        return result
