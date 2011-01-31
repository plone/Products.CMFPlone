
(function($){

var log = function() {
    if (window.console && console.log) {
        // log for FireBug or WebKit console
        console.log(Array.prototype.slice.call(arguments));
    }
};

module("CMFPlone inline-edit", {

    setup: function() {
        var self = this;

        // Create a mock server for testing ajax.
        this.server = new InlineEditMockHttpServer();

        // Start the server
        this.server.start();
    },

    teardown: function() {
        // Stop the server
        this.server.stop();
        // make sure to unbind
        // because it binds to the document, so Qunit's test separation
        // would not work.
        $(document).removeInlineEditing();
    }

});


test("Bind", function() {

    $(document).addInlineEditing('http://base-url');
    $(document).removeInlineEditing();

});

test("Bind to more elements, fails", function() {

    raises(function() {
        $('p').addInlineEditing('http://base-url');
    }, 'Raises exception');

});

test("Bind to window", function() {

    $(window).addInlineEditing('http://base-url');

});

test("Bind to other dom nodes, fails", function() {

    raises(function() {
        $('p').eq(0).addInlineEditing('http://base-url');
    }, 'Raises exception');

});

test("Bind again, fails", function() {

    $(document).addInlineEditing('http://base-url');

    raises(function() {
        $(document).addInlineEditing('http://base-url');
    }, 'Raises exception');

    raises(function() {
        $(window).addInlineEditing('http://base-url');
    }, 'Raises exception');

    $(document).removeInlineEditing();
    $(document).addInlineEditing('http://base-url');

});

test("Click", function() {

    $(document).addInlineEditing('base-url');

    $('#parent-fieldname-title').simulate('click');

    log('test over.');
    $(document).removeInlineEditing();

});



})(jQuery);

