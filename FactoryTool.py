from Products.CMFCore.utils import UniqueObject
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Acquisition import aq_base, aq_parent, Implicit
from DateTime import DateTime
import cgi
import urlparse

import sys


debug = 0  # enable/disable logging
type_map = {}

class FactoryTool(UniqueObject, SimpleItem):
    """ """
    id = 'portal_factory'
    meta_type= 'Plone Factory Tool'
    security = ClassSecurityInfo()

    def __bobo_traverse__(self, REQUEST, name):
        """ """

        # The portal factory intercepts things of the following form:
        # (1) The name of a portal type (with spaces replaced by '_'), e.g. .../portal_factor/News_Item/...
        #     In this case, we auto-generate an ID and relocate to a URL of the form .../portal_factory/News_Item.AUTO_GENERATED_ID/...
        # (2) An auto-generated ID, which is the name of a portal type (with no spaces) followed by a time stamp,
        #       e.g., .../portal_factory/News_Item.2002-08-18.154411/...
        #     For this case, we check to see if News_Item.2002-08-18.154411 exists in the portal_factory's context.
        #     - If it does not exist, we pass along a placeholder object (a PendingCreate) which will result in the
        #          creation of a real object in the ZODB later on when a form has been filled out and validated.
        #     - If it _does_ exist, the portal factory just passes along the existing object.  This is to handle the
        #          case of a user who creates an object, then navigates back to edit the object using the browser's
        #          back button.

        # try to extract a type string from next piece of the URL
        type_string = name
        dot_index = name.find('.')
        if dot_index != -1:
            type_string = name[:dot_index]

        # see if the type string corresponds to a known portal type
        type_name = self._getTypeName(type_string)

        if not type_name:
            # unknown type -- ignore and do normal traversal
            return getattr(aq_parent(self), name)

        # type_string is known type

        # name is a valid type plus a time stamp
        if dot_index != -1:

            # see if the object exists in the parent context
            if name in self.getParentNode().objectIds():
                # if so, just do a pass-through
                return getattr(self.getParentNode(), name)

            # object does not exist in parent context -- return a PendingCreate
            self.log('returning PendingCreate(%s)' % type_name, '__bobo_traverse__')
            return PendingCreate(type_name).__of__(aq_parent(self))  # wrap in acquisition layer

        # name is just type with no time-stamp.  Autogenerate an ID and relocate

        # grab the rest of the URL
        path = REQUEST['TraversalRequestNameStack']
        path = path[:]
        path.reverse()
        # lop off the final type_name string and replace with an automatically generated ID
        url = REQUEST.URL[:REQUEST.URL.rfind('/')] + '/' + self._generateId(type_name) + '/' + '/'.join(path)
        self.log("url = " + url)
        return Relocator(url).__of__(aq_parent(self))  # wrap in acquisition layer so that Relocator has access to REQUEST


    def _generateId(self, type):
        now = DateTime()
        name = type.replace(' ', '_')+'.'+now.strftime('%Y-%m-%d')+'.'+now.strftime('%H%M%S')

        # Reduce chances of an id collision (there is a very small chance that somebody will
        # create another object during this loop)
        base_name = name
        objectIds = self.getParentNode().objectIds()
        i = 1
        while name in objectIds:
            name = base_name + "-" + str(i)
            i = i + 1
        return name


    def _getTypeName(self, name):
        global type_map
        type_name = type_map.get(name, None)
        if not type_name:
            # refresh type map
            self._generateTypeMap()
            type_name = type_map.get(name, None)
        return type_name


    def _generateTypeMap(self):
        types_tool = getattr(self.getParentNode(), 'portal_types')
        content_types = types_tool.listContentTypes()
        
        global type_map
        type_map = {}
        for t in content_types:
            type_map[t.replace(' ', '')] = t


    security.declarePublic('log')
    def log(self, msg, loc=None):
        """ """
        if not debug:
            return
        import sys
        prefix = 'FactoryTool'
        if loc:
            prefix = prefix + '. ' + str(loc)
        sys.stdout.write(prefix+': '+str(msg)+'\n')

InitializeClass(FactoryTool)


class PendingCreate(SimpleItem):
    """ """
    meta_type= 'Object With Creation Pending'
    security = ClassSecurityInfo()

    def __init__(self, type):
        now = DateTime()
        self.id = type.replace(' ', '_')+'.'+now.strftime('%Y-%m-%d')+'.'+now.strftime('%H%M%S')
        self._type = type
        self.Title = ''

    security.declarePublic('getPendingCreateType')
    def getPendingCreateType(self):
        """ """
        return self._type


    def invokeFactory(self, id, *args, **kw):
        self.log('invoking factory')
        container = self.getParentNode()
        container.invokeFactory(self._type, id, *args, **kw)
        return getattr(container, id)


    security.declarePublic('log')
    def log(self, msg, loc=None):
        """ """
        if not debug:
            return
        import sys
        prefix = 'PendingCreate'
        if loc:
            prefix = prefix + '. ' + str(loc)
        sys.stdout.write(prefix+': '+str(msg)+'\n')
InitializeClass(PendingCreate)


class Relocator(Implicit):
    """ """
    security = ClassSecurityInfo()

    def __init__(self, url):
        self.url = url


    def __before_publishing_traverse__(self, other, REQUEST):
        # prevent further traversal
        REQUEST.set('TraversalRequestNameStack', [])


    security.declarePublic('__call__')
    def __call__(self, REQUEST, **kw):
        """ """
        self.log("redirecting to %s" % (self.url))
        return self.REQUEST.RESPONSE.redirect(self.url)


    index_html = None  # call __call__, not index_html


    security.declarePublic('log')
    def log(self, msg, loc=None):
        """ """
        if not debug:
            return
        import sys
        prefix = 'Relocator'
        if loc:
            prefix = prefix + '. ' + str(loc)
        sys.stdout.write(prefix+': '+str(msg)+'\n')

InitializeClass(Relocator)
