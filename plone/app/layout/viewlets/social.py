# -*- coding: utf-8 -*-
from plone.app.layout.viewlets.common import TitleViewlet
from plone.memoize.view import memoize
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.browser.syndication.adapters import BaseItem
from Products.CMFPlone.browser.syndication.adapters import FolderFeed
from Products.CMFPlone.interfaces import ISocialMediaSchema
from Products.CMFPlone.interfaces.syndication import IFeedItem
from Products.CMFPlone.utils import getSiteLogo
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite


class SocialTagsViewlet(TitleViewlet):

    def head_tag_filter(self, value):
        if not isinstance(value, dict):
            return
        return 'itemprop' not in value

    def body_tag_filter(self, value):
        if not isinstance(value, dict):
            return
        return 'itemprop' in value

    @property
    def tags(self):
        # Do not show items with 'itemprop'.
        return filter(self.head_tag_filter, self._get_tags())

    @property
    def body_tags(self):
        # Show only items without 'itemprop'.
        return filter(self.body_tag_filter, self._get_tags())

    @memoize
    def _get_tags(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISocialMediaSchema, prefix="plone",
                                         check=False)

        if not settings.share_social_data:
            return []

        tags = [
            dict(itemprop="name", content=self.page_title),
            dict(name="twitter:card", content="summary"),
            dict(name="twitter:title", content=self.page_title),
            dict(property="og:site_name", content=self.site_title_setting),
            dict(property="og:title", content=self.page_title),
            dict(property="og:type", content="website"),
        ]
        if settings.twitter_username:
            tags.append(dict(name="twitter:site",
                             content="@" + settings.twitter_username))
        if settings.facebook_app_id:
            tags.append(dict(property="fb:app_id",
                             content=settings.facebook_app_id))
        if settings.facebook_username:
            tags.append(
                dict(property="og:article:publisher",
                     content="https://www.facebook.com/" +
                     settings.facebook_username))

        # reuse syndication since that packages the data
        # the way we'd prefer likely
        site = getSite()
        feed = FolderFeed(site)
        item = queryMultiAdapter((self.context, feed), IFeedItem, default=None)
        if item is None:
            item = BaseItem(self.context, feed)

        tags.extend([
            dict(itemprop="description", content=item.description),
            dict(itemprop="url", content=item.link),
            dict(name="twitter:description", content=item.description),
            dict(name="twitter:url", content=item.link),
            dict(property="og:description", content=item.description),
            dict(property="og:url", content=item.link),
        ])

        found_image = False
        if item.has_enclosure and item.file_length > 0:
            if item.file_type.startswith('image'):
                found_image = True
                tags.extend([
                    dict(name="twitter:image", content=item.file_url),
                    dict(property="og:image", content=item.file_url),
                    dict(itemprop="image", content=item.file_url),
                    dict(property="og:image:type", content=item.file_type)
                ])
            elif (item.file_type.startswith('video') or
                    item.file_type == "application/x-shockwave-flash"):
                tags.extend([
                    dict(property="og:video", content=item.file_url),
                    dict(property="og:video:type", content=item.file_type)
                ])
            elif item.file_type.startswith('audio'):
                tags.extend([
                    dict(property="og:audio", content=item.file_url),
                    dict(property="og:audio:type", content=item.file_type)
                ])

        if not found_image:
            url = getSiteLogo()
            tags.extend([
                dict(name="twitter:image", content=url),
                dict(property="og:image", content=url),
                dict(itemprop="image", content=url),
                dict(property="og:image:type", content='image/png')
            ])
        return tags
