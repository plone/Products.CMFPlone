## Script (Python) "CSSImports"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=CSS imports
##
url=context.portal_url()

output = r"""
	<style type="text/css" media="all"> 
		@import "%s";
		@import "%s";
		@import "%s";
		@import "%s";
		@import "%s";
    /*
		@import "%s";
     */
  </style> """ % ( url + '/ploneBasic.css'
                 , url + '/ploneStructure.css'
                 , url + '/ploneWidgets.css'
                 , url + '/ploneDeprecated.css'
                 , url + '/ploneCalendar.css'
                 , url + '/ploneForum.css' ) #ploneForum is commented out

return output

