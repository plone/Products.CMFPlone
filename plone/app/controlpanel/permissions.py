# XXX merge note: switch to import from AccessControl in Zope 2.13
from Products.CMFCore.permissions import setDefaultRoles

for permission in (
    'Plone Site Setup: Overview',
    'Plone Site Setup: Calendar',
    'Plone Site Setup: Editing',
    'Plone Site Setup: Filtering',
    'Plone Site Setup: Language',
    'Plone Site Setup: Mail',
    'Plone Site Setup: Markup',
    'Plone Site Setup: Navigation',
    'Plone Site Setup: Search',
    'Plone Site Setup: Security',
    'Plone Site Setup: Site',
    'Plone Site Setup: Themes',
    'Plone Site Setup: Types',
    ):
    setDefaultRoles(permission, ('Manager', 'SiteAdmin'))
