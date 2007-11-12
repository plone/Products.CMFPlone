from AccessControl.Role import RoleManager

ADD_SECURITY_WARNING = '''
<!-- Added security warning -->
<p style="font-size:120%; color:red; font-weight:bold;">
WARNING!!!
<br />
Do not use this form to adjust security settings for any Plone content objects!
Use the sharing tab or workflows instead.
</p>
<!-- End security warning -->
'''

normal = RoleManager._normal_manage_access
orig = normal.read()
pos = orig.find('</dtml-with>')

# Add in our warning at the right position
new = orig[:pos] + ADD_SECURITY_WARNING + orig[pos:]

# Modify the manage_main
normal.edited_source = new
normal._v_cooked = normal.cook()
