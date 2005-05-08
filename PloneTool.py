import re
import sys
import traceback
from types import TupleType, UnicodeType, StringType
import urlparse

from zLOG import LOG, INFO, WARNING
from Products.PluginIndexes.common import safe_callable

from Acquisition import aq_base, aq_inner, aq_parent
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import _checkPermission, \
     _getAuthenticatedUser, limitGrantedRoles
from Products.CMFCore.utils import getToolByName, _dtmldir
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.interfaces.DublinCore import DublinCore, MutableDublinCore
from Products.CMFCore.interfaces.Discussions import Discussable
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFPlone.interfaces.Translatable import ITranslatable
from Products.CMFPlone import ToolNames, transaction_note
from Products.CMFPlone.interfaces.BrowserDefault import IBrowserDefault

from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import bad_id
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, Unauthorized
from ZODB.POSException import ConflictError
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from DateTime import DateTime

_marker = ()
_icons = {}

CEILING_DATE = DefaultDublinCoreImpl._DefaultDublinCoreImpl__CEILING_DATE
FLOOR_DATE = DefaultDublinCoreImpl._DefaultDublinCoreImpl__FLOOR_DATE

def log(summary='', text='', log_level=INFO):
    LOG('Plone Debug', log_level, summary, text)

from Products.SecureMailHost.SecureMailHost import EMAIL_RE
from Products.SecureMailHost.SecureMailHost import EMAIL_CUTOFF_RE
BAD_CHARS = re.compile(r'[^a-zA-Z0-9-_~,.$\(\)# ]').findall

#XXX Remove this when we don't depend on python2.1 any longer, use email.Utils.getaddresses instead
from rfc822 import AddressList
def _getaddresses(fieldvalues):
    """Return a list of (REALNAME, EMAIL) for each fieldvalue."""
    all = ', '.join(fieldvalues)
    a = AddressList(all)
    return a.addresslist

# table of transliterations that we know how to do
mapping = {138: 's', 140: 'OE', 142: 'z', 154: 's', 156: 'oe', 158: 'z', 159: 'Y',
192: 'A', 193: 'A', 194: 'A', 195: 'A', 196: 'A', 197: 'a', 198: 'E', 199: 'C',
200: 'E', 201: 'E', 202: 'E', 203: 'E', 204: 'I', 205: 'I', 206: 'I', 207: 'I',
208: 'D', 209: 'n', 211: 'O', 212: 'O', 214: 'O', 216: 'O', 217: 'U', 218: 'U',
219: 'U', 220: 'U', 221: 'y', 223: 'ss', 224: 'a', 225: 'a', 226: 'a', 227: 'a',
228: 'a', 229: 'a', 230: 'e', 231: 'c', 232: 'e', 233: 'e', 234: 'e', 235: 'e',
236: 'i', 237: 'i', 238: 'i', 239: 'i', 240: 'd', 241: 'n', 243: 'o', 244: 'o',
246: 'o', 248: 'o', 249: 'u', 250: 'u', 251: 'u', 252: 'u', 253: 'y', 255: 'y'}

def _normalizeChar(c=''):
    if ord(c) < 256:
        return mapping.get(ord(c), c)
    else:
        return mapping.get(ord(c), '%x' % ord(c))

# dublic core accessor name -> metadata name
METADATA_DCNAME = {
    # the first two rows are handle in a special way
    # 'Description'      : 'description',
    # 'Subject'          : 'keywords',
    'Description'      : 'DC.description',
    'Subject'          : 'DC.subject',
    'Creator'          : 'DC.creator',
    'Contributors'     : 'DC.contributors',
    'Publisher'        : 'DC.publisher',
    'CreationDate'     : 'DC.date.created',
    'ModificationDate' : 'DC.date.modified',
    'Type'             : 'DC.type',
    'Format'           : 'DC.format',
    'Language'         : 'DC.language',
    'Rights'           : 'DC.rights',
    }


