from Products.CMFPlone.interfaces.syndication import ISearchFeed
from zope.component import getAdapter
from Products.CMFPlone.interfaces.syndication import IFeed
from zope.component import getMultiAdapter
from Products.Five import BrowserView
from zExceptions import NotFound
from Products.CMFPlone.interfaces.syndication import IFeedSettings
from z3c.form import form, button, field
from Products.CMFPlone import PloneMessageFactory as _
from plone.app.z3cform.layout import wrap_form
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound as pNotFound


class FeedView(BrowserView):

    def feed(self):
        return getAdapter(self.context, IFeed)

    def __call__(self):
        util = getMultiAdapter((self.context, self.request),
                               name='syndication-util')
        if util.context_enabled(raise404=True):
            settings = IFeedSettings(self.context)
            if self.__name__ not in settings.feed_types:
                raise NotFound
            self.request.response.setHeader('Content-Type',
                                            'application/atom+xml')
            return self.index()


class SearchFeedView(FeedView):
    def feed(self):
        return getAdapter(self.context, ISearchFeed)

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


class DownloadArchetypeFile(BrowserView):
    """Straight copy from plone.namedfile

    We need this because itunes *requires* urls to include
    file extensions.
    """
    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(DownloadArchetypeFile, self).__init__(context, request)
        self.fieldname = None
        self.filename = None

    def publishTraverse(self, request, name):

        if self.fieldname is None:  # ../@@download/fieldname
            self.fieldname = name
        elif self.filename is None:  # ../@@download/fieldname/filename
            self.filename = name
        else:
            raise pNotFound(self, name, request)

        return self

    def __call__(self):
        file = self._getFile()
        return file.index_html(disposition='attachment')

    def _getFile(self):
        context = getattr(self.context, 'aq_explicit', self.context)
        field = context.getField(self.fieldname)

        if field is None:
            raise pNotFound(self, self.fieldname, self.request)

        return field.get(context)
