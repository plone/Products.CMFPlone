
(function($){

var log = function() {
    if (window.console && console.log) {
        // log for FireBug or WebKit console
        console.log(Array.prototype.slice.call(arguments));
    }
};

$(document).ready(function() {

    var server = new InlineEditMockHttpServer();
    var starting_value = 'Welcome to Plone!';
    $('#parent-fieldname-title').text(starting_value);
    server.set_server_state({
        value: starting_value
    });
    server.start();


    // wire the widgets
    $(document).addInlineEditing('base-url');

});

})(jQuery);

