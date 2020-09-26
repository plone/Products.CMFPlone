## Script (Python) "external_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=http://cmf.zope.org/Members/tseaver/20020723_external_editor_available

from Products.PythonScripts.standard import url_quote

request = context.REQUEST

if 'Mac OS X' in request.get('HTTP_USER_AGENT', ''):
    return context.REQUEST['RESPONSE'].redirect(
        '{}/externalEdit_/{}.zem?macosx=1'.format(context.aq_parent.absolute_url(),
                                              url_quote(context.getId())))
else:
    return context.REQUEST['RESPONSE'].redirect(
        '{}/externalEdit_/{}'.format(context.aq_parent.absolute_url(),
                                     url_quote(context.getId())))
