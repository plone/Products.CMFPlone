## Script (Python) "selectedTabs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=default_tab, obj=None
##title=
##

# we want to centalize where all tab selection is done
# for now e will start off with the top tabs, 'portal_tabs'

tabs={}
contentpath = None
try:
    # bad things can happen to context if an exception is thrown during traversal
    if obj is None:
        obj = context
    contentpath=context.portal_url.getRelativeContentPath(obj)
except:
    pass
if not contentpath:
    tabs['portal']=default_tab
else:
    tabs['portal']=contentpath[0]
return tabs
