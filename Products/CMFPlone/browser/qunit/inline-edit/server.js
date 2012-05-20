
(function($){

var log = function() {
    if (window.console && console.log) {
        // log for FireBug or WebKit console
        console.log(Array.prototype.slice.call(arguments));
    }
};

window.InlineEditMockHttpServer = function() {
    MoreMockHttpServer.apply(this, arguments);
};
$.extend(InlineEditMockHttpServer.prototype, MoreMockHttpServer.prototype, {

    _decodeParm: function(txt) {
        if (txt) {
            txt = txt.replace(/\+/g, ' ');
            txt = decodeURIComponent(txt);
        }
        return txt;
    },

    getRequestParm: function(request, key) {
        value = request.urlParts.queryKey[key];
        value = this._decodeParm(value);
        return value;
    },


    //
    // Implement a mock server for inline editing functionality.
    //
    handle: function(request, server_state) {
        var server_choose = server_state.choose || 'default';
        if (server_choose == 'error') {
            // simulate an error
            request.receive(500, 'Error');
        } else if (request.urlParts.file == 'base-url@@replaceField') {
            request.setResponseHeader("Content-Type", "text/xml; charset=UTF-8");
            //if (server_choose == 'default') {
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
                    '<input type="text" name="title" class="blurrable firstToFocus" id="title" value="' + server_state.value + '" size="30" maxlength="255" />' +
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

            //}
        } else if (request.urlParts.file == 'base-url@@saveField') {
            request.setResponseHeader("Content-Type", "text/xml; charset=UTF-8");
            //if (server_choose == 'default') {
                var fieldname = this.getRequestParm(request, 'fieldname');
                var value = this.getRequestParm(request, fieldname);
                server_state.value = value;
                var response_text= 
                    '<?xml version="1.0" encoding="utf-8" ?>' +
                    '<kukit>' +
                    '<commands>' +
                    '<command selector="parent-fieldname-' + fieldname + '" name="replaceHTML" selectorType="htmlid">' +
                    '    <param name="html"><![CDATA[<p id="parent-fieldname-' + fieldname + '" class="documentFirstHeading kssattr-atfieldname-' + fieldname + ' kssattr-templateId-kss_generic_macros kssattr-macro-title-field-view inlineEditable">' +
                    '                    ' + value +
                    '                </p>]]></param>' +
                    '    <param name="withKssSetup">True</param>' +
                    '</command>' +
                    '</commands>' +
                    '</kukit>'
                request.receive(200, response_text);

            //}
        } else if (request.urlParts.file == 'base-url@@replaceWithView') {
            request.setResponseHeader("Content-Type", "text/xml; charset=UTF-8");
            //if (server_choose == 'default') {
                var response_text= 
                    '<?xml version="1.0" encoding="utf-8" ?>' +
                    '<kukit>' +
                    '<!-- xmlns="http://www.kukit.org/commands/1.1" removed from kukit tag as it' +
                    '     breaks IE6 XP SP3 -->' +
                    '<commands>' +
                    '<command selector="parent-fieldname-title" name="replaceHTML" selectorType="htmlid">' +
                    '    <param name="html"><![CDATA[<p id="parent-fieldname-title" class="documentFirstHeading kssattr-atfieldname-title kssattr-templateId-kss_generic_macros kssattr-macro-title-field-view inlineEditable">' +
                    '                   ' + server_state.value +
                    '                </p>]]></param>' +
                    '    <param name="withKssSetup">True</param>' +
                    '</command>' +
                    '</commands>' +
                    '</kukit>'
                request.receive(200, response_text);
            //}
        } else {
            request.receive(404, 'Not Found in Mock Server');
        }
    }


});


})(jQuery);
    
