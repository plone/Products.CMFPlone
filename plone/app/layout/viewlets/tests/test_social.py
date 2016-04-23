# -*- coding: utf-8 -*-
from plone.app.layout.viewlets.social import SocialTagsViewlet
from plone.app.layout.viewlets.tests.base import ViewletsTestCase
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import ISocialMediaSchema
from zope.component import getUtility


class TestSocialViewlet(ViewletsTestCase):
    """Test the content views viewlet.
    """

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.folder.invokeFactory('News Item', 'news-item',
                                  title='News Item')
        self.news = self.folder['news-item']

    def _tagFound(self, tags, attr, name=None, value=None):
        for meta in tags:
            if attr in meta:
                if name is None:
                    # only checking for existence
                    return True
                if meta[attr] == name:
                    if value is None:
                        # only checking for existence
                        return True
                    return meta['content'] == value
        return False

    def tagFound(self, viewlet, attr, name=None, value=None):
        return self._tagFound(viewlet.tags, attr, name=name, value=value)

    def bodyTagFound(self, viewlet, attr, name=None, value=None):
        return self._tagFound(viewlet.body_tags, attr, name=name, value=value)

    def testBasicTags(self):
        viewlet = SocialTagsViewlet(self.folder, self.app.REQUEST, None)
        viewlet.update()
        description = self.folder.Description()
        folder_url = self.folder.absolute_url()
        # Twitter
        self.assertTrue(self.tagFound(
            viewlet, 'name', 'twitter:card', "summary"))
        self.assertTrue(self.tagFound(
            viewlet, 'name', 'twitter:title', viewlet.page_title))
        self.assertTrue(self.tagFound(
            viewlet, 'name', 'twitter:description', description))
        self.assertTrue(self.tagFound(
            viewlet, 'name', 'twitter:url', folder_url))
        # OpenGraph/Facebook
        self.assertTrue(self.tagFound(
            viewlet, 'property', 'og:site_name', viewlet.site_title_setting))
        self.assertTrue(self.tagFound(
            viewlet, 'property', 'og:description', description))
        self.assertTrue(self.tagFound(
            viewlet, 'property', 'og:url', folder_url))
        # No schema.org itemprops
        self.assertFalse(self.tagFound(viewlet, 'itemprop'))

    def testBasicItemProps(self):
        viewlet = SocialTagsViewlet(self.folder, self.app.REQUEST, None)
        viewlet.update()
        description = self.folder.Description()
        folder_url = self.folder.absolute_url()
        # No Twitter
        self.assertFalse(self.bodyTagFound(viewlet, 'name'))
        # No OpenGraph/Facebook
        self.assertFalse(self.bodyTagFound(viewlet, 'property'))
        # schema.org itemprops
        self.assertTrue(self.bodyTagFound(
            viewlet, 'itemprop', 'name', viewlet.page_title))
        self.assertTrue(self.bodyTagFound(
            viewlet, 'itemprop', 'description', description))
        self.assertTrue(self.bodyTagFound(
            viewlet, 'itemprop', 'url', folder_url))

    def testDisabled(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ISocialMediaSchema, prefix='plone', check=False)
        settings.share_social_data = False
        viewlet = SocialTagsViewlet(self.folder, self.app.REQUEST, None)
        viewlet.update()
        self.assertEquals(len(viewlet.tags), 0)

    def testIncludeSocialSettings(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(
            ISocialMediaSchema, prefix='plone', check=False)
        settings.twitter_username = u'foobar'
        settings.facebook_app_id = u'foobar'
        settings.facebook_username = u'foobar'

        viewlet = SocialTagsViewlet(self.folder, self.app.REQUEST, None)
        viewlet.update()
        self.assertTrue(self.tagFound(
            viewlet, 'name', 'twitter:site', "@foobar"))
        self.assertTrue(self.tagFound(
            viewlet, 'property', 'fb:app_id', 'foobar'))
        self.assertTrue(self.tagFound(
            viewlet, 'property', 'og:article:publisher',
            'https://www.facebook.com/foobar'))

    def testLogo(self):
        viewlet = SocialTagsViewlet(self.news, self.app.REQUEST, None)
        viewlet.update()
        self.assertTrue(self.tagFound(
            viewlet, 'property', 'og:image', 'http://nohost/plone/logo.png'))
        self.assertTrue(self.tagFound(
            viewlet, 'name', 'twitter:image', 'http://nohost/plone/logo.png'))
        self.assertFalse(self.tagFound(viewlet, 'itemprop'))
        self.assertTrue(self.bodyTagFound(
            viewlet, 'itemprop', 'image', 'http://nohost/plone/logo.png'))
