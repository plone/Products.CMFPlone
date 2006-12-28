Types control panel
====================

Viewing the types control panel
--------------------------------

    >>> self.loginAsRoot()
    >>> self.browser.open('http://nohost/plone/@@types-controlpanel.html')
    >>> self.browser.url
    'http://nohost/plone/@@types-controlpanel.html'

Click the save button without making any changes:

    >>> self.browser.getControl(name="form.actions.save").click()
    >>> self.browser.url
    'http://nohost/plone/%40%40types-controlpanel.html'

We should get a status message:

    >>> 'No changes done.' in self.browser.contents
    True

Now click the cancel button:

    >>> self.browser.getControl(name="form.actions.cancel").click()
    >>> self.browser.url
    'http://nohost/plone/%40%40types-controlpanel.html'

There should be still no changes:

    >>> 'Changes canceled.' in self.browser.contents
    True

Modifiying values
-----------------

    >>> self.browser.getControl(name='form.default_type').value = ['text/x-web-textile',]
    >>> self.browser.getControl(name="form.actions.save").click()
    >>> 'Changes saved' in self.browser.contents
    True

Verify, that the setting has actually been changed:

    >>> from Products.Archetypes.mimetype_utils import getDefaultContentType
    >>> getDefaultContentType(self.portal)
    'text/x-web-textile'

