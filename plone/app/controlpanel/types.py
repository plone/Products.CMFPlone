from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Acquisition import aq_inner, aq_parent, aq_base
from AccessControl import Unauthorized

from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName

from plone.memoize.instance import memoize

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
        portal_types = getToolByName(aq_inner(self.context), 'portal_types')
        return getattr(portal_types, type_id)

    def __call__(self):
        """Perform the update and redirect if necessary, or render the page
        """
        context = aq_inner(self.context)
        
        form = self.request.form
        submitted = form.get('form.submitted', False)
        save_button = form.get('form.button.Save', None) is not None
        cancel_button = form.get('form.button.Cancel', None) is not None
        type_id = form.get('old_type_id', None)

        if submitted and type_id and not cancel_button:
            
            portal_types = getToolByName(context, 'portal_types')
            portal_repository = getToolByName(context, 'portal_repository')
            portal_properties = getToolByName(context, 'portal_properties')
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
                # TODO: Remap
                pass

        
        if cancel_button:
            self.request.response.redirect(self.context.absolute_url() + '/plone_control_panel')
        
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
        portal_repository = getToolByName(context, 'portal_repository')
        return (self.type_id in portal_repository.getVersionableContentTypes())
        
    def is_searchable(self):
        context = aq_inner(self.context)
        portal_properties = getToolByName(context, 'portal_properties')
        blacklisted = portal_properties.site_properties.types_not_searched
        return (self.type_id not in blacklisted)

    @memoize
    def current_workflow(self):
        context = aq_inner(self.context)
        portal_workflow = getToolByName(context, 'portal_workflow')
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
            portal_workflow = getToolByName(aq_inner(self.context), 'portal_workflow')
            wf = getattr(portal_workflow, new_workflow)
            return [dict(id=s.id, title=s.title) for s in wf.states.objectValues()]
        else:
            return []
            
    def suggested_state_map(self):
        current_workflow = self.current_workflow()['id']
        new_workflow = self.new_workflow()
        
        if new_workflow != current_workflow:
            portal_workflow = getToolByName(aq_inner(self.context), 'portal_workflow')
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

    @memoize
    def change_workflow(self):
        """ Changes the workflow on all objects recursively from self """
        # XXX DOES THIS WORK WITH PLACEFUL WORKFLOW?
     
        # Set up variables
        portal = getToolByName(aq_inner(self.context), 'portal_url').getPortalObject()
        typestool = getToolByName(self, 'portal_types')
        wftool = getToolByName(self, 'portal_workflow')

        cbt = wftool._chains_by_type

        wf_mapping = { ( 'plone_workflow', 'community_workflow') :
                     { 'private'   : 'private'
                     , 'visible'   : 'public_draft'
                     , 'pending'   : 'pending'
                     , 'published' : 'published'
                     }
                 }
     
        def walk(obj):
            num = 0
            portal_type = getattr(aq_base(obj), 'portal_type', None)
            if portal_type is not None:
                chain = cbt.get(portal_type, None)
                if chain is None or chain:
                    if chain is None:
                        chain = wftool._default_chain

                    if hasattr(obj, 'workflow_history'):
                        wf_hist = getattr(obj, 'workflow_history', {})

                        for key in wf_hist.keys():
                            for to_wf in chain:
                                mapping = wf_mapping.get((key,'community_workflow'), {})
                                if mapping:
                                    wf_entries = wf_hist[key]
                                    last_entry = wf_entries[-1]
                                    if not mapping[last_entry['review_state']] == last_entry['review_state']:
                                        # We need to insert a transition
                                        transition = { 'action'       : 'script_migrate'
                                                     , 'review_state' : mapping[last_entry['review_state']]
                                                     , 'actor'        : last_entry['actor']
                                                     , 'comments'     : last_entry['comments']
                                                     , 'time'         : last_entry['time']
                                                     }
                                        wf_entries = wf_entries + (transition,)
     
                                    # After massaging and changing, we're ready to reassign
                                    del wf_hist[key]
                                    wf_hist[to_wf] = wf_entries
     
                        obj.workflow_history = wf_hist
                        obj.reindexObject(idxs=['allowedRolesAndUsers','review_state'])
                        num = 1
     
            objlist = []
            if hasattr(aq_base(obj), 'objectValues') and \
               not getattr(aq_base(obj), 'isLayerLanguage', 0):
                objlist = list(aq_base(obj).objectValues())
            if hasattr(aq_base(obj), 'opaqueValues'):
                objlist += list(obj.opaqueValues())
            for o in objlist:
                num += walk(o)

            return num
     
        num = 0
        # Iterate over objects, changing the workflow id in the workflow_history
        objlist = list(portal.objectValues())
        if hasattr(self, 'opaqueValues'):
            objlist += list(self.opaqueValues())
        for o in objlist:
            if o.id == 'front-page': 
                num += walk(o)
       
        # Return the number of objects for which we changed workflow
        return num 
