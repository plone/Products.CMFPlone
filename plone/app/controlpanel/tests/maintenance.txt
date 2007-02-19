Maintenance control panel
=========================

First some initial setup code:

    >>> self.loginAsManager()

Viewing the maintenance control panel
--------------------------------

    >>> self.browser.open('http://nohost/plone/@@maintenance-controlpanel.html')
    >>> self.browser.url.endswith('maintenance-controlpanel.html')
    True

    >>> 'Start packing' in self.browser.contents
    True


Click the save button without making any changes:

# This is not working (swallows cpu) withou providing a -1 we can skip the
# actual manage_pack method.

    >>> self.browser.getControl(name='form.days').value = '-1'
	>>> self.browser.getControl(name="form.actions.pack").click()
	>>> self.browser.url.endswith('maintenance-controlpanel.html')
	True

We should get a status message:

    >>> 'Packed the database.' in self.browser.contents
    True
