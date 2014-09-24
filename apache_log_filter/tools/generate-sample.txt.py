#!/usr/bin/env python3

from apache_log_parser import Parser
from glob import glob
from os.path import abspath, dirname, join
from sys import argv


def broken(ua):
    for pairing in (('(', ')'), ('[', ')'), ('{', '}'), ('"', '"'), ("'", "'")):
        if ua.count(pairing[0]) != ua.count(pairing[1]):
            return False
    return True

if len(argv) > 1:
    directory = argv[1].rstrip('/')
else:
    directory = '.'
if len(argv) > 2:
    file_pattern = argv[2]
else:
    file_pattern = '*/*/access.log'
if len(argv) > 3:
    format_string = argv[3]
else:
    try:
        with open(join(dirname(__file__), '.log_format_string'), 'rt') as f:
            format_string = f.readline().rstrip()   # FIXME must find a way to replace '\\' with '\'; maybe f.read()?
    except FileNotFoundError:
        format_string = '''%h %l %u %t \"%r\" %>s %b'''     # default

# FIXME this is a workaround for testing format strings with backslashes
format_string = '%h - - %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"'

print("Using log format string: '{}'.".format(format_string))
parser = Parser(format_string)
print('looking for ' + join(abspath(directory), file_pattern))
files = glob(join(abspath(directory), file_pattern))
print('Found {} files.'.format(len(files)))

uas = set()
counter, errors = 0, 0
for file in files:
    print("Reading from '{}'".format(file))
    with open(file, 'rt') as f:
        for line in f:
            counter += 1
            # noinspection PyBroadException
            try:
                #print(line.rstrip()) #DEBUG statement
                ua = parser.parse(line.rstrip())['request_header_user_agent']
                #print(ua) #DEBUG statement
                assert not broken(ua)
            except:
                errors += 1
            else:
                #TODO dismiss those that match valids.py
                uas.add(ua)

print("{:.2%} of lines couldn't be parsed.".format(errors/counter))

with open(join(dirname(__file__), 'sample.txt'), 'wt') as f:
    for ua in uas:
        print(ua, file=f)
