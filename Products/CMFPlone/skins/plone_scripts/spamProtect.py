## Script (Python) "spamProtect"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=mailaddress=None, mailname=None, cssclass=None, cssid=None
##title=Returns a spam-protected mail address tag
##

def escape(s):
	if s is not None:
		s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
	return s

mailaddress = escape(mailaddress)
mailname = escape(mailname)
cssclass = escape(cssclass)
cssid = escape(cssid)

email = mailaddress.replace('@', '&#0064;').replace(':', '&#0058;')

if mailname is None:
    mailname = email
if cssid is None:
    cssid = ''
else:
    cssid = ' id="%s"' % cssid
if cssclass is None:
    cssclass = ''
else:
    cssclass = ' class="%s"' % cssclass

return '<a href="&#0109;ailto&#0058;' + email + '"' + cssclass \
        + cssid + '>' + mailname + '</a>'
