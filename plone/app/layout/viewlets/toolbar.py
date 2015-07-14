from plone.app.viewletmanager.manager import OrderedViewletManager
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
from plone.memoize.instance import memoize
from plone.app.layout.viewlets.common import PersonalBarViewlet
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces.controlpanel import ISiteSchema


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

    def get_toolbar_logo(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix='plone')
        portal_url = self.portal_state.portal_url()
        return portal_url + settings.toolbar_logo

    def get_toolbar_position(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix='plone')
        if settings.toolbar_position == 'side':
            return 'plone-toolbar-left pat-toolbar'
        else:
            return 'portal-toolbar-top pat-toolbar'

    def show_switcher(self):
        return False


