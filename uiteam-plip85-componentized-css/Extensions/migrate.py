
from Products.CMFPlone.migrations.oneX_twoBeta2 import doit

def plone1to2(portal):
    doit(portal)
    return 'finished migration'
