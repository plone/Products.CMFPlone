""" 
This tool requires a translation service which supports
the utranslate method and the default parameter.
By time of writing this code, that is only valid for PTS.
"""

from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from DateTime import DateTime
from Products.CMFCore.utils import UniqueObject
from Products.CMFPlone import ToolNames
from AccessControl import ClassSecurityInfo
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFCore.utils import getToolByName
from utils import utranslate

def _numbertoenglishname(number, format='', attr='_days'):
    # returns the english name of day or month number
    # starting with Sunday == 0
    # and January = 1
    # format is either '', 'a' or 'p')
    # see DateTime.py for details of this formats
    
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

class TranslationServiceTool(PloneBaseTool, UniqueObject, SimpleItem):
    """ Utility methods to access the translation machinery """
    
    id = 'translation_service'
    meta_type = ToolNames.TranslationServiceTool
    toolicon = 'skins/plone_images/site_icon.gif'
    security = ClassSecurityInfo()
    
    __implements__ = (PloneBaseTool.__implements__,
                      SimpleItem.__implements__, )
  
    security.declarePublic('utranslate')
    def utranslate(self, *args, **kw):
        # Translate method to access the translation service 
        # from resticted code like skins.
        return utranslate(*args, **kw)

    # support translate method as well .. still return unicode type
    security.declarePublic('translate')
    def translate(self, *args, **kw):
        return self.utranslate(*args, **kw)
        
    security.declarePublic('encode')
    def encode(self, m, input_encoding=None, output_encoding=None, errors='strict'):
        # encode a give unicode type or string type to string type in encoding output_encoding
        
        # check if input is not type unicode
        if not isinstance(m, unicode):
            if input_encoding is None: input_encoding = 'utf-8'
            m = unicode(str(m), input_encoding, errors)
        
        if output_encoding is None:
            # get output encoding from portal
            plone_tool = getToolByName(self, 'plone_utils')
            output_encoding = plone_tool.getSiteEncoding()
        
        # return as type string
        return m.encode(output_encoding, errors)
        
    security.declarePublic('asunicodetype')
    def asunicodetype(self, m, input_encoding=None, errors='strict'):
        # create type unicode from type string
        
        if isinstance(m, unicode): return m
            
        if input_encoding is None:
            # get input encoding from portal
            plone_tool = getToolByName(self, 'plone_utils')
            input_encoding = plone_tool.getSiteEncoding()
            
        # return as type unicode
        return unicode(str(m), input_encoding, errors)
        
    security.declarePublic('localized_time')
    def localized_time(self, time, long_format = None, context = None, domain='plone'):
        # Our one and only l10n method. Probably put that somewhere else once we have more l10n.
  
        # get some context if none is passed
        if context is None: context = self
  
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
        time = DateTime(time)
        
        # split up date
        parts = time.parts()
        
        # add elements to mapping
        for key in ('H', 'I', 'm', 'd', 'M', 'p', 'S', 'Y', 'y', 'Z'):
            mapping[key]=time.strftime('%'+key)
        
        # add weekday name, abbr. weekday name, month name, abbr month name
        weekday = int(time.strftime('%w')) # weekday, sunday = 0
        monthday = int(time.strftime('%m')) # month, january = 1
        mapping['A']=weekdayname_english(weekday)
        mapping['a']=weekdayname_english(weekday, 'a')
        mapping['B']=monthname_english(weekday)
        mapping['b']=monthname_english(weekday, 'a')
        
        # feed translateable elements to translation service
        for key in ('A', 'a', 'B', 'b',):
            mapping[key]=self.utranslate(domain, mapping[key], context=context, default=mapping[key])

        # feed numbers for formatting to translation service
        # XXX: implement me
        
        # translate the time string
        localized_time = self.utranslate(domain, msgid, mapping, context, default=None)
   
        if localized_time is None and context is not None:
            # msg catalog was not able to translate this msgids
            # use default setting

            properties=context.portal_properties.site_properties
            if long_format:
                format=properties.localLongTimeFormat
            else:
                format=properties.localTimeFormat
    
            return time.strftime(format)
    
        # Avoid breakage if no dateFormat and no context (not caught above)
        if localized_time is None:
            return time.ISO()
    
        # return localized_time string
        return localized_time
  
InitializeClass(TranslationServiceTool)
