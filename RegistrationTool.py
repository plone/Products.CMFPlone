import random
import md5
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.RegistrationTool import RegistrationTool as BaseTool

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore import CMFCorePermissions

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


class RegistrationTool( BaseTool ):
    meta_type='Plone Registration Tool'
    security = ClassSecurityInfo()
    plone_tool = 1
    md5key = None

    def __init__(self):
        if hasattr(BaseTool, '__init__'):
            BaseTool.__init__(self)
        # build and persist an MD5 key
        self.md5key = ''
        for i in range(0, 20):
            self.md5key += chr(ord('a')+random.randint(0,26))
        self._v_md5base = None

    def _md5base(self):
        if self._v_md5base == None:
            self._v_md5base = md5.new(self.md5key)
        return self._v_md5base


    # Get a password of the prescribed length
    #
    # For s=None, generates a random password
    # For s!=None, generates a deterministic password using a hash of s
    #   (length must be <= 16 for s != None)
    #
    def getPassword(self, length=5, s=None):
        global password_chars, md5base
        
        if s is None:
            password = ''
            n = len(password_chars)
            for i in range(0,length):
                password += password_chars[random.randint(0,n-1)]
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


    security.declarePublic('generatePassword')
    def generatePassword(self):
        """Generates a password which is guaranteed to comply
        with the password policy."""
        # provide public access to the getPassword methog
        return self.getPassword(6)

InitializeClass(RegistrationTool)

