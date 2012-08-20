#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
splitter.py

Created by Mikio Hokari, CMScom and Manabu Terada, CMScom on 2009-09-30.
"""
import unicodedata

from zope.interface import implements

from Products.ZCTextIndex.ISplitter import ISplitter
from Products.ZCTextIndex.PipelineFactory import element_factory

from Products.CMFPlone.UnicodeSplitter.config import rx_U, rxGlob_U, \
            rx_L, rxGlob_L, rx_all, pattern, pattern_g
from plone.i18n.normalizer.base import baseNormalize


def bigram(u, limit=1):
    """ Split into bi-gram.
    limit arg describes ending process.
    If limit = 0 then
        日本人-> [日本,本人, 人]
        金 -> [金]
    If limit = 1 then
        日本人-> [日本,本人]
        金 -> []
    """
    return [u[i:i + 2] for i in xrange(len(u) - limit)]


def process_str_post(s, enc='utf-8'):
    """Receive str, remove ? and *, then return str.
    If decode gets successful, process str as unicode.
    If decode gets failed, process str as ASCII.
    """
    try:
        if not isinstance(s, unicode):
            uni = s.decode(enc, "strict")
        else:
            uni = s
    except UnicodeDecodeError:
        return s.replace("?", "").replace("*", "")
    try:
        return uni.replace(u"?", u"").replace(u"*", u"").encode(enc, "strict")
    except UnicodeEncodeError:
        return s.replace("?", "").replace("*", "")


def process_str(s, enc='utf-8'):
    """Receive str and encoding, then return the list
    of str as bi-grammed result.
    Decode str into unicode and pass it to process_unicode.
    When decode failed, return the result splitted per word.
    Splitting depends on locale specified by rx_L.
    """
    try:
        if not isinstance(s, unicode):
            uni = s.decode(enc, "strict")
        else:
            uni = s
    except UnicodeDecodeError:
        return rx_L.findall(s)
    bigrams = process_unicode(uni)
    return [x.encode(enc, "strict") for x in bigrams]


def process_str_glob(s, enc='utf-8'):
    """Receive str and encoding, then return the list
    of str considering glob processing.
    Decode str into unicode and pass it to process_unicode_glob.
    When decode failed, return the result splitted per word.
    Splitting depends on locale specified by rxGlob_L.
    """
    try:
        if not isinstance(s, unicode):
            uni = s.decode(enc, "strict")
        else:
            uni = s
    except UnicodeDecodeError:
        return rxGlob_L.findall(s)
    bigrams = process_unicode_glob(uni)
    return [x.encode(enc, "strict") for x in bigrams]


def process_unicode(uni):
    """Receive unicode string, then return a list of unicode
    as bi-grammed result.
    """
    normalized = unicodedata.normalize('NFKC', uni)
    for word in rx_U.findall(normalized):
        swords = [g.group() for g in pattern.finditer(word)]
        for sword in swords:
            if not rx_all.match(sword[0]):
                yield sword
            else:
                for x in bigram(sword, 0):
                    yield x


def process_unicode_glob(uni):
    """Receive unicode string, then return a list of unicode
    as bi-grammed result.  Considering globbing.
    """
    normalized = unicodedata.normalize('NFKC', uni)
    for word in rxGlob_U.findall(normalized):
        swords = [g.group() for g in pattern_g.finditer(word)
                  if g.group() not in u"*?"]
        for i, sword in enumerate(swords):
            if not rx_all.match(sword[0]):
                yield sword
            else:
                if i == len(swords) - 1:
                    limit = 1
                else:
                    limit = 0
                if len(sword) == 1:
                    bigramed = [sword + u"*"]
                else:
                    bigramed = bigram(sword, limit)
                for x in bigramed:
                    yield x


class Splitter(object):

    implements(ISplitter)

    def process(self, lst):
        """ Will be called when indexing.
        Receive list of str, make it bi-grammed, then return
        the list of str.
        """
        return [x for s in lst for x in process_str(s)]

    def processGlob(self, lst):
        """ Will be called once when searching.
        Receive list of str, make it bi-grammed considering
        globbing, then return the list of str.
        """
        return [x for s in lst for x in process_str_glob(s)]

    def process_post_glob(self, lst):
        """ Will be called twice when searching.
        Receive list of str, Remove ? and *, then return
        the list of str.
        """
        return [process_str_post(s) for s in lst]

try:
    element_factory.registerFactory('Word Splitter',
        'Unicode Whitespace splitter', Splitter)
except ValueError:
    # In case the splitter is already registered, ValueError is raised
    pass


class CaseNormalizer(object):

    def process(self, lst):
        enc = 'utf-8'
        result = []
        for s in lst:
            # This is a hack to get the normalizer working with
            # non-unicode text.
            try:
                if not isinstance(s, unicode):
                    s = unicode(s, enc)
            except (UnicodeDecodeError, TypeError):
                result.append(s.lower())
            else:
                result.append(s.lower().encode(enc))

        return result

try:
    element_factory.registerFactory('Case Normalizer',
        'Unicode Case Normalizer', CaseNormalizer)
except ValueError:
    # In case the normalizer is already registered, ValueError is raised
    pass


class I18NNormalizer(object):

    def process(self, lst):
        enc = 'utf-8'
        result = []
        for s in lst:
            try:
                if not isinstance(s, unicode):
                    s = unicode(s, enc)
            except (UnicodeDecodeError, TypeError):
                pass

            if 0x41 <= ord(s[0]) <= 0x24F:
                # normalize latin words
                # words beginning with a latin character
                # are commonly latin words
                s = baseNormalize(s).lower()

            result.append(s.lower())

        return result

try:
    element_factory.registerFactory('Case Normalizer',
        'Unicode Ignoring Accents Case Normalizer', I18NNormalizer)
except ValueError:
    # In case the normalizer is already registered, ValueError is raised
    pass
