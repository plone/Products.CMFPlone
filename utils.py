from os.path import join, abspath, dirname, split
from types import StringType, UnicodeType, IntType
from DateTime import DateTime

import re
import Globals
import OFS
from Products.CMFCore.utils import ToolInit as CMFCoreToolInit
from Products.CMFCore.utils import getToolByName
import Products.CMFPlone as CMFPlone

# get the registered translation service and the dummy
from Products.PageTemplates.GlobalTranslationService import \
     getGlobalTranslationService, DummyTranslationService

# make a dummy translation service
dummy_service = DummyTranslationService()

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

# deprecration warning
import zLOG
def log_deprecated(message, summary='Deprecation Warning',
                   severity=zLOG.WARNING):
    zLOG.LOG('Plone: ',severity,summary,message)

# generic log method
def log(message,summary='',severity=0):
    zLOG.LOG('Plone: ',severity,summary,message)

# unicode aware translate method
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
    
translate = utranslate # backwards compatibility

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
    """ convert value to an integer or just return 0 if can't """
    try:
        return int(value)
    except ValueError:
        return 0

release_levels = ('alpha', 'beta', 'candidate', 'final')
rl_abbr = {'a':'alpha', 'b':'beta', 'rc':'candidate'}

def versionTupleFromString(v_str):
    """ returns version tuple from passed in version string """
    regex_str = "(^\d+)[.]?(\d*)[.]?(\d*)[- ]?(alpha|beta|candidate|final|a|b|rc)?(\d*)"
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
        elif groups[3] in rl_abbr.keys():
            groups[3] = rl_abbr[groups[3]]
        v_tpl = tuple(groups)
    return v_tpl

def getFSVersionTuple():
    vfile = "%s/version.txt" % CMFPlone.__path__[0]
    v_str = open(vfile, 'r').read().lower()
    return versionTupleFromString(v_str)
