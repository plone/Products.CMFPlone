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

class Splitter:

    __implements__ = ISplitter

    rx = re.compile(r"\w+", re.UNICODE)
    rxGlob = re.compile(r"\w+[\w*?]*", re.UNICODE)

    def process(self, lst):
        result = []
        for s in lst:
            # This is a hack to get the word splitting working with
            # non-unicode text. Ultimately unicode should hit this method,
            # but right now we add this hack to get it working with at least
            # utf-8 as well.
            try:
                texts = self.rx.findall(unicode(s, 'utf-8'))
                result += [t.encode('utf-8') for t in texts]
            except (UnicodeDecodeError, TypeError):
                result += self.rx.findall(s)
        return result

    def processGlob(self, lst):
        result = []
        for s in lst:
            # This is a hack to get the word splitting working with
            # non-unicode text. Ultimately unicode should hit this method,
            # but right now we add this hack to get it working with at least
            # utf-8 as well.
            try:
                texts = self.rxGlob.findall(unicode(s, 'utf-8'))
                result += [t.encode('utf-8') for t in texts]
            except (UnicodeDecodeError, TypeError):
                result += self.rxGlob.findall(s)
        return result

classImplements(Splitter, Splitter.__implements__)

try:
    element_factory.registerFactory('Word Splitter',
        'Unicode Whitespace splitter', Splitter)
except ValueError:
    # in case the splitter is already registred, ValueError is raised
    pass

if __name__ == "__main__":
    import sys
    splitter = Splitter()
    for path in sys.argv[1:]:
        f = open(path, "rb")
        buf = f.read()
        f.close()
        print path
        print splitter.process([buf])
