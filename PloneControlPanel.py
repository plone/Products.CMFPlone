from Globals import InitializeClass, DTMLFile, package_home
from Acquisition import aq_base, aq_inner, aq_parent
from AccessControl import ClassSecurityInfo
from OFS.Folder import Folder
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager

from Products.CMFCore.Expression import Expression, createExprContext
from Products.CMFCore.ActionInformation import ActionInformation, oai
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.TypesTool import TypeInformation
from Products.CMFCore.CMFCorePermissions import ManagePortal
from Products.CMFCore.utils import _checkPermission, _dtmldir, getToolByName, SimpleItemWithProperties, UniqueObject

from Products.CMFCore.interfaces.portal_actions import portal_actions as IActionsTool

class PloneConfiglet(ActionInformation):
    def __init__(self,appId,**kwargs):
        self.appId=appId
        ActionInformation.__init__(self,**kwargs)
        
    def getAppId(self):
        return self.appId
    
    def clone(self):
        return self.__class__(**self.__dict__)
    
default_configlets = (
    {'id':'QuickInstaller','appId':'QuickInstaller','name':'Install Products',
        'action':'prefs_install_products_form','category':'Plone','permission': ManagePortal},
    {'id':'PloneReconfig','appId':'Plone','name':'Reconfigure Portal',
        'action':'reconfig_form','category':'Plone','permission': ManagePortal},
)
        
class PloneControlPanel(UniqueObject, Folder, ActionProviderBase, PropertyManager):
    """
        Weave together the various sources of "actions" which are apropos
        to the current user and context.
    """

    __implements__ = (IActionsTool, ActionProviderBase.__implements__)

    security = ClassSecurityInfo()

    id = 'portal_configuration'
    meta_type = 'Plone Control Panel'
    _actions_form = DTMLFile( 'www/editPloneConfiglets', globals() )

    _properties=(
        {'id':'groups','type':'lines'},
    )

    manage_options=ActionProviderBase.manage_options + PropertyManager.manage_options

    groups=['Plone|Plone System','Products|Registered Products']

    def __init__(self,**kw):
        if kw:
            self.__dict__.update(**kw)
        for conf in default_configlets:
            self.registerConfiglet(**conf)
        
    def getGroupIds(self):
        return [g.split('|')[0] for g in self.groups]

    def getGroups(self):
        return [{'id':g.split('|')[0],'title':g.split('|')[-1]} for g in self.groups]

    def enumConfiglets(self,group=None):
        portal=getToolByName(self,'portal_url').getPortalObject()
        context=createExprContext(self,portal,self)
        return [a.getAction(context) for a in self.listActions() if a.category==group and a.testCondition(context)]

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
            except:
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
                                )
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
                 , REQUEST=None
                 ):
        """ Add an action to our list.
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
                                      )

        new_actions.append( new_action )
        self._actions = tuple( new_actions )

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
