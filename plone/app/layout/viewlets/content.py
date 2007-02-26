from zope.component import getMultiAdapter
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName


class DocumentActionsViewlet(ViewletBase):
    def __init__(self, context, request, view, manager):
        super(DocumentActionsViewlet, self).__init__(context, request, view, manager)
        self.context_state = getMultiAdapter((context, request), name=u'plone_context_state')
        plone_utils = getToolByName(context, 'plone_utils')
        self.getIconFor = plone_utils.getIconFor
        self.actions = self.context_state.actions().get('document_actions', None)

    render = ViewPageTemplateFile("document_actions.pt")
