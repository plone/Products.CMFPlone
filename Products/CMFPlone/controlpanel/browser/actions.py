from plone.autoform.form import AutoExtensibleForm
from plone.base import PloneMessageFactory as _
from plone.base.interfaces import IActionSchema
from plone.base.interfaces import INewActionSchema
from plone.base.utils import base_hasattr
from Products.CMFCore.ActionInformation import Action
from Products.CMFCore.interfaces import IAction
from Products.CMFCore.interfaces import IActionCategory
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import form
from zope.component import adapter
from zope.event import notify
from zope.interface import implementer
from zope.lifecycleevent import ObjectCreatedEvent


class ActionListControlPanel(BrowserView):
    """Control panel for the portal actions."""

    template = ViewPageTemplateFile("actions.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.portal_actions = getToolByName(self.context, "portal_actions")

    def display(self):
        actions = []
        for category in self.portal_actions.objectValues():
            if category.id == "controlpanel":
                continue
            if not IActionCategory.providedBy(category):
                continue
            cat_infos = {
                "id": category.id,
                "title": category.title or category.id,
            }
            action_list = []
            for action in category.objectValues():
                if IAction.providedBy(action):
                    action_list.append(
                        {
                            "id": action.id,
                            "title": action.title,
                            "url": action.absolute_url(),
                            "visible": action.visible,
                        }
                    )
            cat_infos["actions"] = action_list
            actions.append(cat_infos)

        self.actions = actions
        return self.template()

    def __call__(self):
        if self.request.get("delete"):
            action_id = self.request["actionid"]
            category = self.portal_actions[self.request["category"]]
            category.manage_delObjects([action_id])
            self.request.RESPONSE.redirect("@@actions-controlpanel")
        if self.request.get("hide"):
            action_id = self.request["actionid"]
            category = self.portal_actions[self.request["category"]]
            category[action_id].visible = False
            self.request.RESPONSE.redirect("@@actions-controlpanel")
        if self.request.get("show"):
            action_id = self.request["actionid"]
            category = self.portal_actions[self.request["category"]]
            category[action_id].visible = True
            self.request.RESPONSE.redirect("@@actions-controlpanel")
        return self.display()


@adapter(IAction)
@implementer(IActionSchema)
class ActionControlPanelAdapter:
    """Adapter for action form."""

    def __init__(self, context):
        self.context = context
        self.current_category = self.context.getParentNode()

    def get_category(self):
        return self.current_category.id

    def set_category(self, value):
        portal_actions = getToolByName(self.context, "portal_actions")
        new_category = portal_actions.get(value)
        cookie = self.current_category.manage_cutObjects(ids=[self.context.id])
        new_category.manage_pasteObjects(cookie)

    category = property(get_category, set_category)

    def get_title(self):
        return self.context.title

    def set_title(self, value):
        self.context._setPropValue("title", value)

    title = property(get_title, set_title)

    def get_description(self):
        return self.context.description

    def set_description(self, value):
        self.context._setPropValue("description", value)

    description = property(get_description, set_description)

    def get_i18n_domain(self):
        return self.context.i18n_domain

    def set_i18n_domain(self, value):
        self.context._setPropValue("i18n_domain", value)

    i18n_domain = property(get_i18n_domain, set_i18n_domain)

    def get_url_expr(self):
        return self.context.url_expr

    def set_url_expr(self, value):
        self.context._setPropValue("url_expr", value)

    url_expr = property(get_url_expr, set_url_expr)

    def get_available_expr(self):
        return self.context.available_expr

    def set_available_expr(self, value):
        self.context._setPropValue("available_expr", value)

    available_expr = property(get_available_expr, set_available_expr)

    def get_permissions(self):
        return self.context.permissions

    def set_permissions(self, value):
        self.context._setPropValue("permissions", value)

    permissions = property(get_permissions, set_permissions)

    def get_visible(self):
        return self.context.visible

    def set_visible(self, value):
        self.context._setPropValue("visible", value)

    visible = property(get_visible, set_visible)

    def get_position(self):
        position = self.current_category.objectIds().index(self.context.id)
        return position + 1

    def set_position(self, value):
        current_position = self.current_category.objectIds().index(self.context.id)
        all_actions = list(self.current_category._objects)
        current_action = all_actions.pop(current_position)
        new_position = value - 1
        all_actions = (
            all_actions[0:new_position] + [current_action] + all_actions[new_position:]
        )
        self.current_category._objects = tuple(all_actions)

    position = property(get_position, set_position)

    def get_modal(self):
        return self.context.modal

    def set_modal(self, value):
        # This property may not exist yet on the context.
        if not self.context.hasProperty("modal"):
            if base_hasattr(self.context, "modal"):
                # We cannot define a property when an attribute with the same
                # name already exists.
                delattr(self.context, "modal")
            self.context._setProperty("modal", value, "string")
        else:
            self.context._setPropValue("modal", value)

    modal = property(get_modal, set_modal)


class ActionControlPanel(AutoExtensibleForm, form.EditForm):
    """A form to edit a portal action."""

    schema = IActionSchema
    ignoreContext = False
    label = _("Action Settings")


class NewActionControlPanel(AutoExtensibleForm, form.AddForm):
    """A form to add a new portal action."""

    schema = INewActionSchema
    ignoreContext = True
    label = _("New action")

    def createAndAdd(self, data):
        portal_actions = getToolByName(self.context, "portal_actions")
        category = portal_actions.get(data["category"])
        action_id = data["id"]
        action = Action(
            action_id,
            title=action_id,
            i18n_domain="plone",
            permissions=["View"],
        )
        category[action_id] = action
        notify(ObjectCreatedEvent(action))
