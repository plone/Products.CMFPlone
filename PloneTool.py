from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.utils import _checkPermission, _getAuthenticatedUser, limitGrantedRoles
from Products.CMFCore.utils import getToolByName, _dtmldir
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.interfaces.DublinCore import DublinCore
from types import TupleType, UnicodeType
from urllib import urlencode
import urlparse
from cgi import parse_qs

import re
import sys

from zLOG import LOG, INFO, WARNING

def log(summary='', text='', log_level=INFO):
    LOG('Plone Debug', log_level, summary, text)

class PloneTool (UniqueObject, SimpleItem):
    id = 'plone_utils'
    meta_type= 'Plone Utility Tool'
    security = ClassSecurityInfo()
    plone_tool = 1
    field_prefix = 'field_' # Formulator prefixes for forms

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
        if title is None:
            title=REQUEST.get(pfx+'title', obj.Title())
        if subject is None:
            subject=REQUEST.get(pfx+'subject', obj.Subject())
        if description is None:
            description=REQUEST.get(pfx+'description', obj.Description())
        if contributors is None:
            contributors=tuplify(REQUEST.get(pfx+'contributors', obj.Contributors()))
        else:    
            contributors=tuplify(contributors)
        if effective_date is None:
            effective_date=REQUEST.get(pfx+'effective_date', obj.EffectiveDate())
        if expiration_date is None:
            expiration_date=REQUEST.get(pfx+'expiration_date', obj.ExpirationDate())
        if format is None:
            format=REQUEST.get('text_format', obj.Format())
        if language is None:
            language=REQUEST.get(pfx+'language', obj.Language())
        if rights is None:
            rights=REQUEST.get(pfx+'rights', obj.Rights())
        if allowDiscussion:
            allowDiscussion=allowDiscussion.lower().strip()
            if allowDiscussion=='default': allowDiscussion=None
            elif allowDiscussion=='off': allowDiscussion=0
            elif allowDiscussion=='on': allowDiscussion=1
            getToolByName(self, 'portal_discussion').overrideDiscussionFor(obj, allowDiscussion)
            
        obj.editMetadata( title=title
                        , description=description
                        , subject=subject
                        , contributors=contributors
                        , effective_date=effective_date
                        , expiration_date=expiration_date
                        , format=format
                        , language=language
                        , rights=rights )

    #XXX do we ever redirect?
    def _renameObject(self, obj, redirect=0, id=''):
        REQUEST=self.REQUEST
        if not id:
            id = REQUEST.get('id', '')
            id = REQUEST.get(self.field_prefix+'id', '')
        if id!=obj.getId():
            try:
                context.manage_renameObjects( (obj.getId(),), (id,), REQUEST )
            except: #XXX have to do this for Topics and maybe other folderish objects
                obj.aq_parent.manage_renameObjects( (obj.getId(),), (id,), REQUEST)
	if redirect:
            status_msg='portal_status_message='+REQUEST.get( 'portal_status_message', 'Changes+have+been+Saved.')
            return REQUEST.RESPONSE.redirect('%s/%s?%s' % ( REQUEST['URL2'], id, status_msg) )

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

        #XXX Interface package appears to be broken.  Atleast for Forum objects.
        #    it may blow up on things that *done* implement the DublinCore interface. 
        #    Someone please look into this.  We should probably catch the exception (think its Tuple error)
        #    instead of swallowing all exceptions.
        try:
            if DublinCore.isImplementedBy(obj):
                apply(self.editMetadata, (obj,), kwargs)
        except: 
            pass
        
        if kwargs.get('id', None) is not None: 
            self._renameObject(obj, id=kwargs['id'].strip()) 
	
        self._makeTransactionNote(obj) #automated the manual transaction noting in xxxx_edit.py

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

    #convienance method since skinstool requires loads of acrobats.
    #we use this for the reconfig form
    security.declareProtected(CMFCorePermissions.ManagePortal, 'setDefaultSkin')
    def setDefaultSkin(self, default_skin):
        """ sets the default skin """
        st=getToolByName(self, 'portal_skins')
        st.default_skin=default_skin        
     
    #XXX deprecated methods
    security.declarePublic('getNextPageFor')
    def getNextPageFor(self, context, action, status, **kwargs):
        log( 'Plone Tool Deprecation', action + ' has called plone_utils.getNextPageFor()'    
           + ' which has been deprecated use portal_navigation.getNextRequestFor() instead.'
           , WARNING)
        
        nav_tool=getToolByName(self, 'portal_navigation')
        return nav_tool.getNextPageFor(context, action, status, **kwargs)
            
    security.declarePublic('getNextRequestFor')
    def getNextRequestFor(self, context, action, status, **kwargs):
        log( 'Plone Tool Deprecation', action + ' has called plone_utils.getNextPageFor()' 
           + ' which has been deprecated use portal_navigation.getNextRequestFor() instead.'
           , WARNING)
        nav_tool=getToolByName(self, 'portal_navigation')
        return nav_tool.getNextRequestFor(context, action, status, **kwargs)

    security.declareProtected(CMFCorePermissions.ManagePortal, 'changeOwnershipOf')
    def changeOwnershipOf(self, object, owner, recursive=0):
        """ changes the ownership of an object """
        membership=getToolByName(self, 'portal_membership')
        if owner not in membership.listMemberIds():
            raise KeyError, 'Only users in this site can be made owners.'
        acl_users=getattr(self, 'acl_users')
        user = acl_users.getUser(owner)
        if user is not None:
            user= user.__of__(acl_users)
        else:
            from AccessControl import getSecurityManager
            user= getSecurityManager().getUser()

        object.changeOwnership(user, recursive) 
    
    security.declarePublic('urlparse')
    def urlparse(self, url):
        """ returns the pieces of url """
        return urlparse.urlparse(url)


    # expose sys.exc_info() to scripts to allow extraction of
    # information from untyped exceptions
    def exc_info(self):
        return sys.exc_info()[0]


InitializeClass(PloneTool)

