## Script (Python) "plone.css"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Rendered version of the Plone CSS for use from external tools
##

portal_css = context.portal_css
stylesheets = portal_css.getEvaluatedResources(context);
current_skin = context.getCurrentSkinName()

for stylesheet in stylesheets:
  if stylesheet.getRendering() in ['import','inline']:
    print portal_css.restrictedTraverse('%s/%s' % (current_skin, stylesheet.getId()))
 
duration = 1
seconds = float(duration)*24.0*3600.0
response = context.REQUEST.RESPONSE
#response.setHeader('Expires',rfc1123_date((DateTime() + duration).timeTime()))
response.setHeader('Cache-Control', 'max-age=%d' % int(seconds))
response.setHeader('Content-Type', 'text/css')
 
return printed
