import random
import md5
import re

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import CMFCorePermissions
from Products.CMFDefault.RegistrationTool import RegistrationTool as BaseTool
from Products.CMFPlone import ToolNames

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

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


class RegistrationTool(BaseTool):

    meta_type = ToolNames.RegistrationTool
    security = ClassSecurityInfo()
    plone_tool = 1
    md5key = None
    _v_md5base = None
    email_regex="""^([0-9a-z_&.+-]+!)*[0-9a-z_&.+-]+@(([0-9a-z]([0-9a-z-]*[0-9a-z])?\.)+[a-z]{2,4}|([0-9]{1,3}\.){3}[0-9]{1,3})$"""

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
    # XXX: Could this be made private?
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
        pattern = re.compile(self.email_regex)
        if pattern.search(email.lower()) == None:
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

RegistrationTool.__doc__ = BaseTool.__doc__

InitializeClass(RegistrationTool)
