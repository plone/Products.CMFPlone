import re
import sys
import traceback
from types import TupleType, UnicodeType, StringType
import urlparse

from Products.CMFPlone.utils import safe_callable
from Products.CMFPlone.utils import log
from Products.CMFPlone.utils import log_exc
from Products.CMFPlone import transaction

from AccessControl import getSecurityManager
from Acquisition import aq_base, aq_inner, aq_parent

from ComputedAttribute import ComputedAttribute

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
from Products.CMFPlone import ToolNames
from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone.interfaces.BrowserDefault import IBrowserDefault

from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import bad_id
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, Unauthorized
from ZODB.POSException import ConflictError
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from DateTime import DateTime
DateTime.SyntaxError
from Products.CMFPlone.UnicodeNormalizer import normalizeUnicode
from Products.CMFPlone.PloneFolder import ReplaceableWrapper

AllowSendto = "Allow sendto"
CMFCorePermissions.setDefaultRoles(AllowSendto, 
                                   ('Anonymous', 'Manager',))

_marker = ()
_icons = {}

CEILING_DATE = DefaultDublinCoreImpl._DefaultDublinCoreImpl__CEILING_DATE
FLOOR_DATE = DefaultDublinCoreImpl._DefaultDublinCoreImpl__FLOOR_DATE

from Products.SecureMailHost.SecureMailHost import EMAIL_RE
from Products.SecureMailHost.SecureMailHost import EMAIL_CUTOFF_RE
BAD_CHARS = re.compile(r'[^a-zA-Z0-9-_~,.$\(\)# ]').findall

# XXX Remove this when we don't depend on python2.1 any longer,
# use email.Utils.getaddresses instead
from rfc822 import AddressList
def _getaddresses(fieldvalues):
    """Return a list of (REALNAME, EMAIL) for each fieldvalue."""
    all = ', '.join(fieldvalues)
    a = AddressList(all)
    return a.addresslist

