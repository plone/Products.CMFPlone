from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.ZopeGuards import guarded_getattr
from AccessControl.ZopeGuards import guarded_import
from OFS.interfaces import ITraversable
from Products.PageTemplates import Expressions
from zExceptions import NotFound
from zExceptions import Unauthorized
from zope.traversing.adapters import traversePathElement

import os
import string
import sys
import types
import warnings


# In the 'bobo aware' Zope traverse methods and functions, various security checks are done.
# For example for content items, permission checks are done.
# But for non-content, for example a Python module or a dictionary, the checks were originally very lax.
# This could be abused.  Now we know that, we want to be as strict as possible.
#
# But being stricter breaks existing code which worked fine so far,
# not knowing that it tried to access code which should have been disallowed.
# One thing that goes wrong, is that any skin template that calls context/main_template/macros/master fails,
# for example when viewing a revision from CMFEditions.
#
# So with this hotfix, by necessity we are still lax/forgiving, but you can change this behavior
# with an environment variable: STRICT_TRAVERSE_CHECK.
# - STRICT_TRAVERSE_CHECK=0 mostly uses the original lax/sloppy checks.
#   This sadly needs to be the default.
# - STRICT_TRAVERSE_CHECK=1 uses the strict logic.
#   When you know what you are doing, you can try this.
# - STRICT_TRAVERSE_CHECK=2 first tries the strict logic.
#   If this fails, log a warning and then fallback to the original lax checks.
#   The idea would be to use this in development or production for a while, to see which code needs a fix.
try:
    STRICT_TRAVERSE_CHECK = int(os.getenv("STRICT_TRAVERSE_CHECK", 0))
except (ValueError, TypeError, AttributeError):
    STRICT_TRAVERSE_CHECK = 0
# Set of names that start with an underscore but that we want to allow anyway.
ALLOWED_UNDERSCORE_NAMES = set([
    # dunder name is used in plone.app.caching, and maybe other places
    "__name__",
    # Zope allows a single underscore to avoid a test failure
    "_",
    # Special case for plone.protect.
    # Fixes a NotFound error when submitting a PloneFormGen form:
    # https://github.com/smcmahon/Products.PloneFormGen/pull/229
    "_authenticator",
])
# Some objects we really do not trust, even when you have found a workaround to reach them.
DISALLOWED_OBJECTS = [
    os,
    sys,
    # string.Formatter sounds innocent, but can be abused.
    string.Formatter,
]
_orig_boboAwareZopeTraverse = Expressions.boboAwareZopeTraverse


def guarded_import_module(base, path_items):
    name = path_items[0]
    try:
        guarded_import(base.__name__, fromlist=path_items)
        # guarded_import will do most security checking
        # but will not return the imported item itself,
        # so we need to call getattr ourselves.
        # Actually, not all security checks are done, so we call guarded_getattr.
        for name in path_items:
            base = guarded_getattr(base, name)
    except Unauthorized:
        # special case for OFS/zpt/main.zpt which uses
        # modules/AccessControl/SecurityManagement/getSecurityManager
        # which should have been modules/AccessControl/getSecurityManager
        # Fixed in Zope 4.6.1 and 5.2.1.
        if name == "SecurityManagement" and path_items[-1] == "getSecurityManager":
            return getSecurityManager
        # Convert Unauthorized to prevent information disclosures
        raise NotFound(name)
    except TypeError:
        # During testing with security-policy-implementation python
        # and verbose-security on, I got this error when an Unauthorized was raised
        # for string.Formatter.get_field:
        # TypeError: descriptor '__repr__' of 'object' object needs an argument
        # This was in the item_repr function of AccessControl.ImplPython.
        raise NotFound(name)
    if base in DISALLOWED_OBJECTS:
        raise NotFound(name)
    return base


