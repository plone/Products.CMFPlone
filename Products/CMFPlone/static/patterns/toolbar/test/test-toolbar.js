/**
 * The tests don't seem to run if we have mockup-core installed
 */

define(['core'], function(core) {
    buster.testCase("A test case", {
        "core foo": function() {
            buster.assert(false, true);
            assert.equals(core.foo(), 'string');
        }
    });
});
