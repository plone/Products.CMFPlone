/*
Validate form fields when they lose focus.
*/

/*jslint white:false, onevar:true, undef:true, nomen:true, eqeqeq:true, plusplus:true, bitwise:true, regexp:true, newcap:true, immed:true, strict:false, browser:true */
/*global jQuery:false, document:false, window:false, location:false */

jQuery(function() {

	var render_error = function($field, errmsg) {
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
  $('input.blurrable,select.blurrable,textarea.blurrable').live('blur', function() {
  	var $input = $(this);
  	var $field = $input.closest('.field');
  	var uid = $field.attr('data-uid');
  	var fname = $field.attr('data-fieldname');
  	var value = $input.val();

  	$.post('at_validate_field', {uid: uid, fname: fname, value: value}, function(data) {
  		render_error($field, data.errmsg);
  	});
  });

  // z3c.form
  var z3cform_validate_field = function(input) {
  	var $input = $(input);
  	var $field = $input.closest('.field');
  	var $form = $field.closest('form');
  	var fset = $input.closest('fieldset').attr('data-fieldset');
  	var fname = $field.attr('data-fieldname');

  	$form.ajaxSubmit({
  		url: $form.attr('action') + '/@@z3cform_validate_field',
  		data: {fname: fname, fset: fset},
  		iframe: false,
  		success: function(data) {
				render_error($field, data.errmsg);
  		},
  		dataType: 'json'
    });
  };
  $('.z3cformInlineValidation input[type="text"]').live('blur', function() { z3cform_validate_field(this); });
  $('.z3cformInlineValidation input[type="password"]').live('blur', function() { z3cform_validate_field(this); });
  $('.z3cformInlineValidation input[type="checkbox"]').live('blur', function() { z3cform_validate_field(this); });
  $('.z3cformInlineValidation input[type="radio"]').live('blur', function() { z3cform_validate_field(this); });
  $('.z3cformInlineValidation select').live('blur', function() { z3cform_validate_field(this); });
  $('.z3cformInlineValidation textarea').live('blur', function() { z3cform_validate_field(this); });

});
