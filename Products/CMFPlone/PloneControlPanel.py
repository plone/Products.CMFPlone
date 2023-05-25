from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from App.special_dtml import DTMLFile
from OFS.Folder import Folder
from OFS.PropertyManager import PropertyManager
from plone.base import PloneMessageFactory as _
from plone.base.interfaces import IControlPanel
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.Expression import createExprContext
from Products.CMFCore.Expression import Expression
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import registerToolInterface
from Products.CMFCore.utils import UniqueObject
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from zope.component.hooks import getSite
from zope.i18n import translate
from zope.i18nmessageid import Message
from zope.interface import implementer


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
        res["description"] = self.getDescription()
        return res


@implementer(IControlPanel)
class PloneControlPanel(
    PloneBaseTool, UniqueObject, Folder, ActionProviderBase, PropertyManager
):
    """Weave together the various sources of "actions" which
    are apropos to the current user and context.
    """

    security = ClassSecurityInfo()

    id = "portal_controlpanel"
    title = "Control Panel"
    toolicon = "skins/plone_images/site_icon.png"
    meta_type = "Plone Control Panel Tool"
    _actions_form = DTMLFile("www/editPloneConfiglets", globals())

    manage_options = ActionProviderBase.manage_options + PropertyManager.manage_options

    group = dict(
        member=[
            ("Member", _("My Preferences")),
        ],
        site=[
            ("plone-general", _("General")),
            ("plone-content", _("Content")),
            ("plone-users", _("Users")),
            ("plone-security", _("Security")),
            ("plone-advanced", _("Advanced")),
            ("Plone", _("Plone Configuration")),
            ("Products", _("Add-on Configuration")),
        ],
    )

    def __init__(self, **kw):
        if kw:
            self.__dict__.update(**kw)

    security.declareProtected(ManagePortal, "registerConfiglets")

    def registerConfiglets(self, configlets):
        for conf in configlets:
            self.registerConfiglet(**conf)

    security.declareProtected(ManagePortal, "getGroupIds")

    def getGroupIds(self, category="site"):
        groups = self.group.get(category, [])
        return [g[0] for g in groups if g]

    security.declareProtected(View, "getGroups")

    def getGroups(self, category="site"):
        groups = self.group.get(category, [])
        return [{"id": g[0], "title": g[1]} for g in groups if g]

    security.declarePrivate("listActions")

    def listActions(self, info=None, object=None):
        # This exists here to shut up a deprecation warning about old-style
        # actions in CMFCore's ActionProviderBase.  It was decided not to
        # move configlets to be based on action tool categories for Plone 4
        # (see PLIP #8804), but that (or an alternative) will have to happen
        # before CMF 2.4 when support for old-style actions is removed.
        return self._actions or ()

    security.declarePublic("maySeeSomeConfiglets")

    def maySeeSomeConfiglets(self):
        groups = self.getGroups("site")

        all = []
        for group in groups:
            all.extend(self.enumConfiglets(group=group["id"]))
        all = [item for item in all if item["visible"]]
        return len(all) != 0

    security.declarePublic("enumConfiglets")

    def enumConfiglets(self, group=None):
        portal = getToolByName(self, "portal_url").getPortalObject()
        context = createExprContext(self, portal, self)
        res = []
        for a in self.listActions():
            verified = 0
            for permission in a.permissions:
                if _checkPermission(permission, portal):
                    verified = 1
            if (
                verified
                and a.category == group
                and a.visible
                and a.testCondition(context)
            ):
                res.append(a.getAction(context))
        # Translate the title for sorting
        if getattr(self, "REQUEST", None) is not None:
            for a in res:
                title = a["title"]
                if not isinstance(title, Message):
                    title = Message(title, domain="plone")
                a["title"] = translate(title, context=self.REQUEST)

        def _title(v):
            return v["title"]

        res.sort(key=_title)
        return res

    security.declareProtected(ManagePortal, "unregisterConfiglet")

    def unregisterConfiglet(self, id):
        actids = [o.id for o in self.listActions()]
        selection = [actids.index(a) for a in actids if a == id]
        if not selection:
            return
        self.deleteActions(selection)

    security.declareProtected(ManagePortal, "unregisterApplication")

    def unregisterApplication(self, appId):
        acts = list(self.listActions())
        selection = [acts.index(a) for a in acts if a.appId == appId]
        if not selection:
            return
        self.deleteActions(selection)

    def _extractAction(self, properties, index):
        # Extract an ActionInformation from the funky form properties.
        id = str(properties.get("id_%d" % index, ""))
        name = str(properties.get("name_%d" % index, ""))
        action = str(properties.get("action_%d" % index, ""))
        condition = str(properties.get("condition_%d" % index, ""))
        category = str(properties.get("category_%d" % index, ""))
        visible = properties.get("visible_%d" % index, 0)
        permissions = properties.get("permission_%d" % index, ())
        appId = properties.get("appId_%d" % index, "")
        description = properties.get("description_%d" % index, "")
        icon_expr = properties.get("icon_expr_%d" % index, "")

        if not name:
            raise ValueError("A name is required.")

        if action != "":
            action = Expression(text=action)

        if condition != "":
            condition = Expression(text=condition)

        if category == "":
            category = "object"

        if not isinstance(visible, int):
            try:
                visible = int(visible)
            except ValueError:
                visible = 0

        if isinstance(permissions, str):
            permissions = (permissions,)

        return PloneConfiglet(
            id=id,
            title=name,
            action=action,
            condition=condition,
            permissions=permissions,
            category=category,
            visible=visible,
            appId=appId,
            description=description,
            icon_expr=icon_expr,
        )

    security.declareProtected(ManagePortal, "addAction")

    def addAction(
        self,
        id,
        name,
        action,
        condition="",
        permission="",
        category="Plone",
        visible=1,
        appId=None,
        icon_expr="",
        description="",
        REQUEST=None,
    ):
        """Add an action to our list."""
        if not name:
            raise ValueError("A name is required.")

        a_expr = action and Expression(text=str(action)) or ""
        c_expr = condition and Expression(text=str(condition)) or ""

        if not isinstance(permission, tuple):
            permission = permission and (str(permission),) or ()

        new_actions = self._cloneActions()

        new_action = PloneConfiglet(
            id=str(id),
            title=name,
            action=a_expr,
            condition=c_expr,
            permissions=permission,
            category=str(category),
            visible=int(visible),
            appId=appId,
            description=description,
            icon_expr=icon_expr,
        )

        new_actions.append(new_action)
        self._actions = tuple(new_actions)

        if REQUEST is not None:
            return self.manage_editActionsForm(REQUEST, manage_tabs_message="Added.")

    security.declareProtected(ManagePortal, "registerConfiglet")
    registerConfiglet = addAction

    security.declareProtected(ManagePortal, "manage_editActionsForm")

    def manage_editActionsForm(self, REQUEST, manage_tabs_message=None):
        """Show the 'Actions' management tab."""
        actions = []

        for a in self.listActions():
            a1 = {}
            a1["id"] = a.getId()
            a1["name"] = a.Title()
            p = a.getPermissions()
            if p:
                a1["permission"] = p[0]
            else:
                a1["permission"] = ""
            a1["category"] = a.getCategory() or "object"
            a1["visible"] = a.getVisibility()
            a1["action"] = a.getActionExpression()
            a1["condition"] = a.getCondition()
            a1["appId"] = a.getAppId()
            a1["description"] = a.getDescription()
            a1["icon_expr"] = a.getIconExpression()
            actions.append(a1)

        # possible_permissions is in OFS.role.RoleManager.
        pp = self.possible_permissions()
        return self._actions_form(
            self,
            REQUEST,
            actions=actions,
            possible_permissions=pp,
            management_view="Actions",
            manage_tabs_message=manage_tabs_message,
        )

    @property
    def site_url(self):
        """Return the absolute URL to the current site, which is likely not
        necessarily the portal root.
        Used by ``portlet_prefs`` to construct the URL to
        ``@@overview-controlpanel``.
        """
        return getSite().absolute_url()


InitializeClass(PloneControlPanel)
registerToolInterface("portal_controlpanel", IControlPanel)
