"""PasswordResetTool.py

Mailback password reset product for CMF.
Author: J Cameron Cooper, Sept 2003
"""
from hashlib import md5

from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from OFS.SimpleItem import SimpleItem
from App.class_init import InitializeClass
from App.special_dtml import DTMLFile
from AccessControl import ClassSecurityInfo
from AccessControl import ModuleSecurityInfo
from plone.registry.interfaces import IRegistry
from Products.CMFCore.permissions import ManagePortal
from Products.CMFPlone.interfaces import IPWResetTool
from Products.CMFPlone.interfaces import ISecuritySchema
from Products.CMFPlone.RegistrationTool import get_member_by_login_name
from Products.CMFPlone import django_random


import datetime
import time
import socket
from DateTime import DateTime
from zope.component import getUtility
from zope.interface import implementer

module_security = ModuleSecurityInfo('Products.PasswordResetTool.PasswordResetTool')

module_security.declarePublic('InvalidRequestError')


class InvalidRequestError(Exception):
    def __init__(self, value=''):
        self.value = value

    def __str__(self):
        return repr(self.value)

module_security.declarePublic('ExpiredRequestError')


class ExpiredRequestError(Exception):
    def __init__(self, value=''):
        self.value = value

    def __str__(self):
        return repr(self.value)


