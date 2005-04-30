import re
import sys
import traceback
from types import TupleType, UnicodeType, StringType
import urlparse

from zLOG import LOG, INFO, WARNING

from Acquisition import aq_base, aq_inner, aq_parent
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.utils import _checkPermission, \
     _getAuthenticatedUser, limitGrantedRoles
from Products.CMFCore.utils import getToolByName, _dtmldir
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.interfaces.DublinCore import DublinCore, MutableDublinCore
from Products.CMFCore.interfaces.Discussions import Discussable
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFPlone import ToolNames, transaction_note

from OFS.SimpleItem import SimpleItem
from OFS.ObjectManager import bad_id
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from StatelessTree import NavigationTreeViewBuilder as NTVB
from ZODB.POSException import ConflictError
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

_marker = ()
_icons = {}

try:
    True
except:
    True=1
    False=0

def log(summary='', text='', log_level=INFO):
    LOG('Plone Debug', log_level, summary, text)

EMAIL_RE = re.compile(r"^(\w&.+-]+!)*[\w&.+-]+@(([0-9a-z]([0-9a-z-]*[0-9a-z])?\.)+[a-z]{2,6}|([0-9]{1,3}\.){3}[0-9]{1,3})$", re.IGNORECASE)
EMAIL_CUTOFF_RE = re.compile(r".*[\n\r][\n\r]") # used to find double new line (in any variant)

#XXX Remove this when we don't depend on python2.1 any longer, use email.Utils.getaddresses instead
from rfc822 import AddressList
def _getaddresses(fieldvalues):
    """Return a list of (REALNAME, EMAIL) for each fieldvalue."""
    all = ', '.join(fieldvalues)
    a = AddressList(all)
    return a.addresslist