def shared_traverse(base, path_items, request, traverse_method="restrictedTraverse"):
    """Shared traverse method for bobo aware zope traverse function and class method.

    They are almost exactly the same, and it is irritating and error prone
    to change similar code in two places.
    """
    validate = getSecurityManager().validate
    path_items = list(path_items)
    path_items.reverse()

    while path_items:
        name = path_items.pop()

        if ITraversable.providedBy(base):
            base = getattr(base, traverse_method)(name)
        elif isinstance(base, types.ModuleType):
            # We should be able to handle the name and all remaining path items at once.
            # Use the correct order again.
            path_items.append(name)
            path_items.reverse()
            return guarded_import_module(base, path_items)
        else:
            found = traversePathElement(base, name, path_items,
                                        request=request)

            # If traverse_method is something other than
            # ``restrictedTraverse`` then traversal is assumed to be
            # unrestricted. This emulates ``unrestrictedTraverse``
            if traverse_method != 'restrictedTraverse':
                base = found
                continue

            # Special backwards compatibility exception for the name ``_``,
            # which was often used for translation message factories.
            # Allow and continue traversal.
            if name == '_':
                warnings.warn('Traversing to the name `_` is deprecated '
                              'and will be removed in Zope 6.',
                              DeprecationWarning)
                base = found
                continue

            if name.startswith('_'):
                if name in ALLOWED_UNDERSCORE_NAMES:
                    base = found
                    continue
                # All other names starting with ``_`` are disallowed.
                # This emulates what restrictedTraverse does.
                raise NotFound(name)

            if found in DISALLOWED_OBJECTS:
                raise NotFound(name)

            if STRICT_TRAVERSE_CHECK:
                # traversePathElement doesn't apply any Zope security policy,
                # so we validate access explicitly here.
                try:
                    validate(base, base, name, found)
                except Unauthorized:
                    if STRICT_TRAVERSE_CHECK == 2:
                        # only warn
                        warnings.warn(
                            'Traversing from {0} to {1} is only allowed because STRICT_TRAVERSE_CHECK=2. '
                            'Possible security problem.'.format(object, name))
                    else:
                        # Convert Unauthorized to prevent information disclosures
                        raise NotFound(name)

            base = found

    return base


def boboAwareZopeTraverse(object, path_items, econtext):
    """Traverses a sequence of names, first trying attributes then items.

    This uses zope.traversing path traversal where possible and interacts
    correctly with objects providing OFS.interface.ITraversable when
    necessary (bobo-awareness).
    """
    request = getattr(econtext, 'request', None)
    result = shared_traverse(object, path_items, request)
    return result


Expressions.boboAwareZopeTraverse = boboAwareZopeTraverse
Expressions.ZopePathExpr._TRAVERSER = staticmethod(boboAwareZopeTraverse)

# But wait, there is also a BoboAwareZopeTraverse class.
from Products.PageTemplates.expression import BoboAwareZopeTraverse
from Products.PageTemplates.expression import TrustedBoboAwareZopeTraverse

# We do not want to change the trusted version.  It inherits the traverse method
# from the untrusted class.  It may be better to give it its own method.
# The @classmethod makes this tricky to get right.
# But the following line essentially makes a copy of the traverse method
# without needing inheritance anymore.
TrustedBoboAwareZopeTraverse.traverse = TrustedBoboAwareZopeTraverse.traverse

BoboAwareZopeTraverse._orig_traverse = BoboAwareZopeTraverse.traverse

def traverse(cls, base, request, path_items):
    """See ``zope.app.pagetemplate.engine``."""
    # When our patching is done correctly, this only gets called for the
    # BoboAwareZopeTraverse class, so cls.traverse_method is always restrictedTraverse.
    # But let's be careful and just pass the attribute on.
    result = shared_traverse(base, path_items, request, traverse_method=cls.traverse_method)
    return result

BoboAwareZopeTraverse.traverse = classmethod(traverse)

# The TrustedBoboAwareZopeTraverse and (untrusted) BoboAwareZopeTraverse class have a problem:
# They have a "traverse_method" attribute, but the "traverse" method
# calls "cls.traverseMethod" instead, so this fails.
# This may mean these classes do not get called anymore, except in test_expressions.py.
name1 = "traverse_method"
name2 = "traverseMethod"
# First do the trusted class, because it inherits from the untrusted class.
# Otherwise the trusted class would have traverse_method=unrestrictedTraverse
# and it would inherit traverseMethod=restrictedTraverse.
for klass in (TrustedBoboAwareZopeTraverse, BoboAwareZopeTraverse):
    if hasattr(klass, name1) and not hasattr(klass, name2):
        setattr(klass, name2, getattr(klass, name1))
