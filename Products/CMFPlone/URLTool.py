# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
from Acquisition import aq_parent
from AccessControl.class_init import InitializeClass
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.URLTool import URLTool as BaseTool
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFPlone.patches.gtbn import rewrap_in_request_container
from zope.component import getUtility

import html
import re
import six
import string
import unicodedata


hp = HTMLParser()
# These schemas are allowed in full urls to consider them in the portal:
# A mailto schema is an obvious sign of a url that is not in the portal.
# This is a whitelist.
ALLOWED_SCHEMAS = [
    'https',
    'http',
]
# These bad parts are not allowed in urls that are in the portal:
# This is a blacklist.
BAD_URL_PARTS = [
    '\\\\',
    '<script',
    '%3cscript',
    'javascript:',
    'javascript%3a',
]

# Determine allowed ascii characters.
# We want to allow most printable characters,
# but no whitespace, and no punctuation, except for a few exceptions.
# This boils down to ascii letters plus digits plus exceptions.
# Exceptions:
# - dot and slash for relative or absolute paths.
# - @ because we have views starting with @@
# - + because we have ++resource++ urls
allowed_ascii = string.ascii_letters + string.digits + "./@+"

def safe_url_first_char(url):
    # For character code points higher than 127, the bytes representation of a character
    # is longer than the unicode representation, so url[0] may give different results
    # for bytes and unicode.  On Python 2:
    # >>> unichr(128)
    # u'\x80'
    # >>> len(unichr(128))
    # 1
    # >>> unichr(128).encode("latin-1")
    # '\x80'
    # >>> len(unichr(128).encode("latin-1"))
    # 1
    # >>> unichr(128).encode("utf-8")
    # '\xc2\x80'
    # >>> len(unichr(128).encode("utf-8"))
    # 2
    # >>> unichr(128).encode("utf-8")[0]
    # '\xc2'
    # So make sure we have unicode here for comparing the first character.
    if isinstance(url, bytes):
        # Remember, on Python 2, bytes == str.
        try:
            first = url.decode("utf-8")[0]
        except UnicodeDecodeError:
            # We don't trust this
            return False
    else:
        first = url[0]
    if ord(first) < 128:
        if first not in allowed_ascii:
            # The first character of the url is ascii but not in the allowed range.
            return False
    else:
        # This is non-ascii, which has lots of control characters, which may be dangerous.
        # Check taken from django.utils.http._is_safe_url.  See
        # https://github.com/django/django/blob/2.1.5/django/utils/http.py#L356-L382
        # Forbid URLs that start with control characters. Some browsers (like
        # Chrome) ignore quite a few control characters at the start of a
        # URL and might consider the URL as scheme relative.
        # For categories, see 5.7.1 General Category Values here:
        # http://www.unicode.org/reports/tr44/tr44-6.html#Property_Values
        # We look for Control categories here.
        if unicodedata.category(first)[0] == "C":
            return False
    return True


class URLTool(PloneBaseTool, BaseTool):

    meta_type = 'Plone URL Tool'
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/link_icon.png'

    @security.public
    def isURLInPortal(self, url, context=None):
        # Note: no docstring, because the method is publicly available
        # but does not need to be callable on site-url/portal_url/isURLInPortal.
        #
        # This method is overridden by Products.isurlinportal,
        # but the public declaration still seems needed.
        #
        # Also, in tests/testURLTool.py we do not use layers,
        # which means the Products code is not loaded,
        # so we need to import it explicitly.
        # This is done once.
        try:
            from Products.isurlinportal import isURLInPortal
        except ImportError:
            # If this somehow fails, it seems better to have a safe fallback,
            # instead of a hard failure.
            return False

        return isURLInPortal(self, url, context=context)

    def getPortalObject(self):
        portal = aq_parent(aq_inner(self))
        if portal is None:
            portal = getUtility(ISiteRoot)
        # Make sure portal can acquire REQUEST
        return rewrap_in_request_container(portal, context=self)


URLTool.__doc__ = BaseTool.__doc__

InitializeClass(URLTool)
