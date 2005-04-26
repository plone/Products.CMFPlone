/*
Copyright (c) 2003-2004, EcmaUnit Contributors
All rights reserved.

LICENSE

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:


    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above
      copyright notice, this list of conditions and the following
      disclaimer in the documentation and/or other materials provided
      with the distribution.

    * Neither the name of EcmaUnit nor the names of its contributors may
      be used to endorse or promote products derived from this
      software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.



CREDITS

This package was written by Guido Wesdorp (guido@infrae.com), with the help of 
Philipp von Weitershausen (philikon@philikon.de).

Inspiration came from the jsUnit package by Edward Hieatt (edward@jsunit.net),
a unit test suite for JavaScript, and Python's pyunit package written by
Steve Purcell.

   Object-oriented prototype-based unit test suite
*/

function TestCase() {
    /* a single test case */
    this.name = 'TestCase';

    this.initialize = function(reporter) {
        // this array's contents will be displayed when done (if it
        // contains anything)
        this._exceptions = new Array();
        this._reporter = reporter;
    };

    this.setUp = function() {
        /* this will be called on before each test method that is ran */
    };

    this.tearDown = function() {
        /* this will be called after each test method that has been ran */
    };

    this.assertEquals = function(var1, var2) {
        /* assert whether 2 vars have the same value */
        if (var1 && var1.toSource && var2 && var2.toSource) {
            if (var1.toSource() != var2.toSource()) {
                throw('Assertion failed: ' + var1 + ' != ' + var2);
            };
        } else {
            if (var1 != var2) {
                throw('Assertion failed: ' + var1 + ' != ' + var2);
            };
        };
    };

    this.assert = function(statement) {
        /* assert whether a variable resolves to true */
        if (!statement) {
            throw('Assertion ' + statement.toString ? statement.toString() : statement + ' failed');
        };
    };

    this.assertTrue = this.assert;

    this.assertFalse = function(statement) {
        /* assert whether a variable resolves to false */
        if (statement) {
            throw('Assertion ' + statement.toString() + ' failed');
        };
    };

    this.assertThrows = function(func, exception, context) {
        /* assert whether a certain exception is raised */
        if (!context) {
            context = null;
        };
        if (!exception) {
            return;
        };
        var exception_thrown = false;
        try {
            func.apply(context, arguments);
        } catch(e) {
            if (exception.toSource && e.toSource) {
                exception = exception.toSource();
                e = e.toSource();
            } else if (exception.toString && e.toString) {
                exception = exception.toString();
                e = e.toString();
            };
            if (e != exception) {
                throw('Function threw the wrong exception ' + 
                        e.toString() + ', while expecting ' + 
                        exception.toString());
            };
            exception_thrown = true;
        };
        if (!exception_thrown) {
            if (exception) {
                throw("function didn\'t raise exception \'" + 
                        exception.toString() + "'");
            } else {
                throw('function didn\'t raise exception');
            };
        };
    };

    this.runTests = function() {
        /* find all methods of which the name starts with 'test'
            and call them */
        var ret = this._runHelper();
	this._reporter.summarize(ret[0], ret[1], this._exceptions);
    };

    this._runHelper = function() {
        /* this actually runs the tests
            return value is an array [total tests ran, total time spent (ms)]
        */
        var now = new Date();
        var starttime = now.getTime();
        var numtests = 0;
        for (var attr in this) {
            if (attr.substr(0, 4) == 'test') {
                this.setUp();
                try {
                    this[attr]();
                    this._reporter.reportSuccess(this.name, attr);
                } catch(e) {
                    this._reporter.reportError(this.name, attr, e);
                    this._exceptions.push(new Array(this.name, attr, e));
                };
                this.tearDown();
                numtests++;
            };
        };
        var now = new Date();
        var totaltime = now.getTime() - starttime;
        return new Array(numtests, totaltime);
    };

};

