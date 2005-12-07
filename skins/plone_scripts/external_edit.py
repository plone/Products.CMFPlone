## Script (Python) "external_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=http://cmf.zope.org/Members/tseaver/20020723_external_editor_available

from Products.PythonScripts.standard import url_quote
return context.REQUEST['RESPONSE'].redirect(
    '%s/externalEdit_/%s' % (context.aq_parent.absolute_url(),
                             url_quote(context.getId())))
