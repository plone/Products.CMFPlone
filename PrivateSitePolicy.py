# These CustomizationPolicies *are not* persisted!!
#
# This "CustomizationPolicy" uses a custom DCWorkflow definition,
# which by default content Members create are not accessible
# to anonymous members.  But there is a questionable use case
# which is letting anonymous members see some sort of content

from Products.CMFPlone.Portal import addPolicy
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.CMFCorePermissions import AddPortalMember

from CustomizationPolicy import DefaultCustomizationPolicy
from interfaces.CustomizationPolicy import ICustomizationPolicy

def register(context, app_state):
    addPolicy('Private Plone site', PrivateSitePolicy())

class PrivateSitePolicy(DefaultCustomizationPolicy):
    """ Customizes the Plone site so that its private """
    __implements__ = ICustomizationPolicy

    def customize(self, portal):
        DefaultCustomizationPolicy.customize(self, portal)
        wf_tool=getToolByName(portal,'portal_workflow')
        wf_tool._delObject('plone_workflow')

        wf_tool.manage_addWorkflow( id='plone_workflow' \
                                    , workflow_type='private_plone_workflow'+\
                                    ' (Private Workflow [Plone])')

        wf_tool._delObject('folder_workflow')

        wf_tool.manage_addWorkflow( id='folder_workflow' \
                                    , workflow_type='private_folder_workflow'+\
                                    ' (Private Folder Workflow [Plone])')

        wf_tool.doActionFor(portal,'publicize', comment='The portal object itself must be visible')
        wf_tool.doActionFor(portal.Members, 'publish', comment='Publish Members folder so navigation slot works')
        wf_tool.doActionFor(portal.index_html, 'show', comment='The frontpage should be public also.')

        portal.manage_permission(AddPortalMember,('Manager',))
        pa_tool=getToolByName(portal,'portal_actions')

        #only Members are allowed to see the default tabs
        actions=pa_tool._cloneActions()
        for a in actions:
            if a.id in ('news', 'search_form', 'index_html'):
                a.condition=Expression('member')
        pa_tool._actions=actions

        #remove the loginBox in left_slots
        filtered_slots=[slot for slot in portal.left_slots if not slot.endswith('loginBox')]
        portal.manage_changeProperties(left_slots=tuple(filtered_slots))
        
        portal.portal_properties.site_properties.manage_changeProperties(allowAnonymousViewAbout=0)

