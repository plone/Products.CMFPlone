from Globals import DTMLFile
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager

from zope.interface import implements
from zope.i18n import translate

from Products.CMFCore.Expression import Expression, createExprContext
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.permissions import ManagePortal, View
from Products.CMFCore.utils import _checkPermission, getToolByName, UniqueObject
from Products.CMFCore.utils import registerToolInterface

import ToolNames
from interfaces import IControlPanel
from Products.CMFPlone.PloneBaseTool import PloneBaseTool

class PloneConfiglet(ActionInformation):

    def __init__(self, appId, **kwargs):
        self.appId=appId
        ActionInformation.__init__(self,**kwargs)

    def getAppId(self):
        return self.appId

    def getDescription(self):
        return self.description

    def clone(self):
        return self.__class__(**self.__dict__)

    def getAction(self,ec):
        res=ActionInformation.getAction(self,ec)
        res['description']=self.getDescription()
        return res

class PloneControlPanel(PloneBaseTool, UniqueObject,
                        Folder, ActionProviderBase, PropertyManager):
    """Weave together the various sources of "actions" which
    are apropos to the current user and context.
    """

    implements(IControlPanel)

    security = ClassSecurityInfo()

    id = 'portal_controlpanel'
    title = 'Control Panel'
    toolicon = 'skins/plone_images/site_icon.gif'
    meta_type = ToolNames.ControlPanelTool
    _actions_form = DTMLFile( 'www/editPloneConfiglets', globals() )

    _properties=(
        {'id':'groups','type':'lines'},
    )

    manage_options = (ActionProviderBase.manage_options +
                      PropertyManager.manage_options)

    # TODO this is still used but should be handled by the GS profile
    groups = ['member|Member|My Preferences',
              'site|Plone|Plone Configuration',
              'site|Products|Add-on Product Configuration']


    def __init__(self, **kw):
        if kw:
            self.__dict__.update(**kw)
        if not self.__dict__.has_key('groups'):
            self.__dict__['groups'] = self.groups

    security.declareProtected( ManagePortal, 'registerConfiglets' )
    def registerConfiglets(self,configlets):
        """ ATTENTION: must be called AFTER portal_actionicons
        is installed
        """
        for conf in configlets:
            self.registerConfiglet(**conf)

    security.declareProtected( ManagePortal, 'getGroupIds' )
    def getGroupIds(self, category=''):
        return [g.split('|')[1] for g in self.groups
                if category=='' or g.split('|')[0]==category]

    security.declareProtected( View, 'getGroups' )
    def getGroups(self,category=''):
        return [{'id':g.split('|')[1], 'title':g.split('|')[2]}
                for g in self.groups
                if category=='' or g.split('|')[0]==category]

    security.declarePublic( 'enumConfiglets' )
    def enumConfiglets(self, group=None):
        portal=getToolByName(self, 'portal_url').getPortalObject()
        mtool = getToolByName(self, 'portal_membership')
        context=createExprContext(self, portal, self)
        res = []
        for a in self.listActions():
            verified = 0
            for permission in a.permissions:
                if _checkPermission(permission, portal):
                    verified = 1
            if verified and a.category==group and a.testCondition(context):
                res.append(a.getAction(context))
        # Translate the title for sorting
        if getattr(self, 'REQUEST', None) is not None:
            for a in res:
                a['title'] = translate(a['title'],
                                       domain='plone',
                                       context=self.REQUEST)
        def _title(v):
            return v['title']
        res.sort(key=_title)
        return res

    security.declareProtected( ManagePortal, 'unregisterConfiglet' )
    def unregisterConfiglet(self,id):
        actids= [o.id for o in self.listActions()]
        selection=[actids.index(a) for a in actids if a==id]
        self.deleteActions(selection)

        actionicons=getToolByName(self,'portal_actionicons')
        if actionicons.queryActionInfo('controlpanel', id, None):
            actionicons.removeActionIcon('controlpanel', id)


    security.declareProtected( ManagePortal, 'unregisterApplication' )
    def unregisterApplication(self,appId):
        acts=list(self.listActions())
        selection=[acts.index(a) for a in acts if a.appId==appId]
        self.deleteActions(selection)

        actionicons=getToolByName(self,'portal_actionicons')
        for a in acts:
            if (a.appId == appId and
                actionicons.queryActionInfo('controlpanel', a.id, None)):
                actionicons.removeActionIcon('controlpanel', a.id)


    def _extractAction( self, properties, index ):
        """ Extract an ActionInformation from the funky form properties.
        """
        id          = str( properties.get( 'id_%d'          % index, '' ) )
        name        = str( properties.get( 'name_%d'        % index, '' ) )
        action      = str( properties.get( 'action_%d'      % index, '' ) )
        condition   = str( properties.get( 'condition_%d'   % index, '' ) )
        category    = str( properties.get( 'category_%d'    % index, '' ))
        visible     =      properties.get( 'visible_%d'     % index, 0  )
        permissions =      properties.get( 'permission_%d'  % index, () )
        appId       =      properties.get( 'appId_%d'  % index, '' )
        description =      properties.get( 'description_%d'  % index, '' )

        if not name:
            raise ValueError('A name is required.')

        if action is not '':
            action = Expression( text=action )

        if condition is not '':
            condition = Expression( text=condition )

        if category == '':
            category = 'object'

        if type( visible ) is not type( 0 ):
            try:
                visible = int( visible )
            except ValueError:
                visible = 0

        if type( permissions ) is type( '' ):
            permissions = ( permissions, )

        return PloneConfiglet( id=id
                                , title=name
                                , action=action
                                , condition=condition
                                , permissions=permissions
                                , category=category
                                , visible=visible
                                , appId = appId
                                , description = description
                                )
    security.declareProtected( ManagePortal, 'addAction' )
    def addAction( self
                 , id
                 , name
                 , action
                 , condition=''
                 , permission=''
                 , category='Plone'
                 , visible=1
                 , appId=None
                 , imageUrl=None
                 , description=''
                 , REQUEST=None
                 ):
        """ Add an action to our list.
            attention: must be called AFTER portal_actionicons is installed
        """
        if not name:
            raise ValueError('A name is required.')

        a_expr = action and Expression(text=str(action)) or ''
        c_expr = condition and Expression(text=str(condition)) or ''

        if type( permission ) != type( () ):
            permission = permission and (str(permission),) or ()

        new_actions = self._cloneActions()

        new_action = PloneConfiglet( id=str(id)
                                      , title=str(name)
                                      , action=a_expr
                                      , condition=c_expr
                                      , permissions=permission
                                      , category=str(category)
                                      , visible=int(visible)
                                      , appId=appId
                                      , description=description
                                      )

        new_actions.append( new_action )
        self._actions = tuple( new_actions )

        if imageUrl:
            actionicons=getToolByName(self,'portal_actionicons')
            actionicons.addActionIcon('controlpanel', new_action.id,
                                      imageUrl, new_action.title)


        if REQUEST is not None:
            return self.manage_editActionsForm(
                REQUEST, manage_tabs_message='Added.')

    registerConfiglet=addAction

    security.declareProtected( ManagePortal, 'manage_editActionsForm' )
    def manage_editActionsForm( self, REQUEST, manage_tabs_message=None ):
        """ Show the 'Actions' management tab.
        """
        actions = []

        for a in self.listActions():

            a1 = {}
            a1['id'] = a.getId()
            a1['name'] = a.Title()
            p = a.getPermissions()
            if p:
                a1['permission'] = p[0]
            else:
                a1['permission'] = ''
            a1['category'] = a.getCategory() or 'object'
            a1['visible'] = a.getVisibility()
            a1['action'] = a.getActionExpression()
            a1['condition'] = a.getCondition()
            a1['appId'] = a.getAppId()
            a1['description']=a.getDescription()
            actions.append(a1)

        # possible_permissions is in AccessControl.Role.RoleManager.
        pp = self.possible_permissions()
        return self._actions_form( self
                                 , REQUEST
                                 , actions=actions
                                 , possible_permissions=pp
                                 , management_view='Actions'
                                 , manage_tabs_message=manage_tabs_message
                                 )

InitializeClass(PloneControlPanel)
registerToolInterface('portal_controlpanel', IControlPanel)
