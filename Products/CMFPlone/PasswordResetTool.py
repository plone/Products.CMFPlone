"""PasswordResetTool.py

Mailback password reset product for CMF.
Author: J Cameron Cooper, Sept 2003
"""
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from OFS.SimpleItem import SimpleItem
from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl import ModuleSecurityInfo
from BTrees.OOBTree import OOBTree
from plone.uuid.interfaces import IUUIDGenerator
from plone.registry.interfaces import IRegistry
from Products.CMFCore.permissions import ManagePortal
from Products.CMFPlone.interfaces import IPWResetTool
from Products.CMFPlone.interfaces import ISecuritySchema
from Products.CMFPlone.RegistrationTool import get_member_by_login_name

import datetime
from zope.component import getUtility
from zope.interface import implementer

module_security = ModuleSecurityInfo('Products.CMFPlone.PasswordResetTool')

module_security.declarePublic('InvalidRequestError')
class InvalidRequestError(Exception):
    """ Request reset URL is invalid """
    def __init__(self, value=''):
        self.value = value

    def __str__(self):
        return repr(self.value)

module_security.declarePublic('ExpiredRequestError')
class ExpiredRequestError(InvalidRequestError):
    """ Request reset URL is expired """


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

    def __init__(self):
        self._requests = OOBTree()

    ## Internal attributes
    _user_check = True
    _timedelta = 7   # DAYS

    ## Interface fulfillment ##
    security.declareProtected(ManagePortal, 'requestReset')

    def requestReset(self, userid):
        """Ask the system to start the password reset procedure for
        user 'userid'.

        Returns a dictionary with the random string that must be
        used to reset the password in 'randomstring', the expiration date
        as a datetime in 'expires', and the userid (for convenience) in
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
        uf.userSetPassword(user.getUserId(), password)
        member.setMemberProperties(dict(must_change_password=0))

        # clean out the request
        del self._requests[randomstring]
        self._p_changed = 1
    ## Implementation ##

    # external

    security.declareProtected(ManagePortal, 'setExpirationTimeout')

    def setExpirationTimeout(self, timedelta):
        """Set the length of time a reset request will be valid in days.
        """
        self._timedelta = abs(timedelta)

    security.declarePublic('getExpirationTimeout')

    def getExpirationTimeout(self):
        """Get the length of time a reset request will be valid.
        """
        return self._timedelta

    security.declarePublic('checkUser')

    def checkUser(self):
        """Returns a boolean representing the state of 'user check' as described
        in 'toggleUserCheck'. True means on, and is the default."""
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


    security.declarePrivate('clearExpired')

    def clearExpired(self, days=0):
        """Destroys all expired reset request records.
        Parameter controls how many days past expired it must be to disappear.
        """
        now = datetime.datetime.utcnow()
        for key, record in self._requests.items():
            stored_user, expiry = record
            if self.expired(expiry, now - datetime.timedelta(days=days)):
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
        will be passed properly in the default implementation.
        """
        uuid_generator = getUtility(IUUIDGenerator)
        return uuid_generator()

    security.declarePrivate('expirationDate')

    def expirationDate(self):
        """Returns a DateTime for exipiry of a request from the
        current time.

        This is used by housekeeping methods (like clearEpired)
        and stored in reset request records."""
        return datetime.datetime.utcnow() + datetime.timedelta(days=self._timedelta)

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


    security.declarePrivate('expired')

    def expired(self, dt, now=None):
        """Tells whether a DateTime or timestamp 'datetime' is expired
        with regards to either 'now', if provided, or the current
        time."""
        if not now:
            now = datetime.datetime.utcnow()
        return now >= dt


InitializeClass(PasswordResetTool)