from zope.component import queryAdapter
from zope.component import getMultiAdapter
from Products.Five import BrowserView
from zExceptions import NotFound

from Products.CMFPlone.interfaces.syndication import ISearchFeed
from Products.CMFPlone.interfaces.syndication import IFeed
from Products.CMFPlone.interfaces.syndication import IFeedSettings
from Products.CMFPlone import PloneMessageFactory as _

from z3c.form import form, button, field
from plone.app.z3cform.layout import wrap_form


class FeedView(BrowserView):

    def feed(self):
        f = queryAdapter(self.context, IFeed)
        if f is None:
            raise NotFound
        return f

    def __call__(self):
        util = getMultiAdapter((self.context, self.request),
                               name='syndication-util')
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        if context_state.is_portal_root() or util.context_enabled(raise404=True):
            settings = IFeedSettings(self.context)
            if self.__name__ not in settings.feed_types:
                raise NotFound
            self.request.response.setHeader('Content-Type',
                                            'application/atom+xml')
            return self.index()


class SearchFeedView(FeedView):
    def feed(self):
        f = queryAdapter(self.context, ISearchFeed)
        if f is None:
            raise NotFound
        return f

    def __call__(self):
        util = getMultiAdapter((self.context, self.request),
                               name='syndication-util')
        if util.search_rss_enabled(raise404=True):
            self.request.response.setHeader('Content-Type',
                                            'application/atom+xml')
            return self.index()


class SettingsForm(form.EditForm):
    label = _(u'heading_syndication_properties',
              default=u'Syndication Properties')
    description = _(u'description_syndication_properties',
                    default=u'Syndication enables you to syndicate this folder so it can'
                            u'be synchronized from other web sites.')
    fields = field.Fields(IFeedSettings)

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
SettingsFormView = wrap_form(SettingsForm)
