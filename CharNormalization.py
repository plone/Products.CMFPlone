# Hand-made table from PloneTool.py
mapping_custom_1 =  {
138: 's', 142: 'z', 154: 's', 158: 'z', 159: 'Y', 
240: 'd', 208: 'D', 216: 'O', 230: 'e', 248: 'o', 198: 'E',}

# UnicodeData.txt does not contain normalization of Greek letters. 
mapping_greek = {
912: 'i', 913: 'A', 914: 'B', 
915: 'G', 916: 'D', 917: 'E', 918: 'Z', 919: 'I', 920: 'TH', 921: 'I', 
922: 'K', 923: 'L', 924: 'M', 925: 'N', 926: 'KS', 927: 'O', 928: 'P', 
929: 'R', 931: 'S', 932: 'T', 933: 'Y', 934: 'F', 936: 'PS', 937: 'O', 
938: 'I', 939: 'Y', 940: 'a', 941: 'e', 943: 'i', 944: 'y', 945: 'a', 
946: 'b', 947: 'g', 948: 'd', 949: 'e', 950: 'z', 951: 'i', 952: 'th', 
953: 'i', 954: 'k', 955: 'l', 956: 'm', 957: 'n', 958: 'ks', 959: 'o', 
960: 'p', 961: 'r', 962: 's', 963: 's', 964: 't', 965: 'y', 966: 'f', 
968: 'ps', 969: 'o', 970: 'i', 971: 'y', 972: 'o', 973: 'y' }

mapping_two_chars = {
140 : 'OE', 156: 'oe', 196: 'Ae', 246: 'oe', 252: 'ue', 214: 'Oe', 
228 : 'ae', 220: 'Ue', 223: 'ss' }

# Feel free to add new user-defined mapping. Don't forget to update mapping dict
# with your dict.

mapping = {}
mapping.update(mapping_custom_1)        
mapping.update(mapping_greek)
mapping.update(mapping_two_chars)


from unicodedata import normalize, decomposition
from Products.CMFCore.utils import getToolByName
from types import UnicodeType
import string

def charNormalization(self, text, encoding=None):
    """
    This method is used for normalization of unicode characters to the base ASCII 
    letters. Output is ASCII encoded string (or char) with only ASCII letters,
    digits, punctuation and whitespace characters. Case is preserved.
    """ 
    if not isinstance(text, UnicodeType):
        if encoding:
            text = unicode(text, encoding)
        else:
            plone_utils = getToolByName(self, 'plone_utils')
            text = unicode(text, plone_utils.getSiteEncoding())

    allowed = string.ascii_letters + string.digits + string.punctuation + string.whitespace
    res = ''
    for ch in text:
        if ch in allowed:
            # ASCII chars, digits etc. stay untouched
            res += ch
        elif mapping.has_key(ord(ch)):
            # try to apply custom mappings 
            res += mapping.get(ord(ch))
        elif decomposition(ch):
            normalized = normalize('NFKD', ch).strip()
            # normalized string may contain non-letter chars too. Remove them
            # normalized string may result to  more than one char
            res += ''.join([c for c in normalized if c in allowed])
        else:
            # hex string instead of unknown char
            res += "%x" % ord(ch)
    return res.encode('ascii')
      
