import re
import Globals
import OFS
from os.path import join, abspath, split
from Products.CMFCore.utils import ToolInit as CMFCoreToolInit
from Products.CMFCore.utils import getToolByName
from types import ClassType
from Acquisition import aq_base

# Duplicated here to avoid import loop
# BBB: Zope 2.7
try:
    import Zope2
except ImportError:
    import transaction_ as transaction
else:
    import transaction

# Canonical way to get at CMFPlone directory
PACKAGE_HOME = Globals.package_home(globals())

# Log methods
from log import log
from log import log_exc
from log import log_deprecated

# Keep these here to not fully change the old API
# please use i18nl10n directly
from i18nl10n import utranslate
from i18nl10n import ulocalized_time
from i18nl10n import getGlobalTranslationService


class IndexIterator:
    """An iterator used to generate tabindexes. Note that tabindexes are not as
    good for accessibility as once thought, and are largely disabled with this
    iterator. Only the first iteration of an iterator instantiated with 
    mainSlot=True will get an index, subsequent iterations will get None (thus
    removing the tabindex attribute).
    """
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, upper=100000, pos=0, mainSlot=True):
        self.upper=upper
        self.pos=pos
        self.mainSlot=mainSlot

        if not mainSlot:
            self.disabled = True
        else:
            self.disabled = False

    def next(self):
        if self.disabled:
            return None
        self.disabled = True
        return self.pos

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
            path = abspath(join(PACKAGE_HOME, path))
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
    """Convert value to integer or just return 0 if we can't"""
    try:
        return int(value)
    except ValueError:
        return 0

release_levels = ('alpha', 'beta', 'candidate', 'final')
rl_abbr = {'a':'alpha', 'b':'beta', 'rc':'candidate'}

def versionTupleFromString(v_str):
    """Returns version tuple from passed in version string"""
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
    """Reads version.txt and returns version tuple"""
    vfile = "%s/version.txt" % PACKAGE_HOME
    v_str = open(vfile, 'r').read().lower()
    return versionTupleFromString(v_str)


def transaction_note(note):
    """Write human legible note"""
    T=transaction.get()
    if isinstance(note, unicode):
        # Convert unicode to a regular string for the backend write IO.
        # UTF-8 is the only reasonable choice, as using unicode means
        # that Latin-1 is probably not enough.
        note = note.encode('utf-8', 'replace')

    if (len(T.description)+len(note))>=65535:
        log('Transaction note too large omitting %s' % str(note))
    else:
        T.note(str(note))


def base_hasattr(obj, name):
    """Like safe_hasattr, but also disables acquisition."""
    return safe_hasattr(aq_base(obj), name)


def safe_hasattr(obj, name, _marker=object()):
    """Make sure we don't mask exceptions like hasattr().

    We don't want exceptions other than AttributeError to be masked,
    since that too often masks other programming errors.
    Three-argument getattr() doesn't mask those, so we use that to
    implement our own hasattr() replacement.
    """
    return getattr(obj, name, _marker) is not _marker


def safe_callable(obj):
    """Make sure our callable checks are ConflictError safe."""
    if safe_hasattr(obj, '__class__'):
        if safe_hasattr(obj, '__call__'):
            return True
        else:
            return isinstance(obj, ClassType)
    else:
        return callable(obj)


def webdav_enabled(obj, container):
    """WebDAV check used in externalEditorEnabled.py"""

    # Object implements lock interface
    interface_tool = getToolByName(container, 'portal_interface')
    if not interface_tool.objectImplements(obj, 'webdav.WriteLockInterface.WriteLockInterface'):
        return False

    # Backwards compatibility code for AT < 1.3.6
    if safe_hasattr(obj, '__dav_marshall__'):
        if obj.__dav_marshall__ == False:
            return False
    return True


# Copied 'unrestricted_rename' from ATCT migrations to avoid
# a dependency.

from App.Dialogs import MessageDialog
from OFS.CopySupport import CopyContainer
from OFS.CopySupport import CopyError
from OFS.CopySupport import eNotSupported
from cgi import escape
import sys

def _unrestricted_rename(container, id, new_id):
    """Rename a particular sub-object

    Copied from OFS.CopySupport

    Less strict version of manage_renameObject:
        * no write lock check
        * no verify object check from PortalFolder so it's allowed to rename
          even unallowed portal types inside a folder
    """
    try: container._checkId(new_id)
    except: raise CopyError, MessageDialog(
                  title='Invalid Id',
                  message=sys.exc_info()[1],
                  action ='manage_main')
    ob=container._getOb(id)
    #!#if ob.wl_isLocked():
    #!#    raise ResourceLockedError, 'Object "%s" is locked via WebDAV' % ob.getId()
    if not ob.cb_isMoveable():
        raise CopyError, eNotSupported % escape(id)
    #!#container._verifyObjectPaste(ob)
    #!#CopyContainer._verifyObjectPaste(container, ob)
    try:    ob._notifyOfCopyTo(container, op=1)
    except: raise CopyError, MessageDialog(
                  title='Rename Error',
                  message=sys.exc_info()[1],
                  action ='manage_main')
    container._delObject(id)
    ob = aq_base(ob)
    ob._setId(new_id)

    # Note - because a rename always keeps the same context, we
    # can just leave the ownership info unchanged.
    container._setObject(new_id, ob, set_owner=0)
    ob = container._getOb(new_id)
    ob._postCopy(container, op=1)

    #!#if REQUEST is not None:
    #!#    return container.manage_main(container, REQUEST, update_menu=1)
    return None
