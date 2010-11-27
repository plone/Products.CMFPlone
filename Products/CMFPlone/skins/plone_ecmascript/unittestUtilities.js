
function TestCaseRegistry() {
    this._testcases = new Object();

    this.registerTestCase = function(testcase, suite_name) {
        if (!testcase) {
            throw('TestCaseRegistry.registerTestCase() requires a testcase as argument');
        }
        testcase = new testcase();
        if (!suite_name) {
            suite_name = 'default';
        }
        if (!this._testcases[suite_name]) {
            this._testcases[suite_name] = new Array();
        }
        this._testcases[suite_name].push(testcase);
    }

    this.setTestSuiteFilter = function(filter) {
        if (filter) {
            this.suite_filter = new RegExp(filter, "i");
        } else {
            this.suite_filter = null;
        }
    }

    this.setTestFilter = function(filter) {
        if (filter) {
            this.test_filter = new RegExp(filter, "i");
        } else {
            this.test_filter = null;
        }
    }

    this.getFilteredTestCases = function() {
        var testcases = new Array();

        var suites = this.getFilteredTestSuitNames();
        for (var suite_index=0; suite_index < suites.length; suite_index++) {
            var suite = this._testcases[suites[suite_index]];
            for (var test_index=0; test_index < suite.length; test_index++) {
                var testcase = suite[test_index];
                if (this.test_filter) {
                    if (!this.test_filter.test(testcase.name)) {
                        continue;
                    }
                }
                testcases.push(testcase);
            }
        }

        return testcases;
    }

    this.getFilteredTestSuitNames = function() {
        var names = new Array();

        for (var suite_name in this._testcases) {
            if (this.suite_filter) {
                if (!this.suite_filter.test(suite_name)) {
                    continue;
                }
            }
            names.push(suite_name);
        }

        return names;
    }

    this.getFilteredTestNames = function() {
        var names = new Array();

        var testcases = this.getFilteredTestCases();
        for (var testcase_index in testcases) {
            names.push(testcases[testcase_index].name);
        }

        return names;
    }
}
testcase_registry = new TestCaseRegistry();

function runTestCase(testCase) {
    // append TOC entry
    var name = testCase.name;
    var toc = document.getElementById("testResultsToc");
    var results_box = document.getElementById("testResultsPlaceHolder");

    // create toc element
    var toc_item = document.createElement("li");
    toc_item.appendChild(createLink("test_ecmascripts#"+name, name+" Results", false));
    toc.appendChild(toc_item);

    // append testcase section
    var placeHolder = document.createElement("div");
    placeHolder.className = "placeholder";
    var link = createLink(name, name+" Results", true);
    var header = document.createElement("h3");
    header.appendChild(link);
    placeHolder.appendChild(header);
    results_box.appendChild(placeHolder);
    testCase.initialize(new HTMLReporter(placeHolder));
    try {
        testCase.runTests();
    } catch(e) {
        var raw = e;
        if (e.name && e.message) { // Microsoft
            e = e.name + ': ' + e.message;
        }
        placeHolder.appendChild(document.createTextNode(e));
    }
};

function runTestCases() {
    var suite_filter = document.getElementById('suite-filter').value;
    var test_filter = document.getElementById('test-filter').value;
    testcase_registry.setTestSuiteFilter(suite_filter);
    testcase_registry.setTestFilter(test_filter);
    var testcases = testcase_registry.getFilteredTestCases();

    var iframe = window.document.getElementById('iframe');
    if (typeof(iframe) != 'undefined') {
        iframe.style.display = 'block';
        // IE seems to re-initialize the iframe on designMode change,
        // destroying the blank document. But only Mozilla needs that mode.
        if (_SARISSA_IS_MOZ) {
            try {
                if (typeof(iframe.contentWindow.document.designMode) != 'undefined')
                    iframe.contentWindow.document.designMode = 'on';
            } catch(e) {
            }
        };
    }

    for (var testcase_index=0; testcase_index < testcases.length; testcase_index++) {
        runTestCase(testcases[testcase_index]);
    }

    if (iframe) {
        if (_SARISSA_IS_MOZ) {
            try {
                if (typeof(iframe.contentWindow.document.designMode) != 'undefined')
                    iframe.contentWindow.document.designMode = 'off';
            } catch(e) {
            }
        };
        iframe.style.display = 'none';
    }
}

function clearOutput() {
    clearChildNodes(document.getElementById("testResultsToc"));
    clearChildNodes(document.getElementById("testResultsPlaceHolder"));
    clearChildNodes(document.getElementById("testSandbox"));
}

function showFilteredTests() {
    var suite_filter = document.getElementById('suite-filter').value;
    var test_filter = document.getElementById('test-filter').value;
    testcase_registry.setTestSuiteFilter(suite_filter);
    testcase_registry.setTestFilter(test_filter);
    putTextInPlaceHolder(testcase_registry.getFilteredTestSuitNames().join(', ') +
                         testcase_registry.getFilteredTestNames().join(', '));
}

function showMarkup() {
    var text = document.getElementById('testResultsPlaceHolder').innerHTML
    var msg = this.document.createTextNode(text);
    var sandbox = document.getElementById("testSandbox");
    clearChildNodes(sandbox);
    sandbox.appendChild(msg);
}

function putTextInPlaceHolder(text) {
    var msg = this.document.createTextNode(text);
    var placeholder = document.getElementById("testResultsPlaceHolder");
    clearChildNodes(placeholder);
    placeholder.appendChild(msg);
}

clearChildNodes = function(oNode) {
    while(oNode.hasChildNodes()) {
        oNode.removeChild(oNode.firstChild);
    }
}

function createLink(link, desc, bName) {
    var a = document.createElement("a");

    a.setAttribute((bName?"name":"href"), link);
    if(desc) 
        a.appendChild(document.createTextNode(desc));
    return a;
}


// from the kupu test runner
var skipped_tests = [];
// Mark a specific test as failing under Opera. When Opera is
// fixed (or the test rewritten to cope with it) the flagged test
// will then fail.
function opera_is_broken(self, fname) {
    var fn = self[fname];
    if (navigator.userAgent.toLowerCase().indexOf("opera") == -1) {
        return; // Browser is not opera.
    }
    //self.debug('Invert test '+fname+'for broken browser');
    function test() {
        try {
            fn.call(self);
        } catch(e) {
            // The function threw an exception, which is what we
            // expect.
            return
        };
        self.assert(false, 'expected test '+fname+' to fail, but it passed!');
    };
    self[fname] = test;
    skipped_tests.push(fname);
}
// To demonstrate fairness, mark a specific test as failing under IE.
function ie_is_broken(self, fname) {
    var fn = self[fname];
    if (!_SARISSA_IS_IE) {
        return; // Browser is not opera.
    }
    //self.debug('Invert test '+fname+'for broken browser');
    function test() {
        try {
            fn.call(self);
        } catch(e) {
            // The function threw an exception, which is what we
            // expect.
            return
        };
        self.assert(false, 'expected test '+fname+' to fail, but it passed!');
    };
    self[fname] = test;
    skipped_tests.push(fname);
}
