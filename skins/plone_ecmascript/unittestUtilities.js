
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
        for (suite_index in suites) {
            var suite = this._testcases[suites[suite_index]];
            for (var test_index in suite) {
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
    testCase.runTests();
};

function runTestCases() {
    var suite_filter = document.getElementById('suite-filter').value;
    var test_filter = document.getElementById('test-filter').value;
    testcase_registry.setTestSuiteFilter(suite_filter);
    testcase_registry.setTestFilter(test_filter);
    var testcases = testcase_registry.getFilteredTestCases();
    for (var testcase_index in testcases) {
        runTestCase(testcases[testcase_index]);
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
    putTextInPlaceHolder(testcase_registry.getFilteredTestSuitNames() +
                         testcase_registry.getFilteredTestNames());
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

