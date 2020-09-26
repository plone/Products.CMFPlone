from DateTime import DateTime
from plone.z3cform.layout import wrap_form
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces.syndication import IFeed
from Products.CMFPlone.interfaces.syndication import IFeedSettings
from Products.CMFPlone.interfaces.syndication import ISearchFeed
from Products.Five import BrowserView
from uuid import NAMESPACE_OID
from uuid import uuid3
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zExceptions import NotFound
from zope.cachedescriptors.property import Lazy as lazy_property
from zope.component import getMultiAdapter
from zope.component import queryAdapter


class FeedView(BrowserView):

    content_type = 'application/atom+xml'

    def feed(self):
        f = queryAdapter(self.context, IFeed)
        if f is None:
            raise NotFound
        return f

    def __call__(self):
        util = getMultiAdapter((self.context, self.request),
                               name='syndication-util')
        context_state = getMultiAdapter((self.context, self.request),
                                        name='plone_context_state')
        if context_state.is_portal_root() or util.context_enabled(raise404=True):
            settings = IFeedSettings(self.context)
            if self.__name__ not in settings.feed_types:
                raise NotFound
            self.request.response.setHeader('Content-Type', self.content_type)
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


class NewsMLFeedView(FeedView):
    content_type = 'application/vnd.iptc.g2.newsitem+xml'

    @lazy_property
    def current_date(self):
        return DateTime()

    def duid(self, item, value):
        uid = uuid3(NAMESPACE_OID, item.uid + str(value))
        return uid.hex

    def get_image(self, item):
        scales = item.context.restrictedTraverse('@@images')
        if scales:
            try:
                return scales.scale('image')
            except AttributeError:
                pass
        return None


class SettingsForm(form.EditForm):
    label = _('heading_syndication_properties',
              default='Syndication Properties')
    description = _(
        'description_syndication_properties',
        default='Syndication enables you to syndicate this folder so it can'
                'be synchronized from other web sites.',
    )
    fields = field.Fields(IFeedSettings)

    @button.buttonAndHandler(_('Save'), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)


SettingsFormView = wrap_form(SettingsForm)
