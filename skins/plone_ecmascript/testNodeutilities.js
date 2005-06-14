
function WrapNodeTestCase() {
    this.name = 'WrapNodeTestCase';

    this.setUp = function() {
        this.sandbox = document.getElementById("testSandbox");
        clearChildNodes(this.sandbox);

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
testcase_registry.registerTestCase(WrapNodeTestCase, 'nodeutilities');


function NodeContainedTestCase() {
    this.name = 'NodeContainedTestCase';

    this.setUp = function() {
        this.sandbox = document.getElementById("testSandbox");
        clearChildNodes(this.sandbox);

    }

//nodeContained

    this.tearDown = function() {
        clearChildNodes(this.sandbox);
    }
}
NodeContainedTestCase.prototype = new TestCase;
testcase_registry.registerTestCase(NodeContainedTestCase, 'nodeutilities');


function FindContainerTestCase() {
    this.name = 'FindContainerTestCase';

    this.setUp = function() {
        this.sandbox = document.getElementById("testSandbox");
        clearChildNodes(this.sandbox);

    }

//findContainer

    this.tearDown = function() {
        clearChildNodes(this.sandbox);
    }
}
FindContainerTestCase.prototype = new TestCase;
testcase_registry.registerTestCase(FindContainerTestCase, 'nodeutilities');


function HasClassNameTestCase() {
    this.name = 'HasClassNameTestCase';

    this.setUp = function() {
        this.sandbox = document.getElementById("testSandbox");
        clearChildNodes(this.sandbox);

    }

//hasClassName

    this.tearDown = function() {
        clearChildNodes(this.sandbox);
    }
}
HasClassNameTestCase.prototype = new TestCase;
testcase_registry.registerTestCase(HasClassNameTestCase, 'nodeutilities');


function AddClassNameTestCase() {
    this.name = 'AddClassNameTestCase';

    this.setUp = function() {
        this.sandbox = document.getElementById("testSandbox");
        clearChildNodes(this.sandbox);

    }

//addClassName

    this.tearDown = function() {
        clearChildNodes(this.sandbox);
    }
}
AddClassNameTestCase.prototype = new TestCase;
testcase_registry.registerTestCase(AddClassNameTestCase, 'nodeutilities');


function RemoveClassNameTestCase() {
    this.name = 'RemoveClassNameTestCase';

    this.setUp = function() {
        this.sandbox = document.getElementById("testSandbox");
        clearChildNodes(this.sandbox);

    }

//removeClassName

    this.tearDown = function() {
        clearChildNodes(this.sandbox);
    }
}
RemoveClassNameTestCase.prototype = new TestCase;
testcase_registry.registerTestCase(RemoveClassNameTestCase, 'nodeutilities');


function ReplaceClassNameTestCase() {
    this.name = 'ReplaceClassNameTestCase';

    this.setUp = function() {
        this.sandbox = document.getElementById("testSandbox");
        clearChildNodes(this.sandbox);

    }

//replaceClassName

    this.tearDown = function() {
        clearChildNodes(this.sandbox);
    }
}
ReplaceClassNameTestCase.prototype = new TestCase;
testcase_registry.registerTestCase(ReplaceClassNameTestCase, 'nodeutilities');