# dublic core accessor name -> metadata name
METADATA_DCNAME = {
    # The first two rows are handle in a special way
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
    meta_type = ToolNames.UtilsTool
    toolicon = 'skins/plone_images/site_icon.gif'
    security = ClassSecurityInfo()
    plone_tool = 1
    # Prefix for forms fields!?
    field_prefix = 'field_'

    __implements__ = (PloneBaseTool.__implements__,
                      SimpleItem.__implements__, )

    security.declareProtected(CMFCorePermissions.ManageUsers,
                              'setMemberProperties')
    def setMemberProperties(self, member, **properties):
        membership = getToolByName(self, 'portal_membership')
        if hasattr(member, 'getId'):
            member = member.getId()
        user = membership.getMemberById(member)
        user.setMemberProperties(properties)

    security.declarePublic('getSiteEncoding')
    def getSiteEncoding(self):
        """Get the default_charset or fallback to utf8."""
        pprop = getToolByName(self, 'portal_properties')
        default = 'utf-8'
        try:
            charset = pprop.site_properties.getProperty('default_charset', default)
        except AttributeError:
            charset = default
        return charset

    security.declarePublic('portal_utf8')
    def portal_utf8(self, str, errors='strict'):
        """Transforms an string in portal encoding to utf8."""
        charset = self.getSiteEncoding()
        if charset.lower() in ('utf-8', 'utf8'):
            # Test
            unicode(str, 'utf-8', errors)
            return str
        else:
            return unicode(str, charset, errors).encode('utf-8', errors)

    security.declarePublic('utf8_portal')
    def utf8_portal(self, str, errors='strict'):
        """Transforms an utf8 string to portal encoding."""
        charset = self.getSiteEncoding()
        if charset.lower() in ('utf-8', 'utf8'):
            # Test
            unicode(str, 'utf-8', errors)
            return str
        else:
            return unicode(str, 'utf-8', errors).encode(charset, errors)

    security.declarePrivate('getMailHost')
    def getMailHost(self):
        """Gets the MailHost."""
        return getattr(aq_parent(self), 'MailHost')

    security.declareProtected(AllowSendto, 'sendto')
    def sendto(self, send_to_address, send_from_address, comment,
               subject='Plone', **kwargs ):
        """Sends a link of a page to someone."""
        host = self.getMailHost()
        template = getattr(self, 'sendto_template')
        encoding = self.getSiteEncoding()
        # Cook from template
        message = template(self, send_to_address=send_to_address,
                           send_from_address=send_from_address,
                           comment=comment, subject=subject, **kwargs
                          )
        result = host.secureSend(message, send_to_address,
                                 send_from_address, subject=subject,
                                 subtype='plain', charset=encoding,
                                 debug=False
                                )

    security.declarePublic('validateSingleNormalizedEmailAddress')
    def validateSingleNormalizedEmailAddress(self, address):
        """Lower-level function to validate a single normalized email address,
        see validateEmailAddress.
        """
        host = self.getMailHost()
        return host.validateSingleNormalizedEmailAddress(address)

    security.declarePublic('validateSingleEmailAddress')
    def validateSingleEmailAddress(self, address):
        """Validate a single email address, see also validateEmailAddresses."""
        host = self.getMailHost()
        return host.validateSingleEmailAddress(address)

    security.declarePublic('validateEmailAddresses')
    def validateEmailAddresses(self, addresses):
        """Validate a list of possibly several email addresses, see also
        validateSingleEmailAddress.
        """
        host = self.getMailHost()
        return host.validateEmailAddresses(addresses)

    security.declarePublic('editMetadata')
    def editMetadata(self
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
        """Responsible for setting metadata on a content object.

        We assume the obj implements IDublinCoreMetadata.
        """
        mt = getToolByName(self, 'portal_membership')
        if not mt.checkPermission(CMFCorePermissions.ModifyPortalContent, obj):
            # FIXME: Some scripts rely on this being string?
            raise Unauthorized

        REQUEST = self.REQUEST
        pfx = self.field_prefix

        def getfield(request, name, default=None, pfx=pfx):
            return request.form.get(pfx + name, default)

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
            if type(allowDiscussion) == StringType:
                allowDiscussion = allowDiscussion.lower().strip()
            if allowDiscussion == 'default':
                allowDiscussion = None
            elif allowDiscussion == 'off':
                allowDiscussion = 0
            elif allowDiscussion == 'on':
                allowDiscussion = 1
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
            REQUEST = self.REQUEST
            id = REQUEST.get('id', '')
            id = REQUEST.get(self.field_prefix + 'id', '')
        if id != obj.getId():
            parent = aq_parent(aq_inner(obj))
            parent.manage_renameObject(obj.getId(), id)

    def _makeTransactionNote(self, obj, msg=''):
        #XXX Why not aq_parent()?
        relative_path = '/'.join(getToolByName(self, 'portal_url').getRelativeContentPath(obj)[:-1])
        charset = self.getSiteEncoding()
        if not msg:
            msg = relative_path + '/' + obj.title_or_id() + ' has been modified.'
        if isinstance(msg, UnicodeType):
            # Convert unicode to a regular string for the backend write IO.
            # UTF-8 is the only reasonable choice, as using unicode means
            # that Latin-1 is probably not enough.
            msg = msg.encode(charset)
        if not transaction.get().description:
            transaction_note(msg)

    security.declarePublic('contentEdit')
    def contentEdit(self, obj, **kwargs):
        """Encapsulates how the editing of content occurs."""
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
        """Returns a map of mimetypes.

        Requires mimetype registry from Archetypes 1.3.
        """
        mtr = getToolByName(self, 'mimetypes_registry')
        return mtr.list_mimetypes()

    security.declareProtected(CMFCorePermissions.View, 'getWorkflowChainFor')
    def getWorkflowChainFor(self, object):
        """Proxy the request for the chain to the workflow tool, as
        this method is private there.
        """
        wftool = getToolByName(self, 'portal_workflow')
        wfs = ()
        try:
            wfs = wftool.getChainFor(object)
        except ConflictError:
            raise
        except:
            pass
        return wfs

    security.declareProtected(CMFCorePermissions.View, 'getIconFor')
    def getIconFor(self, category, id, default=_marker):
        """Cache point for actionicons.getActionIcon call.

        Also we want to allow for a default icon id to be passed in.
        """
        # Short circuit the lookup
        if (category, id) in _icons.keys():
            return _icons[(category, id)]
        try:
            actionicons = getToolByName(self, 'portal_actionicons')
            iconinfo = actionicons.getActionIcon(category, id)
            icon = _icons.setdefault( (category, id), iconinfo )
        except KeyError:
            if default is not _marker:
                icon = default
            else:
                raise
        # We want to return the actual object
        return icon

    security.declareProtected(CMFCorePermissions.View, 'getReviewStateTitleFor')
    def getReviewStateTitleFor(self, obj):
        """Utility method that gets the workflow state title for the
        object's review_state.

        Returns None if no review_state found.
        """
        wf_tool = getToolByName(self, 'portal_workflow')
        wfs = ()
        review_states = ()
        objstate = None
        try:
            objstate = wf_tool.getInfoFor(obj, 'review_state')
            wfs = wf_tool.getWorkflowsFor(obj)
        except WorkflowException, e:
            pass
        if wfs:
            for w in wfs:
                if w.states.has_key(objstate):
                    return w.states[objstate].title
        return None

    security.declareProtected(CMFCorePermissions.View, 'getDiscussionThread')
    def getDiscussionThread(self, discussionContainer):
        """Given a discussionContainer, return the thread it is in, upwards,
        including the parent object that is being discussed.
        """
        if hasattr(discussionContainer, 'parentsInThread'):
            thread = discussionContainer.parentsInThread()
            if discussionContainer.portal_type == 'Discussion Item':
                thread.append(discussionContainer)
        else:
            if discussionContainer.id=='talkback':
                thread=[discussionContainer._getDiscussable()]
            else:
                thread = [discussionContainer]
        return thread

    # Convenience method since skinstool requires loads of acrobatics.
    # We use this for the reconfig form
    security.declareProtected(CMFCorePermissions.ManagePortal, 'setDefaultSkin')
    def setDefaultSkin(self, default_skin):
        """Sets the default skin."""
        st = getToolByName(self, 'portal_skins')
        st.default_skin = default_skin

    # Set the skin on the page to the specified value
    # Can be called from a page template, but it must be called before
    # anything anything on the skin path is resolved (e.g. main_template).
    # XXX Note: This method will eventually be replaced by the setCurrentSkin
    # method that is slated for CMF 1.4
    security.declarePublic('setCurrentSkin')
    def setCurrentSkin(self, skin_name):
        """Sets the current skin."""
        portal = getToolByName(self, 'portal_url').getPortalObject()
        portal._v_skindata = (self.REQUEST, self.getSkinByName(skin_name), {})

    security.declareProtected(CMFCorePermissions.ManagePortal,
                              'changeOwnershipOf')
    def changeOwnershipOf(self, object, owner, recursive=0):
        """Changes the ownership of an object."""
        membership = getToolByName(self, 'portal_membership')
        if owner not in membership.listMemberIds():
            raise KeyError, 'Only users in this site can be made owners.'
        acl_users = getattr(self, 'acl_users')
        user = acl_users.getUser(owner)
        if user is not None:
            user = user.__of__(acl_users)
        else:
            user = getSecurityManager().getUser()

        catalog_tool = getToolByName(self, 'portal_catalog')
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
            subobjects = [b.getObject() for b in \
                         catalog_tool(path={'query':_path,'level':1})]
            for obj in subobjects:
                fixOwnerRole(obj, user.getId())
                catalog_tool.reindexObject(obj)

    security.declarePublic('urlparse')
    def urlparse(self, url):
        """Returns the pieces of url in a six-part tuple.

        See Python standard library urlparse.urlparse:
        http://python.org/doc/lib/module-urlparse.html
        """
        return urlparse.urlparse(url)

    security.declarePublic('urlunparse')
    def urlunparse(self, url_tuple):
        """Puts a url back together again, in the manner that
        urlparse breaks it.

        See also Python standard library: urlparse.urlunparse:
        http://python.org/doc/lib/module-urlparse.html
        """
        return urlparse.urlunparse(url_tuple)

    # Enable scripts to get the string value of an exception even if the
    # thrown exception is a string and not a subclass of Exception.
    def exceptionString(self):
        # Don't assign the traceback to s
        # (otherwise will generate a circular reference)
        s = sys.exc_info()[:2]
        if s[0] == None:
            return None
        if type(s[0]) == type(''):
            return s[0]
        return str(s[1])

    # Provide a way of dumping an exception to the log even if we
    # catch it and otherwise ignore it
    def logException(self):
        """Dumps most recent exception to the log."""
        log_exc()

    security.declarePublic('createSitemap')
    def createSitemap(self, context):
        """Returns a sitemap navtree structure."""
        return self.createNavTree(context, sitemap=1)

    def _addToNavTreeResult(self, result, data):
        """Adds a piece of content to the result tree."""
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

    def typesToList(self):
        ntp = getToolByName(self, 'portal_properties').navtree_properties
        ttool = getToolByName(self, 'portal_types')
        bl = ntp.getProperty('metaTypesNotToList', ())
        bl_dict = {}
        for t in bl:
            bl_dict[t] = 1
        all_types = ttool.listContentTypes()
        wl = [t for t in all_types if not bl_dict.has_key(t)]
        return wl

    # XXX Please, refactor me! :-)
    security.declarePublic('createNavTree')
    def createNavTree(self, context, sitemap=None):
        """Returns a structure that can be used by navigation_tree_slot."""
        ct = getToolByName(self, 'portal_catalog')
        ntp = getToolByName(self, 'portal_properties').navtree_properties
        stp = getToolByName(self, 'portal_properties').site_properties
        view_action_types = stp.getProperty('typesUseViewActionInListings')
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
            query['path'] = {'query':currentPath, 
                             'depth':ntp.getProperty('sitemapDepth', 2)}
        else:
            currentPath = '/'.join(context.getPhysicalPath())
            query['path'] = {'query':currentPath, 'navtree':1}

        query['portal_type'] = self.typesToList()

        if ntp.getProperty('sortAttribute', False):
            query['sort_on'] = ntp.sortAttribute

        if (ntp.getProperty('sortAttribute', False) and 
            ntp.getProperty('sortOrder', False)):
            query['sort_order'] = ntp.sortOrder

        if ntp.getProperty('enable_wf_state_filtering', False):
            query['review_state'] = ntp.wf_states_to_show

        query['is_default_page'] = False

        parentTypesNQ = ntp.getProperty('parentMetaTypesNotToQuery', ())

        # Get ids not to list and make a dict to make the search fast
        ids_not_to_list = ntp.getProperty('idsNotToList', ())
        excluded_ids = {}
        for exc_id in ids_not_to_list:
            excluded_ids[exc_id] = 1

        rawresult = ct(**query)

        # Build result dict
        result = {}
        foundcurrent = False
        for item in rawresult:
            path = item.getPath()
            # Some types may require the 'view' action, respect this
            item_url = (item.portal_type in view_action_types and
                                    item.getURL() + '/view') or item.getURL()
            currentItem = path == currentPath
            if currentItem:
                foundcurrent = path
            data = {'Title':self.pretty_title_or_id(item),
                    'currentItem':currentItem,
                    'absolute_url': item_url,
                    'getURL':item_url,
                    'path': path,
                    'icon':item.getIcon,
                    'creation_date': item.CreationDate,
                    'portal_type': item.portal_type,
                    'review_state': item.review_state,
                    'Description':item.Description,
                    'show_children':item.portal_type not in parentTypesNQ,
                    'children':[],
                    'no_display': excluded_ids.has_key(item.getId) or not not item.exclude_from_nav}
            self._addToNavTreeResult(result, data)

        portalpath = getToolByName(self, 'portal_url').getPortalPath()

        if ntp.getProperty('showAllParents', False):
            portal = getToolByName(self, 'portal_url').getPortalObject()
            parent = context
            parents = [parent]
            while not parent is portal:
                parent = parent.aq_parent
                parents.append(parent)

            wf_tool = getToolByName(self, 'portal_workflow')
            for item in parents:
                if getattr(item, 'getPhysicalPath', None) is None:
                    # when Z3-style views are used, the view class will be in
                    # the 'parents' list, but will not support 'getPhysicalPath'
                    # we can just skip it b/c it's not an object in the content
                    # tree that should be showing up in the nav tree (ra)
                    continue
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
                    # Some types may require the 'view' action, respect this
                    item_url = (item.portal_type in view_action_types and
                         item.absolute_url() + '/view') or item.absolute_url()
                    data = {'Title': self.pretty_title_or_id(item),
                            'currentItem': currentItem,
                            'absolute_url': item_url,
                            'getURL': item_url,
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
        """Returns a structure for the top level tabs."""
        ct = getToolByName(self, 'portal_catalog')
        ntp = getToolByName(self, 'portal_properties').navtree_properties
        stp = getToolByName(self, 'portal_properties').site_properties
        view_action_types = stp.getProperty('typesUseViewActionInListings')

        if stp.getProperty('disable_folder_sections', None):
            return []

        custom_query = getattr(self, 'getCustomNavQuery', None)
        if custom_query is not None and safe_callable(custom_query):
            query = custom_query()
        else:
            query = {}

        portal_path = getToolByName(self, 'portal_url').getPortalPath()
        query['path'] = {'query':portal_path, 'navtree':1}

        query['portal_type'] = self.typesToList()

        if ntp.getProperty('sortAttribute', False):
            query['sort_on'] = ntp.sortAttribute

        if (ntp.getProperty('sortAttribute', False) and 
            ntp.getProperty('sortOrder', False)):
            query['sort_order'] = ntp.sortOrder

        if ntp.getProperty('enable_wf_state_filtering', False):
            query['review_state'] = ntp.wf_states_to_show

        query['is_default_page'] = False
        query['is_folderish'] = True

        # Get ids not to list and make a dict to make the search fast
        ids_not_to_list = ntp.getProperty('idsNotToList', ())
        excluded_ids = {}
        for exc_id in ids_not_to_list:
            excluded_ids[exc_id]=1

        rawresult = ct(**query)

        # Build result dict
        result = []
        for item in rawresult:
            if not (excluded_ids.has_key(item.getId) or item.exclude_from_nav):
                item_url = (item.portal_type in view_action_types and
                         item.getURL() + '/view') or item.getURL()
                data = {'name': self.pretty_title_or_id(item),
                        'id':item.getId, 'url': item_url, 'description':item.Description}
                result.append(data)
        return result

    security.declarePublic('createBreadCrumbs')
    def createBreadCrumbs(self, context):
        """Returns a structure for the portal breadcumbs."""
        ct = getToolByName(self, 'portal_catalog')
        stp = getToolByName(self, 'portal_properties').site_properties
        view_action_types = stp.getProperty('typesUseViewActionInListings')
        query = {}

        # Check to see if the current page is a folder default view, if so
        # get breadcrumbs from the parent folder
        if self.isDefaultPage(context):
            currentPath = '/'.join(context.aq_inner.aq_parent.getPhysicalPath())
        else:
            currentPath = '/'.join(context.getPhysicalPath())
        query['path'] = {'query':currentPath, 'navtree':1, 'depth': 0}

        rawresult = ct(**query)

        # Sort items on path length
        dec_result = [(len(r.getPath()),r) for r in rawresult]
        dec_result.sort()

        # Build result dict
        result = []
        for r_tuple in dec_result:
            item = r_tuple[1]
            item_url = (item.portal_type in view_action_types and
                         item.getURL() + '/view') or item.getURL()
            data = {'Title': self.pretty_title_or_id(item),
                    'absolute_url': item_url}
            result.append(data)
        return result

    security.declarePublic('good_id')
    def good_id(self, id):
        """Exposes ObjectManager's bad_id test to skin scripts."""
        m = bad_id(id)
        if m is not None:
            return 0
        return 1

    security.declarePublic('bad_chars')
    def bad_chars(self, id):
        """Returns a list of the Bad characters."""
        return BAD_CHARS(id)

    security.declarePublic('getInheritedLocalRoles')
    def getInheritedLocalRoles(self, here):
        """Returns a tuple with the acquired local roles."""
        portal = here.portal_url.getPortalObject()
        result = []
        cont = 1
        if portal != here:
            parent = here.aq_parent
            while cont:
                userroles = parent.acl_users.getLocalRolesForDisplay(parent)
                for user, roles, role_type, name in userroles:
                    # Find user in result
                    found = 0
                    for user2, roles2, type2, name2 in result:
                        if user2 == user:
                            # Check which roles must be added to roles2
                            for role in roles:
                                if not role in roles2:
                                    roles2.append(role)
                            found = 1
                            break
                    if found == 0:
                        # Add it to result and make sure roles is a list so
                        # we may append and not overwrite the loop variable
                        result.append([user, list(roles), role_type, name])
                if parent == portal:
                    cont = 0
                elif not self.isLocalRoleAcquired(parent):
                    # Role acquired check here
                    cont = 0
                else:
                    parent = parent.aq_parent

        # Tuplize all inner roles
        for pos in range(len(result)-1,-1,-1):
            result[pos][1] = tuple(result[pos][1])
            result[pos] = tuple(result[pos])

        return tuple(result)

    #
    # The three methods used in determining what the default-page of a folder
    # is. These are:
    #
    #   - getDefaultPage(folder)
    #       : get id of contentish object that is default-page in the folder
    #   - isDefaultPage(object)   
    #       : determine if an object is the default-page in its parent folder
    #   - browserDefault(object)  
    #       : lookup rules for old-style content types
    #

    security.declarePublic('isDefaultPage')
    def isDefaultPage(self, obj):
        """Finds out if the given obj is the default page in its parent folder.

        Only considers explicitly contained objects, either set as index_html,
        with the default_page property, or using IBrowserDefault.
        """

        parent = obj.aq_inner.aq_parent
        if not parent:
            return False

        parentDefaultPage = self.getDefaultPage(parent)
        if parentDefaultPage is None or '/' in parentDefaultPage:
            return False
        else:
            return (parentDefaultPage == obj.getId())

    security.declarePublic('getDefaultPage')
    def getDefaultPage(self, obj):
        """Given a folderish item, find out if it has a defaul-page using
        the following lookup rules:
        
            1. A content object called 'index_html' wins
            2. If the folder implements IBrowserDefault, query this
            3. Else, look up the property default_page on the object
                - Note that in this case, the returned id may *not* be of an
                  object in the folder, since it could be acquired from a
                  parent folder or skin layer
            4. Else, look up the property default_page in site_properties for
                magic ids and test these
            
        The id of the first matching item is returned. If no default page is
        set, None is returned. If a non-folderish item is passed in, return
        None always.
        """

        # XXX: This method is called by CMFDynamicViewFTI directly, as well
        # as by browserDefault() below. browserDefault() contains logic for
        # looking up ITranslatable (LinguaPlone), which browserDefault() retains.
        # However, browserDefault() is no longer called with CMF 1.5 and the new
        # CMFDynamicViewFTI. Because the lookup method is quite different, there
        # is no obvious way to make CMFDynamicViewFTI ITranslatable aware. Thus,
        # if/when LinguaPlone tries to use the new FTI to get CMF 1.5 / Plone 2.1
        # goodness, it will likely break. The simple workaround is to set the
        # (Default) method alias to an empty string, thus falling back on
        # __browser_default__(), but this reduces flexibility. Instead, tesdal
        # & co need to look at CMFDynamicViewFTI to make it ITranslatable aware.
        #   [~optilude]

        # Short circuit if we are not looking at a Folder
        if not obj.isPrincipiaFolderish:
            return None

        # The list of ids where we look for default
        ids = {}

        portal = getToolByName(self, 'portal_url').getPortalObject()
        wftool = getToolByName(self, 'portal_workflow')

        # For BTreeFolders we just use the has_key, otherwise build a dict
        if hasattr(aq_base(obj), 'has_key'):
            ids = obj
        else:
            for id in obj.objectIds():
                ids[id] = 1

        # 1. test for contentish index_html
        if ids.has_key('index_html'):
            return 'index_html'

        # 2. Test for IBrowserDefault
        if IBrowserDefault.isImplementedBy(obj):
            page = obj.getDefaultPage()
            if page is not None and ids.has_key(page):
                return page

        # 3. Test for default_page property in folder, then skins
        pages = getattr(aq_base(obj), 'default_page', [])
        if type(pages) in (StringType, UnicodeType):
            pages = [pages]
        for page in pages:
            if page and ids.has_key(page):
                return page
        for page in pages:
            if portal.unrestrictedTraverse(page, None):
                return page

        # 4. Test for default sitewide default_page setting
        for page in portal.portal_properties.site_properties.getProperty('default_page', []):
            if ids.has_key(page):
                return page

        return None

    security.declarePublic('browserDefault')
    def browserDefault(self, obj):
        """Sets default so we can return whatever we want instead of index_html.

        This method is complex, and interacts with mechanisms such as
        IBrowserDefault (implemented in CMFDynamicViewFTI), LinguaPlone and
        various mechanisms for setting the default page.

        The method returns a tuple (obj, [path]) where path is a path to
        a template or other object to be acquired and displayed on the object.
        The path is determined as follows:

        0. If we're coming from WebDAV, make sure we don't return a contained
            object "default page" ever
        1. If there is an index_html attribute (either a contained object or
            an explicit attribute) on the object, return that as the
            "default page". Note that this may be used by things like
            File and Image to return the contents of the file, for example,
            not just content-space objects created by the user.
        2. If the object implements IBrowserDefault, query this for the
            default page.
        3. If the object has a property default_page set and this gives a list
            of, or single, object id, and that object is is found in the
            folder or is the name of a skin template, return that id
        4. If the property default_page is set in site_properties and that
            property contains a list of ids of which one id is found in the
            folder, return that id
        5. If the object implements IBrowserDefault, try to get the selected
            layout.
        6. If the type has a 'folderlisting' action and no default page is
            set, use this action. This permits folders to have the default
            'view' action be 'string:${object_url}/' and hence default to
            a default page when clicking the 'view' tab, whilst allowing the
            fallback action to be specified TTW in portal_types (this action
            is typically hidden)
        7. If nothing else is found, fall back on the object's 'view' action.
        8. If this is not found, raise an AttributeError

        If the returned path is an object, it is checked for ITranslatable. An
        object which supports translation will then be translated before return.
        """

        # WebDAV in Zope is odd it takes the incoming verb eg: PROPFIND
        # and then requests that object, for example for: /, with verb PROPFIND
        # means acquire PROPFIND from the folder and call it
        # its all very odd and WebDAV'y
        request = getattr(self, 'REQUEST', None)
        if request and request.has_key('REQUEST_METHOD'):
            if request['REQUEST_METHOD'] not in  ['GET', 'POST']:
                return obj, [request['REQUEST_METHOD']]
        # Now back to normal

        portal = getToolByName(self, 'portal_url').getPortalObject()
        wftool = getToolByName(self, 'portal_workflow')

        # Looking up translatable is done several places so we make a
        # method for it.
        def returnPage(obj, page):
            # Only look up for untranslated folderish content,
            # in translated containers we assume the container has default page
            # in the correct language.
            implemented = ITranslatable.isImplementedBy(obj)
            if not implemented or implemented and not obj.isTranslation():
                pageobj = getattr(obj, page, None)
                if pageobj is not None and ITranslatable.isImplementedBy(pageobj):
                    translation = pageobj.getTranslation()
                    if translation is not None and \
                       wftool.getInfoFor(pageobj, 'review_state') == wftool.getInfoFor(translation, 'review_state'):
                        if ids.has_key(translation.getId()):
                            return obj, [translation.getId()]
                        else:
                            return translation, ['view']
            return obj, [page]

        # The list of ids where we look for default
        ids = {}

        # If we are not dealing with a folder, then leave this empty
        if obj.isPrincipiaFolderish:
            # For BTreeFolders we just use the has_key, otherwise build a dict
            if hasattr(aq_base(obj), 'has_key'):
                ids = obj
            else:
                for id in obj.objectIds():
                    ids[id] = 1

        #
        # 1. Get an attribute or contained object index_html
        #

        # Note: The base PloneFolder, as well as ATCT's ATCTOrderedFolder
        # defines a method index_html() which returns a ReplaceableWrapper.
        # This is needed for WebDAV to work properly, and to avoid implicit
        # acquisition of index_html's, which are generally on-object only.
        # For the purposes of determining a default page, we don't want to
        # use this index_html(), nor the ComputedAttribute which defines it.

        if not isinstance(getattr(obj, 'index_html', None), ReplaceableWrapper):
            index_obj = getattr(aq_base(obj), 'index_html', None)
            if index_obj is not None and not isinstance(index_obj, ComputedAttribute):
                return returnPage(obj, 'index_html')

        #
        # 2. Look for a default_page managed by an IBrowserDefault-implementing
        #    object
        #
        # 3. Look for a default_page property on the object
        #
        # 4. Try the default sitewide default_page setting
        #

        if obj.isPrincipiaFolderish:
            defaultPage = self.getDefaultPage(obj)
            if defaultPage is not None:
                if ids.has_key(defaultPage):
                    return returnPage(obj, defaultPage)
                else:
                    # For the default_page property, we may get things in the
                    # skin layers or with an explicit path - split this path
                    # to comply with the __browser_default__() spec
                    return obj, defaultPage.split('/')

        # 5. If there is no default page, try IBrowserDefault.getLayout()

        if IBrowserDefault.isImplementedBy(obj):
            return obj, [obj.getLayout()]

        #
        # 6. If the object has a 'folderlisting' action, use this
        #

        # This allows folders to determine in a flexible manner how they are
        # displayed when there is no default page, whilst still using
        # browserDefault() to show contained objects by default on the 'view'
        # action (this applies to old-style folders only, IBrowserDefault is
        # managed explicitly above)

        try:
            act = obj.getTypeInfo().getActionById('folderlisting')
            if act.startswith('/'):
                act = act[1:]
            return obj, [act]
        except ValueError:
            pass

        #
        # 7. Fall back on the 'view' action
        #

        try:
            act = obj.getTypeInfo().getActionById('view')
            if act.startswith('/'):
                act = act[1:]
            return obj, [act]
        except ValueError:
            pass

        #
        # 8. If we can't find this either, raise an exception
        #

        raise AttributeError, "Failed to get a default page or view_action for %s" %s (obj.absolute_url,)

    security.declarePublic('isTranslatable')
    def isTranslatable(self, obj):
        """Checks if a given object implements the ITranslatable interface."""
        return ITranslatable.isImplementedBy(obj)

    security.declarePublic('acquireLocalRoles')
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

    security.declarePublic('isLocalRoleAcquired')
    def isLocalRoleAcquired(self, obj):
        """Returns local role acquisition blocking status.

        True if normal, false if blocked.
        GRUF IS REQUIRED FOR THIS TO WORK.
        """
        gruf = getToolByName( self, 'portal_url' ).getPortalObject().acl_users
        return gruf.isLocalRoleAcquired(obj, )

    security.declarePublic('getOwnerId')
    def getOwnerId(self, obj):
        """Returns the userid of the owner of an object."""
        mt = getToolByName(self, 'portal_membership')
        if not mt.checkPermission(CMFCorePermissions.View, obj):
            raise Unauthorized
        return obj.owner_info()['id']

    security.declarePublic('normalizeString')
    def normalizeString(self, text):
        """Normalizes a title to an id.

        normalizeString() converts a whole string to a normalized form that
        should be safe to use as in a url, as a css id, etc.

        all punctuation and spacing is removed and replaced with a '-':

        >>> normalizeString("a string with spaces")
        'a-string-with-spaces'

        >>> normalizeString("p.u,n;c(t)u!a@t#i$o%n")
        'p-u-n-c-t-u-a-t-i-o-n'

        strings are lowercased:

        >>> normalizeString("UppERcaSE")
        'uppercase'

        punctuation, spaces, etc. are trimmed and multiples are reduced to just
        one:

        >>> normalizeString(" a string    ")
        'a-string'

        >>> normalizeString(">here's another!")
        'here-s-another'

        >>> normalizeString("one with !@#$!@#$ stuff in the middle")
        'one-with-stuff-in-the-middle'

        the exception to all this is that if there is something that looks like a
        filename with an extension at the end, it will preserve the last period.

        >>> normalizeString("this is a file.gif")
        'this-is-a-file.gif'

        >>> normalizeString("this is. also. a file.html")
        'this-is-also-a-file.html'

        normalizeString() uses normalizeUnicode() to convert stray unicode
        characters. it will attempt to transliterate many of the accented
        letters to rough ASCII equivalents:

        >>> normalizeString(u"Eksempel \xe6\xf8\xe5 norsk \xc6\xd8\xc5")
        'eksempel-eoa-norsk-eoa'

        for characters that we can't transliterate, we just return the hex codes of
        the byte(s) in the character. not pretty, but about the best we can do.

        >>> normalizeString(u"\u9ad8\u8054\u5408 Chinese")
        '9ad880545408-chinese'

        >>> normalizeString(u"\uc774\ubbf8\uc9f1 Korean")
        'c774bbf8c9f1-korean'
        """
        # Make sure we are dealing with a stringish type
        if not isinstance(text, basestring):
            # Catch the special None case or we would return 'none' evaluating
            # to True, which is totally unexpected
            # XXX This seems to break the autogenerated ids, reverting
            #if text is None:
            #    return None

            # This most surely ends up in something the user does not expect
            # to see. But at least it does not break.
            text = repr(text)

        # Make sure we are dealing with a unicode string
        if not isinstance(text, unicode):
            text = unicode(text, self.getSiteEncoding())

        text = text.lower()
        text = text.strip()
        text = normalizeUnicode(text)

        base = text
        ext  = ""

        m = re.match(r"^(.+)\.(\w{,4})$", text)
        if m is not None:
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
        """Lists meta tags helper.

        Creates a mapping of meta tags -> values for the listMetaTags script.
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
                continue

            # Catch AttributeErrors raised by some AT applications
            try:
                value = method()
            except AttributeError:
                value = None

            if not value:
                # No data
                continue
            if accessor == 'Publisher' and value == 'No publisher':
                # No publisher is hardcoded (XXX: still?)
                continue
            if isinstance(value, (list, tuple)):
                # convert a list to a string
                value = ', '.join(value)

            # Special cases
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

            # Filter out DWIMish artifacts on effective / expiration dates
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
        and selection purposes.

        This is the list of types available in the portal, minus those defines
        in the types_not_searched property in site_properties, if it exists.

        If typesList is given, this is used as the base list; else all types
        from portal_types are used.
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

    security.declarePublic('reindexOnReorder')
    def reindexOnReorder(self, parent):
        """ Catalog ordering support """

        # For now we will just reindex all objects in the folder. Later we may
        # optimize to only reindex the objs that got moved. Ordering is more
        # for humans than machines, therefore the fact that this won't scale
        # well for btrees isn't a huge issue, since btrees are more for
        # machines than humans.
        mtool = getToolByName(self, 'portal_membership')
        if not mtool.checkPermission(CMFCorePermissions.ModifyPortalContent,
                                                                    parent):
            return
        cat = getToolByName(self, 'portal_catalog')
        cataloged_objs = cat(path = {'query':'/'.join(parent.getPhysicalPath()), 'depth': 1})
        for brain in cataloged_objs:
            obj = brain.getObject()
            # Don't crash when the catalog has contains a stale entry
            if obj is not None:
                cat.reindexObject(obj,['getObjPositionInParent'],
                                                    update_metadata=0)
            else:
                # Perhaps we should remove the bad entry as well?
                log('Object in catalog no longer exists, cannot reindex: %s.'%
                                    brain.getPath())

    security.declarePublic('isIDAutoGenerated')
    def isIDAutoGenerated(self, id):
        """Determine if an id is autogenerated"""
        autogenerated=False

        # In 2.1 non-autogenerated is the common case, caught exceptions are
        # expensive, so let's make a cheap check first
        if id.count('.') != 2:
            return autogenerated

        try:
            pt = getToolByName(self, 'portal_types')
            obj_type, date_created, random_number = id.split('.')
            type=' '.join(obj_type.split('_'))
            portaltypes=pt.objectIds()
            # new autogenerated ids may have a lower case portal type
            if (type in portaltypes or type in [pt.lower() for pt in portaltypes] ) \
            and DateTime(date_created) and float(random_number):
                autogenerated=True
        except (ValueError, AttributeError, IndexError, DateTime.DateTimeError):
            pass

        return autogenerated

    security.declarePublic('getEmptyTitle')
    def getEmptyTitle(self, translated=True):
        """Returns string to be used for objects with no title or id"""
        empty = self.utf8_portal('\x5b\xc2\xb7\xc2\xb7\xc2\xb7\x5d', 'ignore')
        if translated:
            trans = getToolByName(self, 'translation_service')
            empty = trans.utranslate(domain='plone', msgid='title_unset', default=empty)
        return empty

    def pretty_title_or_id(self, obj, empty_value=_marker):
        """Return the best possible title or id of an item, regardless
        of whether obj is a catalog brain or an object, but returning an
        empty title marker if the id is not set (i.e. it's auto-generated).
        """
        obj = aq_base(obj)
        title = getattr(obj, 'Title', None)
        if safe_callable(title):
            title = title()
        if title:
            return title
        item_id = getattr(obj, 'getId', None)
        if safe_callable(item_id):
            item_id = item_id()
        if item_id and not self.isIDAutoGenerated(item_id):
            return item_id
        if empty_value is _marker:
            empty_value = self.getEmptyTitle()
        return empty_value

    def getMethodAliases(self, typeInfo):
        """Given an FTI, return the dict of method aliases defined on that
        FTI. If there are no method aliases (i.e. this FTI doesn't support it), 
        return None"""
        getMethodAliases = getattr(typeInfo, 'getMethodAliases', None)
        if getMethodAliases is not None and safe_callable(getMethodAliases):
            return getMethodAliases()
        else:
            return None

InitializeClass(PloneTool)
