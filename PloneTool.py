import re
import sys
import traceback
from types import TupleType, UnicodeType, DictType, StringType
from urllib import urlencode
import urlparse
from cgi import parse_qs

from zLOG import LOG, INFO, WARNING

from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.utils import _checkPermission, \
     _getAuthenticatedUser, limitGrantedRoles
from Products.CMFCore.utils import getToolByName, _dtmldir
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.interfaces.DublinCore import DublinCore, MutableDublinCore
from Products.CMFCore.interfaces.Discussions import Discussable
from StatelessTree import constructNavigationTreeViewBuilder, \
     NavigationTreeViewBuilder as NTVB

_marker = ()
_icons = {}

def log(summary='', text='', log_level=INFO):
    LOG('Plone Debug', log_level, summary, text)

class PloneTool (UniqueObject, SimpleItem):
    id = 'plone_utils'
    meta_type= 'Plone Utility Tool'
    security = ClassSecurityInfo()
    plone_tool = 1
    field_prefix = 'field_' # Formulator prefixes for forms

    security.declareProtected(CMFCorePermissions.ManagePortal, 'setMemberProperties')
    def setMemberProperties(self, member, **properties):
        membership=getToolByName(self, 'portal_membership')
        if hasattr(member, 'getId'):
            member=member.getId()
        user=membership.getMemberById(member)
        user.setMemberProperties(properties)

    security.declarePublic('sendto')
    def sendto( self, variables = {} ):
        """Sends a link of a page to someone
        """
        if not variables: return
        mail_text = self.sendto_template( self, **variables)
        host = self.MailHost
        host.send( mail_text )

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
        """ responsible for setting metadata on a content object
            we assume the obj implemented IDublinCoreMetadata
        """
        REQUEST=self.REQUEST
        pfx=self.field_prefix

        def tuplify( value ):
            if not type(value) is TupleType:
                value = tuple( value )
            temp = filter( None, value )
            return tuple( temp )

        if DublinCore.isImplementedBy(obj):
            if title is None:
                title=REQUEST.get(pfx+'title', obj.Title())
            if subject is None:
                subject=REQUEST.get(pfx+'subject', obj.Subject())
            if description is None:
                description=REQUEST.get(pfx+'description', obj.Description())
            if contributors is None:
                contributors=tuplify(REQUEST.get(pfx+'contributors',
                                                 obj.Contributors()))
            else:
                contributors=tuplify(contributors)
                
            if effective_date is None:
                effective_date=REQUEST.get(pfx+'effective_date',
                                           obj.EffectiveDate())
            if effective_date == '':
                effective_date = 'None'
            if expiration_date is None:
                expiration_date=REQUEST.get(pfx+'expiration_date',
                                            obj.ExpirationDate())
            if expiration_date == '':
                expiration_date = 'None'
            if format is None:
                format=REQUEST.get('text_format', obj.Format())
            if language is None:
                language=REQUEST.get(pfx+'language', obj.Language())
            if rights is None:
                rights=REQUEST.get(pfx+'rights', obj.Rights())

        if Discussable.isImplementedBy(obj): 
            if allowDiscussion and type(allowDiscussion)==StringType:
                allowDiscussion=allowDiscussion.lower().strip()
            if allowDiscussion=='default': 
                allowDiscussion=None
            elif allowDiscussion=='off': 
                allowDiscussion=0
            elif allowDiscussion=='on': 
                allowDiscussion=1
            disc_tool = getToolByName(self, 'portal_discussion')
            disc_tool.overrideDiscussionFor(obj, allowDiscussion)

        if MutableDublinCore.isImplementedBy(obj):
            obj.setTitle(title)
            obj.setDescription(description)
            obj.setSubject(subject)
            obj.setContributors(contributors)
            obj.setEffectiveDate(effective_date)
            obj.setExpirationDate(expiration_date)
            obj.setFormat(format)
            obj.setLanguage(language)
            obj.setRights(rights)

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
        get_transaction().note(msg)

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
        except: #XXX ick
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

InitializeClass(PloneTool)

