define([
  'expect',
  'jquery',
  'pat-registry',
  'mockup-patterns-textareamimetypeselector',
  'mockup-patterns-tinymce'
], function(expect, $, registry, textareamimetypeselector, tinymce) {
  'use strict';

  window.mocha.setup('bdd');
  $.fx.off = true;

/* ================================
   TEST: Textarea MimeType Selector
  ================================= */

  describe('Textarea MimeType Selector', function () {

    afterEach(function() {
      $('body').empty();
    });

    it('Switching changes widget', function() {

      var dom_structure =
        '<textarea name="text">hello world</textarea>' +
        '<select' +
        '    name="text.mimeType"' +
        '    class="pat-textareamimetypeselector"' +
        '    data-pat-textareamimetypeselector=\'{' +
        '      "textareaName": "text",' +
        '      "widgets": {' +
        '        "text/html": {' +
        '          "pattern": "tinymce",' +
        '          "patternOptions": {' +
        '            "tiny": {' +
        '              "plugins": [],' +
        '              "menubar": "edit format tools",' +
        '              "toolbar": " "' +
        '            }' +
        '          }' +
        '        }' +
        '      }' +
        '    }\'' +
        '  >' +
        '  <option value="text/html">text/html</option>' +
        '  <option value="text/plain" selected="selected">text/plain</option>' +
        '</select>';

      var $doc = $(dom_structure).appendTo('body');
      registry.scan($doc);

      var $el = $("[name='text.mimeType']");
      var $textarea = $("[name='text']");

      // Initially, text/plain is selected and textarea should be visible.
      expect($textarea.is(":visible")).to.be.ok();
      // But TinyMCE shouldn't be there
      expect($(".mce-tinymce").length).to.be(0);
      // Value should be at it's initial state
      expect($textarea.val()).to.be.equal("hello world");

      // Now, select text/html
      $el.val("text/html").change();

      // Textarea should be hidden
      expect($textarea.is(":hidden")).to.be.ok();
      // And TinyMCE should be shown
      expect($(".mce-tinymce").is(":visible")).to.be.ok();

      // Switching back to text/plain should destroy TinyMCE
      $el.val("text/plain").change();
      expect($textarea.is(":visible")).to.be.ok();
      expect($(".mce-tinymce").length).to.be(0);
      // Unfortunately, TinyMCE changes the value just by loading TinyMCE.
      expect($textarea.val()).to.be.equal("<p>hello world</p>");

    });

    it('Switching changes widget with inline TinyMCE', function() {

      var dom_structure =
        '<textarea name="text">hello world</textarea>' +
        '<select' +
        '    name="text.mimeType"' +
        '    class="pat-textareamimetypeselector"' +
        '    data-pat-textareamimetypeselector=\'{' +
        '      "textareaName": "text",' +
        '      "widgets": {' +
        '        "text/html": {' +
        '          "pattern": "tinymce",' +
        '          "patternOptions": {' +
        '            "inline": true,' +
        '            "tiny": {' +
        '              "plugins": [],' +
        '              "menubar": "edit format tools",' +
        '              "toolbar": " "' +
        '            }' +
        '          }' +
        '        }' +
        '      }' +
        '    }\'' +
        '  >' +
        '  <option value="text/html">text/html</option>' +
        '  <option value="text/plain" selected="selected">text/plain</option>' +
        '</select>';

      var $doc = $(dom_structure).appendTo('body');
      registry.scan($doc);

      var $el = $("[name='text.mimeType']");
      var $textarea = $("[name='text']");

      // Initially, text/plain is selected and textarea should be visible.
      expect($textarea.is(":visible")).to.be.ok();
      // But TinyMCE shouldn't be there
      expect($(".mce-content-body[contenteditable='true']").length).to.be(0);
      // Value should be at it's initial state
      expect($textarea.val()).to.be.equal("hello world");

      // change the textarea's value
      $textarea.val("hello mellow");

      // Now, select text/html
      $el.val("text/html").change();

      // Textarea should be hidden
      expect($textarea.is(":hidden")).to.be.ok();
      // And TinyMCE should be shown
      expect($(".mce-content-body[contenteditable='true']").is(":visible")).to.be.ok();

      // Switching back to text/plain should destroy TinyMCE
      $el.val("text/plain").change();
      expect($textarea.is(":visible")).to.be.ok();
      expect($(".mce-content-body[contenteditable='true']").length).to.be(0);
      // Unfortunately, TinyMCE changes the value just by loading TinyMCE.
      expect($textarea.val()).to.be.equal("<p>hello mellow</p>");

      // switching back to TinyMCE loads it again
      $el.val("text/html").change();
      expect($textarea.is(":hidden")).to.be.ok();
      expect($(".mce-content-body[contenteditable='true']").is(":visible")).to.be.ok();

    });

  });
});