class PloneTool(PloneBaseTool, UniqueObject, SimpleItem):
    """Various utility methods."""

    id = 'plone_utils'
    meta_type= ToolNames.UtilsTool
    toolicon = 'skins/plone_images/site_icon.gif'
    security = ClassSecurityInfo()
    plone_tool = 1
    field_prefix = 'field_' # Prefix for forms fields!?

    __implements__ = (PloneBaseTool.__implements__,
                      SimpleItem.__implements__, )

    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'setMemberProperties')
    def setMemberProperties(self, member, **properties):
        membership=getToolByName(self, 'portal_membership')
        if hasattr(member, 'getId'):
            member=member.getId()
        user=membership.getMemberById(member)
        user.setMemberProperties(properties)

    security.declarePublic('getSiteEncoding')
    def getSiteEncoding(self):
        """Get the default_charset or fallback to utf8
        """
        pprop   = getToolByName(self, 'portal_properties')
        default = 'utf-8'
        try:
            charset = pprop.site_properties.getProperty('default_charset', default)
        except AttributeError:
            charset = default
        return charset

    security.declarePublic('portal_utf8')
    def portal_utf8(self, str, errors='strict'):
        """Transforms an string in portal encoding to utf8
        """
        charset = self.getSiteEncoding()
        if charset.lower() in ('utf-8', 'utf8'):
            # test
            unicode(str, 'utf-8', errors)
            return str
        else:
            return unicode(str, charset, errors).encode('utf-8', errors)

    security.declarePublic('utf8_portal')
    def utf8_portal(self, str, errors='strict'):
        """Transforms an utf8 string to portal encoding
        """
        charset = self.getSiteEncoding()
        if charset.lower() in ('utf-8', 'utf8'):
            # test
            unicode(str, 'utf-8', errors)
            return str
        else:
            return unicode(str, 'utf-8', errors).encode(charset, errors)

    security.declarePrivate('getMailHost')
    def getMailHost(self):
        """Get the MailHost
        """
        return getattr(aq_parent(self), 'MailHost')

    security.declarePublic('sendto')
    def sendto(self, send_to_address, send_from_address, comment,
               subject='Plone', **kwargs ):
        """Sends a link of a page to someone
        """
        host = self.getMailHost()
        template = getattr(self, 'sendto_template')
        encoding = self.getSiteEncoding()
        # cook from template
        message = template(self, send_to_address=send_to_address,
                           send_from_address=send_from_address,
                           comment=comment, subject=subject, **kwargs
                          )
        result = host.secureSend(message, send_to_address,
                                 send_from_address, subject=subject,
                                 subtype='plain', charset=encoding,
                                 debug=False
                                )
        #print result[2].as_string()

    security.declarePublic('validateSingleNormalizedEmailAddress')
    def validateSingleNormalizedEmailAddress(self, address):
        """Lower-level function to validate a single normalized email address, see validateEmailAddress
        """
        host = self.getMailHost()
        return host.validateSingleNormalizedEmailAddress(address)

    security.declarePublic('validateSingleEmailAddress')
    def validateSingleEmailAddress(self, address):
        """Validate a single email address, see also validateEmailAddresses
        """
        host = self.getMailHost()
        return host.validateSingleEmailAddress(address)

    security.declarePublic('validateEmailAddresses')
    def validateEmailAddresses(self, addresses):
        """Validate a list of possibly several email addresses, see also validateSingleEmailAddress
        """
        host = self.getMailHost()
        return host.validateEmailAddresses(addresses)

    security.declarePublic('editMetadata')
    def editMetadata( self
                     , obj
                     , allowDiscussion=None
                     , title=None
                     , subject=None
                     , description=None
                     , contributors=None
                     , effective_date=None
                     , expiration_date=None
                     , format=None
                     , language=None
                     , rights=None
                     ,  **kwargs):
        """ Responsible for setting metadata on a content object
            we assume the obj implements IDublinCoreMetadata.
        """
        mt = getToolByName(self, 'portal_membership')
        if not mt.checkPermission(CMFCorePermissions.ModifyPortalContent, obj):
            raise Unauthorized    # FIXME: Some scripts rely on this being string?

        REQUEST = self.REQUEST
        pfx = self.field_prefix

        def getfield(request, name, default=None, pfx=pfx):
            return request.form.get(pfx+name, default)

        def tuplify(value):
            return tuple(filter(None, value))

        if DublinCore.isImplementedBy(obj):
            if title is None:
                title = getfield(REQUEST, 'title')
            if description is None:
                description = getfield(REQUEST, 'description')
            if subject is None:
                subject = getfield(REQUEST, 'subject')
            if subject is not None:
                subject = tuplify(subject)
            if contributors is None:
                contributors = getfield(REQUEST, 'contributors')
            if contributors is not None:
                contributors = tuplify(contributors)
            if effective_date is None:
                effective_date = getfield(REQUEST, 'effective_date')
            if effective_date == '':
                effective_date = 'None'
            if expiration_date is None:
                expiration_date = getfield(REQUEST, 'expiration_date')
            if expiration_date == '':
                expiration_date = 'None'

        if Discussable.isImplementedBy(obj) or \
            getattr(obj, '_isDiscussable', None):
            disc_tool = getToolByName(self, 'portal_discussion')
            if allowDiscussion is None:
                allowDiscussion = disc_tool.isDiscussionAllowedFor(obj)
                if not hasattr(obj, 'allow_discussion'):
                    allowDiscussion = None
                allowDiscussion = REQUEST.get('allowDiscussion', allowDiscussion)
            if type(allowDiscussion)==StringType:
                allowDiscussion=allowDiscussion.lower().strip()
            if allowDiscussion=='default':
                allowDiscussion=None
            elif allowDiscussion=='off':
                allowDiscussion=0
            elif allowDiscussion=='on':
                allowDiscussion=1
            disc_tool.overrideDiscussionFor(obj, allowDiscussion)

        if MutableDublinCore.isImplementedBy(obj):
            if title is not None:
                obj.setTitle(title)
            if description is not None:
                obj.setDescription(description)
            if subject is not None:
                obj.setSubject(subject)
            if contributors is not None:
                obj.setContributors(contributors)
            if effective_date is not None:
                obj.setEffectiveDate(effective_date)
            if expiration_date is not None:
                obj.setExpirationDate(expiration_date)
            if format is not None:
                obj.setFormat(format)
            if language is not None:
                obj.setLanguage(language)
            if rights is not None:
                obj.setRights(rights)
            # Make the catalog aware of changes
            obj.reindexObject()

    def _renameObject(self, obj, id):
        if not id:
            REQUEST=self.REQUEST
            id = REQUEST.get('id', '')
            id = REQUEST.get(self.field_prefix+'id', '')
        if id != obj.getId():
            parent = aq_parent(aq_inner(obj))
            parent.manage_renameObject(obj.getId(), id)

    def _makeTransactionNote(self, obj, msg=''):
        #XXX why not aq_parent()?
        relative_path='/'.join(getToolByName(self, 'portal_url').getRelativeContentPath(obj)[:-1])
        if not msg:
            msg=relative_path+'/'+obj.title_or_id()+' has been modified.'
        if isinstance(msg, UnicodeType):
            # Convert unicode to a regular string for the backend write IO.
            # UTF-8 is the only reasonable choice, as using unicode means
            # that Latin-1 is probably not enough.
            msg = msg.encode('utf-8')
        if not get_transaction().description:
            transaction_note(msg)

    security.declarePublic('contentEdit')
    def contentEdit(self, obj, **kwargs):
        """ encapsulates how the editing of content occurs """

        try:
            self.editMetadata(obj, **kwargs)
        except AttributeError, msg:
            log('Failure editing metadata at: %s.\n%s\n' %
                (obj.absolute_url(), msg))

        if kwargs.get('id', None) is not None:
            self._renameObject(obj, id=kwargs['id'].strip())

        self._makeTransactionNote(obj)

    security.declarePublic('availableMIMETypes')
    def availableMIMETypes(self):
        """Return a map of mimetypes

        Requires mimetype registry from Archetypes 1.3
        """
        mtr = getToolByName(self, 'mimetypes_registry')
        return mtr.list_mimetypes()

    security.declareProtected(CMFCorePermissions.View, 'getWorkflowChainFor')
    def getWorkflowChainFor(self, object):
        """ Proxy the request for the chain to the workflow
            tool, as this method is private there.
        """
        wftool = getToolByName(self, 'portal_workflow')
        wfs=()
        try:
            wfs=wftool.getChainFor(object)
        except ConflictError:
            raise
        except:
            pass
        return wfs

    security.declareProtected(CMFCorePermissions.View, 'getIconFor')
    def getIconFor(self, category, id, default=_marker):
        """ Cache point for actionicons.getActionIcon call
            also we want to allow for a default icon id to be
            passed in.
        """
        #short circuit the lookup
        if (category, id) in _icons.keys():
            return _icons[ (category, id) ]

        try:
            actionicons=getToolByName(self, 'portal_actionicons')
            iconinfo=actionicons.getActionIcon(category, id)
            icon=_icons.setdefault( (category, id), iconinfo )
        except KeyError:
            if default is not _marker:
                icon=default
            else:
                raise

        #we want to return the actual object
        return icon

    security.declareProtected(CMFCorePermissions.View, 'getReviewStateTitleFor')
    def getReviewStateTitleFor(self, obj):
        """Utility method that gets the workflow state title for the
        object's review_state.  Returns None if no review_state found.
        """

        wf_tool=getToolByName(self, 'portal_workflow')
        wfs=()
        review_states=()
        objstate=None
        try:
            objstate=wf_tool.getInfoFor(obj, 'review_state')
            wfs=wf_tool.getWorkflowsFor(obj)
        except WorkflowException, e:
            pass
        if wfs:
            for w in wfs:
                if w.states.has_key(objstate):
                    return w.states[objstate].title
        return None

    # Convenience method since skinstool requires loads of acrobatics.
    # We use this for the reconfig form
    security.declareProtected(CMFCorePermissions.ManagePortal, 'setDefaultSkin')
    def setDefaultSkin(self, default_skin):
        """ sets the default skin """
        st=getToolByName(self, 'portal_skins')
        st.default_skin=default_skin

    # Set the skin on the page to the specified value
    # Can be called from a page template, but it must be called before
    # anything anything on the skin path is resolved (e.g. main_template).
    # XXX Note: This method will eventually be replaced by the setCurrentSkin
    # method that is slated for CMF 1.4
    security.declarePublic('setCurrentSkin')
    def setCurrentSkin(self, skin_name):
        """ sets the current skin """
        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal._v_skindata=(self.REQUEST, self.getSkinByName(skin_name), {} )

    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'changeOwnershipOf')
    def changeOwnershipOf(self, object, owner, recursive=0):
        """ changes the ownership of an object """
        membership=getToolByName(self, 'portal_membership')
        if owner not in membership.listMemberIds():
            raise KeyError, 'Only users in this site can be made owners.'
        acl_users=getattr(self, 'acl_users')
        user = acl_users.getUser(owner)
        if user is not None:
            user = user.__of__(acl_users)
        else:
            from AccessControl import getSecurityManager
            user = getSecurityManager().getUser()

        catalog_tool=getToolByName(self, 'portal_catalog')
        object.changeOwnership(user, recursive)

        def fixOwnerRole(object, user_id):
            # Get rid of all other owners
            owners = object.users_with_local_role('Owner')
            for o in owners:
                roles = list(object.get_local_roles_for_userid(o))
                roles.remove('Owner')
                if roles:
                    object.manage_setLocalRoles(o, roles)
                else:
                    object.manage_delLocalRoles([o])
            # Fix for 1750
            roles = list(object.get_local_roles_for_userid(user_id))
            roles.append('Owner')
            object.manage_setLocalRoles(user_id, roles)

        fixOwnerRole(object, user.getId())
        catalog_tool.reindexObject(object)

        if recursive:
            purl = getToolByName(self, 'portal_url')
            _path = purl.getRelativeContentURL(object)
            subobjects=[b.getObject() for b in \
                        catalog_tool(path={'query':_path,'level':1})]
            for obj in subobjects:
                fixOwnerRole(obj, user.getId())
                catalog_tool.reindexObject(obj)

    security.declarePublic('urlparse')
    def urlparse(self, url):
        """ Returns the pieces of url in a six-part tuple.

        See Python standard library urlparse.urlparse
        http://python.org/doc/lib/module-urlparse.html
        """
        return urlparse.urlparse(url)

    security.declarePublic('urlunparse')
    def urlunparse(self, url_tuple):
        """ Puts a url back together again, in the manner that urlparse breaks it.

        See also Python standard library: urlparse.urlunparse
        http://python.org/doc/lib/module-urlparse.html
        """
        return urlparse.urlunparse(url_tuple)

    # Enable scripts to get the string value of an exception
    # even if the thrown exception is a string and not a
    # subclass of Exception.
    def exceptionString(self):
        s = sys.exc_info()[:2]  # don't assign the traceback to s
                                # (otherwise will generate a circular reference)
        if s[0] == None:
            return None
        if type(s[0]) == type(''):
            return s[0]
        return str(s[1])

    # provide a way of dumping an exception to the log even if we
    # catch it and otherwise ignore it
    def logException(self):
        """Dump an exception to the log"""
        log(summary=self.exceptionString(),
            text='\n'.join(traceback.format_exception(*sys.exc_info())),
            log_level=WARNING)

    security.declarePublic('createSitemap')
    def createSitemap(self, context):
        return self.createNavTree(context, sitemap=1)

    def _addToNavTreeResult(self, result, data):
        """ add a piece of content to the result tree """
        path = data['path']
        parentpath = '/'.join(path.split('/')[:-1])
        # Tell parent about self
        if result.has_key(parentpath):
            result[parentpath]['children'].append(data)
        else:
            result[parentpath] = {'children':[data]}
        # If we have processed a child already, make sure we register it
        # as a child
        if result.has_key(path):
            data['children'] = result[path]['children']
        result[path] = data

    security.declarePublic('createNavTree')
    def createNavTree(self, context, sitemap=None):
        """Returns a structure that can be used by
        navigation_tree_slot."""
        ct=getToolByName(self, 'portal_catalog')
        ntp=getToolByName(self, 'portal_properties').navtree_properties
        currentPath = None

        custom_query = getattr(self, 'getCustomNavQuery', None)
        if custom_query is not None and safe_callable(custom_query):
            query = custom_query()
        else:
            query = {}

        # XXX check if isDefaultPage is in the catalogs
        #query['isDefaultPage'] = 0

        if context == self or sitemap:
            currentPath = getToolByName(self, 'portal_url').getPortalPath()
            query['path'] = {'query':currentPath, 'depth':ntp.sitemapDepth}
        else:
            currentPath = '/'.join(context.getPhysicalPath())
            query['path'] = {'query':currentPath, 'navtree':1}

        if ntp.typesToList:
            query['portal_type'] = ntp.typesToList

        if ntp.sortAttribute:
            query['sort_on'] = ntp.sortAttribute

        if ntp.sortAttribute and ntp.sortOrder:
            query['sort_order'] = ntp.sortOrder

        # Get ids not to list and make a dict to make the search fast
        ids_not_to_list = ntp.idsNotToList
        excluded_ids = {}
        for exc_id in ids_not_to_list:
            excluded_ids[exc_id] = 1

        rawresult = ct(**query)

        # Build result dict
        result = {}
        foundcurrent = False
        for item in rawresult:
            path = item.getPath()
            currentItem = path == currentPath
            if currentItem:
                foundcurrent = path
            data = {'Title':item.Title or self.utf8_portal('\xe2\x80\xa6', 'ignore'),
                    'currentItem':currentItem,
                    'absolute_url': item.getURL(),
                    'getURL':item.getURL(),
                    'path': path,
                    'icon':item.getIcon,
                    'creation_date': item.CreationDate,
                    'review_state': item.review_state,
                    'Description':item.Description,
                    'children':[],
                    'no_display': excluded_ids.has_key(item.getId) or item.exclude_from_nav}
            self._addToNavTreeResult(result, data)

        portalpath = getToolByName(self, 'portal_url').getPortalPath()

        if ntp.showAllParents:
            portal = getToolByName(self, 'portal_url').getPortalObject()
            parent = context
            parents = [parent]
            while not parent is portal:
                parent = parent.aq_parent
                parents.append(parent)

            wf_tool = getToolByName(self, 'portal_workflow')
            for item in parents:
                path = '/'.join(item.getPhysicalPath())
                if not result.has_key(path) or \
                   not result[path].has_key('path'):
                    # item was not returned in catalog search
                    if foundcurrent:
                        currentItem = False
                    else:
                        currentItem = path == currentPath
                        if currentItem:
                            if self.isDefaultPage(item):
                                # don't list folder default page
                                continue
                            else:
                                foundcurrent = path
                    try:
                        review_state = wf_tool.getInfoFor(item, 'review_state')
                    except WorkflowException:
                        review_state = ''
                    data = {'Title': item.Title() or self.utf8_portal('\xe2\x80\xa6', 'ignore'),
                            'currentItem': currentItem,
                            'absolute_url': item.absolute_url(),
                            'getURL': item.absolute_url(),
                            'path': path,
                            'icon': item.getIcon(),
                            'creation_date': item.CreationDate(),
                            'review_state': review_state,
                            'Description':item.Description(),
                            'children':[],
                            'portal_type':item.portal_type,
                            'no_display': 0}
                    self._addToNavTreeResult(result, data)

        if not foundcurrent:
            #    result['/'.join(currentPath.split('/')[:-1])]['currentItem'] = True
            for i in range(1, len(currentPath.split('/')) - len(portalpath.split('/')) + 1):
                p = '/'.join(currentPath.split('/')[:-i])
                if result.has_key(p):
                    foundcurrent = p
                    result[p]['currentItem'] = True
                    break

        if result.has_key(portalpath):
            return result[portalpath]
        else:
            return {}

    security.declarePublic('createTopLevelTabs')
    def createTopLevelTabs(self):
        """Returns a structure for the top level tabs"""
        ct=getToolByName(self, 'portal_catalog')
        ntp=getToolByName(self, 'portal_properties').navtree_properties
        stp=getToolByName(self, 'portal_properties').site_properties

        if stp.getProperty('disable_folder_sections', None):
            return []

        custom_query = getattr(self, 'getCustomNavQuery', None)
        if custom_query is not None and safe_callable(custom_query):
            query = custom_query()
        else:
            query = {}

        portal_path = getToolByName(self, 'portal_url').getPortalPath()
        query['path'] = {'query':portal_path, 'navtree':1}

        if ntp.typesToList:
            query['portal_type'] = ntp.typesToList

        if ntp.sortAttribute:
            query['sort_on'] = ntp.sortAttribute

        if ntp.sortAttribute and ntp.sortOrder:
            query['sort_order'] = ntp.sortOrder

        # Get ids not to list and make a dict to make the search fast
        ids_not_to_list = ntp.idsNotToList
        excluded_ids = {}
        for exc_id in ids_not_to_list:
            excluded_ids[exc_id]=1

        rawresult = ct(**query)

        # Build result dict
        result = []
        for item in rawresult:
            if not (excluded_ids.has_key(item.getId) or item.exclude_from_nav):
                data = {'name':item.Title or self.utf8_portal('\xe2\x80\xa6', 'ignore'),
                        'id':item.getId, 'url': item.getURL(), 'description':item.Description}
                result.append(data)
        return result

    security.declarePublic('createBreadCrumbs')
    def createBreadCrumbs(self, context):
        "Returns a structure for the portal breadcumbs"""
        ct=getToolByName(self, 'portal_catalog')
        query = {}

        #Check to see if the current page is a folder default view, if so
        #get breadcrumbs from the parent folder
        if self.isDefaultPage(context):
            currentPath = '/'.join(context.aq_inner.aq_parent.getPhysicalPath())
        else:
            currentPath = '/'.join(context.getPhysicalPath())
        query['path'] = {'query':currentPath, 'navtree':1, 'depth': 0}

        rawresult = ct(**query)

        #sort items on path length
        dec_result = [(len(r.getPath()),r) for r in rawresult]
        dec_result.sort()

        # Build result dict
        result = []
        for r_tuple in dec_result:
            item = r_tuple[1]
            data = {'Title':item.Title or self.utf8_portal('\xe2\x80\xa6', 'ignore'),
                    'absolute_url': item.getURL()}
            result.append(data)
        return result

    # expose ObjectManager's bad_id test to skin scripts
    security.declarePublic('good_id')
    def good_id(self, id):
        m = bad_id(id)
        if m is not None:
            return 0
        return 1

    # add a helper function to show what chars are bad in the
    # good_id function
    security.declarePublic('bad_chars')
    def bad_chars(self, id):
        """ Returns a list of the Bad characters """
        return BAD_CHARS(id)

    # returns the acquired local roles
    security.declarePublic('getInheritedLocalRoles')
    def getInheritedLocalRoles(self, here):
        portal = here.portal_url.getPortalObject()
        result=[]
        cont=1
        if portal != here:
            parent = here.aq_parent
            while cont:
                userroles = parent.acl_users.getLocalRolesForDisplay(parent)
                for user, roles, role_type, name in userroles:
                    # find user in result
                    found=0
                    for user2, roles2, type2, name2 in result:
                        if user2==user:
                            # check which roles must be added to roles2
                            for role in roles:
                                if not role in roles2:
                                    roles2=roles2.append(role)
                            found=1
                            break
                    if found==0:
                        # add it to result
                        # make sure roles is a list so we may append and not
                        # overwrite the loop variable
                        result.append([user, list(roles), role_type, name])
                if parent==portal:
                    cont=0
		elif not self.isLocalRoleAcquired(parent):
                    # role acq check here
                    cont=0
                else:
                    parent=parent.aq_parent

        # Tuplize all inner roles
        for pos in range(len(result)-1,-1,-1):
            result[pos][1] = tuple(result[pos][1])
            result[pos] = tuple(result[pos])

        return tuple(result)

    security.declarePublic('browserDefault')
    def browserDefault(self, obj):
        """Set default so we can return whatever we want instead of
        index_html
        """
        # WebDAV in Zope is odd it takes the incoming verb eg: PROPFIND
        # and then requests that object, for example for: /, with verb PROPFIND
        # means acquire PROPFIND from the folder and call it
        # its all very odd and WebDAV'y
        request = getattr(self, 'REQUEST', None)
        if request and request.has_key('REQUEST_METHOD'):
            if request['REQUEST_METHOD'] not in  ['GET', 'HEAD', 'POST']:
                return obj, [request['REQUEST_METHOD']]
        # now back to normal

        portal = getToolByName(self, 'portal_url').getPortalObject()
        wftool = getToolByName(self, 'portal_workflow')

        # The list of ids where we look for default
        ids = {}
        # For BTreeFolders we just use the has_key, otherwise build a dict
        if hasattr(aq_base(obj), 'has_key'):
            ids = obj
        else:
            for id in obj.objectIds():
                ids[id] = 1

        # Looking up translatable is done several places so we make a
        # method for it.
        def returnPage(obj, page):
            # Only look up for untranslated folderish content,
            # in translated containers we assume the container has default page
            # in the correct language.
            implemented = ITranslatable.isImplementedBy(obj)
            if not implemented or implemented and not obj.isTranslation():
                pageobj = getattr(obj,page,None)
                if pageobj is not None and ITranslatable.isImplementedBy(pageobj):
                    translation = pageobj.getTranslation()
                    if translation is not None and \
                       wftool.getInfoFor(pageobj, 'review_state') == wftool.getInfoFor(translation, 'review_state'):
                        if ids.has_key(translation.getId()):
                            return obj, [translation.getId()]
                        else:
                            return translation, ['view']
            return obj, [page]

        # Look for a default_page managed by an IBrowserDefault-implementing
        # object - the behaviour is the same as setting default_page manually
        # on the object, and the current BrowserDefaultMixin implementation
        # actually stores it as the default_page property, but it's nicer to be
        # explicit about getting it from IBrowserDefault
        if IBrowserDefault.isImplementedBy(obj):
            page = obj.getDefaultPage()
            # Be totally anal and triple-check...
            if page and ids.has_key(page):
                return returnPage(obj, page)
            # IBrowserDefault only manages explicitly contained
            # default_page's, so don't look for the id in the skin layers

        # Look for default_page on the object
        pages = getattr(aq_base(obj), 'default_page', [])
        # Make sure we don't break if default_page is a
        # string property instead of a sequence
        if type(pages) in (StringType, UnicodeType):
            pages = [pages]
        # And also filter out empty strings
        pages = filter(None, pages)
        for page in pages:
            if ids.has_key(page):
                return returnPage(obj, page)
        # we look for the default_page in the portal and/or skins aswell.
        # Use path/to/template to reference an object or a skin.
        for page in pages:
            if portal.unrestrictedTraverse(page,None):
                return obj, page.split('/')

        # Try the default sitewide default_page setting
        for page in portal.portal_properties.site_properties.getProperty('default_page', []):
            if ids.has_key(page):
                return returnPage(obj, page)

        # No luck, let's look for hardcoded defaults
        default_pages = ['index_html', ]
        for page in default_pages:
            if ids.has_key(page):
                return returnPage(obj, page)

        # Look for layout page templates from IBrowserDefault implementations
        # This is checked after default_page and index_html, because we want
        # explicitly created index_html's to override any templates set
        if IBrowserDefault.isImplementedBy(obj):
            page = obj.getLayout()
            if page and portal.unrestrictedTraverse(page, None):
                return obj, page.split('/')

        # what if the page isnt found?
        try:
            # look for a type action called "folderlisting"
            act = obj.getTypeInfo().getActionById('folderlisting')
            if act.startswith('/'):
                act = act[1:]
            return obj, [act]
        except ConflictError:
            raise
        except:
            portal.plone_log("plone_utils.browserDefault",
            'Failed to get folderlisting action for folder "%s"' \
            % obj.absolute_url())
            return obj, ['folder_listing']

    security.declarePublic('isDefaultPage')
    def isDefaultPage(self, obj):
        """Find out if the given obj is the default page in its parent folder.
        Only considers explicitly contained objects, either set as index_html,
        with the default_page property, or using IBrowserDefault.
        """

        parent = obj.aq_inner.aq_parent

        if not parent:
            return False

        # Explicitly look at IBrowserDefault
        if IBrowserDefault.isImplementedBy(parent):
            page = parent.getDefaultPage()
            if page and page == obj.getId():
                return True

        # Look for default_page on the object
        pages = getattr(aq_base(obj), 'default_page', [])

        # Make sure we don't break if default_page is a
        # string property instead of a sequence
        if type(pages) in (StringType, UnicodeType):
            pages = [pages]

        # And also filter out empty strings
        pages = filter(None, pages)
        for page in pages:
            if page == obj.getId():
                return True

        utool = getToolByName(self, 'portal_url')
        portal = utool.getPortalObject()

        # Try the default sitewide default_page setting
        for page in portal.portal_properties.site_properties.getProperty('default_page', []):
            if page == obj.getId():
                return True

        # No luck, let's look for hardcoded defaults
        default_pages = ['index_html', ]
        for page in default_pages:
            if page == obj.getId():
                return True

        return False

    security.declarePublic('isTranslatable')
    def isTranslatable(self, obj):
        return ITranslatable.isImplementedBy(obj)

    security.declarePublic("acquireLocalRoles")
    def acquireLocalRoles(self, obj, status = 1):
        """If status is 1, allow acquisition of local roles (regular behaviour).
        If it's 0, prohibit it (it will allow some kind of local role blacklisting).
        GRUF IS REQUIRED FOR THIS TO WORK.
        """
        mt = getToolByName(self, 'portal_membership')
        if not mt.checkPermission(CMFCorePermissions.ModifyPortalContent, obj):
            raise Unauthorized

        # Set local role status
        gruf = getToolByName( self, 'portal_url' ).getPortalObject().acl_users
        gruf._acquireLocalRoles(obj, status)   # We perform our own security check

        # Reindex the whole stuff.
        obj.reindexObjectSecurity()

    security.declarePublic("isLocalRoleAcquired")
    def isLocalRoleAcquired(self, obj):
        """GRUF IS REQUIRED FOR THIS TO WORK.
        Return Local Role acquisition blocking status. True if normal, false if blocked.
        """
        gruf = getToolByName( self, 'portal_url' ).getPortalObject().acl_users
        return gruf.isLocalRoleAcquired(obj, )

    security.declarePublic("getOwnerId")
    def getOwnerId(self, obj):
        """Returns the userid of the owner of an object
        """
        mt = getToolByName(self, 'portal_membership')
        if not mt.checkPermission(CMFCorePermissions.View, obj):
            raise Unauthorized

        return obj.owner_info()['id']

    security.declarePublic('normalizeISO')
    def normalizeISO(self, text=""):
        """
        Convert unicode characters to ASCII

        normalizeISO() will turn unicode characters into nice, safe ASCII. for
        some characters, it will try to transliterate them to something fairly
        reasonable. for other characters that it can't transliterate, it will just
        return the numerical value(s) of the bytes in the character (in hex).

        >>> normalizeISO(u"\xe6")
        'e'

        >>> normalizeISO(u"a")
        'a'

        >>> normalizeISO(u"\u9ad8")
        '9ad8'

        """
        return "".join([_normalizeChar(c) for c in text]).encode('ascii')

    security.declarePublic('titleToNormalizedId')
    def titleToNormalizedId(self, title=""):
        """
        Normalize a title to an id

        titleToNormalizedId() converts a whole string to a normalized form that
        should be safe to use as in a url, as a css id, etc.

        all punctuation and spacing is removed and replaced with a '-':

        >>> titleToNormalizedId("a string with spaces")
        'a-string-with-spaces'

        >>> titleToNormalizedId("p.u,n;c(t)u!a@t#i$o%n")
        'p-u-n-c-t-u-a-t-i-o-n'

        strings are lowercased:

        >>> titleToNormalizedId("UppERcaSE")
        'uppercase'

        punctuation, spaces, etc. are trimmed and multiples are reduced to just
        one:

        >>> titleToNormalizedId(" a string    ")
        'a-string'

        >>> titleToNormalizedId(">here's another!")
        'here-s-another'

        >>> titleToNormalizedId("one with !@#$!@#$ stuff in the middle")
        'one-with-stuff-in-the-middle'

        the exception to all this is that if there is something that looks like a
        filename with an extension at the end, it will preserve the last period.

        >>> titleToNormalizedId("this is a file.gif")
        'this-is-a-file.gif'

        >>> titleToNormalizedId("this is. also. a file.html")
        'this-is-also-a-file.html'

        titleToNormalizedId() uses normalizeISO() to convert stray unicode
        characters. it will attempt to transliterate many of the common european
        accented letters to rough ASCII equivalents:

        >>> titleToNormalizedId(u"Eksempel \xe6\xf8\xe5 norsk \xc6\xd8\xc5")
        'eksempel-eoa-norsk-eoa'

        for characters that we can't transliterate, we just return the hex codes of
        the byte(s) in the character. not pretty, but about the best we can do.

        >>> titleToNormalizedId(u"\u9ad8\u8054\u5408 Chinese")
        '9ad880545408-chinese'

        >>> titleToNormalizedId(u"\uc774\ubbf8\uc9f1 Korean")
        'c774bbf8c9f1-korean'
        """

        # Make sure we are dealing with a unicode string
        if not isinstance(title, unicode):
            title = unicode(title, self.getSiteEncoding())

        title = title.lower()
        title = title.strip()
        title = self.normalizeISO(title)

        base = title
        ext   = ""

        m = re.match(r"^(.+)\.(\w{,4})$",title)
        if m:
            base = m.groups()[0]
            ext  = m.groups()[1]

        base = re.sub(r"[\W\-]+", "-", base)
        base = re.sub(r"^\-+",    "",  base)
        base = re.sub(r"\-+$",    "",  base)

        if ext != "":
            base = base + "." + ext
        return base

    security.declarePublic('listMetaTags')
    def listMetaTags(self, context):
        """List meta tags helper

        Creates a mapping of meta tags -> values for the listMetaTags script
        """
        result = {}

        site_props = getToolByName(self, 'portal_properties').site_properties

        use_all = site_props.getProperty('exposeDCMetaTags', None)

        if not use_all:
            metadata_names = {'Description': METADATA_DCNAME['Description']}
        else:
            metadata_names = METADATA_DCNAME

        for accessor, key in metadata_names.items():
            method = getattr(aq_inner(context).aq_explicit, accessor, None)
            if not callable(method):
                # ups
                continue

            # Catch AttributeErrors raised by some AT applications
            try:
                value = method()
            except AttributeError:
                value = None

            if not value:
                # no data
                continue
            if accessor == 'Publisher' and value == 'No publisher':
                # No publisher is hardcoded (XXX: still?)
                continue
            if isinstance(value, (list, tuple)):
                # convert a list to a string
                value = ', '.join(value)

            # special cases
            if accessor == 'Description':
                result['description'] = value
            elif accessor == 'Subject':
                result['keywords'] = value

            if use_all:
                result[key] = value

        if use_all:
            created = context.CreationDate()

            try:
                effective = context.EffectiveDate()
                if effective == 'None':
                    effective = None
                if effective:
                    effective = DateTime(effective)
            except AttributeError:
                effective = None

            try:
                expires = context.ExpirationDate()
                if expires == 'None':
                    expires = None
                if expires:
                    expires = DateTime(expires)
            except AttributeError:
                expires = None

            #   Filter out DWIMish artifacts on effective / expiration dates
            if effective is not None and effective > FLOOR_DATE and effective != created:
                eff_str = effective.Date()
            else:
                eff_str = ''

            if expires is not None and expires < CEILING_DATE:
                exp_str = expires.Date()
            else:
                exp_str = ''

            if exp_str or exp_str:
                result['DC.date.valid_range'] = '%s - %s' % (eff_str, exp_str)

        return result

    security.declarePublic('getUserFriendlyTypes')
    def getUserFriendlyTypes(self, typesList=[]):
        """Get a list of types which are considered "user friendly" for search
        and selection purposes. This is the list of types available in the
        portal, minus those defines in the types_not_searched property in
        site_properties, if it exists. If typesList is given, this is used
        as the base list; else all types from portal_types are used.
        """

        ptool = getToolByName(self, 'portal_properties')
        siteProperties = getattr(ptool, 'site_properties')
        blacklistedTypes = siteProperties.getProperty('types_not_searched', [])

        ttool = getToolByName(self, 'portal_types')
        types = typesList or ttool.listContentTypes()

        friendlyTypes = []
        for t in types:
            if not t in blacklistedTypes and not t in friendlyTypes:
                friendlyTypes.append(t)

        return friendlyTypes


InitializeClass(PloneTool)

