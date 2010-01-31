from plone.portlets.interfaces import IPortletDataProvider
from plone.app.i18n.locales.browser.selector import LanguageSelector
from zope.component import getMultiAdapter
from zope.interface import implements

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.portlets import base


class ILanguagePortlet(IPortletDataProvider):
    """A portlet which shows the available portal languages.
    """


class Assignment(base.Assignment):
    implements(ILanguagePortlet)

    title = _(u'label_languages', default=u'Languages')


class Renderer(base.Renderer):

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        self.selector=LanguageSelector(context, request, None, None)
        self.selector.update()
        self.languages=self.selector.languages()

        def key(info):
            return info.get("native", info["name"])
        self.languages.sort(key=key)
        portal_state = getMultiAdapter((context, request), name=u'plone_portal_state')
        self.navigation_root_url = portal_state.navigation_root_url()

    def show(self):
        return self.selector.available() and len(self.languages)>1

    @property
    def available(self):
        return self.show()

    def showFlags(self):
        return self.selector.showFlags()

    def update(self):
        pass

    render = ViewPageTemplateFile('language.pt')


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
