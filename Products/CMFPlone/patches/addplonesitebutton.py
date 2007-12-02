from OFS.ObjectManager import ObjectManager

ADD_PLONE_SITE_HTML = '''
<dtml-if "_.len(this().getPhysicalPath()) == 1">
  <!-- Add Plone site button-->
  <form action="&dtml-URL1;/" method="get" style="text-align: right; margin-top:0.5em; margin-bottom:0em">
    <input type="hidden" name=":method" value="manage_addProduct/CMFPlone/addPloneSiteForm" />
    <input class="form-element" type="submit" name="submit" value="Add Plone Site" />
  </form>
</dtml-if>
'''

main = ObjectManager.manage_main
orig = main.read()
pos = orig.find('<!-- Add object widget -->')

# Add in our button html at the right position
new = orig[:pos] + ADD_PLONE_SITE_HTML + orig[pos:]

# Modify the manage_main
main.edited_source = new
main._v_cooked = main.cook()
