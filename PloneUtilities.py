from DateTime import DateTime
from types import StringType, UnicodeType, IntType

class IndexIterator:
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, upper=100000, pos=0):
        self.upper=upper
        self.pos=pos

    def next(self):
        if self.pos <= self.upper:
            self.pos += 1
            return self.pos
        raise KeyError, 'Reached upper bounds'

#deprecration warning
import zLOG
def log_deprecated(message, summary='Deprecation Warning',
                   severity=zLOG.WARNING):
    zLOG.LOG('Plone: ',severity,summary,message)

#generic log method
def log(message,summary='',severity=0):
    zLOG.LOG('Plone: ',severity,summary,message)

# here we go
try:
    # XXX Depends on 2.6
    from Products.PageTemplates.GlobalTranslationService import \
         getGlobalTranslationService, DummyTranslationService
except ImportError:
    class DummyTranslationService:
        """ A very very dummy translation service """
        pass

    def getGlobalTranslationService():
        return DummyTranslationService

service = None
translate = None

def translate_wrapper(domain, msgid, mapping=None, context=None,
                      target_language=None, default=None):
    # wrapper for calling the translate() method with a fallback value
    if service == None:
        initialize()
    try:
        res = service.translate(domain, msgid, mapping=mapping,
                                context=context,
                                target_language=target_language,
                                default=default)
    except TypeError:
        #Localizer does not take a default param
        res = service.translate(domain, msgid, mapping=mapping,
                                context=context,
                                target_language=target_language)

    if res is None or res is msgid:
        return default
    return res

def null_translate(domain, msgid, mapping=None, context=None,
                   target_language=None, default=None):
    return default

def initialize():
    # IMPORTANT: this module is unusable before this is called
    # this must be so because we want to make sure all products
    # (eg, whatever translation service we're supposed to use)
    # is already there and ready
    global service, translate
    service = getGlobalTranslationService()
    if service is DummyTranslationService:
        translate = null_translate
    elif hasattr(service, '_fallbacks'):
        # it accepts the "default" argument
        translate = service.translate
    else:
        translate = translate_wrapper

def initial_translate(domain, msgid, mapping=None, context=None,
                      target_language=None, default=None):
    initialize()
    return translate(domain, msgid, mapping, context, target_language, default)

translate = initial_translate

def localized_time(time = None, long_format = None, context = None):

    """ given a time string or DateTime and convert it into a DateTime
    and then format it appropriately., use time format of translation
    service"""

    if not time:
        return None # why?

    msgid = long_format and 'date_format_long' or 'date_format_short'

    # retrieve date format via translation service
    dateFormat = translate_wrapper('plone', msgid, context = context)

    if not dateFormat and context is not None:
        # fallback to portal_properties if no msgstr received from
        # translation service
        properties=context.portal_properties.site_properties
        if long_format:
            format=properties.localLongTimeFormat
        else:
            format=properties.localTimeFormat

        return DateTime(str(time)).strftime(format)

    if isinstance(time, StringType) or \
       isinstance(time, UnicodeType) or \
       isinstance(time, IntType):
        time = DateTime(time)

    # Avoid breakage if no dateFormat and no context (not caught above)
    if not dateFormat:
        return time.ISO()

    # extract date parts from DateTime object
    dateParts = time.parts()
    day = '%02d' % dateParts[2]
    month = '%02d' % dateParts[1]
    year = dateParts[0]
    hour = '%02d' % dateParts[3]
    minute = '%02d' % dateParts[4]

    # substitute variables with actual values
    localized_time = dateFormat.replace('${DAY}', str(day))
    localized_time = localized_time.replace('${MONTH}', str(month))
    localized_time = localized_time.replace('${YEAR}', str(year))
    localized_time = localized_time.replace('${HOUR}', str(hour))
    localized_time = localized_time.replace('${MINUTE}', str(minute))

    return localized_time

# Portions of this class was copy/pasted from the CMFCore.utils from
# CMF 1.4. Other parts are derived from code in Zope App.ProductContext
# in Zope 2.7
#
# This class is licensed under the ZPL 2.0 as stated here:
# http://www.zope.org/Resources/ZPL
# Zope Public License (ZPL) Version 2.0
# This software is Copyright (c) Zope Corporation (tm) and Contributors. All rights reserved.
from Products.CMFCore.utils import ToolInit as CMFCoreToolInit
import Globals, os, OFS.ObjectManager, OFS.misc_, Products

class ToolInit(CMFCoreToolInit):
    def initialize(self, context):
        """ Wrap the CMFCore Tool Init method """
        CMFCoreToolInit.initialize(self, context)
        for tool in self.tools:
            # get the icon from the icon
            icon = getattr(tool, 'toolicon', None)
            if icon:
                # do some tesdal magic
                pc = getattr(context, '_ProductContext__prod', getattr(context, '__prod',None))
                if pc:
                    pid = pc.id
                    name=os.path.split(icon)[1]
                    try:
                        icon=Globals.ImageFile(icon, getattr(context, '_ProductContext__pack', getattr(context,'__pack__',None)).__dict__)
                        icon.__roles__=None
                        tool.icon = 'misc_/%s/%s' % (self.product_name, name)
                        if not hasattr(OFS.misc_.misc_, pid):
                            setattr(OFS.misc_.misc_, pid, OFS.misc_.Misc_(pid, {}))
                        getattr(OFS.misc_.misc_, pid)[name]=icon
                    except (IOError, OSError):
                        # if there is some problem loading the fancy image from the tool then
                        # tell someone about it
                        log("The icon for the product: %s, icon name: %s, was not found. Using the default." % (self.product_name, icon))