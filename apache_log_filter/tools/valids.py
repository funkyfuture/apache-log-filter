from os.path import abspath, dirname, join
import sys
sys.path.append(abspath(join(dirname(sys.argv[0]), '..', '..')))
from apache_log_filter.bots import BOTS
from re import compile

MOZILLA_APPS = '(AppleWebKit|Chrome|Feedfetcher|Firefox|Friendica|Gecko|Iceweasel|iP(a|o)d|MSIE|Safari)'

valids = compile('|'.join([
    r"""^AppleCoreMedia/.*""",
    r"""^Avant Browser. *""",
    r"""^BlackBerry.*""",
    r"""^Center PC .*""",
    r"""^CyanogenMod/.*""",
    r"""^curl/.*""",
    r"""^facebookexternalhit.*""",
    r"""^Feedfetcher-Google;.*""",
    r"""^Feedreader .*""",
    r"""^Firefox/.*""",
    r"""^HTTP_Request2/.*""",
    r"""^Mozilla/.*\(.*""" + MOZILLA_APPS + r"""?(?!.*(""" + BOTS.pattern + r""")).*\).*""", # FIXME
    r"""^Mozilla/.*\(.*\).*""" + MOZILLA_APPS + r"""?(?!.*(""" + BOTS.pattern + r""")).*""", # FIXME
    r"""^MMS.*""",
    r"""^NetNewsWire/.*""",
    r"""^Opera.*""",
    r"""^python-requests/.*""",
    r"""^QuickTime.*""",
    r"""^RSSOwl/.*""",
    r"""^(Mobile )?Safari/[0-9]{1,4}\.[0-9]{1,2}(\.[0-9]{2})?($|(?!.*Googlebot)).*""",
    r"""^SAMSUNG-GT-.*""",
    r"""^SAMSUNG-SGH-.*""",
    r"""^SonyEricsson.*""",
    r"""^stagefright/.*""",
    r"""^Surf/.*""",
    r"""^Tablet-PC-.*""",
    r"""^VLC media player .*"""
]))
