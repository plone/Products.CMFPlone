# -*- coding: utf-8 -*-
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import INavigationSchema
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer


@adapter(IPloneSiteRoot)
@implementer(INavigationSchema)
class NavigationControlPanelAdapter(object):

    def __init__(self, context):
        self.context = context
        registry = getUtility(IRegistry)
        self.navigation_settings = registry.forInterface(
            INavigationSchema,
            prefix="plone"
        )

    def get_generate_tabs(self):
        return self.navigation_settings.generate_tabs

    def set_generate_tabs(self, value):
        self.navigation_settings.generate_tabs = value

    generate_tabs = property(get_generate_tabs, set_generate_tabs)

    def get_nonfolderish_tabs(self):
        return self.navigation_settings.nonfolderish_tabs

    def set_nonfolderish_tabs(self, value):
        self.navigation_settings.nonfolderish_tabs = value

    nonfolderish_tabs = property(get_nonfolderish_tabs, set_nonfolderish_tabs)

    def get_show_excluded_items(self):
        return self.navigation_settings.show_excluded_items

    def set_show_excluded_items(self, value):
        self.navigation_settings.show_excluded_items = value

    show_excluded_items = property(
        get_show_excluded_items,
        set_show_excluded_items
    )

    def get_displayed_types(self):
        return self.navigation_settings.displayed_types

    def set_displayed_types(self, value):
        self.navigation_settings.displayed_types = value

    displayed_types = property(get_displayed_types, set_displayed_types)

    def get_filter_on_workflow(self):
        return self.navigation_settings.filter_on_workflow

    def set_filter_on_workflow(self, value):
        self.navigation_settings.filter_on_workflow = value

    filter_on_workflow = property(
        get_filter_on_workflow,
        set_filter_on_workflow
    )

    def get_workflow_states_to_show(self):
        return self.navigation_settings.workflow_states_to_show

    def set_workflow_states_to_show(self, value):
        self.navigation_settings.workflow_states_to_show = value

    workflow_states_to_show = property(
        get_workflow_states_to_show,
        set_workflow_states_to_show)

    @property
    def root(self):
        return self.navigation_settings.root

    @root.setter
    def root(self, value):
        self.navigation_settings.root = value
