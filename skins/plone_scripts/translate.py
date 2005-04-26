## Script (Python) "translate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=msgid, mapping={}, default=None, domain='plone', target_language=None

from Products.CMFPlone.utils import translate_wrapper

value = translate_wrapper(domain,
                          msgid,
                          mapping,
                          context=context,
                          target_language=target_language,
                          default=default)

if not value and default is None:
    value = msgid

    for k, v in mapping.items():
        value = value.replace('${%s}' % k, v)

return value
    
