from plone.app.workflow.remap import remap_workflow
from plone.memoize.instance import memoize

from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from Acquisition import aq_inner, aq_parent, aq_base
from AccessControl import Unauthorized

from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFCore.interfaces import ITypesTool
from Products.CMFCore.interfaces import IConfigurableWorkflowTool
from Products.CMFEditions.interfaces.IRepository import IRepositoryTool
from Products.CMFEditions.setuphandlers import DEFAULT_POLICIES
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class TypesControlPanel(BrowserView):
    
    # Actions

    template = ViewPageTemplateFile('types.pt')

    @property
    @memoize
    def type_id(self):
        type_id = self.request.get('type_id', None)
        if type_id is None:
            type_id = self.selectable_types()[0]['id']
        return type_id
        
    @property
    @memoize
    def fti(self):
        type_id = self.type_id
        portal_types = getUtility(ITypesTool)
        return getattr(portal_types, type_id)

    def __call__(self):
        """Perform the update and redirect if necessary, or render the page
        """
        postback = True
        context = aq_inner(self.context)
        
        form = self.request.form
        submitted = form.get('form.submitted', False)
        save_button = form.get('form.button.Save', None) is not None
        cancel_button = form.get('form.button.Cancel', None) is not None
        type_id = form.get('old_type_id', None)

        if submitted and type_id and not cancel_button:
            
            portal_types = getUtility(ITypesTool)
            portal_repository = getUtility(IRepositoryTool)
            portal_properties = getUtility(IPropertiesTool)
            site_properties = getattr(portal_properties, 'site_properties')
            
            fti = getattr(portal_types, type_id)
            
            # Set FTI properties
            
            title = form.get('title', '')
            addable = form.get('addable', False)
            allow_discussion = form.get('allow_discussion', False)
            
            fti.manage_changeProperties(title = title,
                                        global_allow = bool(addable),
                                        allow_discussion = bool(allow_discussion))
            
            versionable = form.get('versionable', False)
            versionable_types = list(portal_repository.getVersionableContentTypes())
            if versionable and type_id not in versionable_types:
                versionable_types.append(type_id)
                # Add default versioning policies to the versioned type
                for policy_id in DEFAULT_POLICIES:
                    portal_repository.addPolicyForContentType(type_id,
                                                              policy_id)
            elif not versionable and type_id in versionable_types:
                versionable_types.remove(type_id)
            portal_repository.setVersionableContentTypes(versionable_types)

            searchable = form.get('searchable', False)
            blacklisted = list(site_properties.getProperty('types_not_searched'))
            if searchable and type_id in blacklisted:
                blacklisted.remove(type_id)
            elif not searchable and type_id not in blacklisted:
                blacklisted.append(type_id)
            site_properties.manage_changeProperties(types_not_searched = blacklisted)

            # Update workflow 
            
            if self.have_new_workflow() and form.get('form.workflow.submitted', False) and save_button:
                new_wf = self.new_workflow()
                if new_wf == '[none]':
                    chain = ()
                else:
                    chain = (new_wf,)
                state_map = dict([(s['old_state'], s['new_state']) for s in form.get('new_wfstates', [])])
                if state_map.has_key('[none]'):
                    state_map[None] = state_map['[none]']
                    del state_map['[none]']
                remap_workflow(context, type_ids=(type_id,), chain=chain, state_map=state_map)
                
                self.request.response.redirect('%s/@@types-controlpanel?type_id=%s' % (context.absolute_url() , type_id))
                postback = False
            
        elif cancel_button:
            self.request.response.redirect(self.context.absolute_url() + '/plone_control_panel')
            postback = False
        
        if postback:
            return self.template()
            
    # View

    @memoize
    def selectable_types(self):
        vocab_factory = getUtility(IVocabularyFactory, name="plone.app.vocabularies.PortalTypes")
        return [dict(id=v.value, title=v.token) for v in vocab_factory(self.context)]

    def selected_type_title(self):
        return self.fti.Title()
        
    def is_addable(self):
        return self.fti.getProperty('global_allow', False)
        
    def is_discussion_allowed(self):
        return self.fti.getProperty('allow_discussion', False)
    
    def is_versionable(self):
        context = aq_inner(self.context)
        portal_repository = getUtility(IRepositoryTool)
        return (self.type_id in portal_repository.getVersionableContentTypes())
        
    def is_searchable(self):
        context = aq_inner(self.context)
        portal_properties = getUtility(IPropertiesTool)
        blacklisted = portal_properties.site_properties.types_not_searched
        return (self.type_id not in blacklisted)

    @memoize
    def current_workflow(self):
        context = aq_inner(self.context)
        portal_workflow = getUtility(IConfigurableWorkflowTool)
        try: 
            wf_id = portal_workflow.getChainForPortalType(self.type_id)[0]
        except IndexError:
            return dict(id='[none]', title=_(u"No workflow"))
        wf = getattr(portal_workflow, wf_id)
        return dict(id=wf.id, title=wf.title)
        
    def available_workflows(self):
        vocab_factory = getUtility(IVocabularyFactory, name="plone.app.vocabularies.Workflows")
        return [dict(id=v.value, title=v.token) for v in vocab_factory(self.context)]

    @memoize
    def new_workflow(self):
        current_workflow = self.current_workflow()['id']
        old_type_id = self.request.form.get('old_type_id', self.type_id)
        if old_type_id != self.type_id:
            return current_workflow
        else:
            return self.request.form.get('new_workflow', current_workflow)

    @memoize
    def have_new_workflow(self):
        return self.current_workflow()['id'] != self.new_workflow()

    @memoize
    def new_workflow_is_none(self):
        return self.new_workflow() == '[none]'

    def new_workflow_available_states(self):
        current_workflow = self.current_workflow()['id']
        new_workflow = self.new_workflow()
        
        if new_workflow != current_workflow:
            portal_workflow = getUtility(IConfigurableWorkflowTool)
            wf = getattr(portal_workflow, new_workflow)
            return [dict(id=s.id, title=s.title) for s in wf.states.objectValues()]
        else:
            return []
            
    def suggested_state_map(self):
        current_workflow = self.current_workflow()['id']
        new_workflow = self.new_workflow()
            
        portal_workflow = getUtility(IConfigurableWorkflowTool)
                
        if current_workflow == '[none]':
            new_wf = getattr(portal_workflow, new_workflow)
            default_state = new_wf.initial_state            
            return [dict(old_id = '[none]',
                         old_title = _(u"No workflow"),
                         suggested_id = default_state)]
                
        elif new_workflow != current_workflow:
            old_wf = getattr(portal_workflow, current_workflow)
            new_wf = getattr(portal_workflow, new_workflow)
            
            new_states = set([s.id for s in new_wf.states.objectValues()])
            default_state = new_wf.initial_state
            
            return [dict(old_id = old.id,
                         old_title = old.title,
                         suggested_id = (old.id in new_states and old.id or default_state))
                    for old in old_wf.states.objectValues()]
    
        else:
            return []
