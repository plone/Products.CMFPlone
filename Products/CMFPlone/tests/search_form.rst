We want to test the search form and the resulting page.

Let's create a user to test upon
see: testControlPanelScripts.txt:
    >>> from DateTime import DateTime
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> app = layer['app']
    >>> portal = layer['portal']
    >>> fullname = 'Test User Full Name'
    >>> username = 'testuser'
    >>> email = 'test@plone.org'
    >>> last_login_time = DateTime()
    >>> membership = portal.portal_membership
    >>> membership.addMember(username, TEST_USER_PASSWORD, [], [])
    >>> member = membership.getMemberById(username)
    >>> member.setMemberProperties({'fullname': fullname, 'email': email,
    ...                             'last_login_time': last_login_time,})

Check the member's properties
    >>> props = membership.getMemberInfo(username)
    >>> props.get('fullname') == fullname
    True


Now we test the members' search form

    >>> import transaction; transaction.commit()
    >>> from plone.testing.zope import Browser
    >>> browser = Browser(app)
    >>> portal_url = portal.absolute_url()
    >>> logout_url = portal_url + '/logout'
    >>> login_url  = portal_url + '/login'
    >>> search_url = portal_url + '/@@search'
    >>> portal.error_log._ignored_exceptions = ()

Now we try to get a list of authors as Anonymous User
    >>> browser.open(logout_url)
    >>> '<h1 class="documentFirstHeading">You are now logged out</h1>' in browser.contents
    True
    >>> 'logged_out' in browser.url
    True
