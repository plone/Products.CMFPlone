
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
        this.server = new MoreMockHttpServer(this.handle_ajax);

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
    },


    //
    // Actual mock response can be produced here.
    //
    handle_ajax: function(request, ajax_heartbeat) {
        log('HANDLE', request);
        if (request.urlParts.file == 'base-url@@replaceField') {
            request.setResponseHeader("Content-Type", "text/xml; charset=UTF-8");
            if (ajax_heartbeat == 0) {
                /* response recorded from the server */
                var response_text= 
                    '<?xml version="1.0" encoding="utf-8" ?>' +
                    '<kukit>' +
                    '<!-- xmlns="http://www.kukit.org/commands/1.1" removed from kukit tag as it' +
                    '     breaks IE6 XP SP3 -->' +
                    '<commands>' +
                    '<command selector=".portalMessage" name="setStyle" selectorType="css">' +
                    '    <param name="name">display</param>' +
                    '    <param name="value">none</param>' +
                    '</command>' +
                    '<command selector="kssPortalMessage" name="replaceInnerHTML" selectorType="htmlid">' +
                    '    <param name="html"><![CDATA[<dt>Info</dt><dd></dd>]]></param>' +
                    '    <param name="withKssSetup">True</param>' +
                    '</command>' +
                    '<command selector="kssPortalMessage" name="setAttribute" selectorType="htmlid">' +
                    '    <param name="name">class</param>' +
                    '    <param name="value">portalMessage info</param>' +
                    '</command>' +
                    '<command selector="kssPortalMessage" name="setStyle" selectorType="htmlid">' +
                    '    <param name="name">display</param>' +
                    '    <param name="value">none</param>' +
                    '</command>' +
                    '<command selector="parent-fieldname-title" name="replaceHTML" selectorType="htmlid">' +
                    '    <param name="html"><![CDATA[<h1 id="parent-fieldname-title" class="documentFirstHeading kssattr-atfieldname-title kssattr-templateId-kss_generic_macros kssattr-macro-title-field-view">' +
                    '<form class="field inlineForm enableUnloadProtection enableUnlockProtection" id="kss-inlineform-title">' +
                    '<div class="field ArchetypesStringWidget  kssattr-atfieldname-title" id="archetypes-fieldname-title">' +
                    '<span></span>' +
                    '<label class="formQuestion" for="title">Title</label>' +
                    '<span class="required" title="Required" style="color: #f00;">' +
                    '            &#x25a0;' +
                    '          </span>' +
                    '<div class="formHelp" id="title_help"></div>' +
                    '<div class="fieldErrorBox"></div>' +
                    '<input type="text" name="title" class="blurrable firstToFocus" id="title" value="Welcome to Plone" size="30" maxlength="255" />' +
                    '</div>' +
                    '<div class="formControls">' +
                    '<input name="kss-save" value="Save" type="button" class="context" />' +
                    '<input name="kss-cancel" value="Cancel" type="button" class="standalone" />' +
                    '</div>' +
                    '</form>' +
                    '</h1>]]></param>' +
                    '    <param name="withKssSetup">True</param>' +
                    '</command>' +
                    '<command selector="#parent-fieldname-title .firstToFocus" name="focus" selectorType="">' +
                    '</command>' +
                    '</commands>' +
                    '</kukit>';
                request.receive(200, response_text);

                log('OK OK OK', request);
            } else if (ajax_heartbeat == 4) {
                // simulate an error
                request.receive(500, 'Error');
            }
        } else {
            request.receive(404, 'Not Found in Mock Server');
        }
        log('HANDLE finished', request);
    }


});


/*
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
*/

test("Click", function() {

    $(document).addInlineEditing('base-url');

    $('#test1').simulate('click');

    log('test over.');
    $(document).removeInlineEditing();

});



})(jQuery);

