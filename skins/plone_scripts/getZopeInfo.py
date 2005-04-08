## Script (Python) "getZopeInfo"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

cp = context.Control_Panel
return (cp.version_txt(), cp.sys_version())
