#These CustomizationPolicies *are not* persisted!!
# <efge> disable anonymous view on index_html and Members and all your content, 
# but NOT on portal_skins or acl_users
# thanks efge ;-)
# 10/6/02 - add publicize state
# This "CustomizationPolicy" configures DCWorkflow in such a
# way that by default content Members create are not accessible
# to anonymous members.  But there is a questionable use case
# which is letting anonymous members see some sort of content
# so today I add a "public" state and a "publicize" transition
# that is available to make a piece of content "publicly"
# available.  This needs to be done by both container and content

#TODO please un-hardcode the View/Modify portal content and use module constants

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
        plone_wf=wf_tool['plone_workflow']
        plone_wf.states.setInitialState(id='private')
        plone_wf.states.published.permission_roles['View'] = ('Member', 'Reviewer', 'Manager')
        plone_wf.states.visible.permission_roles['View'] = ('Member', 'Reviewer', 'Manager')

        #10/6/02 - adding public/publicize state/transition to allow Anonymous 
        plone_wf.states.addState('public')
        sdef=plone_wf.states.public
        sdef.setProperties( title='Publicly available'
                          , transitions=('published', 'reject', 'retract') )
        sdef.setPermission('View', 1, ('Anonymous', 'Authenticated'))
        sdef.setPermission('Access contents information', 1, ('Anonymous', 'Authenticated'))
        sdef.setPermission('Modify portal content', 1, ('Manager', ) )
        plone_wf.transitions.addTransition('publicize')
        tdef = plone_wf.transitions.publicize
        tdef.setProperties( title='Publicize content'
                          , new_state_id='public'
                          , actbox_name='Publicize'
                          , actbox_url='%(content_url)s/content_history_form'
                          , props={'guard_permissions':'Modify portal content'
                                  ,'guard_roles':'Owner;Manager'} )        
        for statedef in plone_wf.states.objectValues():
            if statedef.id != 'public':
                statedef.setProperties( transitions=tuple(statedef.transitions)+('publicize',) )
        folder_wf=wf_tool['folder_workflow']
        folder_wf.states.visible.permission_roles['View'] = ('Member', 'Reviewer', 'Manager')
        folder_wf.states.published.permission_roles['List folder contents'] = ('Authenticated', 'Manager')
        folder_wf.states.published.permission_roles['View'] = ('Member', 'Reviewer', 'Manager')
        folder_wf.states.setInitialState(id='private')
        
        folder_wf.states.addState('public')
        sdef=folder_wf.states.public
        sdef.setProperties( title='Publicly available'
                          , transitions=('published', 'reject', 'retract') ) 
        sdef.setPermission( 'View', 1, ('Anonymous', 'Authenticated') )
        sdef.setPermission( 'Access contents information', 1, ('Anonymous', 'Authenticated') )
        sdef.setPermission( 'List folder contents', 1, ('Anonymous', 'Authenticated') )
        sdef.setPermission( 'Modify portal content', 1, ('Mangager', ) )
        folder_wf.transitions.addTransition('publicize')
        tdef=folder_wf.transitions.publicize
        tdef.setProperties( title='Publicize content'
                          , new_state_id='public'
                          , actbox_name='Publicize'
                          , actbox_url='%(content_url)s/content_history_form'
                          , props={'guard_permissions':'Modify portal content'
                                  ,'guard_roles':'Owner;Manager'} )                                  
        for statedef in folder_wf.states.objectValues():
            if statedef.id != 'public':
                statedef.setProperties( transitions=tuple(statedef.transitions)+('publicize',) )
                
        wf_tool.doActionFor(portal,'show',comment='The portal object itelf but be visible')
        #wf_tool.doActionFor(portal.Members, 'show', comment='Members must be visible')

        portal.index_html.manage_permission('View', ('Anonymous', 'Authenticated') )

        portal.manage_permission(AddPortalMember,('Manager',))
        #portal.manage_delObjects('portal_registration')
        pa_tool=getToolByName(portal,'portal_actions')
        #pa_tool.action_providers=tuple([ap for ap in pa_tool.action_providers if ap!='portal_registration'])

        #only Members are allowed to see the default tabs
        actions=pa_tool._cloneActions()
        for a in actions:
            if a.id in ('news', 'search_form', 'index_html'):
                a.condition=Expression('member')
        pa_tool._actions=actions


