from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.utils import _checkPermission, _getAuthenticatedUser, limitGrantedRoles
from Products.CMFCore.utils import getToolByName, _dtmldir
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass, DTMLFile
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.interfaces.DublinCore import DublinCore
from types import TupleType

class PloneTool (UniqueObject, SimpleItem):
    id = 'plone_utils'
    meta_type= 'Plone Utility Tool'
    security = ClassSecurityInfo()
    plone_tool = 1
    field_prefix = 'field_' #Formulator prefixes for forms

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
            if allowDiscussion.lower().strip()=='default': allowDiscussion=None
            elif allowDiscussion.lower().strip()=='off': allowDiscussion=0
            elif allowDiscussion.lower().strip()=='on': allowDiscussion=1
            getToolByName(self, 'portal_discussion').overrideDiscussionFor(obj, allowDiscussion)
	#mutate metadata on the object
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
	get_transaction().note(msg)
	
    security.declarePublic('contentEdit')
    def contentEdit(self, obj, **kwargs):
        """ encapsulates how the editing of content occurs """

        if DublinCore.isImplementedBy(obj):
            apply(self.editMetadata, (obj,), kwargs)

        if kwargs.get('id', None) is not None: 
            self._renameObject(obj, id=kwargs['id']) 
	
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

InitializeClass(PloneTool)