function TestSuite(reporter) {
    /* run a suite of tests */
    this._reporter = reporter;
    this._tests = new Array();
    this._exceptions = new Array();
    
    this.registerTest = function(test) {
        /* register a test */
        if (!test) {
            throw('TestSuite.registerTest() requires a testcase as argument');
        };
        this._tests.push(test);
    };

    this.runSuite = function() {
        /* run the suite */
        var now = new Date();
        var starttime = now.getTime();
        var testsran = 0;
        for (var i=0; i < this._tests.length; i++) {
            var test = new this._tests[i]();
            test.initialize(this._reporter);
            testsran += test._runHelper()[0];
            // the TestCase class handles output of dots and Fs, but we
            // should take care of the exceptions
            if (test._exceptions.length) {
                for (var j=0; j < test._exceptions.length; j++) {
                    // attr, exc in the org array, so here it becomes
                    // name, attr, exc
                    var excinfo = test._exceptions[j];
                    this._exceptions.push(excinfo);
                };
            };
        };
        var now = new Date();
        var totaltime = now.getTime() - starttime;
        this._reporter.summarize(testsran, totaltime, this._exceptions);
    };
};

function StdoutReporter(verbose) {
  this.verbose = verbose; //XXX verbose not yet supported

    this.reportSuccess = function(testcase, attr) {
        /* report a test success */
        print('.');
    };

    this.reportError = function(testcase, attr, exception) {
        /* report a test failure */
        print('F');
    };

    this.summarize = function(numtests, time, exceptions) {
        print(numtests + ' tests ran in ' + time / 1000.0 + ' seconds');
        if (exceptions.length) {
            for (var i=0; i < exceptions.length; i++) {
                var testcase = exceptions[i][0];
                var attr = exceptions[i][1];
                var exception = exceptions[i][2];
                print(testcase + '.' + attr + ', exception: ' + exception);
            };
            print('NOT OK!');
        } else {
            print('OK!');
        };
    };
};

function HTMLReporter(outputelement, verbose) {
    this.outputelement = outputelement;
    this.document = outputelement.ownerDocument;
    this.verbose = verbose; //XXX verbose not yet supported

    this.reportSuccess = function(testcase, attr) {
        /* report a test success */
        // a single dot looks rather small
        var dot = this.document.createTextNode('+');
        this.outputelement.appendChild(dot);
    };

    this.reportError = function(testcase, attr, exception) {
        /* report a test failure */
        var f = this.document.createTextNode('F');
        this.outputelement.appendChild(f);
    };

    this.summarize = function(numtests, time, exceptions) {
        /* write the result output to the html node */
        var p = this.document.createElement('p');
        var text = this.document.createTextNode(numtests + ' tests ran in ' + 
                                                time / 1000.0 + ' seconds');
        p.appendChild(text);
        this.outputelement.appendChild(p);
        if (exceptions.length) {
            for (var i=0; i < exceptions.length; i++) {
                var testcase = exceptions[i][0];
                var attr = exceptions[i][1];
                var exception = exceptions[i][2];
                var div = this.document.createElement('div');
                var text = this.document.createTextNode(
                    testcase + '.' + attr + ', exception: ' + exception);
                div.appendChild(text);
                div.style.color = 'red';
                this.outputelement.appendChild(div);
            };
            var div = this.document.createElement('div');
            var text = this.document.createTextNode('NOT OK!');
            div.appendChild(text);
            div.style.backgroundColor = 'red';
            div.style.color = 'black';
            div.style.fontWeight = 'bold';
            div.style.textAlign = 'center';
            div.style.marginTop = '1em';
            this.outputelement.appendChild(div);
        } else {
            var div = this.document.createElement('div');
            var text = this.document.createTextNode('OK!');
            div.appendChild(text);
            div.style.backgroundColor = 'lightgreen';
            div.style.color = 'black';
            div.style.fontWeight = 'bold';
            div.style.textAlign = 'center';
            div.style.marginTop = '1em';
            this.outputelement.appendChild(div);
        };
    };
};
