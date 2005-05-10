from os.path import join, abspath, dirname, split
from types import StringType, UnicodeType, IntType
from DateTime import DateTime

import re
import Globals
import OFS
from Products.CMFCore.utils import ToolInit as CMFCoreToolInit
from Products.CMFCore.utils import getToolByName
import Products.CMFPlone as CMFPlone

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
    # use full length day and month, and translate into proper language
    if long_format:
        weekday = translate_wrapper('plone', time.Day(), context = context) or time.Day()
        month = translate_wrapper('plone', time.Mon(), context = context) or time.Mon()
    else:
        weekday = ''
        month = '%02d' % dateParts[1]
    day = '%02d' % dateParts[2]
    year = dateParts[0]
    hour = '%02d' % dateParts[3]
    minute = '%02d' % dateParts[4]

    # substitute variables with actual values
    localized_time = dateFormat.replace('${DAY}', str(day))
    localized_time = localized_time.replace('${WEEKDAY}', str(weekday))
    localized_time = localized_time.replace('${MONTH}', str(month))
    localized_time = localized_time.replace('${YEAR}', str(year))
    localized_time = localized_time.replace('${HOUR}', str(hour))
    localized_time = localized_time.replace('${MINUTE}', str(minute))

    return localized_time

class ToolInit(CMFCoreToolInit):

    def getProductContext(self, context):
        name = '_ProductContext__prod'
        return getattr(context, name, getattr(context, '__prod', None))

    def getPack(self, context):
        name = '_ProductContext__pack'
        return getattr(context, name, getattr(context, '__pack__', None))

    def getIcon(self, context, path):
        pack = self.getPack(context)
        icon = None
        # This variable is just used for the log message
        icon_path = path
        try:
            icon = Globals.ImageFile(path, pack.__dict__)
        except (IOError, OSError):
            # Fallback:
            # Assume path is relative to CMFPlone directory
            plone_path = dirname(__file__)
            path = abspath(join(plone_path, path))
            try:
                icon = Globals.ImageFile(path, pack.__dict__)
            except (IOError, OSError):
                # if there is some problem loading the fancy image
                # from the tool then  tell someone about it
                log(('The icon for the product: %s which was set to: %s, '
                     'was not found. Using the default.' %
                     (self.product_name, icon_path)))
        return icon

    def initialize(self, context):
        """ Wrap the CMFCore Tool Init method """
        CMFCoreToolInit.initialize(self, context)
        for tool in self.tools:
            # Get the icon path from the tool
            path = getattr(tool, 'toolicon', None)
            if path is not None:
                pc = self.getProductContext(context)
                if pc is not None:
                    pid = pc.id
                    name = split(path)[1]
                    icon = self.getIcon(context, path)
                    if icon is None:
                        # Icon was not found
                        return
                    icon.__roles__ = None
                    tool.icon = 'misc_/%s/%s' % (self.product_name, name)
                    misc = OFS.misc_.misc_
                    Misc = OFS.misc_.Misc_
                    if not hasattr(misc, pid):
                        setattr(misc, pid, Misc(pid, {}))
                    getattr(misc, pid)[name] = icon

def _createObjectByType(type_name, container, id, *args, **kw):
    """Create an object without performing security checks
    
    invokeFactory and fti.constructInstance perform some security checks
    before creating the object. Use this function instead if you need to
    skip these checks.
    
    This method uses some code from
    CMFCore.TypesTool.FactoryTypeInformation.constructInstance
    to create the object without security checks.
    """
    id = str(id)
    typesTool = getToolByName(container, 'portal_types')
    fti = typesTool.getTypeInfo(type_name)
    if not fti:
        raise ValueError, 'Invalid type %s' % type_name

    # we have to do it all manually :(
    p = container.manage_addProduct[fti.product]
    m = getattr(p, fti.factory, None)
    if m is None:
        raise ValueError, ('Product factory for %s was invalid' %
                           fti.getId())

    # construct the object
    m(id, *args, **kw)
    ob = container._getOb( id )
    
    return fti._finishConstruction(ob)


def safeToInt(value):
    """ convert value to an integer or just return if can't """
    try:
        return int(value)
    except ValueError:
        return 0

release_levels = ('alpha', 'beta', 'candidate', 'final')

def versionTupleFromString(v_str):
    """ returns version tuple from passed in version string """
    regex_str = "(^\d+)[.]?(\d*)[.]?(\d*)[- ]?(alpha|beta|candidate|final)?(\d*)"
    v_regex = re.compile(regex_str)
    match = v_regex.match(v_str)
    if match is None:
        v_tpl = None
    else:
        groups = list(match.groups())
        for i in (0, 1, 2, 4):
            groups[i] = safeToInt(groups[i])
        if groups[3] is None:
            groups[3] = 'final'
        v_tpl = tuple(groups)
    return v_tpl

def getFSVersionTuple():
    vfile = "%s/version.txt" % CMFPlone.__path__[0]
    v_str = open(vfile, 'r').read().lower()
    return versionTupleFromString(v_str)
