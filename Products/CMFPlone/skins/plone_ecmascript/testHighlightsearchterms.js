
function HighlightTermInNodeTestCase() {
    this.name = 'HighlightTermInNodeTestCase';

    this.setUp = function() {
        this.sandbox = document.getElementById("testSandbox");
        clearChildNodes(this.sandbox);

        testnode = document.createTextNode('foo bar and foostuff hamFoo or spamfoo Foo');
        this.sandbox.appendChild(testnode);
    }

    this.testManyInOneNode = function() {
        highlightTermInNode(this.sandbox.firstChild, 'foo');
        count = jq(this.sandbox).find('span.highlightedSearchTerm').length;
        this.assertEquals(count, 5);
    }

    this.tearDown = function() {
        clearChildNodes(this.sandbox);
    }
}
HighlightTermInNodeTestCase.prototype = new TestCase;
testcase_registry.registerTestCase(HighlightTermInNodeTestCase, 'highlightsearchterms');


function HighlightSearchTermsTestCase() {
    this.name = 'HighlightSearchTermsTestCase';

    this.setUp = function() {
        this.sandbox = document.getElementById("testSandbox");
        clearChildNodes(this.sandbox);

        testnode = document.createTextNode('foo bar and foostuff hamFoo or spamfoo Foo');
        this.sandbox.appendChild(testnode);
    }

    this.testEndlessLoop = function() {
        highlightSearchTerms(['','site:plone.org','plone','rules'], this.sandbox)
    }

    this.tearDown = function() {
        clearChildNodes(this.sandbox);
    }
}
HighlightSearchTermsTestCase.prototype = new TestCase;
testcase_registry.registerTestCase(HighlightSearchTermsTestCase, 'highlightsearchterms');


function GetSearchTermsFromURITestCase() {
    this.name = 'GetSearchTermsFromURITestCase';

    this.setUp = function() {
        this.sandbox = document.getElementById("testSandbox");
        clearChildNodes(this.sandbox);
    }

    this.testDecoding = function() {
        var uri = "?searchterm=foo%20bar";
        var terms = getSearchTermsFromURI(uri);
        this.assertEquals(terms.length, 2, 'number of searchterms in '+uri);
        this.assertEquals(terms[0], 'foo');
        this.assertEquals(terms[1], 'bar');
    }

    this.testPlusSeperator = function() {
        var uri = "?searchterm=foo+bar";
        var terms = getSearchTermsFromURI(uri);
        this.assertEquals(terms.length, 2, 'number of searchterms in '+uri);
        this.assertEquals(terms[0], 'foo');
        this.assertEquals(terms[1], 'bar');
    }

    this.testNoEmptyTerms = function() {
        var uri = "?searchterm=%20bar";
        var terms = getSearchTermsFromURI(uri);
        this.assertEquals(terms.length, 1, 'number of searchterms in '+uri);
        this.assertEquals(terms[0], 'bar');
    }

    this.tearDown = function() {
        clearChildNodes(this.sandbox);
    }
}
GetSearchTermsFromURITestCase.prototype = new TestCase;
testcase_registry.registerTestCase(GetSearchTermsFromURITestCase, 'highlightsearchterms');

if (window.decodeReferrer) {
    function GetSearchTermsFromReferrerTestCase() {
        this.name = 'GetSearchTermsFromReferrerTestCase';

        this.setUp = function() {
            this.sandbox = document.getElementById("testSandbox");
            clearChildNodes(this.sandbox);
        }

        this.testGoogleDecoding = function() {
            var ref = 'http://google.de/search?hl=de&q=google+referrer+string&btnG=Google-Suche&meta='
            var terms = decodeReferrer(ref);
            this.assertEquals(terms.length, 3, 'number of searchterms in '+ref);
            this.assertEquals(terms[0], 'google');
            this.assertEquals(terms[1], 'referrer');
            this.assertEquals(terms[2], 'string');
        }

        this.testExtraQuery = function() {
            var ref = 'http://google.de/search?q=google+referrer+string&aq=something';
            var terms = decodeReferrer(ref);
            this.assertEquals(terms.length, 3, 'number of searchterms in '+ref);
            this.assertEquals(terms[0], 'google');
            this.assertEquals(terms[1], 'referrer');
            this.assertEquals(terms[2], 'string');
        }

        this.testExtraQuery2 = function() {
            var ref = 'http://google.de/search?aq=something&q=google+referrer+string';
            var terms = decodeReferrer(ref);
            this.assertEquals(terms.length, 3, 'number of searchterms in '+ref);
            this.assertEquals(terms[0], 'google');
            this.assertEquals(terms[1], 'referrer');
            this.assertEquals(terms[2], 'string');
        }

        this.tearDown = function() {
            clearChildNodes(this.sandbox);
        }
    }
    GetSearchTermsFromReferrerTestCase.prototype = new TestCase;
    testcase_registry.registerTestCase(GetSearchTermsFromReferrerTestCase, 'highlightsearchterms');
}
