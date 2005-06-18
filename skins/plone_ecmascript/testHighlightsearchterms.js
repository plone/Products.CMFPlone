
function HighlightTermInNodeTestCase() {
    this.name = 'HighlightTermInNodeTestCase';

    this.setUp = function() {
        this.sandbox = document.getElementById("testSandbox");
        clearChildNodes(this.sandbox);

        testnode = document.createTextNode('foo bar and foostuff hamFoo or spamfoo Foo');
        this.sandbox.appendChild(testnode);
    }

    this.testManyInOneNode = function() {
        walkTextNodes(this.sandbox, highlightTermInNode, 'foo');
        var count = new Array();
        count[0] = 0;
        walkTextNodes(this.sandbox,
                      function(node, count) {
                        if (node.parentNode.className == 'highlightedSearchTerm') {
                            count[0]++;
                        }
                      }, count);
        this.assertEquals(count[0], 5);
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

    this.tearDown = function() {
        clearChildNodes(this.sandbox);
    }
}
GetSearchTermsFromURITestCase.prototype = new TestCase;
testcase_registry.registerTestCase(GetSearchTermsFromURITestCase, 'highlightsearchterms');
