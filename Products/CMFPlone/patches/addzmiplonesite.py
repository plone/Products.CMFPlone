# -*- coding: utf-8 -*-
# This is a pretty ugly hack but it has the upside that it even works
# when Products.ExternalEditor patches the main.zpt with its own version.
# Before Plone 5.2 this incected html but the template is rendered with
# RestrictedPython so we defer the logic to the view plone_zmi_patch.
# Maybe we should use a metal-slot instead.
from OFS.ObjectManager import ObjectManager

INJECT = '<div tal:replace="structure context/@@plone_zmi_patch" />'

main = ObjectManager.manage_main
orig = main.read()
pos = orig.find('<main class="container-fluid">')

# Add in our button html at the right position
new = orig[:pos] + INJECT + orig[pos:]
main.write(new)
