# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import ISocialMediaSchema
from plone.app.layout.viewlets.social import SocialTagsViewlet
from plone.app.layout.viewlets.tests.base import ViewletsTestCase
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class TestSocialViewlet(ViewletsTestCase):
    """Test the content views viewlet.
    """

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.folder.invokeFactory('News Item', 'news-item',
                                  title='News Item')
        self.news = self.folder['news-item']

    def tagFound(self, viewlet, attr, name, value):
        for meta in viewlet.tags:
            if attr in meta:
                if meta[attr] == name:
                    return meta['content'] == value
        return False

    def hasTag(self, viewlet, attr, name):
        for meta in viewlet.tags:
            if attr in meta:
                return meta[attr] == name
        return False

    def testBasicTags(self):
        viewlet = SocialTagsViewlet(self.folder, self.app.REQUEST, None)
        viewlet.update()
        self.assertTrue(self.tagFound(viewlet, 'name', 'twitter:card', "summary"))
        self.assertTrue(self.tagFound(viewlet, 'name', 'twitter:title',
                                      viewlet.page_title))
        self.assertTrue(self.tagFound(viewlet, 'property', 'og:site_name',
                                      viewlet.site_title))

    def testDisabled(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISocialMediaSchema, prefix="plone",
                                         check=False)
        settings.share_social_data = False
        viewlet = SocialTagsViewlet(self.folder, self.app.REQUEST, None)
        viewlet.update()
        self.assertEquals(len(viewlet.tags), 0)

    def testIncludeSocialSettings(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISocialMediaSchema, prefix="plone",
                                         check=False)
        settings.twitter_username = u'foobar'
        settings.facebook_app_id = u'foobar'
        settings.facebook_username = u'foobar'

        viewlet = SocialTagsViewlet(self.folder, self.app.REQUEST, None)
        viewlet.update()
        self.assertTrue(self.tagFound(viewlet, 'name', 'twitter:site', "@foobar"))
        self.assertTrue(self.tagFound(viewlet, 'property', 'fb:app_id', 'foobar'))
        self.assertTrue(
            self.tagFound(viewlet, 'property',
                          'og:article:publisher', 'https://www.facebook.com/foobar'))

    def testLogo(self):
        viewlet = SocialTagsViewlet(self.news, self.app.REQUEST, None)
        viewlet.update()
        self.assertTrue(
            self.tagFound(viewlet, 'property',
                          'og:image:type', 'http://nohost/plone/logo.png'))