Types control panel
===================

Viewing the types control panel
-------------------------------

    >>> self.loginAsManager()
    >>> self.browser.open('http://nohost/plone/@@types-controlpanel.html')
    >>> self.browser.url
    'http://nohost/plone/@@types-controlpanel.html'

We have two controls, one for the default type and a multiselection for alternativate formats:

    >>> self.browser.getControl(name='form.default_type').value
    ['text/html']
    >>> self.browser.getControl(name='form.allowed_types').value
    ['text/html', 'text/plain', 'text/restructured', 'text/x-web-textile']

Click the save button without making any changes:

    >>> self.browser.getControl(name="form.actions.save").click()
    >>> self.browser.url.endswith('types-controlpanel.html')
    True

We should get a status message:

    >>> 'Changes saved.' in self.browser.contents
    True

Now click the cancel button:

    >>> self.browser.getControl(name="form.actions.cancel").click()
    >>> self.browser.url.endswith('types-controlpanel.html')
    True

There should be still no changes:

    >>> 'Changes canceled.' in self.browser.contents
    True

Modifying values
----------------

    >>> self.browser.getControl(name='form.default_type').value = ['text/x-web-textile',]
    >>> self.browser.getControl(name='form.allowed_types').value = ['text/html', 'text/x-web-textile']
    >>> self.browser.getControl(name="form.actions.save").click()
    >>> 'Changes saved' in self.browser.contents
    True

Verify, that the settings have actually been changed:

    >>> from Products.Archetypes.mimetype_utils import getDefaultContentType, getAllowedContentTypes
    >>> getDefaultContentType(self.portal)
    'text/x-web-textile'
    >>> getAllowedContentTypes(self.portal)
    ['text/html', 'text/x-web-textile']