@implementer(IPWResetTool)
class PasswordResetTool (UniqueObject, SimpleItem):
    """Provides a default implementation for a password reset scheme.

    From a 'forgotten password' template, you submit your username to
    a handler script that does a 'requestReset', and sends an email
    with an unguessable unique hash in a url as built by 'constructURL'
    to the user.

    The user visits that URL (the 'reset form') and enters their username,
    """

    id = 'portal_password_reset'
    meta_type = 'Password Reset Tool'

    security = ClassSecurityInfo()

    manage_options = (({'label': 'Overview'
                        , 'action': 'manage_overview'
                        },
                      ) + SimpleItem.manage_options
                    )

    ##   ZMI methods
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = DTMLFile('dtml/explainPWResetTool', globals())

    security.declareProtected(ManagePortal, 'manage_setTimeout')

    def manage_setTimeout(self, hours=168, REQUEST=None):
        """ZMI method for setting the expiration timeout in hours."""
        self.setExpirationTimeout(int(hours))
        return self.manage_overview(manage_tabs_message="Timeout set to %s hours" % hours)

    security.declareProtected(ManagePortal, 'manage_toggleUserCheck')

    def manage_toggleUserCheck(self, REQUEST=None):
        """ZMI method for toggling the flag for checking user names on return.
        """
        self.toggleUserCheck()
        m = self.checkUser() and 'on' or 'off'
        return self.manage_overview(manage_tabs_message="Returning username check turned %s" % m)

    def __init__(self):
        self._requests = {}

    ## Internal attributes
    _user_check = 1
    _timedelta = 168  # misleading name, the number of hours are actually stored as int

    ## Interface fulfillment ##
    security.declareProtected(ManagePortal, 'requestReset')

    def requestReset(self, userid):
        """Ask the system to start the password reset procedure for
        user 'userid'.

        Returns a dictionary with the random string that must be
        used to reset the password in 'randomstring', the expiration date
        as a DateTime in 'expires', and the userid (for convenience) in
        'userid'. Returns None if no such user.
        """
        if not self.getValidUser(userid):
            return None
        randomstring = self.uniqueString(userid)
        expiry = self.expirationDate()
        self._requests[randomstring] = (userid, expiry)

        self.clearExpired(10)   # clear out untouched records more than 10 days old
        # this is a cheap sort of "automatic" clearing
        self._p_changed = 1

        retval = {}
        retval['randomstring'] = randomstring
        retval['expires'] = expiry
        retval['userid'] = userid
        return retval

    security.declarePublic('resetPassword')

    def resetPassword(self, userid, randomstring, password):
        """Set the password (in 'password') for the user who maps to
        the string in 'randomstring' iff the entered 'userid' is equal
        to the mapped userid. (This can be turned off with the
        'toggleUserCheck' method.)

        Note that this method will *not* check password validity: this
        must be done by the caller.

        Throws an 'ExpiredRequestError' if request is expired.
        Throws an 'InvalidRequestError' if no such record exists,
        or 'userid' is not in the record.
        """
        if get_member_by_login_name:
            found_member = get_member_by_login_name(
                self, userid, raise_exceptions=False)
            if found_member is not None:
                userid = found_member.getId()
        try:
            stored_user, expiry = self._requests[randomstring]
        except KeyError:
            raise InvalidRequestError

        if self.checkUser() and (userid != stored_user):
            raise InvalidRequestError
        if self.expired(expiry):
            del self._requests[randomstring]
            self._p_changed = 1
            raise ExpiredRequestError

        member = self.getValidUser(stored_user)
        if not member:
            raise InvalidRequestError

        # actually change password
        user = member.getUser()
        uf = getToolByName(self, 'acl_users')
        if getattr(uf, 'userSetPassword', None) is not None:
            uf.userSetPassword(user.getUserId(), password)  # GRUF 3
        else:
            try:
                user.changePassword(password)  # GRUF 2
            except AttributeError:
                # this sets __ directly (via MemberDataTool) which is the usual
                # (and stupid!) way to change a password in Zope
                member.setSecurityProfile(password=password)

        member.setMemberProperties(dict(must_change_password=0))

        # clean out the request
        del self._requests[randomstring]
        self._p_changed = 1
    ## Implementation ##

    # external

    security.declareProtected(ManagePortal, 'setExpirationTimeout')

    def setExpirationTimeout(self, timedelta):
        """Set the length of time a reset request will be valid.

        Takes a 'datetime.timedelta' object (if available, since it's
        new in Python 2.3) or a number of hours, possibly
        fractional. Since a negative delta makes no sense, the
        timedelta's absolute value will be used."""
        self._timedelta = abs(timedelta)

    security.declarePublic('getExpirationTimeout')

    def getExpirationTimeout(self):
        """Get the length of time a reset request will be valid.

        In hours, possibly fractional. Ignores seconds and shorter."""
        try:
            if isinstance(self._timedelta, datetime.timedelta):
                return self._timedelta.days * 24
        except NameError:
            pass  # that's okay, it must be a number of hours...
        return self._timedelta

    security.declareProtected(ManagePortal, 'toggleUserCheck')

    def toggleUserCheck(self):
        """Changes whether or not the tool requires someone to give the uerid
        they're trying to change on a 'password reset' page. Highly recommended
        to LEAVE THIS ON."""
        if not hasattr(self, '_user_check'):
            self._user_check = 1

        self._user_check = not self._user_check

    security.declarePublic('checkUser')

    def checkUser(self):
        """Returns a boolean representing the state of 'user check' as described
        in 'toggleUserCheck'. True means on, and is the default."""
        if not hasattr(self, '_user_check'):
            self._user_check = 1

        return self._user_check

    security.declarePublic('verifyKey')

    def verifyKey(self, key):
        """Verify a key. Raises an exception if the key is invalid or expired.
        """
        try:
            u, expiry = self._requests[key]
        except KeyError:
            raise InvalidRequestError

        if self.expired(expiry):
            raise ExpiredRequestError

        if not self.getValidUser(u):
            raise InvalidRequestError('No such user')

    security.declareProtected(ManagePortal, 'getStats')

    def getStats(self):
        """Return a dictionary like so:
            {"open":3, "expired":0}
        about the number of open and expired reset requests.
        """
        good = 0
        bad = 0
        for stored_user, expiry in self._requests.values():
            if self.expired(expiry):
                bad += 1
            else:
                good += 1

        return {"open": good, "expired": bad}

    security.declarePrivate('clearExpired')

    def clearExpired(self, days=0):
        """Destroys all expired reset request records.
        Parameter controls how many days past expired it must be to disappear.
        """
        for key, record in self._requests.items():
            stored_user, expiry = record
            if self.expired(expiry, DateTime() - days):
                del self._requests[key]
                self._p_changed = 1
    # customization points

    security.declarePrivate('uniqueString')

    def uniqueString(self, userid):
        """Returns a string that is random and unguessable, or at
        least as close as possible.

        This is used by 'requestReset' to generate the auth
        string. Override if you wish different format.

        This implementation ignores userid and simply generates a
        UUID. That parameter is for convenience of extenders, and
        will be passed properly in the default implementation."""
        # this is the informal UUID algorithm of
        # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/213761
        # by Carl Free Jr
        t = long(time.time() * 1000)
        r = django_random.get_random_string(64)
        try:
            a = socket.gethostbyname(socket.gethostname())
        except:
            # if we can't get a network address, just imagine one
            a = django_random.get_random_string(64)
        data = str(t) + ' ' + str(r) + ' ' + str(a)
        data = md5(data).hexdigest()
        return str(data)

    security.declarePrivate('expirationDate')

    def expirationDate(self):
        """Returns a DateTime for exipiry of a request from the
        current time.

        This is used by housekeeping methods (like clearEpired)
        and stored in reset request records."""
        if not hasattr(self, '_timedelta'):
            self._timedelta = 168
        if isinstance(self._timedelta, datetime.timedelta):
            expire = datetime.datetime.utcnow() + self._timedelta
            return DateTime(expire.year,
                            expire.month,
                            expire.day,
                            expire.hour,
                            expire.minute,
                            expire.second,
                            'UTC')
        expire = time.time() + self._timedelta * 3600  # 60 min/hr * 60 sec/min
        return DateTime(expire)

    security.declarePrivate('getValidUser')

    def getValidUser(self, userid):
        """Returns the member with 'userid' if available and None otherwise."""
        if get_member_by_login_name:
            registry = getUtility(IRegistry)
            settings = registry.forInterface(ISecuritySchema, prefix='plone')

            if settings.use_email_as_login:
                return get_member_by_login_name(
                    self, userid, raise_exceptions=False)
        membertool = getToolByName(self, 'portal_membership')
        return membertool.getMemberById(userid)
    # internal

    security.declarePrivate('expired')

    def expired(self, datetime, now=None):
        """Tells whether a DateTime or timestamp 'datetime' is expired
        with regards to either 'now', if provided, or the current
        time."""
        if not now:
            now = DateTime()
        return now.greaterThanEqualTo(datetime)

InitializeClass(PasswordResetTool)
