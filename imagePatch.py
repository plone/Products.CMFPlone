from cgi import escape

# patch Image.py
from OFS.Image import Image

def tag(self, height=None, width=None, alt=None,
        scale=0, xscale=0, yscale=0, css_class=None, title=None, **args):
    if not args.has_key('border'):
        args['border'] = None

    if height is None: height=self.height
    if width is None:  width=self.width

    # Auto-scaling support
    xdelta = xscale or scale
    ydelta = yscale or scale

    if xdelta and width:
        width =  str(int(round(int(width) * xdelta)))
    if ydelta and height:
        height = str(int(round(int(height) * ydelta)))

    result='<img src="%s"' % (self.absolute_url())

    if alt is None:
        alt=getattr(self, 'title', '')
    result = '%s alt="%s"' % (result, escape(alt, 1))

    if title is None:
        title=getattr(self, 'title', '')
    result = '%s title="%s"' % (result, escape(title, 1))

    if height:
        result = '%s height="%s"' % (result, height)

    if width:
        result = '%s width="%s"' % (result, width)

    if not 'border' in [ x.lower() for x in  args.keys()]:
        result = '%s border="0"' % result

    if css_class is not None:
        result = '%s class="%s"' % (result, css_class)

    for key in args.keys():
        value = args.get(key)
        if value:
            result = '%s %s="%s"' % (result, key, value)

    return '%s />' % result
    
Image.tag = tag
