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
//testcase_registry.registerTestCase(NodeContainedTestCase, 'nodeutilities');


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
//testcase_registry.registerTestCase(FindContainerTestCase, 'nodeutilities');


function HasClassNameTestCase() {
    this.name = 'HasClassNameTestCase';

    this.setUp = function() {
        this.sandbox = document.getElementById("testSandbox");
        clearChildNodes(this.sandbox);

        this.node = document.createElement("div");
        this.node.className = "foo bar  hamEggs ";
        this.sandbox.appendChild(this.node);
    }

    this.testAtStart = function() {
        this.assertTrue(hasClassName(this.node, 'foo'));
    }

    this.testAtEnd = function() {
        this.assertTrue(hasClassName(this.node, 'hamEggs'));
    }

    this.testNoPartialMatch = function() {
        this.assertFalse(hasClassName(this.node, 'ham'));
        this.assertFalse(hasClassName(this.node, 'Eggs'));
    }

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

        this.node = document.createElement("div");
        this.sandbox.appendChild(this.node);
    }

    this.testAdd = function() {
        addClassName(this.node, 'spam');
        this.assertEquals(this.node.className, 'spam');
        addClassName(this.node, 'foo');
        this.assertEquals(this.node.className, 'spam foo');
    }

    this.testDoubleAdd = function() {
        addClassName(this.node, 'spam');
        addClassName(this.node, 'spam');
        this.assertEquals(this.node.className, 'spam');
    }

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

        this.node = document.createElement("div");
        this.node.className = "foo bar  hamEggs ";
        this.sandbox.appendChild(this.node);
    }

    this.testRemove = function() {
        removeClassName(this.node, 'bar');
        var current = jQuery.trim(this.node.className).replace(/\s+/g, ' ');
        this.assertTrue(current.indexOf('bar') < 0, current);
    }

    this.testCleanup = function() {
        removeClassName(this.node, 'bar');
        var current = jQuery.trim(this.node.className).replace(/\s+/g, ' ');
        this.assertEquals(current, "foo hamEggs", current);
    }

    this.testPartial = function() {
        removeClassName(this.node, 'ham');
        var current = jQuery.trim(this.node.className).replace(/\s+/g, ' ');
        this.assertEquals(current, "foo bar hamEggs", current);
    }

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

        this.node = document.createElement("div");
        this.node.className = "foo bar  hamEggs ";
        this.sandbox.appendChild(this.node);
    }

    this.testReplace = function() {
        replaceClassName(this.node, 'bar', 'spam');
        this.assertTrue(this.node.className.indexOf('bar') < 0, this.node.className);
        this.assertFalse(this.node.className.indexOf('spam') < 0, this.node.className);
    }

    this.testCleanup = function() {
        replaceClassName(this.node, 'bar', 'spam');
        var current = jQuery.trim(this.node.className).replace(/\s+/g, ' ');
        this.assertEquals(current, "foo hamEggs spam", current);
    }

    this.testPartial = function() {
        replaceClassName(this.node, 'ham', 'spam');
        var current = jQuery.trim(this.node.className).replace(/\s+/g, ' ');
        this.assertEquals(current, "foo bar hamEggs", current);
    }

    this.testMissing = function() {
        replaceClassName(this.node, 'bacon', 'spam');
        var current = jQuery.trim(this.node.className).replace(/\s+/g, ' ');
        this.assertEquals(current, "foo bar hamEggs", current);
    }

    this.testIgnoreMissing = function() {
        replaceClassName(this.node, 'bacon', 'spam', true);
        var current = jQuery.trim(this.node.className).replace(/\s+/g, ' ');
        this.assertEquals(current, "foo bar hamEggs spam", current);
    }

    this.tearDown = function() {
        clearChildNodes(this.sandbox);
    }
}
ReplaceClassNameTestCase.prototype = new TestCase;
testcase_registry.registerTestCase(ReplaceClassNameTestCase, 'nodeutilities');


function GetInnerTextTestCase() {
    this.name = 'GetInnerTextTestCase';

    this.setUp = function() {
        this.sandbox = document.getElementById("testSandbox");
        clearChildNodes(this.sandbox);

        var node = document.createElement("span");
        node.appendChild(document.createTextNode("foo"));
        this.sandbox.appendChild(node);
        var node = document.createElement("div");
        node.appendChild(document.createTextNode("bar"));
        this.sandbox.appendChild(node);
    }

    this.testGetInnerTextFast = function() {
        text = getInnerTextFast(this.sandbox);
        this.assert(text.indexOf('foo') >= 0);
        this.assert(text.indexOf('bar') >= 0);
    }

    this.testGetInnerTextCompatible = function() {
        text = getInnerTextCompatible(this.sandbox);
        this.assertEquals(text, "foobar");
    }

    this.testGetInnerTextFastVsHtml = function() {
        text = getInnerTextFast(this.sandbox);
        html = this.sandbox.innerHTML;
        this.assertNotEquals(text, html);
    }

    this.testGetInnerTextCompatibleVsHtml = function() {
        text = getInnerTextCompatible(this.sandbox);
        html = this.sandbox.innerHTML;
        this.assertNotEquals(text, html);
    }

    this.tearDown = function() {
        clearChildNodes(this.sandbox);
    }
}
GetInnerTextTestCase.prototype = new TestCase;
testcase_registry.registerTestCase(GetInnerTextTestCase, 'nodeutilities');

