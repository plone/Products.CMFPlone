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
def log_deprecated(message,summary='Deprecation Warning',severity=zLOG.WARNING):
    zLOG.LOG('Plone: ',severity,summary,message)

#generic log method
def log(message,summary='',severity=0):
    zLOG.LOG('Plone: ',severity,summary,message)

# here we go
try:
    # XXX Depends on 2.6
    from Products.PageTemplates.GlobalTranslationService import getGlobalTranslationService, \
         DummyTranslationService
except ImportError:
    class DummyTranslationService:
        """ A very very dummy translation service """
        pass

    def getGlobalTranslationService():
        return DummyTranslationService

service = None
translate = None

def translate_wrapper(domain, msgid, mapping=None, context=None, target_language=None, default=None):
    # wrapper for calling the translate() method with a fallback value
    if service == None:
        initialize()
    try:
        res = service.translate(domain, msgid, mapping=mapping, context=context, target_language=target_language, default=default)
    except TypeError:
        #Localizer does not take a default param
        res = service.translate(domain, msgid, mapping=mapping, context=context, target_language=target_language)

    if res is None or res is msgid:
        return default
    return res

def null_translate(domain, msgid, mapping=None, context=None, target_language=None, default=None):
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

def initial_translate(domain, msgid, mapping=None, context=None, target_language=None, default=None):
    initialize()
    return translate(domain, msgid, mapping, context, target_language, default)

translate = initial_translate
