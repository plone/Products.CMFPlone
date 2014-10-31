/*
Validate form fields when they lose focus.
*/

/*jslint white:false, onevar:true, undef:true, nomen:true, eqeqeq:true, plusplus:true, bitwise:true, regexp:true, newcap:true, immed:true, strict:false, browser:true */
/*global jQuery:false, document:false, window:false, location:false */

jQuery(function ($) {

    var render_error = function ($field, errmsg) {
        var $errbox = $('div.fieldErrorBox', $field);
        if (errmsg !== '') {
            $field.addClass('error');
            $errbox.html(errmsg);
        } else {
            $field.removeClass('error');
            $errbox.html('');
        }
    };

    // Archetypes
    $(document).on(
            'blur',
            '.field input.blurrable, ' +
            '.field select.blurrable, ' +
            '.field textarea.blurrable',
            function () {
        var $input = $(this),
            $field = $input.closest('.field'),
            uid = $field.attr('data-uid'),
            fname = $field.attr('data-fieldname'),
            value = $input.val();

        // value is null for empty multiSelection select, turn it into a [] instead
        // so it does not break at_validate_field
        if ($input.attr('multiple') === 'multiple' && value === null) {
            value = $([]).serialize();
        }

        // if value is an Array, it will be send as value[]=value1&value[]=value2 by $.post
        // turn it into something that will be useable or value will be considered omitted from the request
        params = $.param({uid: uid, fname: fname, value: value}, traditional=true)

        if ($field && uid && fname) {
            $.post($('base').attr('href') + '/at_validate_field', params, function (data) {
                render_error($field, data.errmsg);
            });
        }
    });

    // formlib
    var formlib_validate_field = function (input) {
        var $input = $(input),
            $field = $input.closest('.field'),
            $form = $field.closest('form'),
            fname = $field.attr('data-fieldname');

        $form.ajaxSubmit({
            url: $form.attr('action') + '/@@formlib_validate_field',
            data: {fname: fname},
            iframe: false,
            success: function (data) {
                render_error($field, data.errmsg);
            },
            dataType: 'json'
        });
    };
    $(document).on(
        'blur',
        '.formlibInlineValidation input[type="text"], ' +
        '.formlibInlineValidation input[type="password"], ' +
        '.formlibInlineValidation input[type="checkbox"], ' +
        '.formlibInlineValidation input[type="radio"], ' +
        '.formlibInlineValidation select, ' +
        '.formlibInlineValidation textarea',
        function () { formlib_validate_field(this); });

    // z3c.form
    var z3cform_validate_field = function (input) {
        var $input = $(input),
            $field = $input.closest('.field'),
            $form = $field.closest('form'),
            fset = $input.closest('fieldset').attr('data-fieldset'),
            fname = $field.attr('data-fieldname');

        if (fname) {
            $form.ajaxSubmit({
                url: $form.attr('action') + '/@@z3cform_validate_field',
                data: {fname: fname, fset: fset},
                iframe: false,
                success: function (data) {
                    render_error($field, data.errmsg);
                },
                dataType: 'json'
            });
        }
    };
    $(document).on(
        'blur',
        '.z3cformInlineValidation input[type="text"], ' +
        '.z3cformInlineValidation input[type="password"], ' +
        '.z3cformInlineValidation input[type="checkbox"], ' +
        '.z3cformInlineValidation input[type="radio"], ' +
        '.z3cformInlineValidation select, ' +
        '.z3cformInlineValidation textarea',
        function () { z3cform_validate_field(this); });

});
