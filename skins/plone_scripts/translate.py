## Script (Python) "translate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=msgid, mapping={}, default=None

from Products.CMFPlone.PloneUtilities import translate_wrapper

return translate_wrapper('plone',
                         msgid,
                         mapping,
                         context=context,
                         default=default)
