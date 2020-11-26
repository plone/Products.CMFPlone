from zope.component.hooks import getSite
from zope.component import adapts
from zope.interface import implementer
from zope.interface import Interface
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import getUtility

from DateTime import DateTime
from OFS.interfaces import IItem

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFPlone.interfaces.syndication import IFeed
from Products.CMFPlone.interfaces.syndication import IFeedItem
from Products.CMFPlone.interfaces.syndication import ISearchFeed
from Products.CMFPlone.interfaces.syndication import IFeedSettings
from Products.CMFPlone.utils import getSiteLogo

from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from zope.cachedescriptors.property import Lazy as lazy_property

from plone.dexterity.interfaces import IDexterityContent
from plone.rfc822.interfaces import IPrimaryFieldInfo
from plone.namedfile.interfaces import INamedField

from plone.app.contenttypes.behaviors.leadimage import ILeadImage


class BaseFeedData:

    def __init__(self, context):
        self.context = context
        self.settings = IFeedSettings(context)
        self.site = getSite()
        if self.show_about:
            self.pm = getToolByName(self.context, 'portal_membership')
        registry = getUtility(IRegistry)
        self.view_action_types = registry.get(
            'plone.types_use_view_action_in_listings', [])

    @lazy_property
    def show_about(self):
        return self.settings.show_author_info

    @property
    def link(self):
        return self.canonical_url

    @lazy_property
    def base_url(self):
        return self.context.absolute_url()

    @lazy_property
    def canonical_url(self):
        pcs = getMultiAdapter(
            (self.context, self.context.REQUEST), name='plone_context_state')
        return pcs.canonical_object_url()

    @property
    def title(self):
        return self.context.Title()

    @property
    def description(self):
        return self.context.Description()

    @property
    def categories(self):
        return self.context.Subject()

    @property
    def published(self):
        date = self.context.EffectiveDate()
        if date and date != 'None':
            return DateTime(date)

    @property
    def modified(self):
        date = self.context.ModificationDate()
        if date:
            return DateTime(date)

    @property
    def uid(self):
        uuid = IUUID(self.context, None)
        if uuid is None and hasattr(self.context, 'UID'):
            return self.context.UID()
        return uuid

    @property
    def rights(self):
        return self.context.Rights()

    @property
    def publisher(self):
        if hasattr(self.context, 'Publisher'):
            return self.context.Publisher()
        return 'No Publisher'


@implementer(IFeed)
class FolderFeed(BaseFeedData):

    @lazy_property
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
    def logo(self):
        return getSiteLogo(self.site)

    @property
    def icon(self):
        return '%s/favicon.ico' % self.site.absolute_url()

    def _brains(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(path={
            'query': '/'.join(self.context.getPhysicalPath()),
            'depth': 1
        })

    def _items(self):
        """
        do catalog query
        """
        return [b.getObject() for b in self._brains()]

    @property
    def items(self):
        for item in self._items()[:self.limit]:
            # look for custom adapter
            # otherwise, just use default
            adapter = queryMultiAdapter((item, self), IFeedItem)
            if adapter is None:
                adapter = BaseItem(item, self)
            yield adapter

    @property
    def limit(self):
        return self.settings.max_items

    @property
    def language(self):
        langtool = getToolByName(self.context, 'portal_languages')
        return langtool.getDefaultLanguage()


class CollectionFeed(FolderFeed):

    def _brains(self):
        return self.context.queryCatalog(batch=False)[:self.limit]


@implementer(ISearchFeed)
class SearchFeed(FolderFeed):

    def _brains(self):
        max_items = self.limit
        request = self.context.REQUEST
        start = int(request.get('b_start', 0))
        end = int(request.get('b_end', start + max_items))
        request.set('sort_order', 'reverse')
        request.set('sort_on', request.get('sort_on', 'effective'))
        return self.context.queryCatalog(
            show_all=1, use_types_blacklist=True,
            use_navigation_root=True)[start:end]


@implementer(IFeedItem)
class BaseItem(BaseFeedData):
    adapts(IItem, IFeed)

    def __init__(self, context, feed):
        self.context = context
        self.feed = feed

    @lazy_property
    def creator(self):
        if hasattr(self.context, 'Creator'):
            return self.context.Creator()

    @lazy_property
    def author(self):
        if self.feed.show_about:
            creator = self.context.Creator()
            member = self.feed.pm.getMemberById(creator)
            return member and member.getProperty('fullname') or creator

    @property
    def author_name(self):
        author = self.author
        if author and hasattr(author, 'getProperty'):
            return author.getProperty('fullname')

    @property
    def author_email(self):
        author = self.author
        if author and hasattr(author, 'getProperty'):
            return author.getProperty('email')

    @property
    def body(self):
        if hasattr(self.context, 'getText'):
            value = self.context.getText()
        elif hasattr(self.context, 'text'):
            value = self.context.text
        else:
            value = self.description
        if not isinstance(value, str):
            if hasattr(value, 'output'):
                # could be RichTextValue object, needs transform
                value = value.output
        return value

    content_core_template = ViewPageTemplateFile("templates/content_core.pt")

    def render_content_core(self):
        self.request = self.context.REQUEST
        return self.content_core_template()

    @property
    def link(self):
        url = self.base_url
        if self.context.portal_type in self.feed.view_action_types:
            url = url + '/view'
        else:
            url = self.canonical_url
        return url

    guid = link

    @property
    def has_enclosure(self):
        return False

    @lazy_property
    def file(self):
        if self.has_enclosure:
            return self.context.getFile()

    @property
    def file_url(self):
        url = self.base_url
        fi = self.file
        if fi is not None:
            filename = fi.getFilename()
            if filename:
                url += '/@@download/file/%s' % filename
        return url

    @property
    def file_length(self):
        return self.file.get_size()

    @property
    def file_type(self):
        return self.file.getContentType()


class DexterityItem(BaseItem):
    adapts(IDexterityContent, IFeed)

    file = None
    field_name = ''

    def __init__(self, context, feed):
        super().__init__(context, feed)
        self.dexterity = IDexterityContent.providedBy(context)
        lead = ILeadImage(self.context, None)
        if lead:
            if (lead.image
                    and hasattr(lead.image, 'getSize')
                    and lead.image.getSize() > 0):
                self.file = lead.image
                self.field_name = 'image'
        if self.file is None:
            try:
                primary = IPrimaryFieldInfo(self.context, None)
                if (INamedField.providedBy(primary.field)
                        and hasattr(primary.value, 'getSize')
                        and primary.value.getSize() > 0):
                    self.file = primary.value
                    self.field_name = primary.fieldname
            except TypeError:
                pass

    @property
    def file_url(self):
        url = self.base_url
        fi = self.file
        if fi is not None:
            filename = fi.filename
            if filename:
                url += '/@@download/{}/{}'.format(
                    self.field_name, filename)
        return url

    @property
    def has_enclosure(self):
        return self.file is not None

    @property
    def file_length(self):
        if self.has_enclosure:
            return self.file.getSize()
        return 0

    @property
    def file_type(self):
        if self.has_enclosure:
            return self.file.contentType
