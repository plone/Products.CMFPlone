from plone.app.viewletmanager.manager import OrderedViewletManager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from plone.memoize.instance import memoize
from plone.app.layout.viewlets.common import PersonalBarViewlet


class ToolbarViewletManager(OrderedViewletManager):
    custom_template = ViewPageTemplateFile('toolbar.pt')

    def base_render(self):
        return super(ToolbarViewletManager, self).render()

    def render(self):
        return self.custom_template()

    @property
    @memoize
    def portal_state(self):
        return getMultiAdapter((self.context, self.request), name='plone_portal_state')

    def get_personal_bar(self):
        viewlet = PersonalBarViewlet(self.context, self.request, self.__parent__, self)
        viewlet.update()
        return viewlet