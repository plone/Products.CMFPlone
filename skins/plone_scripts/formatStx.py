## Script (Python) "formatStx"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=text=''
##title=Structured Text Previews
##
# A way of getting STX formatted text...
from Products.PythonScripts.standard import structured_text
return structured_text(text)