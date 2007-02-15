## Script (Python) "spamProtect"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=mailaddress=None, mailname=None
##title=Returns a spam-protected mail address tag
##
email = mailaddress.replace('@', '&#0064;').replace(':', '&#0058;')
if mailname is None:
    mailname = email
return '<a href="&#0109;ailto&#0058;' + email + '">' + mailname + '</a>'
