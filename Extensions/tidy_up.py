from mx.Tidy import tidy
import os

plone_dir = '/home/runyaga/Zope-2.6.0b2-linux2-x86/lib/python/Products/CMFPlone'

ignored_errors = [
    'unknown attribute "xmlns:metal"',
    'unknown attribute "xmlns:tal"',
    'unknown attribute "xmlns:i18n"',
    'unknown attribute "tal:',
    'unknown attribute "i18n:',
    'unknown attribute "metal:',
    
    '<tal:block> is not recognized',
    '<metal:block> is not recognized',
    'tal:block is not recognized',
    'metal:block is not recognized',
    
    '<html> has XML attribute "xml:lang"',
    'inserting missing \'title\' element',
    'unknown attribute "onfocus"',  # why does Tidy not like this?
    'discarding unexpected ',
    'trimming empty ',
    '<table> lacks "summary" attribute',
    'img lacks "src" attribute',
    'img lacks "alt" attribute',
    
    'This document has errors that must be fixed before',
    'using HTML Tidy to generate a tidied up version.',
    ]

def check_pt(filename):
    input = open(filename)
    (nerrors, nwarnings, outputdata, errordata) = \
        tidy(input, output_markup=0)

    out = ''
    for err in errordata.split('\n'):
        if err.strip():
            found = -1
            for ignore in ignored_errors:
                found = err.find(ignore)
                if found != -1:
                    break
            if found == -1:
                out = out + '\t' + err + '\n'
    if out:
        print filename
        print out
    input.close()


def visit(arg, dirname, files):
    files = filter(lambda x: x.endswith('.pt'), files)
    if len(files) > 0:
        for f in files:
            check_pt(os.path.join(dirname, f))

os.path.walk(plone_dir, visit, [])
