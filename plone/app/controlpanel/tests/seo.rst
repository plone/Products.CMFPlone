SEO and Anaytics control panel
==============================

First some initial setup code:

    >>> ctool = self.getToolByName('portal_properties')
    >>> self.loginAsManager()

Viewing the seo control panel
-----------------------------

    >>> self.browser.open('http://nohost/plone/@@seo-controlpanel.html')
    >>> self.browser.url
    'http://nohost/plone/@@seo-controlpanel.html'

Click the save button without making any changes:

    >>> self.browser.getControl(name="form.actions.save").click()
    >>> self.browser.url.endswith('seo-controlpanel.html')
    True

We should get a status message:

    >>> 'Changes saved.' in self.browser.contents
    True

Now click the cancel button:

    >>> self.browser.getControl(name="form.actions.cancel").click()
    >>> self.browser.url.endswith('plone_control_panel')
    True

There should be still no changes:

    >>> 'Changes canceled.' in self.browser.contents
    True

Make some changes
-----------------

    >>> self.browser.open('http://nohost/plone/@@seo-controlpanel.html')
    >>> self.browser.url.endswith('seo-controlpanel.html')
    True

    >>> self.browser.getControl(name='form.enable_sitemap').value = False
    >>> self.browser.getControl(name='form.webstats_js').value = "stats"

Click the save button:

    >>> self.browser.getControl(name="form.actions.save").click()
    >>> self.browser.url.endswith('seo-controlpanel.html')
    True

We should be informed that something has changed:

    >>> 'Changes saved.' in self.browser.contents
    True

Make sure the changes have been applied correctly to the tool:

    >>> self.site_props.enable_sitemap
    False

    >>> self.site_props.webstats_js
    u'stats'

Check the sitemap actually, should raise a 404

    >>> self.browser.handleErrors = True
    >>> from zope.publisher.interfaces import NotFound
    >>> from urllib2 import HTTPError
    >>> try:
    ...     self.browser.open("http://nohost/plone/sitemap.xml.gz")
    ... except HTTPError, e:
    ...     if e.code == 404:
    ...         print "ok"
    ok

Make again some changes
-----------------------

    >>> self.browser.open('http://nohost/plone/@@seo-controlpanel.html')
    >>> self.browser.url.endswith('seo-controlpanel.html')
    True

    >>> self.browser.getControl(name='form.enable_sitemap').value = True
    >>> self.browser.getControl(name='form.webstats_js').value = "stats"

Click the save button:

    >>> self.browser.getControl(name="form.actions.save").click()
    >>> self.browser.url.endswith('seo-controlpanel.html')
    True

We should be informed that something has changed:

    >>> 'Changes saved.' in self.browser.contents
    True

Make sure the changes have been applied correctly to the tool:

    >>> self.site_props.enable_sitemap
    True

    >>> self.site_props.webstats_js
    u'stats'

Test if the sitemaps does appear now

    >>> from zope.publisher.interfaces import NotFound
    >>> from urllib2 import HTTPError
    >>> self.browser.open("http://nohost/plone/sitemap.xml.gz")
    >>> headers = self.browser.headers

    >>> headers['status']
    '200 OK'

    >>> headers['content-type']
    'application/octet-stream'
