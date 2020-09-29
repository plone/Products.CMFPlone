from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
from plone.registry.interfaces import IRegistry
from plone.testing.zope import Browser
from Products.CMFPlone.interfaces import ISiteSchema
from Products.CMFPlone.testing import PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING
from io import BytesIO
from zope.component import getMultiAdapter
from zope.component import getUtility

import unittest

# Red pixel with filename pixel.png
SITE_LOGO_BASE64 = b'filenameb64:cGl4ZWwucG5n;datab64:iVBORw0KGgoAAAANSUhEUgA'\
                   b'AAAEAAAABCAIAAACQd1PeAAAADElEQVQI12P4z8AAAAMBAQAY3Y2wAAA'\
                   b'AAElFTkSuQmCC'

SITE_LOGO_HEX = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00'\
                b'\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT'\
                b'\x08\xd7c\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\x18\xdd\x8d'\
                b'\xb0\x00\x00\x00\x00IEND\xaeB`\x82'


class SiteControlPanelFunctionalTest(unittest.TestCase):
    """Test that changes in the site control panel are actually
    stored in the registry.
    """

    layer = PRODUCTS_CMFPLONE_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            f'Basic {SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}'
        )

    def test_site_control_panel_link(self):
        self.browser.open(
            "%s/@@overview-controlpanel" % self.portal_url)
        self.browser.getLink('Site').click()

    def test_site_control_panel_backlink(self):
        self.browser.open(
            "%s/@@site-controlpanel" % self.portal_url)
        self.assertTrue("General" in self.browser.contents)

    def test_site_control_panel_sidebar(self):
        self.browser.open(
            "%s/@@site-controlpanel" % self.portal_url)
        self.browser.getLink('Site Setup').click()
        self.assertTrue(
            self.browser.url.endswith('/plone/@@overview-controlpanel')
        )

    def test_site_controlpanel_view(self):
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name="site-controlpanel")
        self.assertTrue(view())

    def test_site_title_is_stored_in_registry(self):
        self.browser.open(
            "%s/@@site-controlpanel" % self.portal_url)
        self.browser.getControl('Site title').value = "My Site"
        self.browser.getControl('Save').click()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone")
        self.assertEqual(settings.site_title, "My Site")

    def test_site_title_can_be_looked_up_by_plone_portal_state(self):
        self.browser.open(
            "%s/@@site-controlpanel" % self.portal_url)
        self.browser.getControl('Site title').value = "My Site"
        self.browser.getControl('Save').click()

        portal_state = getMultiAdapter(
            (self.portal, self.request),
            name='plone_portal_state'
        )
        self.assertEqual(portal_state.portal_title(), 'My Site')

    @unittest.skip("XXX: TODO! We have to patch CMFDefault for this.")
    def test_site_title_can_be_looked_up_by_portal_title(self):
        self.browser.open(
            "%s/@@site-controlpanel" % self.portal_url)
        self.browser.getControl('Site title').value = "My Site"
        self.browser.getControl('Save').click()

        self.assertEqual(self.portal.title, 'My Site')
        self.assertEqual(self.portal.Title(), 'My Site')

    def test_site_logo_is_stored_in_registry(self):
        self.browser.open(
            "%s/@@site-controlpanel" % self.portal_url)
        ctrl = self.browser.getControl(name="form.widgets.site_logo")
        ctrl.add_file(BytesIO(SITE_LOGO_HEX), 'image/png', 'pixel.png')
        self.browser.getControl('Save').click()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix='plone')
        self.assertEqual(settings.site_logo, SITE_LOGO_BASE64)

    def test_exposeDCMetaTags(self):
        self.browser.open(
            "%s/@@site-controlpanel" % self.portal_url)
        self.browser.getControl('Site title').value = "Plone Site"
        self.browser.getControl('Expose Dublin Core metadata').selected = True
        self.browser.getControl('Save').click()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone")
        self.assertEqual(settings.exposeDCMetaTags, True)

    def test_exposeDCMetaTags_exposes_meta_tags(self):
        self.browser.open(
            "%s/@@site-controlpanel" % self.portal_url)
        self.browser.getControl('Site title').value = "Plone Site"
        self.browser.getControl('Expose Dublin Core metadata').selected = True
        self.browser.getControl('Save').click()

        self.browser.open(self.portal_url)

        self.assertTrue('DC.type' in self.browser.contents)

    def test_enable_sitemap(self):
        self.browser.open(
            "%s/@@site-controlpanel" % self.portal_url)
        self.browser.getControl('Site title').value = "Plone Site"
        self.browser.getControl('Expose sitemap.xml.gz').selected = True
        self.browser.getControl('Save').click()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone")
        self.assertEqual(settings.enable_sitemap, True)

    def test_enable_sitemap_enables_the_sitemap(self):
        self.browser.open(
            "%s/@@site-controlpanel" % self.portal_url)
        self.browser.getControl('Site title').value = "Plone Site"
        self.browser.getControl('Expose sitemap.xml.gz').selected = True
        self.browser.getControl('Save').click()

        self.browser.open("%s/sitemap.xml.gz" % self.portal_url)

        self.assertEqual(
            self.browser.headers['status'].lower(),
            '200 ok'
        )
        self.assertEqual(
            self.browser.headers['content-type'],
            'application/octet-stream'
        )

    def test_webstats_js(self):
        self.browser.open(
            "%s/@@site-controlpanel" % self.portal_url)
        self.browser.getControl('Site title').value = "Plone Site"
        self.browser.getControl(name='form.widgets.webstats_js').value = \
            "<script>a=1</script>"
        self.browser.getControl('Save').click()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone")
        self.assertEqual(settings.webstats_js, "<script>a=1</script>")

    def test_webstat_js_shows_up_on_site(self):
        self.browser.open(
            "%s/@@site-controlpanel" % self.portal_url)
        self.browser.getControl('Site title').value = "Plone Site"
        self.browser.getControl(name='form.widgets.webstats_js').value = \
            "<script>a=1</script>"
        self.browser.getControl('Save').click()

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone")
        self.assertEqual(settings.webstats_js, "<script>a=1</script>")
        self.browser.open(self.portal_url)

        self.assertTrue("<script>a=1</script>" in self.browser.contents)
