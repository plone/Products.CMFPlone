## Script (Python) "getSelectableViews"
##title=Get the view templates available from IBrowserDefault on the context
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=

if not context.canSetLayout():
    return None

# If there is only one template to select and we can't set a default page,
# it's not interesting to show the menu, so return None
try:
    layouts = context.getAvailableLayouts()
except AttributeError:
    # Might happen if FTI has not been migrated
    layouts = ()

if len(layouts) <= 1 and not context.canSetDefaultPage():
    return None
else:
    return layouts
