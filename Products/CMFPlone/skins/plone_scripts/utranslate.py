## Script (Python) "utranslate (alias for translate)"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=msgid, mapping={}, default=None, domain='plone', target_language=None, escape_for_js=False

from zExceptions import Forbidden


if container.REQUEST.get("PUBLISHED") is script:
    raise Forbidden("Script may not be published.")

# handle the possible "nothing" condition in folder_contents.pt ln 21
# gracefully
if msgid is None:
    return None

from Products.CMFCore.utils import getToolByName


# get tool
tool = getToolByName(context, "translation_service")

# this returns type unicode
value = tool.utranslate(
    msgid,
    domain,
    mapping,
    context=context,
    target_language=target_language,
    default=default,
)

if not value and default is None:
    value = msgid

    for k, v in mapping.items():
        value = value.replace("${%s}" % k, v)

if escape_for_js:
    value = value.replace("'", "\\'")

return value
