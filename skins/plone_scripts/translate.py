## Script (Python) "translate (for unicode ignorants)"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=msgid, mapping={}, default=None, domain='plone', target_language=None, escape_for_js=False

# NOTE: using this script means you ignore unicode and hope
#       that the system will handle that for you. Use the
#       utranslate script and use unicode type instead of string type.

# get tool
tool = context.translation_service
asunicodetype = tool.asunicodetype
encode = tool.encode

# make sure the mapping contains unicode type strings
# as the caller does not care about encoding we dont care about errors
# we also assume that passed strings are encoded with the site encoding
for k, v in mapping.items():
    if isinstance(v, str):
        mapping[k]=asunicodetype(v, errors='replace')

# translate using unicode type
value = context.utranslate(msgid, mapping, default, domain, target_language)

# encode using site encoding
result=encode(value)

if escape_for_js:
    return result.replace("'", "\\'")
else:
    return result
