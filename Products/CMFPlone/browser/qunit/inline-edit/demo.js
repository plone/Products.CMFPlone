
(function($){

$(document).ready(function() {

    var server = new InlineEditMockHttpServer();
    server.start();

    // wire the widgets
    $(document).addInlineEditing('base-url');


});

})(jQuery);

