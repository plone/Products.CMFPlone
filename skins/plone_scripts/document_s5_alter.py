##parameters=test=False
# ugly, ugly, ugly code, that basically changes the way the slide is put together
# this should be a HTML parser or XSLT or even JS
body =  context.CookedBody()

# this should be a regex too, but hey this works
tags = ["h1", "H1", "h2", "H2"]
tag = None
for t in tags:
    if body.find("<%s>" % t) > -1:
        tag = t
        break

if tag is None:
    msg = "For Plone to show this page as a presentation to work, it must find some header "\
    "tags (H1, h1, H2, h2) in your document. The document will be "\
    "split into slides based upon those tags. Structured text or Kupu "\
    "will all generate suitable tags for you."
    if test:
        return False
    else:
        raise ValueError, msg
else:
    if test:
        return True

num = int(tag[1])
if num > 1:
    new = "%s1" % (tag[0])
    body = body.replace("<%s>" % tag, "<%s>" % new)
    body = body.replace("</%s>" % tag, "</%s>" % new)
    tag = new

body = body.split('<%s>' % tag)
body = ('</div>\n<div class="slide">\n<%s>' % tag).join(body)
body = body.split('</%s>' % tag)
body = ('</%s>\n' % tag).join(body)
body = '<div class="slide">' + body + '</div>'

return body