import re
import random
import md5
from smtplib import SMTPRecipientsRefused

from zope.component import getUtility

from Products.CMFCore.interfaces import ISiteRoot

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.RegistrationTool import RegistrationTool as BaseTool
from Products.CMFPlone import ToolNames

from Products.CMFCore.permissions import AddPortalMember

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, Unauthorized
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.SecureMailHost.SecureMailHost import EMAIL_RE
from Products.CMFDefault.utils import checkEmailAddress
from Products.CMFDefault.exceptions import EmailAddressInvalid

from Products.PluggableAuthService.interfaces.authservice \
        import IPluggableAuthService

# - remove '1', 'l', and 'I' to avoid confusion
# - remove '0', 'O', and 'Q' to avoid confusion
# - remove vowels to avoid spelling words
invalid_password_chars = ['a','e','i','o','u','y','l','q']

def getValidPasswordChars():
    password_chars = []
    for i in range(0, 26):
        if chr(ord('a')+i) not in invalid_password_chars:
            password_chars.append(chr(ord('a')+i))
            password_chars.append(chr(ord('A')+i))
    for i in range(2, 10):
        password_chars.append(chr(ord('0')+i))
    return password_chars

password_chars = getValidPasswordChars()

# seed the random number generator
random.seed()


class RegistrationTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.RegistrationTool
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/pencil_icon.gif'
    plone_tool = 1
    md5key = None
    _v_md5base = None

    def __init__(self):
        if hasattr(BaseTool, '__init__'):
            BaseTool.__init__(self)
        # build and persist an MD5 key
        self.md5key = ''
        for i in range(0, 20):
            self.md5key += chr(ord('a')+random.randint(0,26))

    def _md5base(self):
        if self._v_md5base is None:
            self._v_md5base = md5.new(self.md5key)
        return self._v_md5base

    # Get a password of the prescribed length
    #
    # For s=None, generates a random password
    # For s!=None, generates a deterministic password using a hash of s
    #   (length must be <= 16 for s != None)
    #
    # TODO: Could this be made private?
    def getPassword(self, length=5, s=None):
        global password_chars, md5base

        if s is None:
            password = ''
            nchars = len(password_chars)
            for i in range(0, length):
                password += password_chars[random.randint(0,nchars-1)]
            return password
        else:
            m = self._md5base().copy()
            m.update(s)
            d = m.digest() # compute md5(md5key + s)
            assert(len(d) >= length)
            password = ''
            nchars = len(password_chars)
            for i in range(0, length):
                password += password_chars[ord(d[i]) % nchars]
            return password

    security.declarePublic('isValidEmail')
    def isValidEmail(self, email):
        """ checks for valid email """
        if EMAIL_RE.search(email) == None:
            return 0
        try:
            checkEmailAddress(email)
        except EmailAddressInvalid:
            return 0
        else:
            return 1

    security.declarePublic( 'testPropertiesValidity' )
    def testPropertiesValidity(self, props, member=None):

        """ Verify that the properties supplied satisfy portal's requirements.

        o If the properties are valid, return None.
        o If not, return a string explaining why.

        This is a customized version of the CMFDefault version: we also
        check if the email property is writable before verifying it.
        """
        if member is None: # New member.

            username = props.get('username', '')
            if not username:
                return 'You must enter a valid name.'

            if not self.isMemberIdAllowed(username):
                return ('The login name you selected is already '
                        'in use or is not valid. Please choose another.')

            email = props.get('email')
            if email is None:
                return 'You must enter an email address.'

            try:
                checkEmailAddress( email )
            except EmailAddressInvalid: 
                return 'You must enter a valid email address.'

        else: # Existing member.
            if not hasattr(member, 'canWriteProperty') or \
                    member.canWriteProperty('email'):

                email = props.get('email')

                if email is not None:

                    try:
                        checkEmailAddress( email )
                    except EmailAddressInvalid:
                        return 'You must enter a valid email address.'

                # Not allowed to clear an existing non-empty email.
                existing = member.getProperty('email')
                
                if existing and email == '':
                    return 'You must enter a valid email address.'

        return None


    security.declareProtected(AddPortalMember, 'isMemberIdAllowed')
    def isMemberIdAllowed(self, id):
        if len(id) < 1 or id == 'Anonymous User':
            return 0
        if not self._ALLOWED_MEMBER_ID_PATTERN.match( id ):
            return 0

        pas = getToolByName("acl_users")
        if IPluggableAuthService.providedBy(pas):
            results = pas.searchPrincipals(id=id)
            if results:
                return 0
        else:
            membership = getToolByName(self, 'portal_membership')
            if membership.getMemberById(id) is not None:
                return 0
            groups = getToolByName(self, 'portal_groups')
            if groups.getGroupById(id) is not None:
                return 0

        return 1


    security.declarePublic('generatePassword')
    def generatePassword(self):
        """Generates a password which is guaranteed to comply
        with the password policy."""
        return self.getPassword(6)

    security.declarePublic('generateResetCode')
    def generateResetCode(self, salt, length=14):
        """Generates a reset code which is guaranteed to return the
        same value for a given length and salt, every time."""
        return self.getPassword(length, salt)

    security.declarePublic('mailPassword')
    def mailPassword(self, forgotten_userid, REQUEST):
        """ Wrapper around mailPassword """
        membership = getToolByName(self, 'portal_membership')
        if not membership.checkPermission('Mail forgotten password', self):
            raise Unauthorized, "Mailing forgotten passwords has been disabled"

        utils = getToolByName(self, 'plone_utils')
        member = membership.getMemberById(forgotten_userid)

        if member is None:
            raise ValueError, 'The username you entered could not be found'

        # assert that we can actually get an email address, otherwise
        # the template will be made with a blank To:, this is bad
        email = member.getProperty('email')
        if not email:
            raise ValueError('That user does not have an email address.')
        else:
            # add the single email address
            if not utils.validateSingleEmailAddress(email):
                raise ValueError, 'The email address did not validate'
        check, msg = _checkEmail(email)
        if not check:
            raise ValueError, msg

        # Rather than have the template try to use the mailhost, we will
        # render the message ourselves and send it from here (where we
        # don't need to worry about 'UseMailHost' permissions).
        reset_tool = getToolByName(self, 'portal_password_reset')
        reset = reset_tool.requestReset(forgotten_userid)

        
        email_charset = getattr(self, 'email_charset', 'UTF-8')
        mail_text = self.mail_password_template( self
                                               , REQUEST
                                               , member=member
                                               , reset=reset
                                               , password=member.getPassword()
                                               , charset=email_charset
                                               )
        if isinstance(mail_text, unicode):
            mail_text = mail_text.encode(email_charset)
        host = self.MailHost
        try:
            host.send( mail_text )

            return self.mail_password_response( self, REQUEST )
        except SMTPRecipientsRefused:
            # Don't disclose email address on failure
            raise SMTPRecipientsRefused('Recipient address rejected by server')

    security.declarePublic('registeredNotify')
    def registeredNotify(self, new_member_id):
        """ Wrapper around registeredNotify """
        membership = getToolByName( self, 'portal_membership' )
        utils = getToolByName(self, 'plone_utils')
        member = membership.getMemberById( new_member_id )

        if member and member.getProperty('email'):
            # add the single email address
            if not utils.validateSingleEmailAddress(member.getProperty('email')):
                raise ValueError, 'The email address did not validate'

        email = member.getProperty( 'email' )
        try:
            checkEmailAddress(email)
        except EmailAddressInvalid:
            raise ValueError, 'The email address did not validate'

        pwrt = getToolByName(self, 'portal_password_reset')
        reset = pwrt.requestReset(new_member_id)

        # Rather than have the template try to use the mailhost, we will
        # render the message ourselves and send it from here (where we
        # don't need to worry about 'UseMailHost' permissions).
        mail_text = self.registered_notify_template( self
                                                   , self.REQUEST
                                                   , member=member
                                                   , reset=reset
                                                   , email=email
                                                   )

        host = self.MailHost
        encoding = getUtility(ISiteRoot).getProperty('email_charset')
        host.send(mail_text.encode(encoding))

        return self.mail_password_response( self, self.REQUEST )

    def isMemberIdAllowed(self, id):
        if len(id) < 1 or id == 'Anonymous User':
            return 0
        if not self._ALLOWED_MEMBER_ID_PATTERN.match( id ):
            return 0

        pas = getToolByName(self, 'acl_users')
        if IPluggableAuthService.providedBy(pas):
            results = pas.searchPrincipals(id=id, exact_match=True)
            if results:
                return 0
        else:
            membership = getToolByName(self, 'portal_membership')
            if membership.getMemberById(id) is not None:
                return 0
            groups = getToolByName(self, 'portal_groups')
            if groups.getGroupById(id) is not None:
                return 0

        return 1

