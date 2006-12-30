Mail control panel
==================

First some initial setup code:

    >>> ctool = self.getToolByName('portal_calendar')
    >>> mailhost = self.getToolByName('MailHost')
    >>> self.loginAsManager()

Viewing the search control panel
--------------------------------

    >>> self.browser.open('http://nohost/plone/@@mail-controlpanel.html')
    >>> self.browser.url.endswith('mail-controlpanel.html')
    True

Click the save button without making any changes:

    >>> self.browser.getControl(name="form.actions.save").click()
    >>> self.browser.url.endswith('mail-controlpanel.html')
    True

We should get a status message:

    >>> 'No changes done.' in self.browser.contents
    True

Now click the cancel button:

    >>> self.browser.getControl(name="form.actions.cancel").click()
    >>> self.browser.url.endswith('mail-controlpanel.html')
    True

There should be still no changes:

    >>> 'Changes canceled.' in self.browser.contents
    True

Make some changes
-----------------

    >>> self.browser.open('http://nohost/plone/@@mail-controlpanel.html')
    >>> self.browser.url.endswith('mail-controlpanel.html')
    True

    >>> self.browser.getControl(name='form.smtp_host').value = 'localhost2'
    >>> self.browser.getControl(name='form.smtp_port').value = '2525'
    >>> self.browser.getControl(name='form.smtp_userid').value = 'admin'
    >>> self.browser.getControl(name='form.smtp_pass').value = 'secret'
    >>> self.browser.getControl(name='form.email_from_name').value = 'Spambot'
    >>> self.browser.getControl(name='form.email_from_address').value = 'spam@localhost'

Click the save button:

    >>> self.browser.getControl(name="form.actions.save").click()
    >>> self.browser.url.endswith('mail-controlpanel.html')
    True

We should be informed that something has changed:

    >>> 'Changes saved.' in self.browser.contents
    True

Make sure the changes have been applied correctly to the mailhost:

    >>> mailhost.smtp_host
    u'localhost2'

    >>> mailhost.smtp_port
    2525

    >>> mailhost.smtp_userid
    u'admin'

    >>> mailhost.smtp_pass
    u'secret'

    >>> self.site_props.email_from_name
    u'Spambot'

    >>> self.site_props.email_from_address
    u'spam@localhost'
