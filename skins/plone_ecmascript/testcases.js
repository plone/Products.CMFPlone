
function runTestCases() {
    runTestCase(new WrapNodeTestCase());
}

clearChildNodes = function(oNode) {
    while(oNode.hasChildNodes()) {
        oNode.removeChild(oNode.firstChild);
    }
}