RegistrationTool.__doc__ = BaseTool.__doc__

InitializeClass(RegistrationTool)

_TESTS = ( ( re.compile("^[0-9a-zA-Z\.\-\_\+\']+\@[0-9a-zA-Z\.\-]+$")
           , True
           , "Failed a"
           )
         , ( re.compile("^[^0-9a-zA-Z]|[^0-9a-zA-Z]$")
           , False
           , "Failed b"
           )
         , ( re.compile("([0-9a-zA-Z_]{1})\@.")
           , True
           , "Failed c"
           )
         , ( re.compile(".\@([0-9a-zA-Z]{1})")
           , True
           , "Failed d"
           )
         , ( re.compile(".\.\-.|.\-\..|.\.\..|.\-\-.")
           , False
           , "Failed e"
           )
         , ( re.compile(".\.\_.|.\-\_.|.\_\..|.\_\-.|.\_\_.")
           , False
           , "Failed f"
           )
         , ( re.compile(".\.([a-zA-Z]{2,3})$|.\.([a-zA-Z]{2,4})$")
           , True
           , "Failed g"
           )
         )

def _checkEmail( address ):
    for pattern, expected, message in _TESTS:
        matched = pattern.search( address ) is not None
        if matched != expected:
            return False, message
    return True, ''

