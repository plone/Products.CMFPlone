"""
Collection of i18n and l10n utility methods.
"""
from Acquisition import aq_acquire
from DateTime import DateTime
from DateTime.interfaces import IDateTime
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.utils import log
from zope.component import getUtility
from zope.i18n import translate
from zope.i18n.locales import locales
from zope.publisher.interfaces.browser import IBrowserRequest

import logging
import re

datetime_formatvariables = {'H', 'I', 'm', 'd', 'M', 'p', 'S', 'Y', 'y', 'Z'}
name_formatvariables = {'a', 'A', 'b', 'B'}
all_formatvariables = datetime_formatvariables | name_formatvariables
_all_regexp_set = ','.join(all_formatvariables)
# regexp to split up ${X} format strings
_interp_regex = re.compile(
    r'(?<!\$)(\$(?:[%(n)s]|{[%(n)s]}))' % ({'n': _all_regexp_set})
)
# regexp to detect if this is a strftime format string
_dt_format_string_regexp = re.compile(fr'\%([{_all_regexp_set}])')

# those are from DateTime.DateTime, but we must not rely on its internal
# structures, so here a copy:
ENGLISH_NAMES = {
    '_days': (
        'Sunday', 'Monday', 'Tuesday', 'Wednesday',  'Thursday', 'Friday',
        'Saturday',
    ),
    '_days_a': ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'),
    '_days_p': ('Sun.', 'Mon.', 'Tue.', 'Wed.', 'Thu.', 'Fri.', 'Sat.'),
    '_months': (
        '', 'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December',
    ),
    '_months_a': (
        '', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
    ),
    '_months_p': (
        '', 'Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'June',
        'July', 'Aug.', 'Sep.', 'Oct.', 'Nov.', 'Dec.'
    ),
}

# The following are helper methods to change the default date and time formats
# for a specific locale. These locale dependent formats are used in the
# date/time widgets to determine the format and decide if a 24 hour or 12 hour
# AM/PM widget should be used. If 'a' is part of the pattern the AM/PM widget
# will be used, otherwise a 24 hour clock.
#
# localeid is a tuple of the form: (language, country, variant)
# for example: (None, ) or ('en', ) or ('en', 'US', None)
#
# value is in the format described by zope.i18n.interfaces.IDateTimeFormat
# for example u'yyyy-MM-dd' or u'HH:mm:ss'
#
# Note that this is a different format than used for the other methods in
# this module.
#
# locales uses a module level cache, so any changes you make with these
# methods will apply to the entire process and only need to be made once.
# You can use them in any code imported at startup, for example in a packages
# __init__ method.
#
# In order to use a 24 hour clock for English speakers, you would do:
#
# from Products.CMFPlone import i18nl10n
# i18nl10n.setDefaultTimeFormat(('en',), u'HH:mm:ss')


def setDefaultDateFormat(localeid, value):
    gregorian = locales.getLocale(*localeid).dates.calendars['gregorian']
    date_format = gregorian.dateFormats['medium'].formats[None]
    date_format.pattern = value


def setDefaultTimeFormat(localeid, value):
    gregorian = locales.getLocale(*localeid).dates.calendars['gregorian']
    time_format = gregorian.timeFormats['medium'].formats[None]
    time_format.pattern = value


def utranslate(domain, msgid, mapping=None, context=None,
               target_language=None, default=None):
    # We used to pass an object as context.
    if not IBrowserRequest.providedBy(context):
        context = aq_acquire(context, 'REQUEST')
    # The signature of zope.i18n's translate has the msgid and domain switched
    return translate(msgid, domain=domain, mapping=mapping, context=context,
                     target_language=target_language, default=default)


def get_formatstring_from_registry(msgid):
    """If the Enabled record is True, return a format string."""
    registry = getUtility(IRegistry)
    name_root = 'Products.CMFPlone.i18nl10n.override_dateformat.'
    if registry.get(name_root + 'Enabled', False) is False:
        return None
    # msgid: "date_format_long", "date_format_short", or "time_format"
    record_name = name_root + msgid
    return registry.get(record_name, None)


