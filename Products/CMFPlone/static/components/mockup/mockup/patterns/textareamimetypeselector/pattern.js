/* TextareaMimetypeSelector pattern.
 *
 *
 * Options:
 *    textareaName(string): Value of name attribute of the textarea ('')
 *    widgets(object): MimeType/PatternConfig pairs ({'text/html': {pattern: 'tinymce', patternOptions: {}}})
 *
 *
 * Documentation:
 *   # General
 *
 *   This pattern displays a mimetype selection widget for textareas. It
 *   switches the widget according to the selected mimetype.
 *
 *   ## widgets option Structure
 *
 *   Complex Object/JSON structure with MimeType/PatternConfig pairs. The
 *   MimeType is a string like "text/html". The PatternConfig is a object with
 *   a "pattern" and an optional "patternOptions" attribute. The "pattern"
 *   attribute's value is a string with the patterns name and the
 *   "patternOptions" attribute is a object with whatever options the pattern
 *   needs. For example, to use the TinyMCE pattern for the HTML mimetype, use
 *   "text/html": {"pattern": "tinymce"}
 *
 *   # Mimetype selection on textarea including text/html mimetype with TinyMCE editor.
 *
 *   {{ example-1 }}
 *
 *   # Mimetype selection on textarea with inline TinyMCE editor.
 *
 *   {{ example-2 }}
 *
  * Example: example-1
 *    <textarea name="text">
 *      <h1>hello world</h1>
 *    </textarea>
 *    <select
 *        name="text.mimeType"
 *        class="pat-textareamimetypeselector"
 *        data-pat-textareamimetypeselector='{
 *          "textareaName": "text",
 *          "widgets": {
 *            "text/html": {
 *              "pattern": "tinymce",
 *              "patternOptions": {
 *                "tiny": {
 *                  "plugins": [],
 *                  "menubar": "edit format tools",
 *                  "toolbar": " "
 *                }
 *              }
 *            }
 *          }
 *        }'
 *      >
 *      <option value="text/html">text/html</option>
 *      <option value="text/plain" selected="selected">text/plain</option>
 *    </select>
 *
 * Example: example-2
 *    <textarea name="text2">
 *      <h1>hello world</h1>
 *    </textarea>
 *    <select
 *        name="text.mimeType"
 *        class="pat-textareamimetypeselector"
 *        data-pat-textareamimetypeselector='{
 *          "textareaName": "text2",
 *          "widgets": {
 *            "text/html": {
 *              "pattern": "tinymce",
 *              "patternOptions": {
 *                "inline": true,
 *                "tiny": {
 *                  "plugins": [],
 *                  "menubar": "edit format tools",
 *                  "toolbar": " "
 *                }
 *              }
 *            }
 *          }
 *        }'
 *      >
 *      <option value="text/html">text/html</option>
 *      <option value="text/plain" selected="selected">text/plain</option>
 *    </select>
 *
 */

define([
  'jquery',
  'mockup-patterns-base',
  'pat-registry',
  'mockup-patterns-tinymce'
], function ($, Base, registry, tinymce) {
  'use strict';

  var TextareaMimetypeSelector = Base.extend({
    name: 'textareamimetypeselector',
    trigger: '.pat-textareamimetypeselector',
    textarea: undefined,
    currentWidget: undefined,
    defaults: {
      textareaName: '',
      widgets: {'text/html': {pattern: 'tinymce', patternOptions: {}}}
    },
    init: function () {
      var self = this,
          $el = self.$el,
          current;
      self.textarea = $('[name="' + self.options.textareaName + '"]');
      $el.change(function (e) {
        self.initTextarea(e.target.value);
      });
      self.initTextarea($el.val());

    },
    initTextarea: function (mimetype) {
      var self = this,
          patternConfig = self.options.widgets[mimetype],
          pattern;
      // First, destroy current
      if (self.currentWidget) {
        // The pattern must implement the destroy method.
        self.currentWidget.destroy();
      }
      // Then, setup new
      if (patternConfig) {
          pattern = new registry.patterns[patternConfig.pattern](
            self.textarea,
            patternConfig.patternOptions || {}
          );
          self.currentWidget = pattern;
      }
    }

  });

  return TextareaMimetypeSelector;
});
