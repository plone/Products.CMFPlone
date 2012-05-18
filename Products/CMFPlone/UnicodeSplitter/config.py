# -*- coding: utf-8 -*-
"""
config.py

Created by Manabu Terada, CMScom on 2009-08-08.
"""
import re

STOP_WORD = []

## Setting, adding langs.
rangetable = dict(
    #ascii = u"a-zA-Z0-9_",
    #digit = u"\d",

    # U+AC00-D7AF       Hangul Syllables        ハングル音節文字
    hangul = u"\uAC00-\uD7AF",

    # U+30A0-30FF       Katakana        片仮名
    # U+3040-309F       Hiragana        平仮名
    #kana = u"\u3040-\u30FF",
    # hiragana = u"\u3040-\u309F\u30FC",
    # katakana = u"\u30A0-\u30FF",

    # U+4E00-9FFF     CJK Unified Ideographs  CJK統合漢字
    # U+3400-4DBF     CJK Unified Ideographs Extension A  CJK統合漢字拡張A
    # U+F900-FAFF     CJK Compatibility Ideographs    CJK互換漢字
    # ideo = u"\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF",

    cj = u"\u3040-\u30FF\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF",
    thai = u"\u0E00-\u0E7F", # U+0E00-0E7F Thai タイ文字
)
## End of setting.


## Splitting core.
ps = rangetable.values()
allp = u"".join(ps)
glob_true = u"[^%s]([^%s]|[\*\?])*|" % (allp, allp) + u"|".join([u"[%s]+" % (x, )  for x in ps])

glob_false = u"[^%s]+|" % allp + u"|".join(u"[%s]+" % x  for x in ps)

rx_all = re.compile(ur"[%s]"%allp, re.UNICODE)
rx_U = re.compile(r"\w+", re.UNICODE)
rxGlob_U = re.compile(r"\w+[\w*?]*", re.UNICODE)

rx_L = re.compile(r"\w+", re.LOCALE)
rxGlob_L = re.compile(r"\w+[\w*?]*", re.LOCALE)

# pattern = re.compile(u"[a-zA-Z0-9_]+|[\uac00-\ud7af]+|[\u4E00-\u9FFF\u3400-\u4dbf\uf900-\ufaff\u3040-\u30ff]+", re.UNICODE)
# pattern_g = re.compile(u"[a-zA-Z0-9_]+[*?]*|[\u4E00-\u9FFF\u3400-\u4dbf\uf900-\ufaff\u3040-\u30ff\uac00-\ud7af]+[*?]*", re.UNICODE)

pattern = re.compile(glob_false, re.UNICODE)
pattern_g = re.compile(glob_true, re.UNICODE)
