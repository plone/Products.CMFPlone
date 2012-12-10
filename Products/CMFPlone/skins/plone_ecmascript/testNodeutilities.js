// TestCase comes from ecmaunit.js

function WrapNodeTestCase() {
    this.name = 'WrapNodeTestCase';

    this.setUp = function() {
        this.sandbox = document.getElementById("testSandbox");
        window.clearChildNodes(this.sandbox);

        var node = document.createElement("span");
        node.appendChild(document.createTextNode("Hallo, Welt!"));
        this.sandbox.appendChild(node);
    };

    this.testPreconditions = function() {
        var node = this.sandbox.firstChild;
        this.assert(node);
        this.assertEquals(node.tagName, 'SPAN');
        this.assert(!node.className);
    };

    this.testPostconditions = function() {
        var node = this.sandbox.firstChild;
        window.wrapNode(node, 'div', 'foo');
        this.assert(node);
        this.assertEquals(node.tagName, 'SPAN');
        this.assertFalse(node.className);
    };

    this.testWrapper = function() {
        var node = this.sandbox.firstChild;
        window.wrapNode(node, 'div', 'foo');
        var wrapper = this.sandbox.firstChild;
        this.assert(wrapper);
        this.assertEquals(wrapper.tagName, 'DIV');
        this.assertEquals(wrapper.className, 'foo');
    };

    this.testWrapped = function() {
        var node = this.sandbox.firstChild;
        window.wrapNode(node, 'div', 'foo');
        var wrapper = this.sandbox.firstChild;
        var  wrapped = wrapper.firstChild;
        this.assert(wrapped);
        this.assertEquals(wrapped.tagName, 'SPAN');
        this.assertFalse(wrapped.className);
    };

    this.tearDown = function() {
        window.clearChildNodes(this.sandbox);
    };
}
WrapNodeTestCase.prototype = new window.TestCase();
window.testcase_registry.registerTestCase(WrapNodeTestCase, 'nodeutilities');


function NodeContainedTestCase() {
    this.name = 'NodeContainedTestCase';

    this.setUp = function() {
        this.sandbox = document.getElementById("testSandbox");
        window.clearChildNodes(this.sandbox);

    };

//nodeContained

    this.tearDown = function() {
        window.clearChildNodes(this.sandbox);
    };
}
NodeContainedTestCase.prototype = new window.TestCase();
//testcase_registry.registerTestCase(NodeContainedTestCase, 'nodeutilities');


function FindContainerTestCase() {
    this.name = 'FindContainerTestCase';

    this.setUp = function() {
        this.sandbox = document.getElementById("testSandbox");
        window.clearChildNodes(this.sandbox);

    };

//findContainer

    this.tearDown = function() {
        window.clearChildNodes(this.sandbox);
    };
}
FindContainerTestCase.prototype = new window.TestCase();
//testcase_registry.registerTestCase(FindContainerTestCase, 'nodeutilities');


function HasClassNameTestCase() {
    this.name = 'HasClassNameTestCase';

    this.setUp = function() {
        this.sandbox = document.getElementById("testSandbox");
        window.clearChildNodes(this.sandbox);

        this.node = document.createElement("div");
        this.node.className = "foo bar  hamEggs ";
        this.sandbox.appendChild(this.node);
    };

    this.testAtStart = function() {
        this.assertTrue(window.hasClassName(this.node, 'foo'));
    };

    this.testAtEnd = function() {
        this.assertTrue(window.hasClassName(this.node, 'hamEggs'));
    };

    this.testNoPartialMatch = function() {
        this.assertFalse(window.hasClassName(this.node, 'ham'));
        this.assertFalse(window.hasClassName(this.node, 'Eggs'));
    };

    this.tearDown = function() {
        window.clearChildNodes(this.sandbox);
    };
}
HasClassNameTestCase.prototype = new window.TestCase();
window.testcase_registry.registerTestCase(HasClassNameTestCase, 'nodeutilities');


function AddClassNameTestCase() {
    this.name = 'AddClassNameTestCase';

    this.setUp = function() {
        this.sandbox = document.getElementById("testSandbox");
        window.clearChildNodes(this.sandbox);

        this.node = document.createElement("div");
        this.sandbox.appendChild(this.node);
    };

    this.testAdd = function() {
        window.addClassName(this.node, 'spam');
        this.assertEquals(this.node.className, 'spam');
        window.addClassName(this.node, 'foo');
        this.assertEquals(this.node.className, 'spam foo');
    };

    this.testDoubleAdd = function() {
        window.addClassName(this.node, 'spam');
        window.addClassName(this.node, 'spam');
        this.assertEquals(this.node.className, 'spam');
    };

    this.tearDown = function() {
        window.clearChildNodes(this.sandbox);
    };
}
AddClassNameTestCase.prototype = new window.TestCase();
window.testcase_registry.registerTestCase(AddClassNameTestCase, 'nodeutilities');


