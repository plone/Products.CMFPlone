from email.Utils import getaddresses
import re
import sys
from types import UnicodeType, StringType
import urlparse
import transaction

from zope.component import queryAdapter
from zope.deprecation import deprecate
from zope.interface import implements
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent

from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl import getSecurityManager
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from ComputedAttribute import ComputedAttribute
from DateTime import DateTime
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import bad_id
from ZODB.POSException import ConflictError

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions
from Products.CMFCore.permissions import AccessContentsInformation, \
                        ManagePortal, ManageUsers, ModifyPortalContent, View
from Products.CMFCore.interfaces import IDublinCore, IMutableDublinCore
from Products.CMFCore.interfaces import IDiscussable
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFDynamicViewFTI.interfaces import IBrowserDefault
from Products.CMFPlone.events import ReorderedEvent
from Products.CMFPlone.interfaces import IPloneTool
from Products.CMFPlone.interfaces import INonStructuralFolder
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFPlone.PloneFolder import ReplaceableWrapper
from Products.CMFPlone import utils
from Products.CMFPlone.utils import log
from Products.CMFPlone.utils import log_exc
from Products.CMFPlone.utils import transaction_note
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import safe_hasattr
from Products.statusmessages.interfaces import IStatusMessage
from AccessControl.requestmethod import postonly
from plone.app.linkintegrity.exceptions \
    import LinkIntegrityNotificationException

# BBB Plone 4.0
from zope.deprecation import __show__
__show__.off()
try:
    from Products.LinguaPlone.interfaces import ITranslatable
except ImportError:
    from Products.CMFPlone.interfaces.Translatable import ITranslatable
__show__.on()


AllowSendto = 'Allow sendto'
permissions.setDefaultRoles(AllowSendto, ('Authenticated', 'Manager', ))

_marker = utils._marker
_icons = {}

CEILING_DATE = DefaultDublinCoreImpl._DefaultDublinCoreImpl__CEILING_DATE
FLOOR_DATE = DefaultDublinCoreImpl._DefaultDublinCoreImpl__FLOOR_DATE
BAD_CHARS = bad_id.__self__.findall

# max 63 chars per label in domains, see RFC1035
EMAIL_RE = re.compile(r"^(\w&.%#$&'\*+-/=?^_`{}|~]+!)*[\w&.%#$&'\*+-/=?^_`{}|~]+@(([0-9a-z]([0-9a-z-]*[0-9a-z])?\.)+[a-z]{2,63}|([0-9]{1,3}\.){3}[0-9]{1,3})$", re.IGNORECASE)
# used to find double new line (in any variant)
EMAIL_CUTOFF_RE = re.compile(r".*[\n\r][\n\r]")

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
METADATA_DC_AUTHORFIELDS = ('Creator', 'Contributors', 'Publisher')


