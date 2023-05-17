from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from AccessControl.class_init import InitializeClass
from Acquisition import aq_base
from plone.base.interfaces import IWorkflowChain
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowTool import WorkflowTool as BaseTool
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.DCWorkflow.Transitions import TRIGGER_USER_ACTION
from ZODB.POSException import ConflictError
from zope.component import getMultiAdapter

import pkg_resources


try:
    pkg_resources.get_distribution("plone.app.multilingual")
except pkg_resources.DistributionNotFound:
    has_new_lang_bypass = False
else:
    has_new_lang_bypass = (
        int(
            pkg_resources.get_distribution("plone.app.multilingual").version.split(".")[
                0
            ]
        )
        > 1
    )


class WorkflowTool(PloneBaseTool, BaseTool):
    meta_type = "Plone Workflow Tool"
    security = ClassSecurityInfo()
    plone_tool = 1
    toolicon = "skins/plone_images/workflow_icon.png"

    # TODO this should not make it into 1.0
    # Refactor me, my maker was tired
    def flattenTransitions(self, objs, container=None):
        # This is really hokey - hold on!!
        if hasattr(objs, "startswith"):
            return ()

        # TODO Need to behave differently for paths
        if len(objs) and "/" in objs[0]:
            return self.flattenTransitionsForPaths(objs)
        transitions = []
        t_names = []

        if container is None:
            container = self
        for o in [getattr(container, oid, None) for oid in objs]:
            trans = ()
            try:
                trans = self.getTransitionsFor(o, container)
            except ConflictError:
                raise
            except Exception:
                pass
            if trans:
                for t in trans:
                    if t["name"] not in t_names:
                        transitions.append(t)
                        t_names.append(t["name"])

        return tuple(transitions[:])

    def flattenTransitionsForPaths(self, paths):
        # This is even more hokey!!
        if hasattr(paths, "startswith"):
            return ()

        transitions = []
        t_names = []
        portal = getToolByName(self, "portal_url").getPortalObject()

        for o in [portal.restrictedTraverse(path) for path in paths]:
            trans = ()
            try:
                trans = self.getTransitionsFor(o, o.aq_inner.aq_parent)
            except ConflictError:
                raise
            except Exception:
                pass
            if trans:
                for t in trans:
                    if t["name"] not in t_names:
                        transitions.append(t)
                        t_names.append(t["name"])

        return tuple(transitions[:])

    security.declarePublic("getTransitionsFor")

    def getTransitionsFor(self, obj=None, container=None, REQUEST=None):
        if isinstance(obj, list):
            return self.flattenTransitions(objs=obj, container=container)
        result = {}
        chain = self.getChainFor(obj)
        for wf_id in chain:
            wf = self.getWorkflowById(wf_id)
            if wf is not None:
                sdef = wf._getWorkflowStateOf(obj)
                if sdef is not None:
                    for tid in sdef.transitions:
                        tdef = wf.transitions.get(tid, None)
                        if (
                            tdef is not None
                            and tdef.trigger_type == TRIGGER_USER_ACTION
                            and tdef.actbox_name
                            and wf._checkTransitionGuard(tdef, obj)
                            and tdef.id not in result
                        ):
                            result[tdef.id] = {
                                "id": tdef.id,
                                "title": tdef.title,
                                "title_or_id": tdef.title_or_id(),
                                "description": tdef.description,
                                "name": tdef.actbox_name,
                                "url": tdef.actbox_url
                                % {
                                    "content_url": obj.absolute_url(),
                                    "portal_url": "",
                                    "folder_url": "",
                                },
                            }
        return tuple(result.values())

    def workflows_in_use(self):
        # Gathers all the available workflow chains (sequence
        # of workflow ids).
        in_use = []

        in_use.append(self._default_chain)

        if self._chains_by_type:
            for chain in self._chains_by_type.values():
                in_use.append(chain)

        return tuple(in_use[:])

    security.declarePublic("getWorklists")

    def getWorklists(self):
        # Instead of manually scraping actions_box, let's
        # query for all worklists in all workflow definitions.
        # Returns a dictionary whose value is a sequence of dictionaries.

        # i.e. map[workflow_id]=(workflow definition map, )
        # each workflow definition map contains the following:
        # (worklist)id, guard (Guard instance), guard_permissions (permission
        # of Guard instance), guard_roles (roles of Guard instance),
        # catalog_vars (mapping), actbox_name (actions box label),
        # actbox_url (actions box url) and types (list of portal types)

        # We want to know which types use the workflows with worklists
        # This for example avoids displaying 'pending' of multiple workflows in
        # the same worklist
        types_tool = getToolByName(self, "portal_types")
        list_ptypes = types_tool.listContentTypes()
        types_by_wf = {}  # wf:[list,of,types]
        for t in list_ptypes:
            for wf in self.getChainFor(t):
                types_by_wf[wf] = types_by_wf.get(wf, []) + [t]

        # Placeful stuff
        placeful_tool = getToolByName(self, "portal_placeful_workflow", None)
        if placeful_tool is not None:
            for policy in placeful_tool.getWorkflowPolicies():
                for t in list_ptypes:
                    chain = policy.getChainFor(t) or ()
                    for wf in chain:
                        types_by_wf[wf] = types_by_wf.get(wf, []) + [t]

        wf_with_wlists = {}
        for id in self.getWorkflowIds():
            # the above list incomprehension merely _flattens_ nested sequences
            # into 1 sequence

            wf = self.getWorkflowById(id)
            if hasattr(wf, "worklists"):
                wlists = []
                for worklist in wf.worklists:
                    wlist_def = wf.worklists[worklist]
                    # Make the var_matches a dict instead of PersistentMapping
                    # to enable access from scripts
                    var_matches = {}
                    for key in wlist_def.var_matches.keys():
                        var_matches[key] = wlist_def.var_matches[key]

                    a_wlist = {
                        "id": worklist,
                        "guard": wlist_def.getGuard(),
                        "guard_permissions": wlist_def.getGuard().permissions,
                        "guard_roles": wlist_def.getGuard().roles,
                        "catalog_vars": var_matches,
                        "name": getattr(wlist_def, "actbox_name", None),
                        "url": getattr(wlist_def, "actbox_url", None),
                        "types": types_by_wf.get(id, []),
                    }
                    wlists.append(a_wlist)
                # yes, we can duplicates, we filter duplicates out on the
                # calling PyhtonScript client
                wf_with_wlists[id] = wlists

        return wf_with_wlists

    security.declarePublic("getWorklistsResults")

    def getWorklistsResults(self):
        # Return all the objects concerned by one or more worklists.
        #
        # This method replace 'getWorklists' by implementing the whole
        # worklists work for the script.  An object is returned only once, even
        # if is return by several worklists. Make the whole work as expensive
        # it is.
        sm = getSecurityManager()
        # We want to know which types use the workflows with worklists
        # This for example avoids displaying 'pending' of multiple workflows in
        # the same worklist
        types_tool = getToolByName(self, "portal_types")
        catalog = getToolByName(self, "portal_catalog")

        list_ptypes = types_tool.listContentTypes()
        types_by_wf = {}  # wf:[list,of,types]
        for t in list_ptypes:
            for wf in self.getChainFor(t):
                types_by_wf[wf] = types_by_wf.get(wf, []) + [t]

        # PlacefulWorkflowTool will give us other results
        placeful_tool = getToolByName(self, "portal_placeful_workflow", None)
        if placeful_tool is not None:
            for policy in placeful_tool.getWorkflowPolicies():
                for t in list_ptypes:
                    chain = policy.getChainFor(t) or ()
                    for wf in chain:
                        types_by_wf[wf] = types_by_wf.get(wf, []) + [t]

        objects_by_path = {}
        for id in self.getWorkflowIds():
            wf = self.getWorkflowById(id)
            if hasattr(wf, "worklists"):
                for worklist in wf.worklists:
                    wlist_def = wf.worklists[worklist]
                    # Make the var_matches a dict instead of PersistentMapping
                    # to enable access from scripts
                    catalog_vars = dict(portal_type=types_by_wf.get(id, []))
                    for key in wlist_def.var_matches:
                        catalog_vars[key] = wlist_def.var_matches[key]
                    # Support LinguaPlone review situations, you want to see
                    # content in *all* languages
                    if "Language" not in catalog_vars:
                        if has_new_lang_bypass:
                            catalog_vars["path"] = "/"
                        else:
                            catalog_vars["Language"] = "all"
                    # Include inactive content in result list. This is
                    # especially important for content scheduled to go public
                    # in the future, but needs to be reviewed before this.
                    catalog_vars["show_inactive"] = True
                    for result in catalog.searchResults(catalog_vars):
                        o = result.getObject()
                        if (
                            o
                            and id in self.getChainFor(o)
                            and wlist_def.getGuard().check(sm, wf, o)
                        ):
                            absurl = o.absolute_url()
                            if absurl:
                                objects_by_path[absurl] = (o.modified(), o)

        results = objects_by_path.values()
        return tuple(obj[1] for obj in sorted(results))

    security.declareProtected(ManagePortal, "getChainForPortalType")

    def getChainForPortalType(self, pt_name, managescreen=0):
        # Get a chain for a specific portal type.
        if pt_name in self._chains_by_type:
            return self._chains_by_type[pt_name]
        else:
            # (Default) is _not_ a chain nor a workflow in a chain.
            if managescreen:
                return "(Default)"
            else:
                # Return the default chain.
                return self._default_chain

    security.declareProtected(ManagePortal, "listWorkflows")

    def listWorkflows(self):
        # Return the list of workflows.
        return self.keys()

    security.declarePublic("getTitleForStateOnType")

    def getTitleForStateOnType(self, state_name, p_type):
        # Returns the workflow state title for a given state name,
        # uses a portal_type to determine which workflow to use.
        if state_name and p_type is not None:
            chain = self.getChainForPortalType(p_type)
            for wf_id in chain:
                wf = self.getWorkflowById(wf_id)
                if wf is not None:
                    states = wf.states
                    state = getattr(states, state_name, None)
                    if state is not None:
                        return getattr(aq_base(state), "title", None) or state_name
        return state_name

    security.declarePublic("getTitleForTransitionOnType")

    def getTitleForTransitionOnType(self, trans_name, p_type):
        # Returns the workflow transition title for a given transition name,
        # uses a portal_type to determine which workflow to use.
        if trans_name and p_type is not None:
            chain = self.getChainForPortalType(p_type)
            for wf_id in chain:
                wf = self.getWorkflowById(wf_id)
                if wf is not None:
                    transitions = wf.transitions
                    trans = getattr(transitions, trans_name, None)
                    if trans is not None:
                        return (
                            getattr(aq_base(trans), "actbox_name", None) or trans_name
                        )
        return trans_name

    security.declarePublic("listWFStatesByTitle")

    def listWFStatesByTitle(self, filter_similar=False):
        # Returns the states of all available workflows, optionally filtering
        # out states with matching title and id.
        states = []
        dup_list = {}
        for wf in self.values():
            state_folder = getattr(wf, "states", None)
            if state_folder is not None:
                if not filter_similar:
                    states.extend(state_folder.values())
                else:
                    for state in state_folder.values():
                        key = f"{state.id}:{state.title}"
                        if key not in dup_list:
                            states.append(state)
                        dup_list[key] = 1
        return [(s.title, s.getId()) for s in states]

    # PLIP 217 Workflow by adaptation
    def getChainFor(self, ob):
        # Returns the chain that applies to the given object.
        # If we get a string as the ob parameter, use it as
        # the portal_type.
        return getMultiAdapter((ob, self), IWorkflowChain)

    security.declarePrivate("listActions")

    def listActions(self, info=None, object=None):
        """Returns a list of actions to be displayed to the user.

        o Invoked by the portal_actions tool.

        o Allows workflows to include actions to be displayed in the
          actions box.

        o Object actions are supplied by workflows that apply to the object.
        """
        if object is not None or info is None:
            info = self._getOAI(object)
        chain = self.getChainFor(info.object)
        actions = []

        for wf_id in chain:
            wf = self.getWorkflowById(wf_id)
            if wf is not None:
                a = wf.listObjectActions(info)
                if a is not None:
                    actions.extend(a)
        return actions


WorkflowTool.__doc__ = BaseTool.__doc__

InitializeClass(WorkflowTool)
