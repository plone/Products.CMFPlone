Calendar control panel
======================

First some initial setup code:

    >>> ctool = self.getToolByName('portal_calendar')
    >>> self.loginAsManager()

Viewing the calendar control panel
----------------------------------

    >>> self.browser.open('http://nohost/plone/@@calendar-controlpanel.html')
    >>> self.browser.url
    'http://nohost/plone/@@calendar-controlpanel.html'

Click the save button without making any changes:

    >>> self.browser.getControl(name="form.actions.save").click()
    >>> self.browser.url.endswith('calendar-controlpanel.html')
    True

We should get a status message:

    >>> 'No changes done.' in self.browser.contents
    True

Now click the cancel button:

    >>> self.browser.getControl(name="form.actions.cancel").click()
    >>> self.browser.url.endswith('calendar-controlpanel.html')
    True

There should be still no changes:

    >>> 'Changes canceled.' in self.browser.contents
    True

Make some changes
-----------------

    >>> self.browser.open('http://nohost/plone/@@calendar-controlpanel.html')
    >>> self.browser.url.endswith('calendar-controlpanel.html')
    True

    >>> self.browser.getControl(name='form.firstweekday').value = ['Sunday']
    >>> self.browser.getControl(name='form.calendar_types:list').value = ['Event', 'Page']

Click the save button:

    >>> self.browser.getControl(name="form.actions.save").click()
    >>> self.browser.url.endswith('calendar-controlpanel.html')
    True

We should be informed that something has changed:

    >>> 'Changes saved.' in self.browser.contents
    True

Make sure the changes have been applied correctly to the tool:

    >>> ctool.calendar_types
    ('Event', 'Document')

    >>> ctool.firstweekday
    6
