from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.component import adapts
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from zope.component import queryMultiAdapter
from Products.ZCatalog.interfaces import ICatalogBrain
from Products.CMFPlone.interfaces.syndication import IFeed
from Products.CMFPlone.interfaces.syndication import IFeedItem
from Products.CMFPlone.interfaces.syndication import ISearchFeed
from Products.CMFPlone.interfaces.syndication import IFeedSettings
from DateTime import DateTime


ADAPTER_NAME_PREFIX = 'syndicate-'


class FolderFeed(object):
    implements(IFeed)

    def __init__(self, context):
        self.context = context
        self.settings = IFeedSettings(context)
        self.site = getSite()
        if self.show_about:
            self.pm = getToolByName(self.context, 'portal_membership')
        self.full_objects = False

    @property
    def show_about(self):
        pprops = getToolByName(self.context, 'portal_properties')
        return pprops.site_properties.allowAnonymousViewAbout

    @property
    def author(self):
        if self.show_about:
            creator = self.context.Creator()
            member = self.pm.getMemberById(creator)
            return member

    @property
    def author_name(self):
        if self.author:
            return self.author.getProperty('fullname')

    @property
    def author_email(self):
        if self.author:
            return self.author.getProperty('email')

    @property
    def title(self):
        return self.context.Title()

    @property
    def description(self):
        return self.context.Description()

    @property
    def logo(self):
        return '%s/logo.png' % self.site.absolute_url()

    @property
    def icon(self):
        return '%s/favicon.ico' % self.site.absolute_url()

    @property
    def categories(self):
        return self.context.Subject()

    @property
    def published(self):
        return DateTime(self.context.EffectiveDate())

    @property
    def modified(self):
        return DateTime(self.context.ModificationDate())

    @property
    def uid(self):
        return self.context.UID()

    def _items(self):
        """
        do catalog query
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(path={
            'query': '/'.join(self.context.getPhysicalPath()),
            'depth': 1
            })

    @property
    def items(self):
        for item in self._items():
            # look for custom adapter
            # otherwise, just use default
            adapter = queryMultiAdapter(
                (item, self), name=ADAPTER_NAME_PREFIX + item.portal_type)
            if adapter is None:
                adapter = BaseItem(item, self)
            yield adapter

    @property
    def limit(self):
        return self.settings.max_items

    @property
    def full_object(self):
        return self.settings.render_body or self.settings.media_feed or \
            self.full_objects

    @property
    def media_feed(self):
        return self.settings.media_feed


class CollectionFeed(FolderFeed):
    def _items(self):
        return self.context.queryCatalog()[:self.limit]


class SearchFeed(FolderFeed):
    implements(ISearchFeed)

    def _items(self):
        max_items = self.limit
        request = self.context.REQUEST
        start = int(request.get('b_start', 0))
        end = int(request.get('b_end', start + max_items))
        request.set('sort_order', 'reverse')
        request.set('sort_on', request.get('sort_on', 'effective'))
        return self.context.queryCatalog(show_all=1, use_types_blacklist=True,
            use_navigation_root=True)[start:end]


class BaseItem(object):
    implements(IFeedItem)
    adapts(ICatalogBrain, IFeed)

    def __init__(self, brain, feed):
        self.brain = brain
        if feed.full_object:
            self.content = brain.getObject()
        else:
            self.content = None
        self.feed = feed

    @property
    def author(self):
        if self.feed.show_about:
            creator = self.brain.Creator
            member = self.feed.pm.getMemberById(creator)
            return member and member.getProperty('fullname') or creator

    @property
    def author_name(self):
        if self.author:
            return self.author.getProperty('fullname')

    @property
    def author_email(self):
        if self.author:
            return self.author.getProperty('email')

    @property
    def title(self):
        return self.brain.Title

    @property
    def body(self):
        if self.content is not None:
            if hasattr(self.content, 'getBody'):
                return self.content.getBody()
            elif hasattr(self.content, 'body'):
                return self.content.body
        return self.description

    @property
    def base_url(self):
        return self.brain.getURL()

    @property
    def link(self):
        # XXX check for file and image types
        url = self.base_url
        if self.brain.portal_type in ('File', 'Image'):
            url = url + '/view'
        return url

    guid = link

    @property
    def description(self):
        return self.brain.Description

    @property
    def categories(self):
        return self.brain.Subject

    @property
    def published(self):
        date = self.brain.EffectiveDate
        if date and date != 'None':
            return DateTime(date)

    @property
    def modified(self):
        date = self.brain.ModificationDate
        if date:
            return DateTime(date)

    @property
    def file(self):
        if self.brain.portal_type == 'File':
            return self.content.getFile()
        elif self.brain.portal_type == 'Image':
            return self.content.getImage()

    @property
    def file_url(self):
        url = self.base_url
        fi = self.file
        if fi is not None:
            url += '++byfilename++' + fi.getFilename()
        return url

    @property
    def file_length(self):
        return self.file.getSize()

    @property
    def file_type(self):
        return self.file.getContentType()

    @property
    def uid(self):
        return self.brain.UID