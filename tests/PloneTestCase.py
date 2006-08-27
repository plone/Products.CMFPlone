#
# PloneTestCase
#

# $Id$

from Products.PloneTestCase.ptc import *

setupPloneSite()


class PloneTestCase(PloneTestCase):
    """This is a stub now, but in case you want to try
       something fancy on Your Branch (tm), put it here.
    """


class FunctionalTestCase(Functional, PloneTestCase):
    """This is a stub now, but in case you want to try
       something fancy on Your Branch (tm), put it here.
    """
