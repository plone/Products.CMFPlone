/* This looks for input fields with a title and the class "inputLabel". When
   the field is empty the title will be set as it's value and the class
   "inputLabel" will be replaced with the class "inputLabelActive" to make
   it styleable with css. When the field gets focus, the content is removed
   and the class "inputLabelActive" is removed. When the field looses focus,
   then the game starts again if the value is empty, if not then the field
   is left as is. When the form is submitted, the values are cleaned up
   before they are sent to the server.
   
   Provides global: ploneInputLabel
*/

/*jslint nomen:false */

var ploneInputLabel = {
    focus: function() {
        var t = jQuery(this);
        if (t.hasClass('inputLabelActive') && t.val() === t.attr('title')) {
            t.val('').removeClass('inputLabelActive');
        }
        if (t.hasClass('inputLabelPassword')) {
            ploneInputLabel._setInputType(t.removeClass('inputLabelPassword'), 
                'password').focus().bind('blur.ploneInputLabel', ploneInputLabel.blur);
        }
    },

    blur: function(e) {
        var t = jQuery(this);
        if (t.is(':password[value=""]')) {
            t = ploneInputLabel._setInputType(this, 'text')
                .addClass('inputLabelPassword')
                .bind('focus.ploneInputLabel', ploneInputLabel.focus);
            if (e.originalEvent && e.originalEvent.explicitOriginalTarget) {
                // Re-focus next element in Gecko browsers
                jQuery(e.originalEvent.explicitOriginalTarget).trigger('focus!');
            }
        }
        if (!t.val()) {
            t.addClass('inputLabelActive').val(t.attr('title'));
        }
    },

    submit: function() {
        jQuery('input[title].inputLabelActive').trigger('focus.ploneInputLabel');
    },

    _setInputType: function(elem, ntype) {
        var $ = jQuery,
            otype,
            nelem;
        // You can't change the type on an <input> element, but you can 
        // replace the element itself. Following .replace dance is to make it
        // work correctly in IE, as usual.
        otype = new RegExp('type="?' + $(elem).attr('type') + '"?');
        nelem = $($('<div></div>').append($(elem).clone()).html()
                .replace(otype, '').replace(/\/?>/, 'type="' + ntype + '" />'));
        $(elem).replaceWith(nelem);
        return nelem;
    }
};

jQuery(function($) {
    $('form:has(input[title].inputLabel)').submit(ploneInputLabel.submit);
    $('input[title].inputLabel')
        .bind('focus.ploneInputLabel', ploneInputLabel.focus)
        .bind('blur.ploneInputLabel', ploneInputLabel.blur)
        .trigger('blur.ploneInputLabel'); // Apply the title
});
