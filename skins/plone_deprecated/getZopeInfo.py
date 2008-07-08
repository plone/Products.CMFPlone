## Script (Python) "getZopeInfo"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
context.plone_log("The getZopeInfo script is deprecated and will be removed "
                  "in Plone 4.0. Use the coreVersions method of the migration "
                  "tool instead.")

cp = context.Control_Panel
return (cp.version_txt(), cp.sys_version())
