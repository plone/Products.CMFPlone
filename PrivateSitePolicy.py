#These CustomizationPolicies *are not* persisted!!
#<efge> disable anonymous view on index_html and Members and all your content, but NOT on portal_skins or acl_users

from Products.CMFPlone.Portal import addPolicy
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Products.CMFCore import CMFCorePermissions

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
        plone_wf=wf_tool['plone_workflow']
        plone_wf.states.setInitialState(id='private')
        plone_wf.states.published.permission_roles['View'] = ('Member', 'Reviewer', 'Manager')
        plone_wf.states.visible.permission_roles['View'] = ('Member', 'Reviewer', 'Manager')

        folder_wf=wf_tool['folder_workflow']
        folder_wf.states.published.permission_roles['View'] = ('Member', 'Reviewer', 'Manager')
        folder_wf.states.setInitialState(id='private')
        
        wf_tool.updateRoleMappings()
        wf_tool.doActionFor(portal,'show',comment='The portal object itelf but be visible')
        #wf_tool.doActionFor(portal.index_html,'hide',comment='frontpage is not viewable')

        portal.manage_delObjects('portal_registration')
        pa_tool=getToolByName(portal,'portal_actions')
        pa_tool.action_providers=tuple([ap for ap in pa_tool.action_providers if ap!='portal_registration'])
     
        #only Members are allowed to see the default tabs
        actions=pa_tool._cloneActions()
        for a in actions:
            if a.id in ('news', 'search_form', 'index_html'):
                a.condition=Expression('member')
        pa_tool._actions=actions


