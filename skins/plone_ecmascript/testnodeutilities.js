
function WrapNodeTestCase(){
    this.name = 'WrapNodeTestCase';

    this.testSimple = function(){
        var sandbox = document.getElementById("testSandbox");
        var node = document.createElement("span");
        
        node.appendChild(document.createTextNode("Hallo, Welt!"));
        sandbox.appendChild(node);
        // check preconditions
        this.assert(node);
        this.assertEquals(node.tagName, 'SPAN');
        this.assert(!node.className);
        // do it
        wrapNode(node, 'div', 'foo');
        // test node itself again
        this.assert(node);
        this.assertEquals(node.tagName, 'SPAN');
        this.assert(!node.className);
        // test the wrapper
        wrapper = sandbox.firstChild;
        this.assert(wrapper);
        this.assertEquals(wrapper.tagName, 'DIV');
        this.assertEquals(wrapper.className, 'foo');

        clearChildNodes(sandbox);
    }
}
WrapNodeTestCase.prototype = new TestCase;
