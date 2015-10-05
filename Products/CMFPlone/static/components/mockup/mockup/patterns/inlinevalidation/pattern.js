/* Inline Validation pattern.
 *
 * Options:
 *    type(string): The type of form generating library. Either z3c.form, formlib or archetypes
 *
 * Documentation:
 *
 *    # z3c.form
 *
 *    {{ example-1 }}
 *
 * Example: example-1
 *    <div class="pat-inlinevalidation" data-pat-upload='{"type": "z3c.form"}'>
 *      <input id="form-widgets-IDublinCore-title"
 *             name="form.widgets.IDublinCore.title"
 *             class="text-widget required textline-field"
 *             value="Welcome to Plone" type="text">
 *    </div>
 */

define([
  'jquery',
  'mockup-patterns-base'
], function ($, Base) {
  'use strict';

  var InlineValidation = Base.extend({
    name: 'inlinevalidation',
    trigger: '.pat-inlinevalidation',

    render_error: function ($field, errmsg) {
       var $errbox = $('div.fieldErrorBox', $field);
       if (errmsg !== '') {
           $field.addClass('error');
           $errbox.html(errmsg);
       } else {
           $field.removeClass('error');
           $errbox.html('');
       }
    },

    append_url_path: function (url, extra) {
        // Add '/extra' on to the end of the URL, respecting querystring
        var i, ret, urlParts = url.split(/\?/);
        ret = urlParts[0];
        if (ret[ret.length - 1] !== '/') { ret += '/'; }
        ret += extra;
        for (i = 1; i < urlParts.length; i+=1) {
            ret += '?' + urlParts[i];
        }
        return ret;
    },

    validate_archetypes_field: function (input) {
        var $input = $(input),
            $field = $input.closest('.field'),
            uid = $field.attr('data-uid'),
            fname = $field.attr('data-fieldname'),
            value = $input.val();

        // value is null for empty multiSelection select, turn it into a [] instead
        // so it does not break at_validate_field
        if ($input.prop('multiple') && value === null) {
            value = $([]).serialize();
        }

        // if value is an Array, it will be send as value[]=value1&value[]=value2 by $.post
        // turn it into something that will be useable or value will be omitted from the request
        var traditional;
        var params = $.param({uid: uid, fname: fname, value: value}, traditional = true);
        if ($field && uid && fname) {
            $.post($('base').attr('href') + '/at_validate_field', params, function (data) {
                this.render_error($field, data.errmsg);
            });
        }
    },

    validate_formlib_field: function (input) {
        var $input = $(input),
            $field = $input.closest('.field'),
            $form = $field.closest('form'),
            fname = $field.attr('data-fieldname');

        $form.ajaxSubmit({
            url: this.append_url_path($form.attr('action'), '@@formlib_validate_field'),
            data: {fname: fname},
            iframe: false,
            success: $.proxy(function (data) {
                this.render_error($field, data.errmsg);
            }, this),
            dataType: 'json'
        });
    },

    validate_z3cform_field: function (input) {
        var $input = $(input),
            $field = $input.closest('.field'),
            $form = $field.closest('form'),
            fset = $input.closest('fieldset').attr('data-fieldset'),
            fname = $field.attr('data-fieldname');

        if (fname) {
            $form.ajaxSubmit({
                url: this.append_url_path($form.attr('action'), '@@z3cform_validate_field'),
                data: {fname: fname, fset: fset},
                iframe: false,
                success: $.proxy(function (data) {
                    this.render_error($field, data.errmsg);
                }, this),
                dataType: 'json'
            });
        }
    },

    init: function () {

      this.$el.find(
          'input[type="text"], ' +
          'input[type="password"], ' +
          'input[type="checkbox"], ' +
          'select, ' +
          'textarea').on('blur', 

          $.proxy(function (ev) {
            if (this.options.type === 'archetypes') {
              this.validate_archetypes_field(ev.target);
            } else if (this.options.type === 'z3c.form') {
              this.validate_z3cform_field(ev.target);
            } else if (this.options.type === 'formlib') {
              this.validate_formlib_field(ev.target);
            }
          }, this));
      },
  });
  return InlineValidation;
});
