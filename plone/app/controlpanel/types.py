from plone.app.workflow.remap import remap_workflow
from plone.memoize.instance import memoize

from zope.component import getUtility

from zope.event import notify

from zope.i18n import translate
from zope.schema.interfaces import IVocabularyFactory

from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.controlpanel.events import ConfigurationChangedEvent

from plone.app.controlpanel.form import ControlPanelView


def format_description(text, request=None):
    # We expect the workflow to be a text of '- ' divided bullet points.
    text = translate(text.strip(), domain='plone', context=request)
    return [s.strip() for s in text.split('- ') if s]


# These are convenient / user friendly versioning policies.
VERSION_POLICIES = [
        dict(id="off",
             policy=(),
             title=_(u"versioning_off",
                     default=u"No versioning")),

        dict(id="manual",
             policy=("version_on_revert",),
             title=_(u"versioning_manual",
                     default=u"Manual")),

        dict(id="automatic",
             policy=("at_edit_autoversion", "version_on_revert"),
             title=_(u"versioning_automatic",
                     default=u"Automatic")),
        ]

class TypesControlPanel(ControlPanelView):

    # Actions

    template = ViewPageTemplateFile('types.pt')

    @property
    @memoize
    def type_id(self):
        type_id = self.request.get('type_id', None)
        if type_id is None:
            type_id=''
        return type_id

    @property
    @memoize
    def fti(self):
        type_id = self.type_id
        portal_types = getToolByName(self.context, 'portal_types')
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

        if submitted and not cancel_button:
            if type_id:
                portal_types = getToolByName(self.context, 'portal_types')
                portal_repository = getToolByName(self.context,
                                                  'portal_repository')
                portal_properties = getToolByName(self.context,
                                                  'portal_properties')
                site_properties = getattr(portal_properties, 'site_properties')

                fti = getattr(portal_types, type_id)

                # Set FTI properties

                addable = form.get('addable', False)
                allow_discussion = form.get('allow_discussion', False)

                fti.manage_changeProperties(global_allow = bool(addable),
                                            allow_discussion = bool(allow_discussion))

                version_policy = form.get('versionpolicy', "off")
                if version_policy!=self.current_versioning_policy():
                    newpolicy=[p for p in VERSION_POLICIES if p["id"]==version_policy][0]


                    versionable_types = list(portal_repository.getVersionableContentTypes())
                    if not newpolicy["policy"]:
                        if type_id in versionable_types:
                            versionable_types.remove(type_id)
                    else:
                        if type_id not in versionable_types:
                            versionable_types.append(type_id)

                    for policy in portal_repository.listPolicies():
                        policy_id = policy.getId()
                        if policy_id in newpolicy["policy"]:
                            portal_repository.addPolicyForContentType(type_id, policy_id)
                        else:
                            portal_repository.removePolicyFromContentType(type_id, policy_id)

                    portal_repository.setVersionableContentTypes(versionable_types)

                searchable = form.get('searchable', False)
                blacklisted = list(site_properties.getProperty('types_not_searched'))
                if searchable and type_id in blacklisted:
                    blacklisted.remove(type_id)
                elif not searchable and type_id not in blacklisted:
                    blacklisted.append(type_id)
                site_properties.manage_changeProperties(types_not_searched = \
                                                        blacklisted)

                redirect_links = form.get('redirect_links', False)
                site_properties.manage_changeProperties(redirect_links = \
                                                        redirect_links)

            # Update workflow
            if self.have_new_workflow() and \
               form.get('form.workflow.submitted', False) and \
               save_button:
                if self.new_workflow_is_different():
                    new_wf = self.new_workflow()
                    if new_wf == '[none]':
                        chain = ()
                    elif new_wf == '(Default)':
                        chain = new_wf
                    else:
                        chain = (new_wf,)
                    state_map = dict([(s['old_state'], s['new_state']) for s in \
                                      form.get('new_wfstates', [])])
                    if state_map.has_key('[none]'):
                        state_map[None] = state_map['[none]']
                        del state_map['[none]']
                    if type_id:
                        type_ids=(type_id,)
                    else:
                        wt = getToolByName(self.context, 'portal_workflow')
                        tt = getToolByName(self.context, 'portal_types')
                        nondefault = [info[0] for info in wt.listChainOverrides()]
                        type_ids = [type for type in tt.listContentTypes() if type not in nondefault]
                        wt.setChainForPortalTypes(type_ids, wt.getDefaultChain())
                        wt.setDefaultChain(','.join(chain))
                        chain='(Default)'

                    remap_workflow(context, type_ids=type_ids, chain=chain,
                                   state_map=state_map)

                    data = {'workflow': new_wf}
                    notify(ConfigurationChangedEvent(self, data))

                else:
                    portal_workflow = getToolByName(context, 'portal_workflow')
                    if self.new_workflow()=='(Default)':
                        # The WorkflowTool API can not handle this sanely
                        cbt=portal_workflow._chains_by_type
                        if cbt.has_key(type_id):
                            del cbt[type_id]
                    else:
                        portal_workflow.setChainForPortalTypes((type_id,),
                                self.new_workflow())

                self.request.response.redirect('%s/@@types-controlpanel?\
type_id=%s' % (context.absolute_url() , type_id))
                postback = False

        elif cancel_button:
            self.request.response.redirect(self.context.absolute_url() + \
                                           '/plone_control_panel')
            postback = False

        if postback:
            return self.template()

    # View

    def versioning_policies(self):
        return VERSION_POLICIES

    @memoize
    def selectable_types(self):
        vocab_factory = getUtility(IVocabularyFactory,
                                   name="plone.app.vocabularies.ReallyUserFriendlyTypes")
        types = []
        for v in vocab_factory(self.context):
            if v.title:
                title = translate(v.title, context=self.request)
            else:
                title = translate(v.token, domain='plone', context=self.request)
            types.append(dict(id=v.value, title=title) )
        def _key(v):
            return v['title']
        types.sort(key=_key)
        return types

    def selected_type_title(self):
        return self.fti.Title()

    def selected_type_description(self):
        return self.fti.Description()

    def is_addable(self):
        return self.fti.getProperty('global_allow', False)

    def is_discussion_allowed(self):
        return self.fti.getProperty('allow_discussion', False)

    def current_versioning_policy(self):
        portal_repository = getToolByName(self.context, 'portal_repository')
        if self.type_id not in portal_repository.getVersionableContentTypes():
            return "off"
        policy = set(portal_repository.getPolicyMap().get(self.type_id, ()))
        for info in VERSION_POLICIES:
            if set(info["policy"]) == policy:
                return info["id"]
        return None

    def is_searchable(self):
        context = aq_inner(self.context)
        portal_properties = getToolByName(context, 'portal_properties')
        blacklisted = portal_properties.site_properties.types_not_searched
        return (self.type_id not in blacklisted)

    def is_redirect_links_enabled(self):
        context = aq_inner(self.context)
        portal_properties = getToolByName(context, 'portal_properties')
        site_props = portal_properties.site_properties
        return self.type_id == 'Link' and site_props.getProperty('redirect_links') or False

    @memoize
    def current_workflow(self):
        context = aq_inner(self.context)
        portal_workflow = getToolByName(context, 'portal_workflow')
        default_workflow = self.default_workflow(False)
        nondefault = [info[0] for info in portal_workflow.listChainOverrides()]
        chain = portal_workflow.getChainForPortalType(self.type_id)
        empty_workflow_dict = dict(id='[none]',
                                   title=_(u"label_no_workflow"),
                                   description= [_(u"description_no_workflow",
                                   default=u"This type has no workflow. The visibilty "
                                       u"of items of this type is determined by "
                                       u"the folder they are in.")])

        if self.type_id in nondefault:
            if chain:
                wf_id = chain[0]
                wf = getattr(portal_workflow, wf_id)
                title = translate(wf.title, domain='plone', context=self.request)
                return dict(id=wf.id, title=title, description=format_description(wf.description, self.request))
            else:
                return empty_workflow_dict

        if default_workflow == '[none]':
            return empty_workflow_dict

        default_title = translate(default_workflow.title, domain='plone',
                                  context=self.request)
        return dict(id='(Default)',
                    title=_(u"label_default_workflow_title",
                        default=u"Default workflow (${title})",
                        mapping=dict(title=default_title)),
                    description=format_description(default_workflow.description, self.request))


    def available_workflows(self):
        vocab_factory = getUtility(IVocabularyFactory,
                                   name="plone.app.vocabularies.Workflows")
        workflows = []
        for v in vocab_factory(self.context):
            if v.title:
                title = translate(v.title, context=self.request)
            else:
                title = translate(v.token, domain='plone', context=self.request)
            workflows.append(dict(id=v.value, title=title) )
        def _key(v):
            return v['title']
        workflows.sort(key=_key)

        default_workflow = self.default_workflow(False)
        if self.type_id and default_workflow != '[none]':
            # Only offer a default workflow option on a real type
            default_workflow = self.default_workflow(False)
            default_title = translate(default_workflow.title,
                                      domain='plone', context=self.request)
            workflows.insert(0, dict(id='(Default)',
                    title=_(u"label_default_workflow_title",
                            default=u"Default workflow (${title})",
                            mapping=dict(title=default_title)),
                    description=format_description(default_workflow.description, self.request)))

        return workflows

    @memoize
    def new_workflow(self):
        current_workflow = self.current_workflow()['id']
        if self.type_id=='':
            # If we are looking at the default workflow we need to show
            # the real workflow
            current_workflow=self.real_workflow(current_workflow)
        old_type_id = self.request.form.get('old_type_id', self.type_id)
        if old_type_id != self.type_id:
            return current_workflow
        else:
            return self.request.form.get('new_workflow', current_workflow)

    @memoize
    def have_new_workflow(self):
        return self.current_workflow()['id'] != self.new_workflow()

    @memoize
    def default_workflow(self, id_only=True):
        portal_workflow = getToolByName(self.context, 'portal_workflow')
        default_chain = portal_workflow.getDefaultChain()
        if not default_chain:
            # There is no default workflow
            return '[none]'
        id = default_chain[0]
        if id_only:
            return id
        else:
            return portal_workflow.getWorkflowById(id)

    @memoize
    def real_workflow(self, wf):
        if wf=='(Default)':
            return self.default_workflow()
        else:
            return wf

    @memoize
    def new_workflow_is_different(self):
        new_workflow = self.new_workflow()
        current_workflow = self.current_workflow()['id']

        return self.real_workflow(new_workflow)!=self.real_workflow(current_workflow)

    @memoize
    def new_workflow_is_none(self):
        return self.new_workflow() == '[none]'

    def new_workflow_description(self):
        portal_workflow = getToolByName(self.context, 'portal_workflow')
        new_workflow = self.new_workflow()

        if self.new_workflow_is_different():
            if self.new_workflow_is_none():
                return [_(u"description_no_workflow",
                    default=u"This type has no workflow. The visibilty of "
                            u"items of this type is determined by the "
                            u"folder they are in.")]
            new_workflow = self.real_workflow(self.new_workflow())
            wf = getattr(portal_workflow, new_workflow)
            return format_description(wf.description, self.request)

        return None


    def new_workflow_available_states(self):
        if self.new_workflow_is_different():
            new_workflow = self.real_workflow(self.new_workflow())
            portal_workflow = getToolByName(self.context, 'portal_workflow')
            wf = getattr(portal_workflow, new_workflow)
            states = []
            for s in wf.states.objectValues():
                title = translate(s.title, domain='plone', context=self.request)
                states.append(dict(id=s.id, title=title))
            return states
        else:
            return []

    def suggested_state_map(self):
        current_workflow = self.real_workflow(self.current_workflow()['id'])
        new_workflow = self.real_workflow(self.new_workflow())

        portal_workflow = getToolByName(self.context, 'portal_workflow')

        if current_workflow == '[none]':
            new_wf = getattr(portal_workflow, new_workflow)
            default_state = new_wf.initial_state
            return [dict(old_id = '[none]',
                         old_title = _(u"No workflow"),
                         suggested_id = default_state)]

        elif self.new_workflow_is_different():
            old_wf = getattr(portal_workflow, current_workflow)
            new_wf = getattr(portal_workflow, new_workflow)

            new_states = set([s.id for s in new_wf.states.objectValues()])
            default_state = new_wf.initial_state

            states = []
            for old in old_wf.states.objectValues():
                title = translate(old.title, domain='plone', context=self.request)
                states.append(
                    dict(old_id = old.id,
                         old_title = title,
                         suggested_id = (old.id in new_states and \
                                         old.id or default_state)))
            return states
        else:
            return []
