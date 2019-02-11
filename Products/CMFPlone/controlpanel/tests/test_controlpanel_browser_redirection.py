# -*- coding: utf-8 -*-
from plone.app.redirector.interfaces import IRedirectionStorage
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser
from Products.CMFPlone.controlpanel.browser.redirects import RedirectionSet
from Products.CMFPlone.PloneBatch import Batch
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from zope.component import getMultiAdapter
from zope.component import getUtility

import math
import transaction
import unittest


class RedirectionControlPanelFunctionalTest(unittest.TestCase):
    """Test that changes in the redirection control panel are actually
    stored in the registry.
    """

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

    def test_redirection_controlpanel_link(self):
        self.browser.open("%s/@@overview-controlpanel" % self.portal_url)
        self.browser.getLink('URL Management').click()

    def test_redirection_controlpanel_backlink(self):
        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        self.assertTrue("General" in self.browser.contents)

    def test_redirection_controlpanel_sidebar(self):
        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        self.browser.getLink('Site Setup').click()
        self.assertTrue(
            self.browser.url.endswith('/plone/@@overview-controlpanel')
        )

    def test_redirection_controlpanel_view(self):
        view = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name="redirection-controlpanel"
        )
        self.assertTrue(view())

    def test_redirection_controlpanel_add_redirect(self):
        storage = getUtility(IRedirectionStorage)
        redirection_path = '/alias-folder'
        target_path = '/test-folder'
        storage_path = '/plone/alias-folder'

        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        self.browser.getControl(name='redirection').value = redirection_path
        self.browser.getControl(name='target_path').value = target_path
        self.browser.getControl(name='form.button.Add').click()

        self.assertTrue(
            storage.has_path(storage_path),
            u'Redirection storage should have path "{0}"'.format(storage_path),
        )

    def test_redirection_controlpanel_set(self):
        storage = getUtility(IRedirectionStorage)
        portal_path = self.layer['portal'].absolute_url_path()
        for i in range(1000):
            storage.add(
                '{0:s}/foo/{1:s}'.format(portal_path, str(i)),
                '{0:s}/bar/{1:s}'.format(portal_path, str(i)),
            )
        redirects = RedirectionSet()
        self.assertEqual(len(redirects), 1000)
        self.assertDictEqual(
            redirects[0],
            {
                'redirect': '{0:s}/foo/0'.format(portal_path),
                'path': '/foo/0',
                'redirect-to': '/bar/0',
            },
        )
        self.assertDictEqual(
            redirects[999],
            {
                'redirect': '{0:s}/foo/999'.format(portal_path),
                'path': '/foo/999',
                'redirect-to': '/bar/999',
            },
        )
        self.assertEqual(len(list(iter(redirects))), 1000)
        self.assertDictEqual(
            list(iter(redirects))[0],
            {
                'redirect': '{0:s}/foo/0'.format(portal_path),
                'path': '/foo/0',
                'redirect-to': '/bar/0',
            },
        )

    def test_redirection_controlpanel_batching(self):
        storage = getUtility(IRedirectionStorage)
        portal_path = self.layer['portal'].absolute_url_path()
        for i in range(1000):
            storage.add(
                '{0:s}/foo/{1:s}'.format(portal_path, str(i)),
                '{0:s}/bar/{1:s}'.format(portal_path, str(i)),
            )
        view = getMultiAdapter(
            (self.layer['portal'], self.layer['request']),
            name='redirection-controlpanel',
        )
        # Test that view/redirects returns batch
        self.assertIsInstance(view.redirects(), Batch)

        # Test that view/batching returns batching with anchor in urls
        batching = view.batching()
        self.assertIn('?b_start:int=990#manage-existing-aliases', batching)

    def test_redirection_controlpanel_redirect_alias_exists(self):
        path_alias = '/alias'
        path_target = '/test-folder'
        storage_alias = '/plone{0}'.format(path_alias)
        storage_target = '/plone{0}'.format(path_target)
        storage = getUtility(IRedirectionStorage)
        storage.add(storage_alias, storage_target)
        transaction.commit()

        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        self.browser.getControl(name='redirection').value = path_alias
        self.browser.getControl(name='target_path').value = path_target
        self.browser.getControl(name='form.button.Add').click()

        self.assertTrue(
            storage.get(storage_alias) == storage_target,
            '{0} not target of alternative url!'.format(storage_target),
        )
        self.assertTrue(
            'The provided alternative url already exists!'
            in self.browser.contents,
            u'Message "alternative url already exists" not in page!',
        )

    def test_redirection_controlpanel_filtering(self):
        storage = getUtility(IRedirectionStorage)
        portal_path = self.layer['portal'].absolute_url_path()
        for i in range(1000):
            storage.add(
                '{0:s}/foo1/{1:s}'.format(portal_path, str(i)),
                '{0:s}/bar/{1:s}'.format(portal_path, str(i)),
            )
        for i in range(1000):
            storage.add(
                '{0:s}/foo2/{1:s}'.format(portal_path, str(i)),
                '{0:s}/bar/{1:s}'.format(portal_path, str(i)),
            )

        redirects = RedirectionSet()
        self.assertEqual(len(redirects), 2000)
        redirects = RedirectionSet(query='/foo')
        self.assertEqual(len(redirects), 2000)
        redirects = RedirectionSet(query='/foo1')
        self.assertEqual(len(redirects), 1000)
        redirects = RedirectionSet(query='/foo2')
        self.assertEqual(len(redirects), 1000)

        request = self.layer['request'].clone()
        request.form['q'] = '/foo'
        view = getMultiAdapter(
            (self.layer['portal'], request), name='redirection-controlpanel'
        )
        self.assertEqual(view.redirects().numpages, math.ceil(2000 / 15.0))

        request = self.layer['request'].clone()
        request.form['q'] = '/foo1'
        view = getMultiAdapter(
            (self.layer['portal'], request), name='redirection-controlpanel'
        )
        self.assertEqual(view.redirects().numpages, math.ceil(1000 / 15.0))

        request = self.layer['request'].clone()
        request.form['q'] = '/foo2'
        view = getMultiAdapter(
            (self.layer['portal'], request), name='redirection-controlpanel'
        )
        self.assertEqual(view.redirects().numpages, math.ceil(1000 / 15.0))

        request = self.layer['request'].clone()
        view = getMultiAdapter(
            (self.layer['portal'], request), name='redirection-controlpanel'
        )
        self.assertEqual(view.redirects().numpages, math.ceil(2000 / 15.0))

        # Filtering without new request does not have effect because memoize
        request.form['q'] = '/foo2'
        self.assertEqual(view.redirects().numpages, math.ceil(2000 / 15.0))

    def test_redirection_controlpanel_redirect_no_target(self):
        path_alias = '/alias'
        path_target = '/not-existing'

        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        self.browser.getControl(name='redirection').value = path_alias
        self.browser.getControl(name='target_path').value = path_target
        self.browser.getControl(name='form.button.Add').click()

        self.assertTrue(
            'The provided target object does not exist.'
            in self.browser.contents,
            u'Message "target does not exist" not in page!',
        )

    def test_redirection_controlpanel_missing_slash_target(self):
        path_alias = '/alias'
        path_target = 'Members'

        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        self.browser.getControl(name='redirection').value = path_alias
        self.browser.getControl(name='target_path').value = path_target
        self.browser.getControl(name='form.button.Add').click()

        self.assertTrue(
            'Target path must start with a slash.' in self.browser.contents,
            u'Errormessage for missing slash on target path missing',
        )

    def test_redirection_controlpanel_missing_slash_alias(self):
        path_alias = 'alias'
        path_target = '/Members'

        self.browser.open("%s/@@redirection-controlpanel" % self.portal_url)
        self.browser.getControl(name='redirection').value = path_alias
        self.browser.getControl(name='target_path').value = path_target
        self.browser.getControl(name='form.button.Add').click()

        self.assertTrue(
            'Alternative url path must start with a slash.'
            in self.browser.contents,
            u'Errormessage for missing slash on alternative url missing',
        )

    def test_manage_aliases_standard(self):
        storage = getUtility(IRedirectionStorage)
        folder = self.portal['test-folder']

        self.browser.open("%s/@@manage-aliases" % folder.absolute_url())
        self.browser.getControl(name='redirection').value = '/alias'
        self.browser.getControl(name='form.button.Add').click()

        self.assertTrue(
            'Alternative url added.' in self.browser.contents,
            u'Message for added alternative url missing',
        )
        self.assertTrue(storage.has_path('/plone/alias'))
        self.assertEqual(storage.get('/plone/alias'), '/plone/test-folder')

    def test_manage_aliases_navigation_root(self):
        from zope.interface import alsoProvides
        from plone.app.layout.navigation.interfaces import INavigationRoot

        storage = getUtility(IRedirectionStorage)
        folder = self.portal['test-folder']
        alsoProvides(folder, INavigationRoot)
        transaction.commit()

        self.browser.open("%s/@@manage-aliases" % folder.absolute_url())
        self.browser.getControl(name='redirection').value = '/alias'
        self.browser.getControl(name='form.button.Add').click()

        self.assertTrue(
            'Alternative url added.' in self.browser.contents,
            u'Message for added alternative url missing',
        )
        self.assertTrue(storage.has_path('/plone/test-folder/alias'))
        self.assertEqual(
            storage.get('/plone/test-folder/alias'), '/plone/test-folder'
        )

        # Add the navigation root path explicitly.
        self.browser.getControl(
            name='redirection'
        ).value = '/test-folder/alias2'
        self.browser.getControl(name='form.button.Add').click()

        self.assertTrue(
            'Alternative url added.' in self.browser.contents,
            u'Message for added alternative url missing',
        )
        self.assertTrue(storage.has_path('/plone/test-folder/alias2'))
        self.assertEqual(
            storage.get('/plone/test-folder/alias2'), '/plone/test-folder'
        )

    def test_absolutize_path(self):
        # absolutize_path is a helper function that returns a tuple
        # of absolute path and error message.
        from Products.CMFPlone.controlpanel.browser.redirects import (
            absolutize_path as ap,
        )

        # A path is required.
        self.assertEqual(ap(''), ('', 'You have to enter an alternative url.'))
        self.assertEqual(
            ap('', is_source=False), ('', 'You have to enter a target.')
        )

        # relative paths are not accepted
        self.assertEqual(
            ap('foo'), ('foo', 'Alternative url path must start with a slash.')
        )
        self.assertEqual(
            ap('foo', is_source=True),
            ('foo', 'Alternative url path must start with a slash.'),
        )
        self.assertEqual(
            ap('foo', is_source=False),
            ('foo', 'Target path must start with a slash.'),
        )

        # absolute paths are good
        self.assertEqual(ap('/foo'), ('/plone/foo', None))
        self.assertEqual(ap('/foo', is_source=True), ('/plone/foo', None))

        # for targets, an object must exist on the path
        self.assertEqual(
            ap('/foo', is_source=False),
            ('/plone/foo', 'The provided target object does not exist.'),
        )
        self.assertEqual(
            ap('/test-folder', is_source=False), ('/plone/test-folder', None)
        )
        self.assertEqual(
            ap('/test-folder/@@sharing', is_source=False),
            ('/test-folder/@@sharing', 'Target path must not be a view.'),
        )

        # A source must not exist.
        self.assertEqual(
            ap('/test-folder'),
            (
                '/plone/test-folder',
                'Cannot use a working path as alternative url.',
            ),
        )
        # More general: a source must not be traversable already.
        self.assertEqual(
            ap('/view'),
            ('/plone/view', 'Cannot use a working path as alternative url.'),
        )
        self.assertEqual(
            ap('/@@overview-controlpanel'),
            (
                '/@@overview-controlpanel',
                'Alternative url path must not be a view.',
            ),
        )

        # And a source must not exist via (implicit) acquisition.
        # We might *want* to allow this, but such a redirect would not have effect,
        # because acquisition happens earlier.
        # See https://github.com/collective/Products.RedirectionTool/issues/12
        self.portal.invokeFactory('Document', 'doc')
        self.assertEqual(
            ap('/test-folder/doc'),
            (
                '/plone/test-folder/doc',
                'Cannot use a working path as alternative url.',
            ),
        )

        # A source must not already exist in the redirect list.
        storage = getUtility(IRedirectionStorage)
        portal_path = self.portal.absolute_url_path()
        storage.add(
            '{0:s}/foo'.format(portal_path),
            '{0:s}/test-folder'.format(portal_path),
        )
        self.assertEqual(
            ap('/foo', is_source=True),
            ('/plone/foo', 'The provided alternative url already exists!'),
        )

        # For targets, we now accept external urls.
        # Note that this can only be done on the control panel,
        # so by default only by Site Administrators or Managers.
        self.assertEqual(
            ap('https://example.org', is_source=False),
            ('https://example.org', None),
        )
        self.assertEqual(
            ap('http://example.org', is_source=False),
            ('http://example.org', None),
        )
        self.assertEqual(
            ap(
                'https://example.org/some/path?foo=bar&bar=foo',
                is_source=False,
            ),
            ('https://example.org/some/path?foo=bar&bar=foo', None),
        )
        self.assertEqual(
            ap('http://', is_source=False),
            ('http://', 'Target path must start with a slash.'),
        )
        # Using '//' to ignore http/https differences seems useless,
        # as we don't include content but only link to it.
        self.assertEqual(
            ap('//example.org', is_source=False),
            (
                '/plone//example.org',
                'The provided target object does not exist.',
            ),
        )
