##parameters=templateId
#!/usr/bin/python
#$Id$
#Copyright: ClearWind Consulting Ltd

# please someone fix this!

# this is a horrific hack to take a page template and rummage
# through the tool to find the parent template
parentPages = {
  'Products':'plone_control_panel',
  'Plone':'plone_control_panel',
  'Member':'plone_memberprefs_panel',
  }


tool = context.portal_controlpanel

parent = None

for group in tool.getGroups():
    item = tool.enumConfiglets(group['id'])
    for thing in item:
        if thing['url'].endswith(templateId):
            parent = group['id']
            break

return parentPages.get(parent, None)
