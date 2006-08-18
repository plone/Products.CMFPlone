#
# PloneTestCase
#

# $Id$

from Products.PloneTestCase.ptc import *

setupPloneSite()

# BBB once we don't have to deal with non-unicode anymore
# For the transition phase of mixed Unicode and encoded string usage applying
# this patch is mandatory or we will see endless UnicodeDecodeErrors
from Products.PlacelessTranslationService import PatchStringIO


class PloneTestCase(PloneTestCase):
    """This is a stub now, but in case you want to try
       something fancy on Your Branch (tm), put it here.
    """


class FunctionalTestCase(Functional, PloneTestCase):
    """This is a stub now, but in case you want to try
       something fancy on Your Branch (tm), put it here.
    """
