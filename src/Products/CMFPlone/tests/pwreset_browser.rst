Functional tests for PasswordResetTool
======================================

Introduction
------------

Note that our usage of testbrowser is unusual and inconsistent, mostly
because Plone forms have inconsistencies and because testbrowser makes
assumptions that are not true for Plone forms.

  >>> from DateTime import DateTime
  >>> from plone.testing.zope import Browser
  >>> from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
  >>> browser = Browser(layer['app'])
  >>> from plone.registry.interfaces import IRegistry
  >>> from zope.component import getUtility
  >>> registry = getUtility(IRegistry, context=layer['portal'])

  >>> from plone.base.interfaces.controlpanel import IMailSchema
  >>> mail_settings = registry.forInterface(IMailSchema, prefix="plone")
  >>> mail_settings.smtp_host = u'localhost'
  >>> mail_settings.email_from_address = 'smith@example.com'
  >>> import transaction
  >>> transaction.commit()

Assumptions
-----------

First of all we have to be aware that Plone by default implements two
distinct password policies regarding member registration.

  A. Users can provide their own password (and can optionally be send
     an e-mail with login credentials) and can login directly without
     validation of the e-mail address.

  B. A password is generated for the users (and an e-mail with login
     credentials is sent automatically).

This policy can be enabled or disabled with the ``enable_user_pwd_choice``
setting in the security control panel.  By default ``enable_user_pwd_choice`` is
disabled and the second policy applies.

Another aspect we have to take into account is the fact that Plone by
default only allows Administrators to register (other) members, but allowing
users to register themselves can be enabled.

Users of PasswordResetTool don't want any credentials to be sent out
via e-mail.  Instead, PasswordResetTool sends out an e-mail containing
an URL where the user can set their password.

The PasswordResetTool has to respect both policies (A and B) and both
use cases (Anonymous or Admin?).  The desired result after installing
PasswordResetTool is as follows:

  1. Anonymous user registers himself

    A. Users can provide their own password during registration, but
       don't have the option to send credentials by e-mail.

    B. Users can't provide a password but are sent an e-mail with a
       link to set their password.  (Validates e-mail address.)

  2. Site Admin registers a user

    A. The Site Admin can provide a password.  He is not allowed to
       send the credentials via e-mail.

    B. The Site Admin can't provide a password.  Instead, Plone will
       send the registered user an e-mail with a link to set the
       password.  (Validates e-mail address.)

In addition, we want users to be logged in directly whenever possible.
E.g., whenever a user enters his credentials he should not be asked
for it again on the next page.


1A. User joins and forgets password
-----------------------------------

What we do here:

  - Join the portal
  - Log in
  - Log out again
  - Forget our password (this is where PasswordResetTool comes in)
  - Check if this is a soft reset (old password already works until changed)
  - Read the e-mail that contains the URL we visit to reset our password
  - Reset our password
  - Log in with our new password

