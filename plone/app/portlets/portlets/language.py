import operator
from zope.interface import implements
from zope.component import getMultiAdapter
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.app.i18n.locales.browser.selector import LanguageSelector
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _


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
        self.languages=self.selector.languages()

        def key(info):
            return info.get("native", info["name"])
        self.languages.sort(key=key)
        portal_state = getMultiAdapter((context, request), name=u'plone_portal_state')
        self.portal_url = portal_state.portal_url()

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