class PloneTool(PloneBaseTool, UniqueObject, SimpleItem):
    """Various utility methods."""

    id = 'plone_utils'
    meta_type = 'Plone Utility Tool'
    toolicon = 'skins/plone_images/site_icon.png'
    security = ClassSecurityInfo()
    plone_tool = 1
    # Prefix for forms fields!?
    field_prefix = 'field_'

    implements(IPloneTool)

    security.declareProtected(ManageUsers, 'setMemberProperties')
    def setMemberProperties(self, member, REQUEST=None, **properties):
        pas = getToolByName(self, 'acl_users')
        if safe_hasattr(member, 'getId'):
            member = member.getId()
        user = pas.getUserById(member)
        user.setProperties(**properties)

    security.declarePublic('getSiteEncoding')
    @deprecate(('`getSiteEncoding` is deprecated. Plone only supports UTF-8 '
                'currently. This method always returns "utf-8"'))
    def getSiteEncoding(self):
        """ Get the the site encoding, which is utf-8.

        >>> ptool = self.portal.plone_utils

        >>> ptool.getSiteEncoding()
        'utf-8'
        """
        return 'utf-8'

    security.declarePublic('portal_utf8')
    def portal_utf8(self, str, errors='strict'):
        """ Transforms an string in portal encoding to utf8.

        >>> ptool = self.portal.plone_utils
        >>> text = u'Eksempel \xe6\xf8\xe5'
        >>> sitetext = text.encode('utf-8')

        >>> ptool.portal_utf8(sitetext) == text.encode('utf-8')
        True
        """
        return utils.portal_utf8(self, str, errors)

    security.declarePublic('utf8_portal')
    def utf8_portal(self, str, errors='strict'):
        """ Transforms an utf8 string to portal encoding.

        >>> ptool = self.portal.plone_utils
        >>> text = u'Eksempel \xe6\xf8\xe5'
        >>> utf8text = text.encode('utf-8')

        >>> ptool.utf8_portal(utf8text) == text.encode('utf-8')
        True
        """
        return utils.utf8_portal(self, str, errors)

    security.declarePrivate('getMailHost')
    def getMailHost(self):
        """ Gets the MailHost.

        >>> ptool = self.portal.plone_utils

        >>> ptool.getMailHost()
        <MailHost ...>
        """
        return getattr(aq_parent(self), 'MailHost')

    security.declareProtected(AllowSendto, 'sendto')
    def sendto(self, send_to_address, send_from_address, comment,
               subject='Plone', **kwargs):
        # Sends a link of a page to someone.
        host = self.getMailHost()
        template = getattr(self, 'sendto_template')
        portal = getToolByName(self, 'portal_url').getPortalObject()
        encoding = portal.getProperty('email_charset')
        if 'envelope_from' in kwargs:
            envelope_from = kwargs['envelope_from']
        else:
            envelope_from = send_from_address
        # Cook from template
        message = template(self, send_to_address=send_to_address,
                           send_from_address=send_from_address,
                           comment=comment, subject=subject, **kwargs)
        message = message.encode(encoding)
        host.send(message, mto=send_to_address,
                  mfrom=envelope_from, subject=subject,
                  charset='utf-8')

    security.declarePublic('validateSingleNormalizedEmailAddress')
    def validateSingleNormalizedEmailAddress(self, address):
        """Lower-level function to validate a single normalized email address,
        see validateEmailAddress.
        """
        if not isinstance(address, basestring):
            return False

        sub = EMAIL_CUTOFF_RE.match(address)
        if sub != None:
            # Address contains two newlines (possible spammer relay attack)
            return False

        # sub is an empty string if the address is valid
        sub = EMAIL_RE.sub('', address)
        if sub == '':
            return True
        return False

    security.declarePublic('validateSingleEmailAddress')
    def validateSingleEmailAddress(self, address):
        """Validate a single email address, see also validateEmailAddresses."""
        if not isinstance(address, basestring):
            return False

        sub = EMAIL_CUTOFF_RE.match(address)
        if sub != None:
            # Address contains two newlines (spammer attack using
            # "address\n\nSpam message")
            return False

        if len(getaddresses([address])) != 1:
            # none or more than one address
            return False

        # Validate the address
        for name, addr in getaddresses([address]):
            if not self.validateSingleNormalizedEmailAddress(addr):
                return False
        return True

    security.declarePublic('validateEmailAddresses')
    def validateEmailAddresses(self, addresses):
        """Validate a list of possibly several email addresses, see also
        validateSingleEmailAddress.
        """
        if not isinstance(addresses, basestring):
            return False

        sub = EMAIL_CUTOFF_RE.match(addresses)
        if sub != None:
            # Addresses contains two newlines (spammer attack using
            # "To: list\n\nSpam message")
            return False

        # Validate each address
        for name, addr in getaddresses([addresses]):
            if not self.validateSingleNormalizedEmailAddress(addr):
                return False
        return True

    security.declarePublic('editMetadata')
    def editMetadata(self, obj, allowDiscussion=None, title=None,
                     subject=None, description=None, contributors=None,
                     effective_date=None, expiration_date=None, format=None,
                     language=None, rights=None, **kwargs):
        """Responsible for setting metadata on a content object.

        We assume the obj implements IDublinCoreMetadata.
        """
        mt = getToolByName(self, 'portal_membership')
        if not mt.checkPermission(ModifyPortalContent, obj):
            # FIXME: Some scripts rely on this being string?
            raise Unauthorized

        REQUEST = self.REQUEST
        pfx = self.field_prefix

        def getfield(request, name, default=None, pfx=pfx):
            return request.form.get(pfx + name, default)

        def tuplify(value):
            return tuple(filter(None, value))

        if IDublinCore.providedBy(obj):
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

        if IDiscussable.providedBy(obj) or \
            getattr(obj, '_isDiscussable', None):
            disc_tool = getToolByName(self, 'portal_discussion')
            if allowDiscussion is None:
                allowDiscussion = disc_tool.isDiscussionAllowedFor(obj)
                if not safe_hasattr(obj, 'allow_discussion'):
                    allowDiscussion = None
                allowDiscussion = REQUEST.get('allowDiscussion',
                                              allowDiscussion)
            if type(allowDiscussion) == StringType:
                allowDiscussion = allowDiscussion.lower().strip()
            if allowDiscussion == 'default':
                allowDiscussion = None
            elif allowDiscussion == 'off':
                allowDiscussion = 0
            elif allowDiscussion == 'on':
                allowDiscussion = 1
            disc_tool.overrideDiscussionFor(obj, allowDiscussion)

        if IMutableDublinCore.providedBy(obj):
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
        #TODO Why not aq_parent()?
        relative_path = '/'.join(getToolByName(self, 'portal_url') \
                                    .getRelativeContentPath(obj)[:-1])
        if not msg:
            msg = relative_path + '/' + obj.title_or_id() \
                    + ' has been modified.'
        if isinstance(msg, UnicodeType):
            # Convert unicode to a regular string for the backend write IO.
            # UTF-8 is the only reasonable choice, as using unicode means
            # that Latin-1 is probably not enough.
            msg = msg.encode('utf-8')
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

        Requires mimetype registry from Archetypes >= 1.3.
        """
        mtr = getToolByName(self, 'mimetypes_registry')
        return mtr.list_mimetypes()

    security.declareProtected(View, 'getWorkflowChainFor')
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

    security.declareProtected(View, 'getIconFor')
    def getIconFor(self, category, id, default=_marker, context=None):
        """Get an icon for an action. Prefer the icon_expr on the action
        itself and if not specified fall back to the icon from the
        action icons tool.
        """
        if context is None:
            context = aq_parent(self)
        if category == 'controlpanel':
            tool = getToolByName(context, 'portal_controlpanel')
            actions = [ai for ai in tool.listActionInfos() if ai['id'] == id]
        else:
            tool = getToolByName(context, 'portal_actions')
            actions = tool.listActionInfos(
                        action_chain='%s/%s' % (category, id),
                        object=context)
        if len(actions) > 0:
            icon = actions[0].get('icon', None)
            if icon:
                return icon

        # Short circuit the lookup
        if (category, id) in _icons.keys():
            return _icons[(category, id)]
        try:
            # BBB icon lookup on action icons tool
            actionicons = getToolByName(context, 'portal_actionicons')
            iconinfo = actionicons.getActionIcon(category, id)
            icon = _icons.setdefault((category, id), iconinfo)
        except KeyError:
            if default is not _marker:
                icon = default
            else:
                raise
        # We want to return the actual object
        return icon

    security.declareProtected(View, 'getReviewStateTitleFor')
    def getReviewStateTitleFor(self, obj):
        """Utility method that gets the workflow state title for the
        object's review_state.

        Returns None if no review_state found.

        >>> ptool = self.portal.plone_utils

        >>> ptool.getReviewStateTitleFor(self.folder).lower()
        'public draft'
        """
        wf_tool = getToolByName(self, 'portal_workflow')
        wfs = ()
        objstate = None
        try:
            objstate = wf_tool.getInfoFor(obj, 'review_state')
            wfs = wf_tool.getWorkflowsFor(obj)
        except WorkflowException:
            pass
        if wfs:
            for w in wfs:
                if objstate in w.states:
                    return w.states[objstate].title or objstate
        return None

    security.declareProtected(View, 'getDiscussionThread')
    def getDiscussionThread(self, discussionContainer):
        """Given a discussionContainer, return the thread it is in, upwards,
        including the parent object that is being discussed.
        """
        if safe_hasattr(discussionContainer, 'parentsInThread'):
            thread = discussionContainer.parentsInThread()
            if discussionContainer.portal_type == 'Discussion Item':
                thread.append(discussionContainer)
        else:
            if discussionContainer.id == 'talkback':
                thread = [discussionContainer._getDiscussable()]
            else:
                thread = [discussionContainer]
        return thread

    security.declareProtected(ManagePortal, 'changeOwnershipOf')
    def changeOwnershipOf(self, object, userid, recursive=0, REQUEST=None):
        """Changes the ownership of an object."""
        membership = getToolByName(self, 'portal_membership')
        acl_users = getattr(self, 'acl_users')
        user = acl_users.getUserById(userid)
        if user is None:
            # The user could be in the top level acl_users folder in
            # the Zope root, in which case this should find him:
            user = membership.getMemberById(userid)
            if user is None:
                raise KeyError(
                    'Only retrievable users in this site can be made owners.')
            # Be careful not to pass MemberData to changeOwnership
            user = user.getUser()
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
        if base_hasattr(object, 'reindexObject'):
            object.reindexObject()

        if recursive:
            catalog_tool = getToolByName(self, 'portal_catalog')
            purl = getToolByName(self, 'portal_url')
            _path = purl.getRelativeContentURL(object)
            subobjects = [b.getObject() for b in
                         catalog_tool(path={'query': _path, 'level': 1})]
            for obj in subobjects:
                fixOwnerRole(obj, user.getId())
                if base_hasattr(obj, 'reindexObject'):
                    obj.reindexObject()
    changeOwnershipOf = postonly(changeOwnershipOf)

    security.declarePublic('urlparse')
    def urlparse(self, url):
        """Returns the pieces of url in a six-part tuple.

        See Python standard library urlparse.urlparse:
        http://python.org/doc/lib/module-urlparse.html

        >>> ptool = self.portal.plone_utils

        >>> url = 'http://dev.plone.org/plone/query?milestone=2.1#foo'
        >>> tuple(ptool.urlparse(url))
        ('http', 'dev.plone.org', '/plone/query', '', 'milestone=2.1', 'foo')

        New in Python 2.6: urlparse now returns a ParseReusult object.
        We just need the tuple form which is tuple(result).
        """
        return tuple(urlparse.urlparse(url))

    security.declarePublic('urlunparse')
    def urlunparse(self, url_tuple):
        """Puts a url back together again, in the manner that
        urlparse breaks it.

        See also Python standard library: urlparse.urlunparse:
        http://python.org/doc/lib/module-urlparse.html

        >>> ptool = self.portal.plone_utils

        >>> ptool.urlunparse(('http', 'plone.org', '/support', '', '', 'users'))
        'http://plone.org/support#users'
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
        """Dumps most recent exception to the log.
        """
        log_exc()

    security.declarePublic('createSitemap')
    def createSitemap(self, context, request=None):
        """Returns a sitemap navtree structure.
        """
        if request is None:
            request = self.REQUEST
        return utils.createSiteMap(context, request)

    def _addToNavTreeResult(self, result, data):
        """Adds a piece of content to the result tree.
        """
        return utils.addToNavTreeResult(result, data)

    security.declareProtected(AccessContentsInformation, 'typesToList')
    def typesToList(self):
        return utils.typesToList(self)

    security.declarePublic('createNavTree')
    def createNavTree(self, context, sitemap=None, request=None):
        """Returns a structure that can be used by navigation_tree_slot.
        """
        if request is None:
            request = self.REQUEST
        return utils.createNavTree(context, request)

    security.declarePublic('createBreadCrumbs')
    def createBreadCrumbs(self, context, request=None):
        """Returns a structure for the portal breadcumbs.
        """
        if request is None:
            request = self.REQUEST
        return utils.createBreadCrumbs(context, request)

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
    def getInheritedLocalRoles(self, context):
        """Returns a tuple with the acquired local roles."""
        portal = getToolByName(context, 'portal_url').getPortalObject()
        result = []
        cont = 1
        if portal != context:
            parent = aq_parent(context)
            while cont:
                if not getattr(parent, 'acl_users', False):
                    break
                userroles = parent.acl_users._getLocalRolesForDisplay(parent)
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
                    parent = aq_parent(parent)

        # Tuplize all inner roles
        for pos in range(len(result) - 1, -1, -1):
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
    def isDefaultPage(self, obj, request=None):
        """Finds out if the given obj is the default page in its parent folder.

        Only considers explicitly contained objects, either set as index_html,
        with the default_page property, or using IBrowserDefault.
        """
        if request is None:
            request = self.REQUEST
        return utils.isDefaultPage(obj, request)

    security.declarePublic('getDefaultPage')
    def getDefaultPage(self, obj, request=None):
        """Given a folderish item, find out if it has a default-page using
        the following lookup rules:

            1. A content object called 'index_html' wins
            2. If the folder implements IBrowserDefault, query this
            3. Else, look up the property default_page on the object
                - Note that in this case, the returned id may *not* be of an
                  object in the folder, since it could be acquired from a
                  parent folder or skin layer
            4. Else, look up the property default_page in site_properties for
                magic ids and test these

        The id of the first matching item is then used to lookup a translation
        and if found, its id is returned. If no default page is set, None is
        returned. If a non-folderish item is passed in, return None always.
        """
        if request is None:
            request = self.REQUEST
        return utils.getDefaultPage(obj, request)

    security.declarePublic('addPortalMessage')
    def addPortalMessage(self, message, type='info', request=None):
        """\
        Call this once or more to add messages to be displayed at the
        top of the web page.

        Examples:

        >>> ptool = self.portal.plone_utils

        >>> ptool.addPortalMessage(u'A random warning message', 'warning')

        If no type is given it defaults to 'info'
        >>> ptool.addPortalMessage(u'A random info message')

        The arguments are:
            message:   a string, with the text message you want to show,
                       or a HTML fragment (see type='structure' below)
            type:      optional, defaults to 'info'. The type determines how
                       the message will be rendered, as it is used to select
                       the CSS class for the message. Predefined types are:
                       'info' - for informational messages
                       'warning' - for warning messages
                       'error' - for messages about restricted access or
                                 errors.

        Portal messages are by default rendered by the global_statusmessage.pt
        page template.

        It is also possible to add messages from page templates, as
        long as they are processed before the portal_message macro is
        called by the main template. Example:

          <tal:block tal:define="temp python:context.plone_utils.addPortalMessage('A random info message')" />
        """
        if request is None:
            request = self.REQUEST
        IStatusMessage(request).add(message, type=type)

    security.declarePublic('showPortalMessages')
    def showPortalMessages(self, request=None):
        """\
        Return portal status messages that will be displayed when the
        response web page is rendered. Portal status messages are by default
        rendered by the global_statusmessage.pt page template. They will be
        removed after they have been shown.

        See addPortalMessages for examples.
        """
        if request is None:
            request = self.REQUEST
        return IStatusMessage(request).show()

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
        object which supports translation will then be translated before
        return.
        """

        # WebDAV in Zope is odd it takes the incoming verb eg: PROPFIND
        # and then requests that object, for example for: /, with verb PROPFIND
        # means acquire PROPFIND from the folder and call it
        # its all very odd and WebDAV'y
        request = getattr(self, 'REQUEST', None)
        if request is not None and 'REQUEST_METHOD' in request:
            if request['REQUEST_METHOD'] not in ['GET', 'POST']:
                return obj, [request['REQUEST_METHOD']]
        # Now back to normal

        #
        # 1. Get an attribute or contained object index_html
        #

        # Note: The base PloneFolder, as well as ATCT's ATCTOrderedFolder
        # defines a method index_html() which returns a ReplaceableWrapper.
        # This is needed for WebDAV to work properly, and to avoid implicit
        # acquisition of index_html's, which are generally on-object only.
        # For the purposes of determining a default page, we don't want to
        # use this index_html(), nor the ComputedAttribute which defines it.

        if not isinstance(getattr(obj, 'index_html', None),
                          ReplaceableWrapper):
            index_obj = getattr(aq_base(obj), 'index_html', None)
            if index_obj is not None \
                    and not isinstance(index_obj, ComputedAttribute):
                return obj, ['index_html']

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
                if defaultPage in obj:
                    return obj, [defaultPage]
                # Avoid infinite recursion in the case that the page id == the
                # object id
                elif defaultPage != obj.getId() and \
                     defaultPage != '/'.join(obj.getPhysicalPath()):
                    # For the default_page property, we may get things in the
                    # skin layers or with an explicit path - split this path
                    # to comply with the __browser_default__() spec
                    return obj, defaultPage.split('/')

        # 5. If there is no default page, try IBrowserDefault.getLayout()
        if IBrowserDefault.providedBy(obj):
            browserDefault = obj
        else:
            browserDefault = queryAdapter(obj, IBrowserDefault)
        if browserDefault is not None:
            layout = browserDefault.getLayout()
            if layout is None:
                raise AttributeError(
                    "%s has no assigned layout, perhaps it needs an FTI" % obj)
            else:
                return obj, [layout]

        #
        # 6. If the object has a 'folderlisting' action, use this
        #

        # This allows folders to determine in a flexible manner how they are
        # displayed when there is no default page, whilst still using
        # browserDefault() to show contained objects by default on the 'view'
        # action (this applies to old-style folders only, IBrowserDefault is
        # managed explicitly above)

        if base_hasattr(obj, 'getTypeInfo'):
            try:
                # XXX: This isn't quite right since it assumes the action
                # starts with ${object_url}.  Should we raise an error if
                # it doesn't?
                act = obj.getTypeInfo().getActionInfo('folder/folderlisting')['url'].split('/')[-1]
                return obj, [act]
            except ValueError:
                pass

            #
            # 7. Fall back on the 'view' action
            #

            try:
                # XXX: This isn't quite right since it assumes the action
                # starts with ${object_url}.  Should we raise an error if
                # it doesn't?
                act = obj.getTypeInfo().getActionInfo('object/view')['url'].split('/')[-1]
                return obj, [act]
            except ValueError:
                pass

        #
        # 8. If we can't find this either, raise an exception
        #

        raise AttributeError(
                "Failed to get a default page or view_action for %s"
                    % (obj.absolute_url(),))

    security.declarePublic('isTranslatable')
    def isTranslatable(self, obj):
        """Checks if a given object implements the ITranslatable interface."""
        return ITranslatable.providedBy(obj)

    security.declarePublic('isStructuralFolder')
    def isStructuralFolder(self, obj):
        """Checks if a given object is a "structural folder".

        That is, a folderish item which does not explicitly implement
        INonStructuralFolder to declare that it doesn't wish to be treated
        as a folder by the navtree, the tab generation etc.

        >>> ptool = self.portal.plone_utils

        >>> ptool.isStructuralFolder(self.folder)
        True
        """
        if not obj.isPrincipiaFolderish:
            return False
        elif INonStructuralFolder.providedBy(obj):
            return False
        else:
            return True

    security.declarePublic('acquireLocalRoles')
    def acquireLocalRoles(self, obj, status=1, REQUEST=None):
        """If status is 1, allow acquisition of local roles (regular
        behaviour).

        If it's 0, prohibit it (it will allow some kind of local role
        blacklisting).
        """
        mt = getToolByName(self, 'portal_membership')
        if not mt.checkPermission(ModifyPortalContent, obj):
            raise Unauthorized

        # Set local role status...
        # set the variable (or unset it if it's defined)
        if not status:
            obj.__ac_local_roles_block__ = 1
        else:
            if getattr(obj, '__ac_local_roles_block__', None):
                obj.__ac_local_roles_block__ = None

        # Reindex the whole stuff.
        obj.reindexObjectSecurity()
    acquireLocalRoles = postonly(acquireLocalRoles)

    security.declarePublic('isLocalRoleAcquired')
    def isLocalRoleAcquired(self, obj):
        """Returns local role acquisition blocking status.

        True if normal, false if blocked.
        """
        if getattr(obj, '__ac_local_roles_block__', None):
            return False
        return True

    security.declarePublic('getOwnerName')
    def getOwnerName(self, obj):
        """ Returns the userid of the owner of an object.

        >>> ptool = self.portal.plone_utils
        >>> from Products.PloneTestCase.PloneTestCase import default_user

        >>> ptool.getOwnerName(self.folder) == default_user
        True
        """
        mt = getToolByName(self, 'portal_membership')
        if not mt.checkPermission(View, obj):
            raise Unauthorized
        return obj.getOwner().getId()

    security.declarePublic('normalizeString')
    def normalizeString(self, text):
        """Normalizes a title to an id.

        The relaxed mode was removed in Plone 4.0. You should use either the
        url or file name normalizer from the plone.i18n package instead.

        normalizeString() converts a whole string to a normalized form that
        should be safe to use as in a url, as a css id, etc.

        >>> ptool = self.portal.plone_utils

        >>> ptool.normalizeString("Foo bar")
        'foo-bar'

        >>> ptool.normalizeString("Some!_are allowed, others&?:are not")
        'some-_are-allowed-others-are-not'

        >>> ptool.normalizeString("Some!_are allowed, others&?:are not")
        'some-_are-allowed-others-are-not'

        all punctuation and spacing is removed and replaced with a '-':

        >>> ptool.normalizeString("a string with spaces")
        'a-string-with-spaces'

        >>> ptool.normalizeString("p.u,n;c(t)u!a@t#i$o%n")
        'p-u-n-c-t-u-a-t-i-o-n'

        strings are lowercased:

        >>> ptool.normalizeString("UppERcaSE")
        'uppercase'

        punctuation, spaces, etc. are trimmed and multiples are reduced to just
        one:

        >>> ptool.normalizeString(" a string    ")
        'a-string'
        >>> ptool.normalizeString(">here's another!")
        'heres-another'

        >>> ptool.normalizeString("one with !@#$!@#$ stuff in the middle")
        'one-with-stuff-in-the-middle'

        the exception to all this is that if there is something that looks like
        a filename with an extension at the end, it will preserve the last
        period.

        >>> ptool.normalizeString("this is a file.gif")
        'this-is-a-file-gif'

        >>> ptool.normalizeString("this is. also. a file.html")
        'this-is-also-a-file-html'
        """
        return utils.normalizeString(text, context=self)

    security.declarePublic('listMetaTags')
    def listMetaTags(self, context):
        """Lists meta tags helper.

        Creates a mapping of meta tags -> values for the listMetaTags script.
        """
        result = {}
        site_props = getToolByName(self, 'portal_properties').site_properties
        mt = getToolByName(self, 'portal_membership')

        use_all = site_props.getProperty('exposeDCMetaTags', None)
        view_about = site_props.getProperty('allowAnonymousViewAbout', False) \
                     or not mt.isAnonymousUser()

        if not use_all:
            metadata_names = {'Description': METADATA_DCNAME['Description']}
        else:
            metadata_names = METADATA_DCNAME

        for accessor, key in metadata_names.items():
            # check non-public properties
            if not view_about and accessor in METADATA_DC_AUTHORFIELDS:
                continue

            # short circuit non-special cases
            if not use_all and accessor not in ('Description', 'Subject'):
                continue

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
                # No publisher is hardcoded (TODO: still?)
                continue

            # Check for fullnames
            if view_about and accessor in METADATA_DC_AUTHORFIELDS:
                if not isinstance(value, (list, tuple)):
                    value = [value]
                tmp = []
                for userid in value:
                    member = mt.getMemberInfo(userid)
                    name = userid
                    if member:
                        name = member['fullname'] or userid
                    tmp.append(name)
                value = tmp

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
            if effective is not None and \
               effective > FLOOR_DATE and \
               effective != created:
                eff_str = effective.Date()
            else:
                eff_str = ''

            if expires is not None and expires < CEILING_DATE:
                exp_str = expires.Date()
            else:
                exp_str = ''

            if eff_str or exp_str:
                result['DC.date.valid_range'] = '%s - %s' % (eff_str, exp_str)

        return result

    security.declarePublic('getUserFriendlyTypes')
    def getUserFriendlyTypes(self, typesList=None):
        """Get a list of types which are considered "user friendly" for search
        and selection purposes.

        This is the list of types available in the portal, minus those defined
        in the types_not_searched property in site_properties, if it exists.

        If typesList is given, this is used as the base list; else all types
        from portal_types are used.
        """
        if typesList is None:
            typesList = []
        ptool = getToolByName(self, 'portal_properties')
        siteProperties = getattr(ptool, 'site_properties')
        blacklistedTypes = siteProperties.getProperty('types_not_searched', [])

        ttool = getToolByName(self, 'portal_types')
        tool_types = ttool.keys()
        if typesList:
            types = [t for t in typesList if t in tool_types]
        else:
            types = tool_types

        friendlyTypes = set(types) - set(blacklistedTypes)
        return list(friendlyTypes)

    security.declarePublic('reindexOnReorder')
    def reindexOnReorder(self, parent):
        """ reindexing of "gopip" isn't needed any longer,
        but some extensions might need the info anyway :("""
        notify(ReorderedEvent(parent))

    security.declarePublic('isIDAutoGenerated')
    def isIDAutoGenerated(self, id):
        """Determine if an id is autogenerated"""
        return utils.isIDAutoGenerated(self, id)

    security.declarePublic('getEmptyTitle')
    def getEmptyTitle(self, translated=True):
        """ Returns string to be used for objects with no title or id.

        >>> ptool = self.portal.plone_utils

        >>> ptool.getEmptyTitle(translated=False) == u'[\xb7\xb7\xb7]'
        True
        """
        return utils.getEmptyTitle(self, translated)

    security.declarePublic('pretty_title_or_id')
    def pretty_title_or_id(self, obj, empty_value=_marker):
        """Return the best possible title or id of an item, regardless
        of whether obj is a catalog brain or an object, but returning an
        empty title marker if the id is not set (i.e. it's auto-generated).
        """
        return utils.pretty_title_or_id(self, obj, empty_value=empty_value)

    security.declarePublic('getMethodAliases')
    def getMethodAliases(self, typeInfo):
        """Given an FTI, return the dict of method aliases defined on that
        FTI. If there are no method aliases (i.e. this FTI doesn't support it),
        return None"""
        getMethodAliases = getattr(typeInfo, 'getMethodAliases', None)
        if getMethodAliases is not None \
                and utils.safe_callable(getMethodAliases):
            return getMethodAliases()
        else:
            return None

    # This is public because we don't know what permissions the user
    # has on the objects to be deleted.  The restrictedTraverse and
    # manage_delObjects calls should handle permission checks for us.
    security.declarePublic('deleteObjectsByPaths')
    def deleteObjectsByPaths(self, paths, handle_errors=True, REQUEST=None):
        failure = {}
        success = []
        # use the portal for traversal in case we have relative paths
        portal = getToolByName(self, 'portal_url').getPortalObject()
        traverse = portal.restrictedTraverse
        for path in paths:
            # Skip and note any errors
            if handle_errors:
                sp = transaction.savepoint(optimistic=True)
            try:
                # To avoid issues with the check for acquisition,
                # relative paths should not be part of the API anymore.
                # Plone core itself does not use relative paths.
                if not path.startswith("/".join(portal.getPhysicalPath())):
                    msg = (
                        'Path {} does not start '
                        'with path to portal'.format(path)
                    )
                    raise ValueError(msg)
                obj = traverse(path)
                if list(obj.getPhysicalPath()) != path.split('/'):
                    msg = (
                        'Path {} does not match '
                        'traversed object physical path. '
                        'This is likely an acquisition issue.'.format(path)
                    )
                    raise ValueError(msg)
                obj_parent = aq_parent(aq_inner(obj))
                obj_parent.manage_delObjects([obj.getId()])
                success.append('%s (%s)' % (obj.getId(), path))
            except ConflictError:
                raise
            except LinkIntegrityNotificationException:
                raise
            except Exception, e:
                if handle_errors:
                    sp.rollback()
                    failure[path] = e
                    log_exc()
                else:
                    raise
        transaction_note('Deleted %s' % (', '.join(success)))
        return success, failure
    deleteObjectsByPaths = postonly(deleteObjectsByPaths)

    security.declarePublic('transitionObjectsByPaths')
    def transitionObjectsByPaths(self, workflow_action, paths, comment='',
                                 expiration_date=None, effective_date=None,
                                 include_children=False, handle_errors=True,
                                 REQUEST=None):
        failure = {}
        # use the portal for traversal in case we have relative paths
        portal = getToolByName(self, 'portal_url').getPortalObject()
        traverse = portal.restrictedTraverse
        for path in paths:
            if handle_errors:
                sp = transaction.savepoint(optimistic=True)
            try:
                o = traverse(path, None)
                if o is not None:
                    o.content_status_modify(workflow_action,
                                            comment,
                                            effective_date=effective_date,
                                            expiration_date=expiration_date)
            except ConflictError:
                raise
            except Exception, e:
                if handle_errors:
                    # skip this object but continue with sub-objects.
                    sp.rollback()
                    failure[path] = e
                else:
                    raise
            if getattr(o, 'isPrincipiaFolderish', None) and include_children:
                subobject_paths = ["%s/%s" % (path, id) for id in o]
                self.transitionObjectsByPaths(workflow_action, subobject_paths,
                                              comment, expiration_date,
                                              effective_date, include_children,
                                              handle_errors)
        return failure
    transitionObjectsByPaths = postonly(transitionObjectsByPaths)

    security.declarePublic('renameObjectsByPaths')
    def renameObjectsByPaths(self, paths, new_ids, new_titles,
                             handle_errors=True, REQUEST=None):
        failure = {}
        success = {}
        # use the portal for traversal in case we have relative paths
        portal = getToolByName(self, 'portal_url').getPortalObject()
        traverse = portal.restrictedTraverse
        for i, path in enumerate(paths):
            new_id = new_ids[i]
            new_title = new_titles[i]
            if handle_errors:
                sp = transaction.savepoint(optimistic=True)
            try:
                obj = traverse(path, None)
                obid = obj.getId()
                title = obj.Title()
                change_title = new_title and title != new_title
                changed = False
                if change_title:
                    getSecurityManager().validate(obj, obj, 'setTitle', obj.setTitle)
                    obj.setTitle(new_title)
                    notify(ObjectModifiedEvent(obj))
                    changed = True
                if new_id and obid != new_id:
                    parent = aq_parent(aq_inner(obj))

                    #Don't forget default page.
                    if hasattr(parent, 'getDefaultPage'):
                        default_page = parent.getDefaultPage()
                        if default_page == obid:
                            parent.setDefaultPage(new_id)

                    parent.manage_renameObjects((obid,), (new_id,))
                    changed = True

                elif change_title:
                    # the rename will have already triggered a reindex
                    obj.reindexObject()
                if changed:
                    success[path] = (new_id, new_title)
            except ConflictError:
                raise
            except Exception, e:
                if handle_errors:
                    # skip this object but continue with sub-objects.
                    sp.rollback()
                    failure[path] = e
                else:
                    raise
        transaction_note('Renamed %s' % str(success.keys()))
        return success, failure
    renameObjectsByPaths = postonly(renameObjectsByPaths)

InitializeClass(PloneTool)
