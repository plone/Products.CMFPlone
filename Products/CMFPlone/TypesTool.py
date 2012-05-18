from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from Products.CMFCore.ActionInformation import ActionInfo
from Products.CMFCore.interfaces import IAction
from Products.CMFCore.TypesTool import TypesTool as BaseTool

from Products.CMFPlone.PloneBaseTool import PloneBaseTool


class TypesTool(PloneBaseTool, BaseTool):

    meta_type = 'Plone Types Tool'
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/document_icon.png'

    security.declarePublic('listTypeTitles')
    def listTypeTitles(self, container=None):
        """ Return a dictionary of id/Title combinations """
        typenames = {}
        for t in self.listTypeInfo(container):
            name = t.getId()
            if name:
                typenames[name] = t.title_or_id()

        return typenames

    security.declarePrivate('listActions')
    def listActions(self, info=None, object=None, category=None):
        """ List all the actions defined by a provider.
        """
        actions = []
        if object is None and info is not None:
            object = info.object
        if object is not None:
            type_info = self.getTypeInfo(object)
            if type_info is not None:
                type_actions = type_info.listActions(info, object)
                if category is not None:
                    type_actions = [a for a in type_actions
                                    if a.category == category ]
                actions.extend(type_actions)

        if category == 'folder/add':
            add_actions = [ti for ti in self.values()
                            if IAction.providedBy(ti)]
            actions.extend(add_actions)

        return actions

    security.declarePublic('listActionInfos')
    def listActionInfos(self, action_chain=None, object=None,
                        check_visibility=1, check_permissions=1,
                        check_condition=1, max=-1, category=None):
        # List ActionInfo objects.
        # (method is without docstring to disable publishing)
        #
        actions = self.listActions(object=object, category=category)
        if len(actions) == 0:
            return []

        ec = self._getExprContext(object)
        actions = [ActionInfo(action, ec) for action in actions]

        if action_chain:
            filtered_actions = []
            if isinstance(action_chain, basestring):
                action_chain = (action_chain, )
            for action_ident in action_chain:
                sep = action_ident.rfind('/')
                category, id = action_ident[:sep], action_ident[sep+1:]
                for ai in actions:
                    if id == ai['id'] and category == ai['category']:
                        filtered_actions.append(ai)
            actions = filtered_actions

        action_infos = []
        for ai in actions:
            if check_visibility and not ai['visible']:
                continue
            if check_permissions and not ai['allowed']:
                continue
            if check_condition and not ai['available']:
                continue
            action_infos.append(ai)
            if max + 1 and len(action_infos) >= max:
                break
        return action_infos

TypesTool.__doc__ = BaseTool.__doc__

InitializeClass(TypesTool)
