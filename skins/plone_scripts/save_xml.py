## Script (Python) "edit_xml" 
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=title='', description='', text=''
##title=Edit xml

context.edit( 'html'
            , text
            , ''
            , '' )
context.plone_utils.contentEdit( context
                               , id=context.getId()
                               , title=title
                               , description=description )