def ulocalized_time(time, long_format=None, time_only=False, context=None,
                    domain='plonelocales', request=None, target_language=None):
    """unicode aware localized time method (l10n)"""

    if time_only:
        msgid = 'time_format'
    elif long_format:
        msgid = 'date_format_long'
    else:
        msgid = 'date_format_short'

    # NOTE: this requires the presence of three msgids inside the translation
    #       catalog date_format_long, date_format_short, and time_format
    #       These msgids are translated using interpolation.
    #       The variables used here are the same as used in the strftime
    #       formating.
    #       Supported are:
    #           %A, %a, %B, %b, %H, %I, %m, %d, %M, %p, %S, %Y, %y, %Z
    #       Each used as variable in the msgstr without the %.
    #       For example: "${A} ${d}. ${B} ${Y}, ${H}:${M} ${Z}"
    #       Each language dependend part is translated itself as well.

    # From http://docs.python.org/lib/module-time.html
    #
    # %a    Locale's abbreviated weekday name.
    # %A        Locale's full weekday name.
    # %b        Locale's abbreviated month name.
    # %B        Locale's full month name.
    # %d        Day of the month as a decimal number [01,31].
    # %H        Hour (24-hour clock) as a decimal number [00,23].
    # %I        Hour (12-hour clock) as a decimal number [01,12].
    # %m        Month as a decimal number [01,12].
    # %M        Minute as a decimal number [00,59].
    # %p        Locale's equivalent of either AM or PM.
    # %S        Second as a decimal number [00,61].
    # %y        Year without century as a decimal number [00,99].
    # %Y        Year with century as a decimal number.
    # %Z        Time zone name (no characters if no time zone exists).

    mapping = {}
    # convert to DateTime instances. Either a date string or
    # a DateTime instance needs to be passed.
    if not IDateTime.providedBy(time):
        try:
            time = DateTime(time)
        except:
            log('Failed to convert %s to a DateTime object' % time,
                severity=logging.DEBUG)
            return None

    if context is None:
        # when without context, we cannot do very much.
        return time.ISO8601()

    if request is None:
        request = aq_acquire(context, 'REQUEST')

    # 1. if our Enabled flag in the configuration registry is set,
    # the format string there should override the translation machinery
    formatstring = get_formatstring_from_registry(msgid)

    if formatstring is not None:
        if _dt_format_string_regexp.findall(formatstring):
            # classic strftime formatting, no i18n/l10n
            return time.strftime(formatstring)
    else:
        # 2. the normal case: translation machinery,
        # that is the ".../LC_MESSAGES/plonelocales.po" files
        formatstring = translate(
            msgid, domain, mapping, request, target_language=target_language
        )

    # 3. if both failed, fall back to hardcoded ISO style
    if formatstring == msgid:
        if msgid == 'date_format_long':
            formatstring = '%Y-%m-%d %H:%M'  # 2038-01-19 03:14
        elif msgid == 'date_format_short':
            formatstring = '%Y-%m-%d'  # 2038-01-19
        elif msgid == 'time_format':
            formatstring = '%H:%M'  # 03:14
        else:
            formatstring = '[INTERNAL ERROR]'
        return time.strftime(formatstring)

    # get the format elements used in the formatstring
    formatelements = {el[2:-1] for el in _interp_regex.findall(formatstring)}

    # add used elements to mapping
    elements = formatelements & datetime_formatvariables
    for key in elements:
        mapping[key] = time.strftime('%' + key)

    # add weekday name, abbr. weekday name, month name, abbr month name
    name_elements = formatelements & name_formatvariables
    if {'a', 'A'} & name_elements:
        weekday = int(time.strftime('%w'))  # weekday, sunday = 0
        if 'a' in name_elements:
            mapping['a'] = weekdayname_msgid_abbr(weekday)
        if 'A' in name_elements:
            mapping['A'] = weekdayname_msgid(weekday)
    if {'b', 'B'} & name_elements:
        monthday = int(time.strftime('%m'))  # month, january = 1
        if 'b' in name_elements:
            mapping['b'] = monthname_msgid_abbr(monthday)
        if 'B' in name_elements:
            mapping['B'] = monthname_msgid(monthday)

    # translate translateable elements
    for key in name_elements:
        mapping[key] = translate(
            mapping[key],
            domain,
            context=request,
            default=mapping[key],
            target_language=target_language,
        )

    # translate the time string
    return translate(
        msgid, domain, mapping, request, target_language=target_language
    )


def _numbertoenglishname(number, format=None, attr='_days'):
    # returns the english name of day or month number
    # starting with Sunday == 0
    # and January = 1
    # format is either None, 'a' or 'p')
    #   None  means full name (January, February, ...)
    #   'a' means abbreviated (Jan, Feb, ..)
    #   'p' means abbreviated with . (dot) at end (Jan., Feb., ...)

    number = int(number)
    if format is not None:
        attr = f'{attr}_{format}'
    return ENGLISH_NAMES[attr][number]


def monthname_english(number, format=None):
    # returns the english name of month with number
    return _numbertoenglishname(number, format=format, attr='_months')


def weekdayname_english(number, format=None):
    # returns the english name of week with number
    return _numbertoenglishname(number, format=format, attr='_days')


def monthname_msgid(number):
    # returns the msgid for monthname
    # use to translate to full monthname (January, February, ...)
    # e.g. month_jan, month_feb, ...
    return "month_%s" % monthname_english(number, format='a').lower()


def monthname_msgid_abbr(number):
    # returns the msgid for the abbreviated monthname
    # use to translate to abbreviated format (Jan, Feb, ...)
    # e.g. month_jan_abbr, month_feb_abbr, ...
    return "month_%s_abbr" % monthname_english(number, format='a').lower()


def weekdayname_msgid(number):
    # returns the msgid for the weekdayname
    # use to translate to full weekdayname (Monday, Tuesday, ...)
    # e.g. weekday_mon, weekday_tue, ...
    return "weekday_%s" % weekdayname_english(number, format='a').lower()


def weekdayname_msgid_abbr(number):
    # returns the msgid for abbreviated weekdayname
    # use to translate to abbreviated format (Mon, Tue, ...)
    # e.g. weekday_mon_abbr, weekday_tue_abbr, ...
    return "weekday_%s_abbr" % weekdayname_english(number, format='a').lower()


def weekdayname_msgid_short(number):
    # return the msgid for short weekdayname
    # use to translate to 2 char format (Mo, Tu, ...)
    # e.g. weekday_mon_short, weekday_tue_short, ...
    return "weekday_%s_short" % weekdayname_english(number, format='a').lower()
