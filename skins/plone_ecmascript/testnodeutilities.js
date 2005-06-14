
function WrapNodeTestCase(){
    this.name = 'WrapNodeTestCase';

    this.setUp = function() {
        this.sandbox = document.getElementById("testSandbox");

        var node = document.createElement("span");
        node.appendChild(document.createTextNode("Hallo, Welt!"));
        this.sandbox.appendChild(node);
    }

    this.testPreconditions = function() {
        var node = this.sandbox.firstChild;
        this.assert(node);
        this.assertEquals(node.tagName, 'SPAN');
        this.assert(!node.className);
    }

    this.testPostconditions = function() {
        var node = this.sandbox.firstChild;
        wrapNode(node, 'div', 'foo');
        this.assert(node);
        this.assertEquals(node.tagName, 'SPAN');
        this.assertFalse(node.className);
    }

    this.testWrapper = function() {
        var node = this.sandbox.firstChild;
        wrapNode(node, 'div', 'foo');
        wrapper = this.sandbox.firstChild;
        this.assert(wrapper);
        this.assertEquals(wrapper.tagName, 'DIV');
        this.assertEquals(wrapper.className, 'foo');
    }

    this.testWrapped = function() {
        var node = this.sandbox.firstChild;
        wrapNode(node, 'div', 'foo');
        wrapper = this.sandbox.firstChild;
        wrapped = wrapper.firstChild;
        this.assert(wrapped);
        this.assertEquals(wrapped.tagName, 'SPAN');
        this.assertFalse(wrapped.className);
    }

    this.tearDown = function() {
        clearChildNodes(this.sandbox);
    }
}
WrapNodeTestCase.prototype = new TestCase;