Let's go directly to the security control panel:

  >>> from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
  >>> browser.addHeader('Authorization',
  ...                   'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD))
  >>> browser.open('http://nohost/plone/@@security-controlpanel')
  >>> ctrl = browser.getControl(name="form.widgets.enable_self_reg:list")
  >>> ctrl.value = ['selected']
  >>> ctrl = browser.getControl(name="form.widgets.enable_user_pwd_choice:list")
  >>> ctrl.value = ['selected']
  >>> browser.getControl("Save").click()

Let's join as a new user. Plone's default settings won't let the user
type in his initial password, so we need to enable that:

  >>> browser = Browser(layer['app'])
  >>> browser.open('http://nohost/plone/login')
  >>> browser.getLink('Log in').click()
  >>> browser.getControl(name='__ac_name').value = TEST_USER_NAME
  >>> browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
  >>> browser.getControl(name='buttons.login').click()
  >>> "You are now logged in" in browser.contents
  True

Log out again and then join:

  >>> browser.getLink('Log out').click()
  >>> "You are now logged out" in browser.contents
  True
  >>> 'Register' in browser.contents
  True

Now register a new user:

  >>> browser.open('http://nohost/plone/@@register')
  >>> browser.url
  'http://nohost/plone/@@register'

  >>> browser.getControl('User Name').value = 'jsmith'
  >>> browser.getControl('Email').value = 'jsmith@example.com'
  >>> browser.getControl('Password').value = TEST_USER_PASSWORD
  >>> browser.getControl('Confirm password').value = TEST_USER_PASSWORD
  >>> browser.getControl('Register').click()

XXX Make sure we don't have a way to receive our credentials via
e-mail.

  >>> "You have been registered" in browser.contents
  True

The login times are set to the default in 2000:

  >>> portal_membership = layer['portal'].portal_membership
  >>> member = portal_membership.getMemberById('jsmith')
  >>> login_time = member.getProperty('login_time')
  >>> isinstance(login_time, DateTime)
  True
  >>> login_time.Date()
  '2000/01/01'
  >>> last_login_time = member.getProperty('last_login_time')
  >>> isinstance(last_login_time, DateTime)
  True
  >>> last_login_time <= login_time
  True
  >>> last_login_time.Date()
  '2000/01/01'

We are not logged in yet at this point.  Let's try to log in:

  >>> browser.getLink('Log in').click()
  >>> browser.url.startswith('http://nohost/plone/login')
  True
  >>> browser.getControl(name='__ac_name').value = 'jsmith'
  >>> browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
  >>> browser.getControl(name='buttons.login').click()
  >>> "You are now logged in" in browser.contents
  True

Two login time properties should have been set on the user:

  >>> member = portal_membership.getMemberById('jsmith')
  >>> login_time = member.getProperty('login_time')
  >>> isinstance(login_time, DateTime)
  True
  >>> last_login_time = member.getProperty('last_login_time')
  >>> isinstance(last_login_time, DateTime)
  True
  >>> last_login_time <= login_time
  True

The default login time is January 1 2000.  Check that it is much newer now:

  >>> login_time > DateTime(2020, 2, 2)
  True
  >>> last_login_time > DateTime(2020, 2, 2)
  True

Log out again:

  >>> browser.getLink('Log out').click()
  >>> "You are now logged out" in browser.contents
  True

Now it is time to forget our password and click the ``Get help`` in the login form:

  >>> browser.open('http://nohost/plone/login')
  >>> browser.getLink('Get help').click()
  >>> browser.url.startswith('http://nohost/plone/@@login-help')
  True
  >>> form = browser.getForm(index=1)
  >>> form.getControl(name='form.widgets.reset_password').value = 'jsmith'
  >>> form.submit(name='form.buttons.reset')

We check if the old password still works.

  >>> browser.open('http://nohost/plone/login')
  >>> browser.getControl(name='__ac_name').value = 'jsmith'
  >>> browser.getControl(name='__ac_password').value = TEST_USER_PASSWORD
  >>> browser.getControl(name='buttons.login').click()

We should be logged in now:

  >>> "You are now logged in" in browser.contents
  True

Log out again:

  >>> browser.getLink('Log out').click()
  >>> "You are now logged out" in browser.contents
  True

As part of our test setup, we replaced the original MailHost with our
own version.  Our version doesn't mail messages, it just collects them
in a list called ``messages``:

  >>> mailhost = layer['portal'].MailHost
  >>> len(mailhost.messages)
  1
  >>> msg = mailhost.messages[0]

Now that we have the message, we want to look at its contents, and
then we extract the address that lets us reset our password:

  >>> import quopri
  >>> msg = quopri.decodestring(msg)
  >>> b"To: jsmith@example.com" in msg
  True
  >>> b"The site administrator asks you to reset your password for 'jsmith' userid" in msg
  False
  >>> please_visit_text = b"The following link will take you to a page where you can reset your password for Plone site site:"
  >>> please_visit_text in msg
  True
  >>> url_index = msg.index(please_visit_text) + len(please_visit_text)
  >>> address = msg[url_index:].strip().split()[0].decode()
  >>> address # doctest: +ELLIPSIS
  u'http://nohost/plone/passwordreset/...'
  >>> b"If you didn't expect to receive this email" in msg
  True

Save the current login times again so we can compare them after password reset.

  >>> member = portal_membership.getMemberById('jsmith')
  >>> login_time = member.getProperty('login_time')
  >>> last_login_time = member.getProperty('last_login_time')

Now that we have the address, we will reset our password:

  >>> browser.open(address)
  >>> "Set your password" in browser.contents
  True

  >>> form = browser.getForm(name='pwreset_action')
  >>> form.getControl(name='userid').value = 'jsmith'
  >>> form.getControl(name='password').value = 'secretion'
  >>> form.getControl(name='password2').value = 'secretion'
  >>> form.submit()

By default 'autologin_after_password_reset' is turned on, so we are now logged in:

  >>> "Password reset successful, you are logged in now!" in browser.contents
  True

The two login time properties should have been updated on the user:

  >>> member = portal_membership.getMemberById('jsmith')
  >>> login_time < member.getProperty('login_time')
  True
  >>> last_login_time < member.getProperty('last_login_time')
  True

The last login time is now set to the previous value of login time:

  >>> login_time == member.getProperty('last_login_time')
  True

Log out again:

  >>> browser.getLink('Log out').click()
  >>> "You are now logged out" in browser.contents
  True


2A. Administrator registers user
--------------------------------

  - Log in as the portal owner
  - Browse to User and Group Management and add user
  - Register a member (with send email checked???)
  - Log out
  - Log in as the new member
  - A manager resets a user password
  - Check if this is a hard reset (old password is changed)
  - Check the received mail

First, we want to login as the portal owner:

  >>> browser.open('http://nohost/plone/login')
  >>> browser.getControl(name='__ac_name').value = SITE_OWNER_NAME
  >>> browser.getControl(name='__ac_password').value = SITE_OWNER_PASSWORD
  >>> browser.getControl(name='buttons.login').click()
  >>> "You are now logged in" in browser.contents
  True

We navigate to the Users Add page and register a new user:

  >>> browser.open('http://nohost/plone/@@new-user')
  >>> browser.getControl('User Name').value = 'wsmith'
  >>> browser.getControl('Email').value = 'wsmith@example.com'
  >>> browser.getControl('Password').value = 'supersecret'
  >>> browser.getControl('Confirm password').value = 'supersecret'
  >>> browser.getControl('Register').click()
  >>> 'User added.' in browser.contents
  True

XXX Make sure we don't have a way to send the credentials via e-mail.

We want to logout and login as the new member:

  >>> browser.getLink('Log out').click()
  >>> browser.open('http://nohost/plone/login')
  >>> browser.getControl(name='__ac_name').value = 'wsmith'
  >>> browser.getControl(name='__ac_password').value = 'supersecret'
  >>> browser.getControl(name='buttons.login').click()
  >>> "You are now logged in" in browser.contents
  True

  >>> browser.getLink('Log out').click()

Again, we want to login as the portal owner:

  >>> browser.open('http://nohost/plone/login')
  >>> browser.getControl(name='__ac_name').value = SITE_OWNER_NAME
  >>> browser.getControl(name='__ac_password').value = SITE_OWNER_PASSWORD
  >>> browser.getControl(name='buttons.login').click()
  >>> "You are now logged in" in browser.contents
  True

We navigate to the Users Overview page and reset a password user:

  >>> browser.open('http://nohost/plone/@@usergroup-userprefs')
  >>> resets = browser.getControl(name='users.resetpassword:records')
  >>> reset = resets.getControl(value='wsmith')
  >>> reset.selected = True
  >>> browser.getControl(name="form.button.Modify").click()
  >>> "Changes applied." in browser.contents
  True
  >>> browser.getLink('Log out').click()
  >>> "You are now logged out" in browser.contents
  True

We check if the old password is well changed.

  >>> browser.open('http://nohost/plone/login')
  >>> browser.getControl(name='__ac_name').value = 'wsmith'
  >>> browser.getControl(name='__ac_password').value = 'supersecret'
  >>> browser.getControl(name='buttons.login').click()

We should not be logged in:

  >>> "Login failed" in browser.contents
  True

We should have received an e-mail at this point:

  >>> mailhost = layer['portal'].MailHost
  >>> len(mailhost.messages)
  2
  >>> import quopri
  >>> msg = quopri.decodestring(mailhost.messages[-1])
  >>> b"The site administrator asks you to reset your password for 'wsmith' userid" in msg
  True
  >>> please_visit_text = b"The following link will take you to a page where you can reset your password for Plone site site:"
  >>> please_visit_text in msg
  True
  >>> b"If you didn't expect to receive this email" in msg
  False


1B. User joins with e-mail validation enabled and forgets password
------------------------------------------------------------------

What we do here is quite similar to 1A, but instead of typing in the
password ourselves, we will be sent an e-mail with the URL to set our
password.

We will setup an adapter to capture IUserLoggedInEvent events:

  >>> from zope.component import adapter
  >>> from Products.PluggableAuthService.interfaces.events import IUserLoggedInEvent
  >>> from zope.component import getGlobalSiteManager
  >>> events_fired = []
  >>> @adapter(IUserLoggedInEvent)
  ... def got_user_logged_in_event(event):
  ...     events_fired.append(event)
  >>> gsm = getGlobalSiteManager()
  >>> gsm.registerHandler(got_user_logged_in_event)


First off, we need to set ``validate_mail`` to False:

  >>> browser.open('http://nohost/plone/login')
  >>> browser.getControl(name='__ac_name').value = SITE_OWNER_NAME
  >>> browser.getControl(name='__ac_password').value = SITE_OWNER_PASSWORD
  >>> browser.getControl(name='buttons.login').click()
  >>> "You are now logged in" in browser.contents
  True

Let's go directly to the security control panel:

  >>> browser.open('http://nohost/plone/@@security-controlpanel')
  >>> ctrl = browser.getControl("Let users select their own passwords")
  >>> ctrl.selected = False
  >>> browser.getControl('Save').click()

Log out again and then join:

  >>> browser.getLink('Log out').click()
  >>> "You are now logged out" in browser.contents
  True
  >>> browser.open('http://nohost/plone/@@register')
  >>> browser.getControl('User Name').value = 'bsmith'
  >>> browser.getControl('Email').value = 'bsmith@example.com'

We shouldn't be able to fill in our password:

  >>> browser.getControl('Password').value = TEST_USER_PASSWORD # doctest: +ELLIPSIS
  Traceback (most recent call last):
  ...
  LookupError: label 'Password'
  ...

Now register:

  >>> browser.getControl('Register').click()
  >>> "You have been registered" in browser.contents
  True

We should have received an e-mail at this point:

  >>> mailhost = layer['portal'].MailHost
  >>> len(mailhost.messages)
  3
  >>> msg = mailhost.messages[-1]

Let's clear the events storage:

  >>> events_fired = []

Now that we have the message, we want to look at its contents, and
then we extract the address that lets us reset our password:

  >>> from email.parser import Parser
  >>> import re
  >>> parser = Parser()
  >>> message = parser.parsestr(msg.decode("utf-8"))
  >>> message["To"]
  'bsmith@example.com'
  >>> msgtext = quopri.decodestring(message.get_payload())
  >>> b"Please activate it by visiting" in msgtext
  True

We need to be careful to keep this working in both Python 2 and 3 without invalid escape sequences.
It is best to convert msgtext to text first.

  >>> msgtext = msgtext.decode()
  >>> address = re.search(r'(http://nohost/plone/passwordreset/[a-z0-9]+\?userid=[\w]*)\s', msgtext).groups()[0]

Now that we have the address, we will reset our password:

  >>> browser.open(address)
  >>> "Please fill out the form below to set your password" in browser.contents
  True
  >>> browser.getControl(name='userid').value = 'bsmith'
  >>> browser.getControl(name='password').value = TEST_USER_PASSWORD
  >>> browser.getControl(name='password2').value = TEST_USER_PASSWORD
  >>> browser.getControl("Set my password").click()
  >>> "Password reset successful, you are logged in now!" in browser.contents
  True

User is logged in, let's check the event fired for the correct user:

  >>> len(events_fired) == 1
  True
  >>> events_fired[0].principal
  <PloneUser 'bsmith'>

Log out again:

  >>> browser.getLink('Log out').click()
  >>> "You are now logged out" in browser.contents
  True

Remove got_user_logged_in_event registration:

  >>> gsm.unregisterHandler(got_user_logged_in_event)
  True


2B. Administrator adds user with email validation enabled
---------------------------------------------------------

Similar to 2A, but instead of setting the password for new member, an
e-mail is sent containing the URL that lets the user log in.

First, we want to login as the portal owner:

  >>> from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
  >>> browser.open('http://nohost/plone/login')
  >>> browser.getControl(name='__ac_name').value = SITE_OWNER_NAME
  >>> browser.getControl(name='__ac_password').value = SITE_OWNER_PASSWORD
  >>> browser.getControl(name='buttons.login').click()
  >>> "You are now logged in" in browser.contents
  True

We navigate to the Users Adding page and register a new user:

  >>> browser.open('http://nohost/plone/@@new-user')
  >>> browser.getControl('User Name').value = 'wwwsmith'
  >>> browser.getControl('Email').value = 'wwwsmith@example.com'
  >>> browser.getControl('Password').value = TEST_USER_PASSWORD
  >>> browser.getControl('Confirm password').value = TEST_USER_PASSWORD
  >>> browser.getControl('Send a confirmation mail with a link to set the password').selected = True

Now register and logout:

  >>> browser.getControl('Register').click()
  >>> browser.getLink('Log out').click()
  >>> "You are now logged out" in browser.contents
  True

We should have received an e-mail at this point:

  >>> mailhost = layer['portal'].MailHost
  >>> len(mailhost.messages)
  4
  >>> msg = mailhost.messages[-1]

Now that we have the message, we want to look at its contents, and
then we extract the address that lets us reset our password:

  >>> message = parser.parsestr(msg.decode("utf-8"))
  >>> message["To"]
  'wwwsmith@example.com'
  >>> msgtext = quopri.decodestring(message.get_payload())
  >>> b"Please activate it by visiting" in msgtext
  True
  >>> msgtext = msgtext.decode()
  >>> address = re.search(r'(http://nohost/plone/passwordreset/[a-z0-9]+\?userid=[\w]*)\s', msgtext).groups()[0]

Now that we have the address, we will reset our password:

  >>> browser.open(address)
  >>> "Please fill out the form below to set your password" in browser.contents
  True
  >>> browser.getControl(name='userid').value = 'wwwsmith'
  >>> browser.getControl(name='password').value = 'superstr0ng'
  >>> browser.getControl(name='password2').value = 'superstr0ng'
  >>> browser.getControl("Set my password").click()
  >>> "Password reset successful, you are logged in now!" in browser.contents
  True

Log out

  >>> browser.getLink('Log out').click()

Test passwordreset BrowserView

    Setup Plone email sender

    >>> portal = layer['portal']
    >>> mail_settings.email_from_name = u'Old\u0159ich a Bo\u017eena'
    >>> from plone.base.interfaces.controlpanel import ISiteSchema
    >>> site_settings = registry.forInterface(ISiteSchema, prefix='plone')
    >>> site_settings.site_title = u'Koko\u0159\xedn Portal'

    Check view methods

    >>> view = portal.restrictedTraverse('@@mail_password_template')
    >>> view.encoded_mail_sender()
    '"=?utf-8?q?Old=C5=99ich_a_Bo=C5=BEena?=" <smith@example.com>'

    >>> view.registered_notify_subject()
    u'User Account Information for Koko\u0159\xedn Portal'

    >>> view.mail_password_subject()
    u'Password reset request'
