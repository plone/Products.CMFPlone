## Script (Python) "canConstrainTypes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Find out if the context supports per-instance addable type restriction

if getattr(context, 'canSetConstrainTypes', None):
    return context.canSetConstrainTypes()
else:
    return False
