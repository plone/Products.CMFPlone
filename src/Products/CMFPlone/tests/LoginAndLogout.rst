Logging in and out
==================

A very simple and underdocumented testbrowser test.  This is all about
logging in and out.

    >>> from plone.testing.zope import Browser
    >>> from plone.testing.zope import login
    >>> from plone.testing.zope import logout
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import SITE_OWNER_NAME
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_NAME
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> import transaction
    >>> app = layer['app']
    >>> portal = layer['portal']
    >>> setRoles(portal, TEST_USER_ID, ['Manager'])
    >>> transaction.commit()
    >>> browser = Browser(app)

Using the Login Form
--------------------

First we try to log in with bad credentials:

    >>> browser.open('http://nohost/plone/login')
    >>> browser.getLink('Log in').click()
    >>> browser.url
    'http://nohost/plone/login'
    >>> browser.getControl('Login Name').value = TEST_USER_NAME
    >>> browser.getControl('Password').value = 'wrongpassword'
    >>> browser.getControl('Log in').click()
    >>> "Login failed" in browser.contents
    True
    >>> browser.url
    'http://nohost/plone/login_form'

And then we try again with the right credentials:

    >>> browser.open('http://nohost/plone/login')
    >>> browser.getLink('Log in').click()
    >>> browser.url
    'http://nohost/plone/login'
    >>> browser.getControl('Login Name').value = TEST_USER_NAME
    >>> browser.getControl('Password').value = TEST_USER_PASSWORD
    >>> browser.getControl('Log in').click()
    >>> "You are now logged in" in browser.contents
    True
    >>> browser.url
    'http://nohost/plone/login_form'
    >>> browser.getLink('Log out').click()
    >>> browser.url
    'http://nohost/plone/logged_out'

Using the Login Portlet
-----------------------

Let's first add the login portlet

    >>> login(app['acl_users'], SITE_OWNER_NAME)
    >>> from zope.component import getUtility
    >>> from plone.portlets.interfaces import IPortletType
    >>> portlet = getUtility(IPortletType, name='portlets.Login')
    >>> mapping = portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
    >>> addview = mapping.restrictedTraverse('+/' + portlet.addview)
    >>> addview()
    ''
    >>> logout()
    >>> transaction.commit()

First we try to log in with bad credentials:

    >>> browser.getLink('Home').click()
    >>> browser.url
    'http://nohost/plone'
    >>> browser.getControl('Login Name').value = TEST_USER_NAME
    >>> browser.getControl('Password').value = 'wrongpassword'
    >>> browser.getControl('Log in').click()
    >>> "Login failed" in browser.contents
    True
    >>> browser.url
    'http://nohost/plone/login_form'

And then we try again with the right credentials:

    >>> browser.getLink('Home').click()
    >>> browser.url
    'http://nohost/plone'
    >>> browser.getControl('Login Name').value = TEST_USER_NAME
    >>> browser.getControl('Password').value = TEST_USER_PASSWORD
    >>> browser.getControl('Log in').click()

Verify that we are given a status message saying we've logged in:

    >>> 'You are now logged in' in browser.contents
    True

    The returned view is the default view of the current context:

    >>> browser.url
    'http://nohost/plone'

Let's reload the page and then try logging out:

    >>> browser.reload()
    >>> browser.getLink('Log out').click()
    >>> 'You are now logged out' in browser.contents
    True

Login with user defined in root user folder
-------------------------------------------

A user defined in the root user folder should be able to log in into
the site:

    >>> browser.getLink('Home').click()
    >>> app.acl_users.userFolderAddUser('rootuser', TEST_USER_PASSWORD, [], [])
    >>> transaction.commit()
    >>> browser.open('http://nohost/plone/login_form')
    >>> browser.getControl('Login Name').value = 'rootuser'
    >>> browser.getControl('Password').value = TEST_USER_PASSWORD
    >>> browser.getControl('Log in').click()
    >>> 'You are now logged in' in browser.contents
    True

Redirection to login page on unauthorized exception
---------------------------------------------------

Let's logout again and then try viewing folder contents page
of test_user_1_:

    >>> browser.reload()
    >>> browser.getLink('Log out').click()
    >>> browser.open('http://nohost/plone/folder_contents')
    >>> 'require_login' in browser.url
    True

    >>> browser.getControl('Login Name').value = TEST_USER_NAME
    >>> browser.getControl('Password').value = TEST_USER_PASSWORD
    >>> browser.getControl('Log in').click()
    >>> browser.open('http://nohost/plone')
    >>> browser.getLink('Contents').click()
    >>> browser.url
    'http://nohost/plone/folder_contents...'

We were automatically redirected to the page that triggered the
login request.

Note that we may end up at atct_edit instead of edit. This happens
because the CMFCore DynamicType before-publish-traversal hook resolves
method aliases and updates the request.

Test must_change_password
-------------------------

Start with a fresh testbrowser

    >>> browser = Browser(app)
    >>> browser.open('http://nohost/plone/')

Configure must_change_password (not enabled by default).

    >>> memberdata = portal.portal_memberdata
    >>> memberdata.manage_addProperty('must_change_password', True, 'boolean')
    >>> member = portal.portal_membership.getMemberById(TEST_USER_ID)

We want to make sure that the property "must_change_password" was properly
configured.

    >>> member.setMemberProperties(dict(must_change_password=1))
    >>> member.getProperty('must_change_password')
    1

Try to login.

    >>> transaction.commit()
    >>> browser.getLink('Log in').click()
    >>> browser.url
    'http://nohost/plone/login'
    >>> browser.getControl('Login Name').value = TEST_USER_NAME
    >>> browser.getControl('Password').value = TEST_USER_PASSWORD
    >>> browser.getControl('Log in').click()
    >>> "You are now logged in" in browser.contents
    False

The user should receive a message asking them to change their password.

    >>> browser.url
    'http://nohost/plone/login_form'
    >>> 'Please use the form below to change your password.' in browser.contents
    True
    >>> browser.getControl(name='password').value = 'Testing23'
    >>> browser.getControl(name='confirm').value = 'Testing23'
    >>> browser.getControl(name='submit').click()

In the past this error message would come up erroneously.

    >>> 'You must enable cookies before you can log in.' in browser.contents
    False

After submitting the password change the user is now logged in.

    >>> 'Plone site' in browser.contents
    True

Reload the page so we can ensure the login sticks around.  There was problem
in the past where the cookie did not persist on the client side.

    >>> browser.reload()
    >>> 'Plone site' in browser.contents
    True

Logout.  This would fail if the user lost their login session for example.

    >>> browser.getLink('Log out').click()
    >>> browser.url
    'http://nohost/plone/logged_out'
