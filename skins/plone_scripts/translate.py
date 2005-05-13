## Script (Python) "translate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=msgid, mapping={}, default=None, domain='plone', target_language=None

# translate using unicode type
value = context.utranslate(msgid, mapping, default, domain, target_language)

# get tool
tool = context.translation_service

# encode using site encoding
return tool.encode(value)
