Test form links against different navigation roots
--------------------------------------------------

Links that are present within each of the forms should adhere to 
the current navigation root for the site.

    >>> from Products.Five.utilities.marker import mark
    >>> from plone.app.layout.navigation.interfaces import INavigationRoot

We'll create the test context and have the relevant navigation root marker
interface ready to be applied:

    >>> self.loginAsPortalOwner()
    >>> self.portal.invokeFactory('Folder', id='folder_navroot', title="Navroot")
    'folder_navroot'


So let's login as Plone admin:
    >>> self.browser.open('http://nohost/plone/')
    >>> self.browser.getLink('Log in').click()
    >>> self.browser.getControl('Login Name').value = 'admin'
    >>> self.browser.getControl('Password').value = 'secret'
    >>> self.browser.getControl('Log in').click()

Let's see if we can navigate to the user information and options forms
in the 'Users and Groups' settings. Each of the 3 forms all use the
same base class so if the fix works on one, it works on them all.

    >>> self.browser.getLink('Navroot').click()

    >>> self.browser.getLink('Preferences').click()
    >>> self.browser.url
    'http://nohost/plone/@@personal-preferences'

Check the existance and links for a standard site context (navigation root
is the Plone site itself since the marker interface isn't applied here 
yet).

    >>> self.browser.getLink('Personal Information').url
    'http://nohost/plone/@@personal-information'
    >>> self.browser.getLink('Personal Preferences').url
    'http://nohost/plone/@@personal-preferences'

Now, let's mark this folder and see what happens.  All links should
now be rooted to the given folder and not the Plone site proper.
 
    >>> mark(self.portal.folder_navroot, INavigationRoot)

    >>> self.browser.getLink('Navroot').click()

    >>> self.browser.getLink('Preferences').click()
    >>> self.browser.url
    'http://nohost/plone/folder_navroot/@@personal-preferences'

    >>> self.browser.getLink('Personal Information').url
    'http://nohost/plone/folder_navroot/@@personal-information'
    >>> self.browser.getLink('Personal Preferences').url
    'http://nohost/plone/folder_navroot/@@personal-preferences'


