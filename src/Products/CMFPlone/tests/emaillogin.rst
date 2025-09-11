Email login
===========

Instead of the normal userid or login name, you can let Plone use the
email address of the user as login id. If the email address is changed,
so is the login name. Of course, this email address will have to be
unique across the site.

Some bootstrapping::

    >>> from plone.testing.zope import Browser
    >>> app = layer['app']
    >>> portal = layer['portal']
    >>> browser = Browser(app)

First we login as admin::

    >>> from plone.app.testing import SITE_OWNER_NAME
    >>> from plone.app.testing import SITE_OWNER_PASSWORD
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> browser.open('http://nohost/plone/login')
    >>> browser.getControl(name='__ac_name').value = SITE_OWNER_NAME
    >>> browser.getControl(name='__ac_password').value = SITE_OWNER_PASSWORD
    >>> browser.getControl('Log in').click()

Now we allow users to register themselves. We also allow them to pick
their own passwords to ease testing::

    >>> browser.open('http://nohost/plone/@@security-controlpanel')
    >>> browser.getControl(name='form.widgets.enable_self_reg:list').value = True
    >>> browser.getControl(name='form.widgets.enable_user_pwd_choice:list').value = True
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

We logout::

    >>> browser.open('http://nohost/plone/logout')


Registration
------------

We then visit the registration form. We can fill in a user name
there::

    >>> browser.open('http://nohost/plone/@@register')
    >>> browser.getControl('User Name').value='username'
    >>> browser.getControl('Email').value='username@example.org'
    >>> browser.getControl('Password').value = TEST_USER_PASSWORD
    >>> browser.getControl('Confirm password').value = TEST_USER_PASSWORD
    >>> browser.getControl('Register').click()
    >>> 'You have been registered.' in browser.contents
    True

So that still works. Now we become admin again::

    >>> browser.open('http://nohost/plone/login')
    >>> browser.getControl(name='__ac_name').value = SITE_OWNER_NAME
    >>> browser.getControl(name='__ac_password').value = SITE_OWNER_PASSWORD
    >>> browser.getControl('Log in').click()

We switch on using the email address as login name::

    >>> browser.open('http://nohost/plone/@@security-controlpanel')
    >>> browser.getControl(name='form.widgets.use_email_as_login:list').value = ['selected']
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True
    >>> browser.open('http://nohost/plone/logout')

Now we visit the registration form. The user name field is no longer
there::

    >>> browser.open('http://nohost/plone/@@register')
    >>> browser.getControl('User Name')
    Traceback (most recent call last):
    ...
    LookupError: label 'User Name'...

We fill in the rest of the form::

    >>> browser.getControl('Email').value='email@example.org'
    >>> browser.getControl('Password').value = TEST_USER_PASSWORD
    >>> browser.getControl('Confirm password').value = TEST_USER_PASSWORD
    >>> browser.getControl('Register').click()
    >>> 'You have been registered.' in browser.contents
    True


Login
-----

We can now login with this email address::

    >>> browser.open('http://nohost/plone/login')
    >>> browser.getControl(name='__ac_name').value = 'email@example.org'
    >>> browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
    >>> browser.getControl('Log in').click()
    >>> 'You are now logged in' in browser.contents
    True

Due to some subtlety the message 'You are now logged in' can appear in
the browser even when the user is not actually logged in: the text
'Log in' still appears and no link to the user's dashboard is
available. Or even more subtle: that text and that link are there,
but visiting another page will show that the user does not remain
logged it. This test should be enough::

    >>> browser.open('http://nohost/plone')
    >>> 'Log in' in browser.contents
    False
    >>> browser.open('http://nohost/plone/logout')

The first registered user might still be able to login with his
non-email login name, but cannot login with his email address, as his
account was created before the policy to use emails as logins was
used. A future Plone version may solve that automatically. For now,
this can be remedied by running the provided migration::

    >>> from zope.component import getMultiAdapter
    >>> migrationView = getMultiAdapter((portal, portal.REQUEST), name='migrate-to-emaillogin')
    >>> result = migrationView.switch_to_email()
    >>> import transaction; transaction.commit()

Now we try logging out and in again with the given email address::

    >>> browser.open('http://nohost/plone/logout')
    >>> browser.open('http://nohost/plone/login')
    >>> browser.getControl(name='__ac_name').value = 'username@example.org'
    >>> browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
    >>> browser.getControl('Log in').click()
    >>> browser.open('http://nohost/plone')
    >>> 'Log in' in browser.contents
    False

Logging in with the initial user name no longer works.
This may be fixable by changing PluggableAuthService if we
want. (See PLIP9214 notes.)


Changing the email address
--------------------------

