# -*- coding: utf-8 -*-
from plone.autoform.form import AutoExtensibleForm
from Products.CMFCore.ActionInformation import Action
from Products.CMFCore.interfaces import IAction
from Products.CMFCore.interfaces import IActionCategory
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IActionSchema
from Products.CMFPlone.interfaces import INewActionSchema
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import form
from zope.component import adapter
from zope.event import notify
from zope.interface import implementer
from zope.lifecycleevent import ObjectCreatedEvent


class ActionListControlPanel(BrowserView):
    """Control panel for the portal actions."""

    template = ViewPageTemplateFile('actions.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.portal_actions = getToolByName(self.context, 'portal_actions')

    def display(self):
        actions = []
        for category in self.portal_actions.objectValues():
            if category.id == 'controlpanel':
                continue
            if not IActionCategory.providedBy(category):
                continue
            cat_infos = {
                'id': category.id,
                'title': category.title or category.id,
            }
            action_list = []
            for action in category.objectValues():
                if IAction.providedBy(action):
                    action_list.append({
                        'id': action.id,
                        'title': action.title,
                        'url': action.absolute_url(),
                        'visible': action.visible,
                    })
            cat_infos['actions'] = action_list
            actions.append(cat_infos)

        self.actions = actions
        return self.template()

    def __call__(self):
        if self.request.get('delete'):
            action_id = self.request['actionid']
            category = self.portal_actions[self.request['category']]
            category.manage_delObjects([action_id])
            self.request.RESPONSE.redirect('@@actions-controlpanel')
        if self.request.get('hide'):
            action_id = self.request['actionid']
            category = self.portal_actions[self.request['category']]
            category[action_id].visible = False
            self.request.RESPONSE.redirect('@@actions-controlpanel')
        if self.request.get('show'):
            action_id = self.request['actionid']
            category = self.portal_actions[self.request['category']]
            category[action_id].visible = True
            self.request.RESPONSE.redirect('@@actions-controlpanel')
        return self.display()


@implementer(IActionSchema)
@adapter(IAction)
class ActionControlPanelAdapter(object):
    """Adapter for action form."""

    def __init__(self, context):
        self.context = context
        self.current_category = self.context.getParentNode()

    @property
    def category(self):
        return self.current_category.id

    @category.setter
    def category(self, value):
        portal_actions = getToolByName(self.context, 'portal_actions')
        new_category = portal_actions.get(value)
        cookie = self.current_category.manage_cutObjects(ids=[self.context.id])
        new_category.manage_pasteObjects(cookie)

    @property
    def title(self):
        return self.context.title

    @title.setter
    def title(self, value):
        self.context._setPropValue('title', value)

    @property
    def description(self):
        return self.context.description

    @description.setter
    def description(self, value):
        self.context._setPropValue('description', value)

    @property
    def i18n_domain(self):
        return self.context.i18n_domain

    @i18n_domain.setter
    def i18n_domain(self, value):
        self.context._setPropValue('i18n_domain', value)

    @property
    def url_expr(self):
        return self.context.url_expr

    @url_expr.setter
    def url_expr(self, value):
        self.context._setPropValue('url_expr', value)

    @property
    def available_expr(self):
        return self.context.available_expr

    @available_expr.setter
    def available_expr(self, value):
        self.context._setPropValue('available_expr', value)

    @property
    def permissions(self):
        return self.context.permissions

    @permissions.setter
    def permissions(self, value):
        self.context._setPropValue('permissions', value)

    @property
    def visible(self):
        return self.context.visible

    @visible.setter
    def visible(self, value):
        self.context._setPropValue('visible', value)

    @property
    def position(self):
        position = self.current_category.objectIds().index(self.context.id)
        return position + 1

    @position.setter
    def position(self, value):
        current_position = self.current_category.objectIds().index(
            self.context.id)
        all_actions = list(self.current_category._objects)
        current_action = all_actions.pop(current_position)
        new_position = value - 1
        all_actions = all_actions[0:new_position] + [current_action] + \
            all_actions[new_position:]
        self.current_category._objects = tuple(all_actions)


class ActionControlPanel(AutoExtensibleForm, form.EditForm):
    """A form to edit a portal action."""

    schema = IActionSchema
    ignoreContext = False
    label = _(u'Action Settings')


class NewActionControlPanel(AutoExtensibleForm, form.AddForm):
    """A form to add a new portal action."""

    schema = INewActionSchema
    ignoreContext = True
    label = _(u'New action')

    def createAndAdd(self, data):
        portal_actions = getToolByName(self.context, 'portal_actions')
        category = portal_actions.get(data['category'])
        action_id = data['id']
        action = Action(
            action_id,
            title=action_id,
            i18n_domain='plone',
            permissions=['View'],
        )
        category[action_id] = action
        notify(ObjectCreatedEvent(action))
