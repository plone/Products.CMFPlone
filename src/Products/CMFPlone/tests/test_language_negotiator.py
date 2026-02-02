from zope.component import getUtility
from zope.i18n.interfaces import INegotiator


# It will Ensure we are not using a Zope default or fallback negotiator
def test_plone_registers_i18n_negotiator():
    negotiator = getUtility(INegotiator)
    assert negotiator.__class__.__module__.startswith("plone.i18n")
