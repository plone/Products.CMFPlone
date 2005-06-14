
function TestCaseRegistry() {
    this._testcases = new Object();

    this.registerTestCase = function(testcase, suite_name) {
        if (!testcase) {
            throw('TestCaseRegistry.registerTestCase() requires a testcase as argument');
        }
        if (!suite_name) {
            suite_name = 'default';
        }
        if (!this._testcases[suite_name]) {
            this._testcases[suite_name] = new Array();
        }
        this._testcases[suite_name].push(testcase);
    }

    this.getFilteredTestCases = function() {
        var testcases = new Array();

        for (suite_name in this._testcases) {
            var suite = this._testcases[suite_name];
            for (test_index in suite) {
                testcases.push(suite[test_index]);
            }
        }

        return testcases;
    }

    this.getTestSuitNames = function() {
        var names = new Array();

        for (suite_name in this._testcases) {
            names.push(suite_name);
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
    var testcases = testcase_registry.getFilteredTestCases();
    for (testcase_index in testcases) {
        testcase = testcases[testcase_index];
        runTestCase(new testcase());
    }
}

function clearOutput() {
    clearChildNodes(document.getElementById("testResultsToc"));
    clearChildNodes(document.getElementById("testResultsPlaceHolder"));
    clearChildNodes(document.getElementById("testSandbox"));
}

function showTestSuites() {
    putTextInPlaceHolder(testcase_registry.getTestSuitNames());
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