We again log in as the user created after using email as login was
switched on::

    >>> browser.open('http://nohost/plone/login')
    >>> browser.getControl(name='__ac_name').value = 'email@example.org'
    >>> browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
    >>> browser.getControl('Log in').click()
    >>> browser.open('http://nohost/plone')
    >>> 'Log in' in browser.contents
    False

We change the email address::

    >>> browser.open('http://nohost/plone/@@personal-information')
    >>> browser.getControl('Email').value = 'email2@example.org'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved.' in browser.contents
    True
    >>> browser.getControl('Email').value
    'email2@example.org'

After those two changes, we can no longer login with our first email
address. This may be fixable by changing PluggableAuthService if we
want. (See PLIP9214 notes.)::

    >>> browser.open('http://nohost/plone/logout')
    >>> browser.open('http://nohost/plone/login')
    >>> browser.getControl(name='__ac_name').value = 'email1@example.org'
    >>> browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
    >>> browser.getControl('Log in').click()
    >>> 'Login failed' in browser.contents
    True

The current email address of course works fine for logging in::

    >>> browser.open('http://nohost/plone/logout')
    >>> browser.open('http://nohost/plone/login')
    >>> browser.getControl(name='__ac_name').value = 'email2@example.org'
    >>> browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
    >>> browser.getControl('Log in').click()
    >>> browser.open('http://nohost/plone')
    >>> 'Log in' in browser.contents
    False

Picking the e-mail address of another user should of course fail::

    >>> browser.open('http://nohost/plone/@@personal-information')
    >>> browser.getControl('Email').value = 'username@example.org'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved.' in browser.contents
    False
    >>> browser.open('http://nohost/plone/logout')

Resetting the password
----------------------

These tests are partly copied from... PasswordResetTool. (surprise!)

Now it is time to forget our password and click the ``Forgot your password`` link in the login form.
This should work by just filling in our current email address::

    >>> browser.open('http://nohost/plone/login')
    >>> browser.getLink('Get help').click()
    >>> browser.url.startswith('http://nohost/plone/@@login-help')
    True
    >>> form = browser.getForm(index=1)
    >>> form.getControl(name='form.widgets.reset_password').value = 'email2@example.org'
    >>> form.getControl('Reset your password').click()
    >>> 'An email has been sent with instructions on how to reset your password.' in browser.contents
    True

As part of our test setup, we replaced the original MailHost with our
own version. Our version doesn't mail messages, it just collects them
in a list called ``messages``::

    >>> mailhost = portal.MailHost
    >>> len(mailhost.messages)
    1
    >>> msg = mailhost.messages[0]

Now that we have the message, we want to look at its contents, and
then we extract the address that lets us reset our password::

    >>> b"To: email2@example.org" in msg
    True

Now get the link::

    >>> import quopri
    >>> msg = quopri.decodestring(msg)
    >>> url_index = msg.index(b'http://nohost/plone/passwordreset/')
    >>> address = msg[url_index:].split()[0].decode()

Now that we have the address, we will reset our password::

    >>> browser.open(address)
    >>> "Set your password" in browser.contents
    True
    >>> form = browser.getForm(name='pwreset_action')
    >>> form.getControl(name='userid').value = 'email2@example.org'
    >>> form.getControl(name='password').value = 'secretion'
    >>> form.getControl(name='password2').value = 'secretion'
    >>> form.submit()
    >>> "Password reset successful, you are logged in now!" in browser.contents
    True

Logout and continue with first user:

    >>> browser.open('http://nohost/plone/logout')

The first user can still reset his password with his user id::

    >>> browser.open('http://nohost/plone/mail_password_form')
    >>> form = browser.getForm(name='mail_password')
    >>> form.getControl(name='userid').value = 'username'
    >>> form.getControl('Start password reset').click()
    >>> 'Password reset confirmation sent' in browser.contents
    True

The email is sent to the correct email address::

    >>> len(mailhost.messages)
    2
    >>> msg = mailhost.messages[-1]
    >>> b"To: username@example.org" in msg
    True

Now get the link::

    >>> msg = quopri.decodestring(msg)
    >>> url_index = msg.index(b'http://nohost/plone/passwordreset/')
    >>> address = msg[url_index:].split()[0].decode()

Now that we have the address, we will reset our password::

    >>> browser.open(address)
    >>> "Set your password" in browser.contents
    True
    >>> form = browser.getForm(name='pwreset_action')
    >>> form.getControl(name='userid').value = 'username'
    >>> form.getControl(name='password').value = 'secretion'
    >>> form.getControl(name='password2').value = 'secretion'
    >>> form.submit()
    >>> "Password reset successful, you are logged in now!" in browser.contents
    True