function RemoveClassNameTestCase() {
    this.name = 'RemoveClassNameTestCase';

    this.setUp = function() {
        this.sandbox = document.getElementById("testSandbox");
        window.clearChildNodes(this.sandbox);

        this.node = document.createElement("div");
        this.node.className = "foo bar  hamEggs ";
        this.sandbox.appendChild(this.node);
    };

    this.testRemove = function() {
        window.removeClassName(this.node, 'bar');
        var current = jQuery.trim(this.node.className).replace(/\s+/g, ' ');
        this.assertTrue(current.indexOf('bar') < 0, current);
    };

    this.testCleanup = function() {
        window.removeClassName(this.node, 'bar');
        var current = jQuery.trim(this.node.className).replace(/\s+/g, ' ');
        this.assertEquals(current, "foo hamEggs", current);
    };

    this.testPartial = function() {
        window.removeClassName(this.node, 'ham');
        var current = jQuery.trim(this.node.className).replace(/\s+/g, ' ');
        this.assertEquals(current, "foo bar hamEggs", current);
    };

    this.tearDown = function() {
        window.clearChildNodes(this.sandbox);
    };
}
RemoveClassNameTestCase.prototype = new window.TestCase();
window.testcase_registry.registerTestCase(RemoveClassNameTestCase, 'nodeutilities');


function ReplaceClassNameTestCase() {
    this.name = 'ReplaceClassNameTestCase';

    this.setUp = function() {
        this.sandbox = document.getElementById("testSandbox");
        window.clearChildNodes(this.sandbox);

        this.node = document.createElement("div");
        this.node.className = "foo bar  hamEggs ";
        this.sandbox.appendChild(this.node);
    };

    this.testReplace = function() {
        window.replaceClassName(this.node, 'bar', 'spam');
        this.assertTrue(this.node.className.indexOf('bar') < 0, this.node.className);
        this.assertFalse(this.node.className.indexOf('spam') < 0, this.node.className);
    };

    this.testCleanup = function() {
        window.replaceClassName(this.node, 'bar', 'spam');
        var current = jQuery.trim(this.node.className).replace(/\s+/g, ' ');
        this.assertEquals(current, "foo hamEggs spam", current);
    };

    this.testPartial = function() {
        window.replaceClassName(this.node, 'ham', 'spam');
        var current = jQuery.trim(this.node.className).replace(/\s+/g, ' ');
        this.assertEquals(current, "foo bar hamEggs", current);
    };

    this.testMissing = function() {
        window.replaceClassName(this.node, 'bacon', 'spam');
        var current = jQuery.trim(this.node.className).replace(/\s+/g, ' ');
        this.assertEquals(current, "foo bar hamEggs", current);
    };

    this.testIgnoreMissing = function() {
        window.replaceClassName(this.node, 'bacon', 'spam', true);
        var current = jQuery.trim(this.node.className).replace(/\s+/g, ' ');
        this.assertEquals(current, "foo bar hamEggs spam", current);
    };

    this.tearDown = function() {
        window.clearChildNodes(this.sandbox);
    };
}
ReplaceClassNameTestCase.prototype = new window.TestCase();
window.testcase_registry.registerTestCase(ReplaceClassNameTestCase, 'nodeutilities');


function GetInnerTextTestCase() {
    this.name = 'GetInnerTextTestCase';

    this.setUp = function() {
        this.sandbox = document.getElementById("testSandbox");
        window.clearChildNodes(this.sandbox);

        var node = document.createElement("span");
        node.appendChild(document.createTextNode("foo"));
        this.sandbox.appendChild(node);
        var node2 = document.createElement("div");
        node2.appendChild(document.createTextNode("bar"));
        this.sandbox.appendChild(node2);
    };

    this.testGetInnerTextFast = function() {
        var text = window.getInnerTextFast(this.sandbox);
        this.assert(text.indexOf('foo') >= 0);
        this.assert(text.indexOf('bar') >= 0);
    };

    this.testGetInnerTextCompatible = function() {
        var text = window.getInnerTextCompatible(this.sandbox);
        this.assertEquals(text, "foobar");
    };

    this.testGetInnerTextFastVsHtml = function() {
        var text = window.getInnerTextFast(this.sandbox);
        var html = this.sandbox.innerHTML;
        this.assertNotEquals(text, html);
    };

    this.testGetInnerTextCompatibleVsHtml = function() {
        var text = window.getInnerTextCompatible(this.sandbox);
        var html = this.sandbox.innerHTML;
        this.assertNotEquals(text, html);
    };

    this.tearDown = function() {
        window.clearChildNodes(this.sandbox);
    };
}
GetInnerTextTestCase.prototype = new window.TestCase();
window.testcase_registry.registerTestCase(GetInnerTextTestCase, 'nodeutilities');