class PloneTool(PloneBaseTool, UniqueObject, SimpleItem):
    """Various utility methods."""

    id = 'plone_utils'
    meta_type= ToolNames.UtilsTool
    toolicon = 'skins/plone_images/site_icon.gif'
    security = ClassSecurityInfo()
    plone_tool = 1
    field_prefix = 'field_' # Formulator prefixes for forms

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

    def _safeSendTo(self, body, mto, mfrom):
        # this function is private in Plone and should be
        # the function used for sending
        # email. It does the following:
        #    
        #  - ensures that anything being sent through is only
        #    sent to the emails specified and not headers in the
        #    email
        #
        #  - ensure that from and to are only one, and only one email
        if not self.validateSingleEmailAddress(mfrom):
            raise ValueError, 'The "from" email address did not validate'
        
        if not self.validateEmailAddresses(mto):
            raise ValueError, 'The "to" email address did not validate'
        
        host = self.MailHost
        host.send(body, mto, mfrom)

    security.declarePublic('sendto')
    def sendto( self, variables = {} ):
        """Sends a link of a page to someone
        """
        if not variables: return

        # the subject is in the header, so must be checked
        if variables['title'].find('\n') >= 0:
            raise ValueError, 'That title contains a new line, which is illegal'

        mail_text = self.sendto_template(self, **variables)

        # the template is built with send_to and send_from
        # but we know _safeSendTo will check them as well
        # so we should be ok
        self._safeSendTo(mail_text, 
            variables['send_to_address'], 
            variables['send_from_address'])

    security.declarePublic('validateSingleNormalizedEmailAddress')
    def validateSingleNormalizedEmailAddress(self, address):
        """Lower-level function to validate a single normalized email address, see validateEmailAddress
        """
        if type(address) is not StringType:
            return False

        sub = EMAIL_CUTOFF_RE.match(address);
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
        """Validate a single email address, see also validateEmailAddresses
        """
        if type(address) is not StringType:
            return False
        
        sub = EMAIL_CUTOFF_RE.match(address);
        if sub != None:
            # Address contains two newlines (spammer attack using "address\n\nSpam message")
            return False
        
        if len(_getaddresses([address])) != 1:
            # none or more than one address
            return False
        
        # Validate the address
        for name,addr in _getaddresses([address]):
            if not self.validateSingleNormalizedEmailAddress(addr):
                return False
        return True

    security.declarePublic('validateEmailAddresses')
    def validateEmailAddresses(self, addresses):
        """Validate a list of possibly several email addresses, see also validateSingleEmailAddress
        """
        if type(addresses) is not StringType:
            return False
        
        sub = EMAIL_CUTOFF_RE.match(addresses);
        if sub != None:
            # Addresses contains two newlines (spammer attack using "To: list\n\nSpam message")
            return False
        
        # Validate each address
        for name,addr in _getaddresses([addresses]):
            if not self.validateSingleNormalizedEmailAddress(addr):
                return False
        return True

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
            raise 'Unauthorized'    # FIXME: Some scripts rely on this being string?

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
        """ Return a map of mimetypes """
        # This should probably be done in a more efficent way.
        import mimetypes

        result = []
        for mimetype in mimetypes.types_map.values():
            if not mimetype in result:
                result.append(mimetype)

        result.sort()
        return result

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

    #XXX deprecated methods
    security.declarePublic('getNextPageFor')
    def getNextPageFor(self, context, action, status, **kwargs):
        log( 'Plone Tool Deprecation', action + \
             ' has called plone_utils.getNextPageFor()' + \
             ' which has been deprecated. ' + \
             'Use portal_navigation.getNextRequestFor() instead.', WARNING)

        nav_tool=getToolByName(self, 'portal_navigation')
        return nav_tool.getNextPageFor(context, action, status, **kwargs)

    security.declarePublic('getNextRequestFor')
    def getNextRequestFor(self, context, action, status, **kwargs):
        log( 'Plone Tool Deprecation', action + \
             ' has called plone_utils.getNextPageFor()' + \
             ' which has been deprecated. ' + \
             'Use portal_navigation.getNextRequestFor() instead.', WARNING)
        nav_tool=getToolByName(self, 'portal_navigation')
        return nav_tool.getNextRequestFor(context, action, status, **kwargs)

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

        # get rid of all other owners
        owners = object.users_with_local_role('Owner')
        for o in owners:
            roles = list(object.get_local_roles_for_userid(o))
            roles.remove('Owner')
            if roles:
                object.manage_setLocalRoles(o, roles)
            else:
                object.manage_delLocalRoles([o])

        #FIX for 1750
        roles = list(object.get_local_roles_for_userid(user.getId()))
        roles.append('Owner')
        object.manage_setLocalRoles( user.getId(), roles )

        catalog_tool.reindexObject(object)
        if recursive:
            purl = getToolByName(self, 'portal_url')
            _path = purl.getRelativeContentURL(object)
            subobjects=[b.getObject() for b in \
                        catalog_tool(path={'query':_path,'level':1})]
            for obj in subobjects:
                catalog_tool.reindexObject(obj)

    security.declarePublic('urlparse')
    def urlparse(self, url):
        """ returns the pieces of url """
        return urlparse.urlparse(url)

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

    #replaces navigation_tree_builder.py
    def createNavigationTreeBuilder(self, tree_root,
                                    navBatchStart=None,
                                    showMyUserFolderOnly=None,
                                    includeTop=None,
                                    showFolderishSiblingsOnly=None,
                                    showFolderishChildrenOnly=None,
                                    showNonFolderishObject=None,
                                    topLevel=None,
                                    batchSize=None,
                                    showTopicResults=None,
                                    rolesSeeUnpublishedContent=None,
                                    sortCriteria=None,
                                    metaTypesNotToList=None,
                                    parentMetaTypesNotToQuery=None,
                                    forceParentsInBatch=None,
                                    skipIndex_html=None,
                                    rolesSeeHiddenContent=None,
                                    bottomLevel=None):

        """ Returns a structure that can be used by
        navigation_tree_slot.  We are being quite lazy because of
        massive signature.  """

        t_builder = NTVB(tree_root=tree_root,
                         navBatchStart=navBatchStart,
                         showMyUserFolderOnly=showMyUserFolderOnly,
                         includeTop=includeTop,
                         showFolderishSiblingsOnly=showFolderishSiblingsOnly,
                         showFolderishChildrenOnly=showFolderishChildrenOnly,
                         showNonFolderishObject=showNonFolderishObject,
                         topLevel=topLevel,
                         batchSize=batchSize,
                         showTopicResults=showTopicResults,
                         rolesSeeUnpublishedContent=rolesSeeUnpublishedContent,
                         sortCriteria=sortCriteria,
                         metaTypesNotToList=metaTypesNotToList,
                         parentMetaTypesNotToQuery=parentMetaTypesNotToQuery,
                         forceParentsInBatch=forceParentsInBatch,
                         skipIndex_html=skipIndex_html,
                         rolesSeeHiddenContent=rolesSeeHiddenContent,
                         bottomLevel=bottomLevel  )
        ctx_tree_builder=t_builder.__of__(self)
        return ctx_tree_builder()

    # expose ObjectManager's bad_id test to skin scripts
    security.declarePublic('good_id')
    def good_id(self, id):
        m = bad_id(id)
        if m is not None:
            return 0
        return 1

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
                for user, roles, type, name in userroles:
                    # find user in result
                    found=0
                    for user2, roles2, type2, name2 in result:
                        if user2==user:
                            # check which roles must be added to roles2
                            for role in roles:
                                if not role in roles2:
                                    roles2=roles2+(role,)
                            found=1
                            break
                    if found==0:
                        # add it to result
                        result.append((user, roles, type, name))
                if parent==portal:
                    cont=0
                else:
                    parent=parent.aq_parent

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

        # The list of ids where we look for default
        ids = {}
        # For BTreeFolders we just use the has_key, otherwise build a dict
        if hasattr(aq_base(obj), 'has_key'):
            ids = obj
        else:
            for id in obj.objectIds():
                ids[id] = 1

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
                return obj, [page]
        # we look for the default_page in the portal and/or skins aswell.
        # Use path/to/template to reference an object or a skin.
        for page in pages:
            if portal.unrestrictedTraverse(page,None):
                return obj, page.split('/')

        # Try the default sitewide default_page setting
        for page in portal.portal_properties.site_properties.getProperty('default_page', []):
            if ids.has_key(page):
                return obj, [page]

        # No luck, let's look for hardcoded defaults
        default_pages = ['index_html', ]
        for page in default_pages:
            if ids.has_key(page):
                return obj, [page]

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
            'Total failure getting the folderlisting action for the folder, "%s"' \
            % obj.absolute_url())
            return obj, ['folder_listing']


InitializeClass(PloneTool)
