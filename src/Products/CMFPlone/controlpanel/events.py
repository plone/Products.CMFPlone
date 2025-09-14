from plone.base import PloneMessageFactory as _
from plone.base.interfaces import IConfigurationChangedEvent
from plone.base.interfaces import ISecuritySchema
from plone.base.utils import safe_hasattr
from plone.registry.interfaces import IRecordModifiedEvent
from Products.CMFCore.ActionInformation import Action
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.controlpanel.utils import migrate_from_email_login
from Products.CMFPlone.controlpanel.utils import migrate_to_email_login
from zope.component import adapter
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.ramcache.interfaces.ram import IRAMCache


@implementer(IConfigurationChangedEvent)
class ConfigurationChangedEvent:
    def __init__(self, context, data):
        self.context = context
        self.data = data


@adapter(IConfigurationChangedEvent)
def handleConfigurationChangedEvent(event):
    util = queryUtility(IRAMCache)
    if util is not None:
        util.invalidateAll()


@adapter(ISecuritySchema, IRecordModifiedEvent)
def handle_enable_self_reg(obj, event):
    """Additional configuration when the ``enable_self_reg``
    setting is updated in the ``Security```control panel.

    If the setting is enabled, the ``Add portal member`` permission is
    added to ``Anonymous`` role to allow self registration for anonymous
    users. If the setting is disabled, this permission is removed.
    """
    if event.record.fieldName != "enable_self_reg":
        return

    portal = getSite()
    value = event.newValue
    app_perms = portal.rolesOfPermission(permission="Add portal member")
    reg_roles = []

    for app_perm in app_perms:
        if app_perm["selected"] == "SELECTED":
            reg_roles.append(app_perm["name"])
    if value is True and "Anonymous" not in reg_roles:
        reg_roles.append("Anonymous")
    if value is False and "Anonymous" in reg_roles:
        reg_roles.remove("Anonymous")

    portal.manage_permission("Add portal member", roles=reg_roles, acquire=0)


@adapter(ISecuritySchema, IRecordModifiedEvent)
def handle_enable_user_folders(obj, event):
    """Additional configuration when the ``enable_user_folders``
    setting is updated in the ``Security```control panel.

    If the setting is enabled, a new user action is added with a link to
    the personal folder. If the setting is disabled, the action is hidden.
    """
    if event.record.fieldName != "enable_user_folders":
        return

    portal = getSite()
    value = event.newValue

    membership = getToolByName(portal, "portal_membership")
    membership.memberareaCreationFlag = value

    # support the 'my folder' user action #8417
    portal_actions = getToolByName(portal, "portal_actions", None)
    if portal_actions is not None:
        object_category = getattr(portal_actions, "user", None)
        if value and not safe_hasattr(object_category, "mystuff"):
            # add action
            _add_mystuff_action(object_category)
        elif safe_hasattr(object_category, "mystuff"):
            a = getattr(object_category, "mystuff")
            a.visible = bool(value)  # show/hide action


def _add_mystuff_action(object_category):
    new_action = Action(
        "mystuff",
        title=_("My Folder"),
        description="",
        url_expr="string:${portal/portal_membership/getHomeUrl}",
        available_expr="python:(member is not None) and \
            (portal.portal_membership.getHomeFolder() is not None) ",
        permissions=("View",),
        visible=True,
        i18n_domain="plone",
    )
    object_category._setObject("mystuff", new_action)
    # move action to top, at least before the logout action
    object_category.moveObjectsToTop("mystuff")


@adapter(ISecuritySchema, IRecordModifiedEvent)
def handle_use_email_as_login(obj, event):
    """Additional configuration when the ``use_email_as_login``
    setting is updated in the ``Security```control panel.

    If the setting is enabled, existing users' login names are migrated
    to email. If the setting is disabled, then the login names are migrated
    back to user ids.
    """
    if event.record.fieldName != "use_email_as_login":
        return

    value = event.newValue
    if value == event.oldValue:
        # no change
        return
    context = getSite()
    if value:
        migrate_to_email_login(context)
    else:
        migrate_from_email_login(context)
