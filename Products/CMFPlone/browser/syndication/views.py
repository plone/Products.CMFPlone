from zExceptions import NotFound
from zope.publisher.interfaces import IPublishTraverse
from zope.component import queryMultiAdapter
from zope.interface import implements
from Products.CMFPlone.interfaces.syndication import IFeedSettings
from Products.CMFPlone.interfaces.syndication import IFeeds
from z3c.form import form, button, field
from Products.CMFPlone import PloneMessageFactory as _
from plone.app.z3cform.layout import wrap_form
from OFS.SimpleItem import SimpleItem


class Feeds(SimpleItem):
    """
    The /feeds part of the url
    """
    implements(IPublishTraverse, IFeeds)

    def __init__(self, context, request):
        super(Feeds, self).__init__(context, request)
        self.id = 'feeds'
        self.Title = lambda: u'Feeds'
        self.context = context

    def publishTraverse(self, request, name):
        syntool = queryMultiAdapter(
            (self.context, self.request), name='syndication-tool')
        if not syntool.site_enabled():
            raise NotFound
        settings = IFeedSettings(self.context)
        if settings.enabled and name in settings.feed_types:
            # XXX Check enabled and enabled feed type
            view = queryMultiAdapter(
                (self, self.request), name=name)
            if view:
                return view.__of__(self)
        raise NotFound

    def getPhysicalPath(self):
        return self.context.getPhysicalPath() + (self.id,)


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
