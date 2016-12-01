# Some security patches were done here until Plone 4.3.11, but they needed to
# be loaded earlier.  No one should be importing from this place, but let's not
# break if that happens.
from Products.CMFPlone.earlypatches.security import *  # noqa
