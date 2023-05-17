from OFS.ObjectManager import ObjectManager


# FIXME: This no longer works with the new ZMI

ADD_PLONE_SITE_HTML = """
<dtml-if "_.len(this().getPhysicalPath()) == 1 or this().meta_type == 'Folder' and 'PloneSite' not in [o.__class__.__name__ for o in this().aq_chain]">
  <!-- Add Plone site action-->
  <form method="get"
        action="&dtml-URL1;/@@plone-addsite"
        style="text-align: right; margin-top:0.5em; margin-bottom:0em;"
        target="_top">
    <input type="hidden" name="site_id" value="Plone" />
    <input type="submit" value="Add Plone Site" />
    <label><input type="checkbox" name="advanced">advanced</label>
  </form>
</dtml-if>
<dtml-if "this().meta_type == 'Plone Site'">
  <!-- Warn if outdated -->
  <dtml-if "this().portal_migration.needUpgrading()">
    <div style="background: url(/misc_/PageTemplates/exclamation.gif) top left no-repeat;
                padding: 0 0 0 1.2em; font-weight: bold; font-size: 125%;
                margin-top: 1em;">
      The site configuration is outdated and needs to be upgraded.
      <a href="&dtml-URL1;/@@plone-upgrade" title="Go to the upgrade page">
        Please continue with the upgrade.
      </a>
    </div>
  </dtml-if>
</dtml-if>
"""

main = ObjectManager.manage_main
orig = main.read()
pos = orig.find("<!-- Add object widget -->")

# Add in our button html at the right position
new = orig[:pos] + ADD_PLONE_SITE_HTML + orig[pos:]

# Modify the manage_main
main.edited_source = new
main._v_cooked = main.cook()
