## Copyright (c) 2002, Infrae. All rights reserved.

## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:

##   1. Redistributions of source code must retain the above copyright
##      notice, this list of conditions and the following disclaimer.

##   2. Redistributions in binary form must reproduce the above copyright
##      notice, this list of conditions and the following disclaimer in
##      the documentation and/or other materials provided with the
##      distribution.

##   3. Neither the name of Infrae nor the names of its contributors may
##      be used to endorse or promote products derived from this software
##      without specific prior written permission.

## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL INFRAE OR
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
## PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
## LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
## NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from utils import classImplements
from Products.ZCTextIndex.ISplitter import ISplitter
from Products.ZCTextIndex.PipelineFactory import element_factory

import re
enc = 'utf-8'

class Splitter:

    __implements__ = ISplitter

    rx_L = re.compile(r"\w+", re.LOCALE)
    rxGlob_L = re.compile(r"\w+[\w*?]*", re.LOCALE)

    rx_U = re.compile(r"\w+", re.UNICODE)
    rxGlob_U = re.compile(r"\w+[\w*?]*", re.UNICODE)

    def process(self, lst):
        result = []
        for s in lst:
            # This is a hack to get the word splitting working with
            # non-unicode text.
            try:
                if not isinstance(s, unicode):
                    s = unicode(s, enc)
            except (UnicodeDecodeError, TypeError):
                # Fall back to locale aware splitter
                result += self.rx_L.findall(s)
            else:
                words = self.rx_U.findall(s)
                result += [w.encode(enc) for w in words]
        return result

    def processGlob(self, lst):
        result = []
        for s in lst:
            # This is a hack to get the word splitting working with
            # non-unicode text.
            try:
                if not isinstance(s, unicode):
                    s = unicode(s, enc)
            except (UnicodeDecodeError, TypeError):
                # Fall back to locale aware splitter
                result += self.rxGlob_L.findall(s)
            else:
                words = self.rxGlob_U.findall(s)
                result += [w.encode(enc) for w in words]
        return result

classImplements(Splitter, Splitter.__implements__)

try:
    element_factory.registerFactory('Word Splitter',
        'Unicode Whitespace splitter', Splitter)
except ValueError:
    # In case the splitter is already registered, ValueError is raised
    pass

class CaseNormalizer:

    def process(self, lst):
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

