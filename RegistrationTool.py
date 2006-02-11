import random
import md5

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.RegistrationTool import RegistrationTool as BaseTool
from Products.CMFDefault.RegistrationTool import _checkEmail
from Products.CMFPlone import ToolNames
from Products.CMFPlone.utils import classImplements

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo, Unauthorized
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFPlone.PloneTool import EMAIL_RE

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
    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )
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
        if not _checkEmail(email)[0]:
            return 0
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

            ok, message =  _checkEmail( email )
            if not ok:
                return 'You must enter a valid email address.'

        else: # Existing member.
            if not hasattr(member, 'canWriteProperty') or \
                    member.canWriteProperty('email'):

                email = props.get('email')

                if email is not None:

                    ok, message =  _checkEmail( email )
                    if not ok:
                        return 'You must enter a valid email address.'

                # Not allowed to clear an existing non-empty email.
                existing = member.getProperty('email')
                
                if existing and email == '':
                    return 'You must enter a valid email address.'

        return None

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

        if member.getProperty('email'):
            # add the single email address
            if not utils.validateSingleEmailAddress(member.getProperty('email')):
                raise ValueError, 'The email address did not validate'

        return BaseTool.mailPassword(self, forgotten_userid, REQUEST)

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

        return BaseTool.registeredNotify(self, new_member_id)


RegistrationTool.__doc__ = BaseTool.__doc__

classImplements(RegistrationTool,
                RegistrationTool.__implements__)
InitializeClass(RegistrationTool)
