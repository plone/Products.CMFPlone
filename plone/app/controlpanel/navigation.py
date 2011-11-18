from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope.formlib import form
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import Tuple

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot

from form import ControlPanelForm
from widgets import MultiCheckBoxThreeColumnWidget
from widgets import MultiCheckBoxVocabularyWidget

from plone.app.vocabularies.types import BAD_TYPES

class INavigationSchema(Interface):
    """Fields for the navigation control panel."""
    generate_tabs = Bool(title=_(u"Automatically generate tabs"),
                       description=_(u"By default, all items created at the root level will add to the global section navigation. You can turn this off if you prefer manually constructing this part of the navigation."),
                       default=True,
                       required=False)

    nonfolderish_tabs = Bool(title=_(u"Generate tabs for items other than folders."),
                         description=_(u"By default, any content item in the root of the portal will be shown as a global section. If you turn this option off, only folders will be shown. This only has an effect if 'Automatically generate tabs' is enabled."),
                         default=True,
                         required=False)

    displayed_types = Tuple(
        title=_(u"Displayed content types"),
        description=_(u"The content types that should be shown in the navigation and site map."),
        required=False,
        missing_value=tuple(),
        value_type=Choice(
            vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes")
        )

    filter_on_workflow = Bool(
        title=_(u"Filter on workflow state"),
        description=_(u"The workflow states that should be shown in the navigation tree and the site map."),
        default=False,
        required=False)

    workflow_states_to_show = Tuple(
        required=False,
        missing_value=tuple(),
        value_type=Choice(
            vocabulary="plone.app.vocabularies.WorkflowStates")
        )

    show_excluded_items = Bool(title=_(u"Show items normally excluded from navigation if viewing their children."),
                               description=_(u"If an item has been excluded from navigation should it be shown in navigation when viewing content contained within it or within a subfolder."),
                               default=True,
                               required=False)


class NavigationControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(INavigationSchema)

    def __init__(self, context):
        super(NavigationControlPanelAdapter, self).__init__(context)
        pprop = getToolByName(context, 'portal_properties')
        self.siteProps = pprop.site_properties
        self.navProps = pprop.navtree_properties
        self.ttool = getToolByName(context, 'portal_types')

    def get_generate_tabs(self):
        return not self.siteProps.getProperty('disable_folder_sections')

    def set_generate_tabs(self, value):
        self.siteProps._updateProperty('disable_folder_sections', not value)

    generate_tabs = property(get_generate_tabs, set_generate_tabs)

    def get_nonfolderish_tabs(self):
        return not self.siteProps.getProperty('disable_nonfolderish_sections')

    def set_nonfolderish_tabs(self, value):
        self.siteProps._updateProperty('disable_nonfolderish_sections', not value)

    nonfolderish_tabs = property(get_nonfolderish_tabs, set_nonfolderish_tabs)

    def get_show_excluded_items(self):
        return self.navProps.getProperty('showAllParents')

    def set_show_excluded_items(self, value):
        self.navProps._updateProperty('showAllParents', value)

    show_excluded_items = property(get_show_excluded_items, set_show_excluded_items)

    def get_displayed_types(self):
        allTypes = self.ttool.listContentTypes()
        blacklist = self.navProps.metaTypesNotToList
        return [t for t in allTypes if t not in blacklist
                                    and t not in BAD_TYPES]

    def set_displayed_types(self, value):
        # The menu pretends to be a whitelist, but we are storing a blacklist so that
        # new types are searchable by default. Inverse the list.
        allTypes = self.ttool.listContentTypes()
        blacklistedTypes = [t for t in allTypes if t not in value
                                                or t in BAD_TYPES]
        self.navProps._updateProperty('metaTypesNotToList', blacklistedTypes)

    displayed_types = property(get_displayed_types, set_displayed_types)

    def get_filter_on_workflow(self):
        return self.navProps.getProperty('enable_wf_state_filtering')

    def set_filter_on_workflow(self, value):
        self.navProps._updateProperty('enable_wf_state_filtering', value)

    filter_on_workflow = property(get_filter_on_workflow, set_filter_on_workflow)

    def get_workflow_states_to_show(self):
        return self.navProps.getProperty('wf_states_to_show')

    def set_workflow_states_to_show(self, value):
        self.navProps._updateProperty('wf_states_to_show', value)

    workflow_states_to_show = property(get_workflow_states_to_show, set_workflow_states_to_show)

class NavigationControlPanel(ControlPanelForm):

    label = _("Navigation settings")
    description = _("""Lets you control how navigation is constructed in your site. Note that to control how the navigation tree is displayed, you should go to 'Manage portlets' at the root of the site (or wherever a navigation tree portlet has been added) and change its settings directly.""")
    form_name = _("Navigation details")
    form_fields = form.FormFields(INavigationSchema)
    form_fields['displayed_types'].custom_widget = MultiCheckBoxThreeColumnWidget
    form_fields['workflow_states_to_show'].custom_widget = MultiCheckBoxVocabularyWidget
