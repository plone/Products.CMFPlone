from plone.app.viewletmanager.manager import OrderedViewletManager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter


class ToolbarViewletManager(OrderedViewletManager):
    custom_template = ViewPageTemplateFile('toolbar.pt')

    def base_render(self):
        return super(ToolbarViewletManager, self).render()

    def render(self):
        return self.custom_template()

    def portal_state(self):
        return getMultiAdapter((self.context, self.request), name='plone_portal_state')