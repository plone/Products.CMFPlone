## Script (Python) "add_ext_editor"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=adds ext_edit actions to types
types=context.portal_types
omit_types=('Folder','Discussion Item','Event','Topic')
for ctype in [ctype for ctype in types.objectValues() if ctype.Title() not in omit_types]:
    try:
        ctype.getActionById('external_edit')
    except (TypeError, KeyError):
        ctype.addAction( 'external_edit',
                         'External Editor',
                         'external_edit',
                         'Modify portal content',
                         'object', 
                         visible=0 )
context.portal_properties.site_properties.manage_changeProperties( {'ext_editor':1} )
return 'Successfully configured system to use External Editor.'
