# XXX merge note: switch to import from AccessControl in Zope 2.13
from Products.CMFCore.permissions import setDefaultRoles

Overview = 'Plone Site Setup: Overview'
setDefaultRoles(Overview, ('Manager', 'SiteAdmin'))
