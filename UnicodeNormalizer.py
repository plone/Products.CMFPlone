from unicodedata import normalize, decomposition
import string

# UnicodeData.txt does not contain normalization of Greek letters.
mapping_greek = {
912: 'i', 913: 'A', 914: 'B', 915: 'G', 916: 'D', 917: 'E', 918: 'Z',
919: 'I', 920: 'TH', 921: 'I', 922: 'K', 923: 'L', 924: 'M', 925: 'N',
926: 'KS', 927: 'O', 928: 'P', 929: 'R', 931: 'S', 932: 'T', 933: 'Y',
934: 'F', 936: 'PS', 937: 'O', 938: 'I', 939: 'Y', 940: 'a', 941: 'e',
943: 'i', 944: 'y', 945: 'a', 946: 'b', 947: 'g', 948: 'd', 949: 'e',
950: 'z', 951: 'i', 952: 'th', 953: 'i', 954: 'k', 955: 'l', 956: 'm',
957: 'n', 958: 'ks', 959: 'o', 960: 'p', 961: 'r', 962: 's', 963: 's',
964: 't', 965: 'y', 966: 'f', 968: 'ps', 969: 'o', 970: 'i', 971: 'y',
972: 'o', 973: 'y' }

# Russian character mapping thanks to Xenru.
mapping_russian = {
1081 : 'i', 1049 : 'I', 1094 : 'c', 1062 : 'C',
1091 : 'u', 1059 : 'U', 1082 : 'k', 1050 : 'K',
1077 : 'e', 1045 : 'E', 1085 : 'n', 1053 : 'N',
1075 : 'g', 1043 : 'G', 1096 : 'sh', 1064 : 'SH',
1097 : 'sch', 1065 : 'SCH', 1079 : 'z', 1047 : 'Z',
1093 : 'h', 1061 : 'H', 1098 : '', 1066 : '',
1092 : 'f', 1060 : 'F', 1099 : 'y', 1067 : 'Y',
1074 : 'v', 1042 : 'V', 1072 : 'a', 1040 : 'A',
1087 : 'p', 1055 : 'P', 1088 : 'r', 1056 : 'R',
1086 : 'o', 1054 : 'O', 1083 : 'l', 1051 : 'L',
1076 : 'd', 1044 : 'D', 1078 : 'zh', 1046 : 'ZH',
1101 : 'e', 1069 : 'E', 1103 : 'ya', 1071 : 'YA',
1095 : 'ch', 1063 : 'CH', 1089 : 's', 1057 : 'S',
1084 : 'm', 1052 : 'M', 1080 : 'i', 1048 : 'I',
1090 : 't', 1058 : 'T', 1100 : '', 1068 : '',
1073 : 'b', 1041 : 'B', 1102 : 'yu', 1070 : 'YU',
1105 : 'yo', 1025 : 'YO' }

# Turkish character mapping.
mapping_turkish = {
286 : 'G', 287 : 'g', 304 : 'I', 305 : 'i', 350 : 'S', 351 : 's' }

# Latin characters with accents, etc.
mapping_latin_chars = {
138 : 's', 140 : 'O', 142 : 'z', 154 : 's', 156 : 'o', 158 : 'z', 159 : 'Y',
192 : 'A', 193 : 'A', 194 : 'A', 195 : 'a', 196 : 'A', 197 : 'A', 198 : 'E',
199 : 'C', 200 : 'E', 201 : 'E', 202 : 'E', 203 : 'E', 204 : 'I', 205 : 'I',
206 : 'I', 207 : 'I', 208 : 'D', 209 : 'N', 210 : 'O', 211 : 'O', 212 : 'O',
213 : 'O', 214 : 'O', 215 : 'x', 216 : 'O', 217 : 'U', 218 : 'U', 219 : 'U',
220 : 'U', 221 : 'Y', 223 : 's', 224 : 'a', 225 : 'a', 226 : 'a', 227 : 'a',
228 : 'a', 229 : 'a', 230 : 'e', 231 : 'c', 232 : 'e', 233 : 'e', 234 : 'e',
235 : 'e', 236 : 'i', 237 : 'i', 238 : 'i', 239 : 'i', 240 : 'd', 241 : 'n',
242 : 'o', 243 : 'o', 244 : 'o', 245 : 'o', 246 : 'o', 248 : 'o', 249 : 'u',
250 : 'u', 251 : 'u', 252 : 'u', 253 : 'y', 255 : 'y' }

# Feel free to add new user-defined mapping. Don't forget to update mapping dict
# with your dict.
mapping = {}
mapping.update(mapping_greek)
mapping.update(mapping_russian)
mapping.update(mapping_latin_chars)
mapping.update(mapping_turkish)

# On OpenBSD string.whitespace has a non-standard implementation
# See http://dev.plone.org/plone/ticket/4704 for details
whitespace = ''.join([c for c in string.whitespace if ord(c) < 128])
allowed = string.ascii_letters + string.digits + string.punctuation + whitespace

def normalizeUnicode(text):
    """
    This method is used for normalization of unicode characters to the base ASCII
    letters. Output is ASCII encoded string (or char) with only ASCII letters,
    digits, punctuation and whitespace characters. Case is preserved.
    """
    if not isinstance(text, unicode):
        raise TypeError('must pass Unicode argument to normalizeUnicode()')

    res = ''
    for ch in text:
        if ch in allowed:
            # ASCII chars, digits etc. stay untouched
            res += ch
        else:
            ordinal = ord(ch)
            if mapping.has_key(ordinal):
                # try to apply custom mappings
                res += mapping.get(ordinal)
            elif decomposition(ch):
                normalized = normalize('NFKD', ch).strip()
                # normalized string may contain non-letter chars too. Remove them
                # normalized string may result to  more than one char
                res += ''.join([c for c in normalized if c in allowed])
            else:
                # hex string instead of unknown char
                res += "%x" % ordinal
    return res.encode('ascii')

