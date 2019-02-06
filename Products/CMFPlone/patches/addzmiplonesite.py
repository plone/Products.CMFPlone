# -*- coding: utf-8 -*-
# This is a pretty ugly hack but it has the upside that it even works
# when Products.ExternalEditor patches the main.zpt with its own version.
# Maybe we should use a metal-slot instead.

from OFS.ObjectManager import ObjectManager

ADD_PLONE_SITE_HTML = '''
<tal:createplone tal:condition="python: len(context.getPhysicalPath()) == 1 or context.meta_type == 'Folder' and 'PloneSite' not in [str(o) for o in context.aq_chain]">
  <form method="get"
        class="text-right"
        action="@@plone-addsite"
        target="_top">
    <input type="hidden" name="site_id" value="Plone" />
    <button type="submit" class="btn btn-outline-primary btn-sm">Add Plone Site</button>
    <div class="form-group form-check">
      <input type="checkbox" class="form-check-input" name="advanced" id="advanced">
      <label for="advanced">advanced</label>
    </div>
  </form>
</tal:createplone>

<tal:upgrade tal:condition="python: context.meta_type == 'Plone Site' and context.portal_migration.needUpgrading()">
<div class="alert alert-danger" role="alert">
  The site configuration is outdated and needs to be upgraded.
  <a class="alert-link"
     tal:attributes="href python:context.absolute_url() + '/@@plone-upgrade'"
     title="Go to the upgrade page">
    Please continue with the upgrade.
  </a>
</div>
</tal:upgrade>
'''

main = ObjectManager.manage_main
orig = main.read()
pos = orig.find('<main class="container-fluid">')

# Add in our button html at the right position
new = orig[:pos] + ADD_PLONE_SITE_HTML + orig[pos:]
main.write(new)
