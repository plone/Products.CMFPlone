"""
Collection of i18n and l10n utility methods.
All methods here may return unicode type.
"""

from DateTime import DateTime

# get the registered translation service and the dummy
from Products.PageTemplates.GlobalTranslationService import \
     getGlobalTranslationService, DummyTranslationService

# make a dummy translation service
dummy_service = DummyTranslationService()

# unicode aware translate method (i18n)
def utranslate(*args, **kw):
    # python useable unicode aware translate method

    # get the global translation service
    service = getGlobalTranslationService()

    # check for a translation method for unicode translations
    translate = getattr(service, 'utranslate', None)
    if translate is None:
        # fallback code when the translation service does not
        # support unicode. The dummy service will do 
        # interpolation but nothing more.
        return dummy_service.translate(*args, **kw)

    # this returns the translation as type unicode
    return service.utranslate(*args, **kw)

# unicode aware localized time method (l10n)
def ulocalized_time(time, long_format = None, context = None, domain='plone'):
    # python useable unicode aware localized time method

    # get msgid
    msgid = long_format and 'date_format_long' or 'date_format_short'

    # NOTE: this requires the presence of two msgids inside the translation catalog
    #       date_format_long and date_format_short
    #       These msgids are translated using translation service interpolation.
    #       The variables used here are the same as used in the strftime formating.
    #       Supported are %A, %a, %B, %b, %H, %I, %m, %d, %M, %p, %S, %Y, %y, %Z, each used as
    #       variable in the msgstr without the %.
    #       For example: "${A} ${d}. ${B} ${Y}, ${H}:${M} ${Z}"
    #       Each language dependend part is translated itself as well.

    # From http://docs.python.org/lib/module-time.html
    #
    # %a    Locale's abbreviated weekday name.  	
    # %A 	Locale's full weekday name. 	
    # %b 	Locale's abbreviated month name. 	
    # %B 	Locale's full month name. 	
    # %d 	Day of the month as a decimal number [01,31]. 	
    # %H 	Hour (24-hour clock) as a decimal number [00,23]. 	
    # %I 	Hour (12-hour clock) as a decimal number [01,12]. 	
    # %m 	Month as a decimal number [01,12]. 	
    # %M 	Minute as a decimal number [00,59]. 	
    # %p 	Locale's equivalent of either AM or PM. 	
    # %S 	Second as a decimal number [00,61]. 	
    # %y 	Year without century as a decimal number [00,99]. 	
    # %Y 	Year with century as a decimal number. 	
    # %Z 	Time zone name (no characters if no time zone exists). 	

    mapping = {}
    # convert to DateTime instances. Either a date string or 
    # a DateTime instance needs to be passed.
    time = DateTime(time)
       
    if context is None:
        # when without context, we cannot do very much.
        return time.ISO()
    
    # add elements to mapping
    for key in ('H', 'I', 'm', 'd', 'M', 'p', 'S', 'Y', 'y', 'Z'):
        mapping[key]=time.strftime('%'+key)
    
    # add weekday name, abbr. weekday name, month name, abbr month name
    weekday = int(time.strftime('%w')) # weekday, sunday = 0
    monthday = int(time.strftime('%m')) # month, january = 1
    mapping['A']=weekdayname_msgid(weekday)
    mapping['a']=weekdayname_msgid_abbr(weekday)
    mapping['B']=monthname_msgid(weekday)
    mapping['b']=monthname_msgid_abbr(weekday)
    
    # feed translateable elements to translation service
    for key in ('A', 'a', 'B', 'b',):
        mapping[key]=utranslate(domain, mapping[key], context=context, default=mapping[key])

    # feed numbers for formatting to translation service
    # XXX: implement me
    
    # translate the time string
    localized_time = utranslate(domain, msgid, mapping, context)
    if localized_time is None or localized_time.startswith('date_'):
        # msg catalog was not able to translate this msgids
        # use default setting

        properties=context.portal_properties.site_properties
        if long_format:
            format=properties.localLongTimeFormat
        else:
            format=properties.localTimeFormat

        return time.strftime(format)

    # return localized_time string
    return localized_time

def _numbertoenglishname(number, format='', attr='_days'):
    # returns the english name of day or month number
    # starting with Sunday == 0
    # and January = 1
    # format is either '', 'a' or 'p')
    #   ''  means full name (January, February, ...)
    #   'a' means abbreviated (Jan, Feb, ..)
    #   'p' means abbreviated with . (dot) at end (Jan., Feb., ...)
    
    number = int(number)
    if format: attr = '%s_%s' % (attr, format)
    
    # get list from DateTime attribute
    thelist = getattr(DateTime, attr)

    return thelist[number]
    
def monthname_english(number, format=''):
    # returns the english name of month with number
    return _numbertoenglishname(number, format=format, attr='_months')

def weekdayname_english(number, format=''):
    # returns the english name of month with number
    return _numbertoenglishname(number, format=format, attr='_days')

def monthname_msgid(number):
    # returns the msgid for monthname
    # use to translate to full monthname (January, February, ...)
    # eg. month_jan, month_feb, ...
    return "month_%s" % monthname_english(number, format='a').lower()
    
def monthname_msgid_abbr(number):
    # returns the msgid for the abbreviated monthname
    # use to translate to abbreviated format (Jan, Feb, ...)
    # eg. month_jan_abbr, month_feb_abbr, ...
    return "month_%s_abbr" % monthname_english(number, format='a').lower()
    
def weekdayname_msgid(number):
    # returns the msgid for the weekdayname
    # use to translate to full weekdayname (Monday, Tuesday, ...)
    # eg. weekday_mon, weekday_tue, ...
    return "weekday_%s" % weekdayname_english(number, format='a').lower()
    
def weekdayname_msgid_abbr(number):
    # returns the msgid for abbreviated weekdayname
    # use to translate to abbreviated format (Mon, Tue, ...)
    # eg. weekday_mon_abbr, weekday_tue_abbr, ...
    return "weekday_%s_abbr" % weekdayname_english(number, format='a').lower()
    
def weekdayname_msgid_short(number):
    # return the msgid for short weekdayname
    # use to translate to 2 char format (Mo, Tu, ...)
    # eg. weekday_mon_short, weekday_tue_short, ...
    return "weekday_%s_short" % weekdayname_english(number, format='a').lower()
