from AccessControl import ClassSecurityInfo
from App.special_dtml import DTMLFile
from App.class_init import InitializeClass
from OFS.Folder import Folder
from OFS.PropertyManager import PropertyManager

from zope.interface import implements
from zope.i18n import translate
from zope.i18nmessageid import Message

from Products.CMFCore.Expression import Expression, createExprContext
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.permissions import ManagePortal, View
from Products.CMFCore.utils import _checkPermission, getToolByName, UniqueObject
from Products.CMFCore.utils import registerToolInterface

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IControlPanel
from Products.CMFPlone.log import log_deprecated
from Products.CMFPlone.PloneBaseTool import PloneBaseTool


class PloneConfiglet(ActionInformation):

    def __init__(self, appId, **kwargs):
        self.appId = appId
        ActionInformation.__init__(self, **kwargs)

    def getAppId(self):
        return self.appId

    def getDescription(self):
        return self.description

    def clone(self):
        return self.__class__(**self.__dict__)

    def getAction(self, ec):
        res = ActionInformation.getAction(self, ec)
        res['description'] = self.getDescription()
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
    toolicon = 'skins/plone_images/site_icon.png'
    meta_type = 'Plone Control Panel Tool'
    _actions_form = DTMLFile('www/editPloneConfiglets', globals())

    manage_options = (ActionProviderBase.manage_options +
                      PropertyManager.manage_options)

    group = dict(
        member=[
            ('Member', _(u'My Preferences')),
        ],
        site=[('Plone', _(u'Plone Configuration')),
              ('Products', _(u'Add-on Configuration')),
             ]
    )

    def __init__(self, **kw):
        if kw:
            self.__dict__.update(**kw)

    security.declareProtected(ManagePortal, 'registerConfiglets')
    def registerConfiglets(self, configlets):
        """ ATTENTION: must be called AFTER portal_actionicons
        is installed
        """
        for conf in configlets:
            self.registerConfiglet(**conf)

    security.declareProtected(ManagePortal, 'getGroupIds')
    def getGroupIds(self, category='site'):
        groups = self.group.get(category, [])
        return [g[0] for g in groups if g]

    security.declareProtected(View, 'getGroups')
    def getGroups(self, category='site'):
        groups = self.group.get(category, [])
        return [{'id': g[0], 'title': g[1]} for g in groups if g]

    security.declarePrivate('listActions')
    def listActions(self, info=None, object=None):
        # This exists here to shut up a deprecation warning about old-style
        # actions in CMFCore's ActionProviderBase.  It was decided not to
        # move configlets to be based on action tool categories for Plone 4
        # (see PLIP #8804), but that (or an alternative) will have to happen
        # before CMF 2.4 when support for old-style actions is removed.
        return self._actions or ()

    security.declarePublic('enumConfiglets')
    def enumConfiglets(self, group=None):
        portal = getToolByName(self, 'portal_url').getPortalObject()
        context = createExprContext(self, portal, self)
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
                title = a['title']
                if not isinstance(title, Message):
                    title = Message(title, domain='plone')
                a['title'] = translate(title,
                                       context=self.REQUEST)

        def _title(v):
            return v['title']

        res.sort(key=_title)
        return res

    security.declareProtected(ManagePortal, 'unregisterConfiglet')
    def unregisterConfiglet(self, id):
        actids = [o.id for o in self.listActions()]
        selection = [actids.index(a) for a in actids if a==id]
        self.deleteActions(selection)

        # BBB
        actionicons = getToolByName(self, 'portal_actionicons', None)
        if actionicons is not None:
            if actionicons.queryActionInfo('controlpanel', id, None):
                actionicons.removeActionIcon('controlpanel', id)


    security.declareProtected(ManagePortal, 'unregisterApplication')
    def unregisterApplication(self, appId):
        acts = list(self.listActions())
        selection = [acts.index(a) for a in acts if a.appId == appId]
        self.deleteActions(selection)

        # BBB
        actionicons=getToolByName(self, 'portal_actionicons', None)
        if actionicons is not None:
            for a in acts:
                if (a.appId == appId and
                    actionicons.queryActionInfo('controlpanel', a.id, None)):
                    actionicons.removeActionIcon('controlpanel', a.id)


    def _extractAction(self, properties, index):
        """ Extract an ActionInformation from the funky form properties.
        """
        id          = str(properties.get('id_%d'          % index, ''))
        name        = str(properties.get('name_%d'        % index, ''))
        action      = str(properties.get('action_%d'      % index, ''))
        condition   = str(properties.get('condition_%d'   % index, ''))
        category    = str(properties.get('category_%d'    % index, ''))
        visible     =     properties.get('visible_%d'     % index, 0)
        permissions =     properties.get('permission_%d'  % index, ())
        appId       =     properties.get('appId_%d'  % index, '')
        description =     properties.get('description_%d'  % index, '')
        icon_expr   =     properties.get('icon_expr_%d'   % index, '')

        if not name:
            raise ValueError('A name is required.')

        if action is not '':
            action = Expression(text=action)

        if condition is not '':
            condition = Expression(text=condition)

        if category == '':
            category = 'object'

        if type(visible) is not type(0):
            try:
                visible = int(visible)
            except ValueError:
                visible = 0

        if type(permissions) is type(''):
            permissions = (permissions, )

        return PloneConfiglet(id=id,
                              title=name,
                              action=action,
                              condition=condition,
                              permissions=permissions,
                              category=category,
                              visible=visible,
                              appId = appId,
                              description = description,
                              icon_expr = icon_expr,
                              )

    security.declareProtected(ManagePortal, 'addAction')
    def addAction(self,
                  id,
                  name,
                  action,
                  condition='',
                  permission='',
                  category='Plone',
                  visible=1,
                  appId=None,
                  imageUrl=None,
                  icon_expr = '',
                  description='',
                  REQUEST=None,
                  ):
        """ Add an action to our list.
        """
        if not name:
            raise ValueError('A name is required.')

        a_expr = action and Expression(text=str(action)) or ''
        c_expr = condition and Expression(text=str(condition)) or ''

        if type(permission) != type(()):
            permission = permission and (str(permission), ) or ()

        if imageUrl:
            log_deprecated("The imageUrl parameter of the control panel tool's "
                           "addAction/registerConfiglet method has been "
                           "deprecated and will be removed in Plone 5. "
                           "Please use the icon_expr parameter instead.")
            icon_expr = 'string:${portal_url}/%s' % imageUrl

        new_actions = self._cloneActions()

        new_action = PloneConfiglet(id=str(id),
                                    title=name,
                                    action=a_expr,
                                    condition=c_expr,
                                    permissions=permission,
                                    category=str(category),
                                    visible=int(visible),
                                    appId=appId,
                                    description=description,
                                    icon_expr = icon_expr,
                                    )

        new_actions.append(new_action)
        self._actions = tuple(new_actions)

        if REQUEST is not None:
            return self.manage_editActionsForm(
                REQUEST, manage_tabs_message='Added.')

    registerConfiglet = addAction

    security.declareProtected(ManagePortal, 'manage_editActionsForm')
    def manage_editActionsForm(self, REQUEST, manage_tabs_message=None):
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
            a1['icon_expr'] = a.getIconExpression()
            actions.append(a1)

        # possible_permissions is in OFS.role.RoleManager.
        pp = self.possible_permissions()
        return self._actions_form(self,
                                  REQUEST,
                                  actions=actions,
                                  possible_permissions=pp,
                                  management_view='Actions',
                                  manage_tabs_message=manage_tabs_message,
                                 )

InitializeClass(PloneControlPanel)
registerToolInterface('portal_controlpanel', IControlPanel)
