#!/usr/bin/python

""" 
Normalization Stuff
"""

# table of transliterations that we know how to do
mapping = {138: 's', 140: 'OE', 142: 'z', 154: 's', 156: 'oe', 158: 'z', 159: 'Y', 
192: 'A', 193: 'A', 194: 'A', 195: 'A', 196: 'A', 197: 'a', 198: 'E', 199: 'C', 
200: 'E', 201: 'E', 202: 'E', 203: 'E', 204: 'I', 205: 'I', 206: 'I', 207: 'I', 
208: 'D', 209: 'n', 211: 'O', 212: 'O', 214: 'O', 216: 'O', 217: 'U', 218: 'U', 
219: 'U', 220: 'U', 221: 'y', 223: 'ss', 224: 'a', 225: 'a', 226: 'a', 227: 'a', 
228: 'a', 229: 'a', 230: 'e', 231: 'c', 232: 'e', 233: 'e', 234: 'e', 235: 'e', 
236: 'i', 237: 'i', 238: 'i', 239: 'i', 240: 'd', 241: 'n', 243: 'o', 244: 'o', 
246: 'o', 248: 'o', 249: 'u', 250: 'u', 251: 'u', 252: 'u', 253: 'y', 255: 'y'}

def _normalizeChar(c=''):
    if ord(c) < 256:
        return mapping.get(ord(c),c)
    else:
        return "%x" % ord(c)

def normalizeISO(text=""):
    """ convert unicode characters to ascii 

    normalizeISO() will turn unicode characters into nice, safe ascii. for
    some characters, it will try to transliterate them to something fairly
    reasonable. for other characters that it can't transliterate, it will just
    return the numerical value(s) of the bytes in the character (in hex).

    >>> normalizeISO(u"\xe6")
    'e'
    >>> normalizeISO(u"a")
    'a'
    >>> normalizeISO(u"\u9ad8")
    '9ad8'

    """
    return "".join([_normalizeChar(c) for c in text]).encode('ascii')

import re

def titleToNormalizedId(title=""):
    """
    normalize a title to an id

    titleToNormalizedId() converts a whole string to a normalized form that
    should be safe to use as in a url, as a css id, etc. 

    all punctuation and spacing is removed and replaced with a '-':

    >>> titleToNormalizedId("a string with spaces")
    'a-string-with-spaces'
    >>> titleToNormalizedId("p.u,n;c(t)u!a@t#i$o%n")
    'p-u-n-c-t-u-a-t-i-o-n'

    strings are lowercased:

    >>> titleToNormalizedId("UppERcaSE")
    'uppercase'

    punctuation, spaces, etc. are trimmed and multiples are reduced to just
    one:

    >>> titleToNormalizedId(" a string    ")
    'a-string'
    >>> titleToNormalizedId(">here's another!")
    'here-s-another'
    >>> titleToNormalizedId("one with !@#$!@#$ stuff in the middle")
    'one-with-stuff-in-the-middle'

    the exception to all this is that if there is something that looks like a
    filename with an extension at the end, it will preserve the last period.

    >>> titleToNormalizedId('this is a file.gif')
    'this-is-a-file.gif'
    >>> titleToNormalizedId('this is. also. a file.html')
    'this-is-also-a-file.html'

    titleToNormalizedId() uses normalizeISO() to convert stray unicode
    characters. it will attempt to transliterate many of the common european
    accented letters to rough ascii equivalents:

    >>> titleToNormalizedId(u'Eksempel \xe6\xf8\xe5 norsk \xc6\xd8\xc5')
    'eksempel-eoa-norsk-eoa'

    for characters that we can't transliterate, we just return the hex codes of
    the byte(s) in the character. not pretty, but about the best we can do.

    >>> titleToNormalizedId(u'\u9ad8\u8054\u5408 Chinese')
    '9ad880545408-chinese'
    >>> titleToNormalizedId(u'\u30a2\u30ec\u30af\u30b5\u30f3\u30c0\u30fc\u3000\u30ea\u30df Japanese')
    '30a230ec30af30b530f330c030fc300030ea30df-japanese'
    >>> titleToNormalizedId(u'\uc774\ubbf8\uc9f1 Korean')
    'c774bbf8c9f1-korean'
    >>> titleToNormalizedId(u'\u0e2d\u0e40\u0e25\u0e47\u0e01\u0e0b\u0e32\u0e19\u0e40\u0e14\u0e2d\u0e23\u0e4c\u0e25\u0e35\u0e21 Thai')
    'e2de40e25e47e01e0be32e19e40e14e2de23e4ce25e35e21-thai'
    """    
    title = title.lower()
    title = title.strip()
    title = normalizeISO(title)

    base = title
    ext   = ""
    
    m = re.match(r"^(.+)\.(\w{,4})$",title)
    if m:
        base = m.groups()[0]
        ext  = m.groups()[1]
        
    base = re.sub(r"[\W\-]+", "-", base)
    base = re.sub(r"^\-+",    "",  base)
    base = re.sub(r"\-+$",    "",  base)
    
    if ext != "":
        base = base + "." + ext
    return base

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
