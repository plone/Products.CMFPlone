/* Select2 pattern.
 *
 * Options:
 *    separator(string): Analagous to the separator constructor parameter from Select2. Defines a custom separator used to distinguish the tag values. Ex: a value of ";" will allow tags and initialValues to have values separated by ";" instead of the default ",". (',')
 *    initialValues(string): This can be a json encoded string, or a list of id:text values. Ex: Red:The Color Red,Orange:The Color Orange  This is used inside the initSelection method, if AJAX options are NOT set. (null)
 *    vocabularyUrl(string): This is a URL to a JSON-formatted file used to populate the list (null)
 *    allowNewItems(string): All new items to be entered into the widget(true)
 *    OTHER OPTIONS(): For more options on select2 go to http://ivaynberg.github.io/select2/#documentation ()
 *
 * Documentation:
 *    # Autocomplete with search (single select)
 *
 *    {{ example-1 }}
 *
 *    # Tagging
 *
 *    {{ example-2 }}
 *
 *    # Orderable tags
 *
 *    {{ example-3 }}
 *
 *    # AJAX tags
 *
 *    {{ example-4 }}
 *
 * Example: example-1
 *    <select class="pat-select2" data-pat-select2="width:20em">
 *      <option value="Acholi">Acholi</option>
 *      <option value="Afrikaans">Afrikaans</option>
 *      <option value="Akan">Akan</option>
 *      <option value="Albanian">Albanian</option>
 *      <option value="Amharic">Amharic</option>
 *      <option value="Arabic">Arabic</option>
 *      <option value="Ashante">Ashante</option>
 *      <option value="Asl">Asl</option>
 *      <option value="Assyrian">Assyrian</option>
 *      <option value="Azerbaijani">Azerbaijani</option>
 *      <option value="Azeri">Azeri</option>
 *    </select>
 *
 * Example: example-2
 *    <input type="text" class="pat-select2"
 *           data-pat-select2="separator:,;
 *                             tags:Red,Yellow,Green,Orange,Purple;
 *                             width:20em;
 *                             initialValues:Red:The Color Red,Orange:The Color Orange"
 *           value="Red,Orange"/>
 *
 * Example: example-3
 *    <input type="text" class="pat-select2"
 *           data-pat-select2="orderable:true;
 *                             tags:Red,Yellow,Green;
 *                             width:20em" />
 * Example: example-4
 *    <input type="hidden" class="pat-select2"
 *           data-pat-select2="placeholder:Search for a Value;
 *                             vocabularyUrl:select2-test.json;
 *                             width:20em" />
 *
 */


define([
  'jquery',
  'mockup-patterns-base',
  'select2',
  'jquery.event.drag',
  'jquery.event.drop'
], function($, Base) {
  'use strict';

  var Select2 = Base.extend({
    name: 'select2',
    trigger: '.pat-select2',
    defaults: {
      separator: ','
    },
    initializeValues: function() {
      var self = this;
      // Init Selection ---------------------------------------------
      if (self.options.initialValues) {
        self.options.id = function(term) {
          return term.id;
        };
        self.options.initSelection = function ($el, callback) {
          var data = [],
              value = $el.val(),
              seldefaults = self.options.initialValues;

          // Create the initSelection value that contains the default selection,
          // but in a javascript object
          if (typeof(self.options.initialValues) === 'string' && self.options.initialValues !== '') {
            // if default selection value starts with a '{', then treat the value as
            // a JSON object that needs to be parsed
            if (self.options.initialValues[0] === '{') {
              seldefaults = JSON.parse(self.options.initialValues);
            }
            // otherwise, treat the value as a list, separated by the defaults.separator value of
            // strings in the format "id:text", and convert it to an object
            else {
              seldefaults = {};
              $(self.options.initialValues.split(self.options.separator)).each(function() {
                var selection = this.split(':');
                var id = $.trim(selection[0]);
                var text = $.trim(selection[1]);
                seldefaults[id] = text;
              });
            }
          }

          $(value.split(self.options.separator)).each(function() {
            var text = this;
            if (seldefaults[this]) {
              text = seldefaults[this];
            }
            data.push({id: this, text: text});
          });
          callback(data);
        };
      }
    },
    initializeTags: function() {
      var self = this;
      if (self.options.tags && typeof(self.options.tags) === 'string') {
        if (self.options.tags.substr(0, 1) === '[') {
          self.options.tags = JSON.parse(self.options.tags);
        } else {
          self.options.tags = self.options.tags.split(self.options.separator);
        }
      }

      if (self.options.tags && !self.options.allowNewItems) {
        self.options.data = $.map (self.options.tags, function (value, i) {
          return { id: value, text: value };
        });
        self.options.multiple = true;
        delete self.options.tags;
      }
    },
    initializeOrdering: function() {
      var self = this;
      if (self.options.orderable) {
        var formatSelection = function(data, $container) {
          return data ? data.text : undefined;
        };
        if (self.options.formatSelection) {
          formatSelection = self.options.formatSelection;
        }

        self.options.formatSelection = function(data, $container) {
          $container.parents('li')
            .drag('start', function(e, dd) {
              $(this).addClass('select2-choice-dragging');
              self.$el.select2('onSortStart');
              $.drop({
                tolerance: function(event, proxy, target) {
                  var test = event.pageY > (target.top + target.height / 2);
                  $.data(target.elem, 'drop+reorder', test ? 'insertAfter' : 'insertBefore' );
                  return this.contains(target, [event.pageX, event.pageY]);
                }
              });
              return $( this ).clone().
                addClass('dragging').
                css({opacity: 0.75, position: 'absolute'}).
                appendTo(document.body);
            })
            .drag(function(e, dd) {
              /*jshint eqeqeq:false */
              $( dd.proxy ).css({
                top: dd.offsetY,
                left: dd.offsetX
              });
              var drop = dd.drop[0],
                  method = $.data(drop || {}, 'drop+reorder');

              /* XXX Cannot use triple equals here */
              if (drop && (drop != dd.current || method != dd.method)) {
                $(this)[method](drop);
                dd.current = drop;
                dd.method = method;
                dd.update();
              }
            })
            .drag('end', function(e, dd) {
              $(this).removeClass('select2-choice-dragging');
              self.$el.select2('onSortEnd');
              $( dd.proxy ).remove();
            })
            .drop('init', function(e, dd ) {
              /*jshint eqeqeq:false */
              /* XXX Cannot use triple equals here */
              return (this == dd.drag) ? false: true;
            });
          return formatSelection(data, $container);
        };
      }
    },
    initializeSelect2: function() {
      var self = this;
      self.$el.select2(self.options);
      self.$select2 = self.$el.parent().find('.select2-container');
      self.$el.parent().off('close.plone-modal.patterns');
      if (self.options.orderable) {
        self.$select2.addClass('select2-orderable');
      }
    },
    init: function() {
      var self = this;

      self.options.allowNewItems = self.options.hasOwnProperty ('allowNewItems') ?
            JSON.parse(self.options.allowNewItems) : true;

      if (self.options.ajax || self.options.vocabularyUrl) {
        if (self.options.vocabularyUrl) {
          self.options.multiple = self.options.multiple === undefined ? true : self.options.multiple;
          self.options.ajax = self.options.ajax || {};
          self.options.ajax.url = self.options.vocabularyUrl;
          // XXX removing the following function does'nt break tests. dead code?
          self.options.initSelection = function ($el, callback) {
            var data = [], value = $el.val();
            $(value.split(self.options.separator)).each(function () {
              data.push({id: this, text: this});
            });
            callback(data);
          };
        }

        var queryTerm = '';
        self.options.ajax = $.extend({
          quietMillis: 300,
          data: function (term, page) {
            queryTerm = term;
            return {
              query: term,
              'page_limit': 10,
              page: page
            };
          },
          results: function (data, page) {
            var results = data.results;
            if (self.options.vocabularyUrl) {
              var dataIds = [];
              $.each(data.results, function(i, item) {
                dataIds.push(item.id);
              });
              results = [];

              var haveResult = queryTerm === '' || $.inArray(queryTerm, dataIds) >= 0;
              if (self.options.allowNewItems && !haveResult) {
                results.push({id: queryTerm, text: queryTerm});
              }

              $.each(data.results, function(i, item) {
                results.push(item);
              });
            }
            return { results: results };
          }
        }, self.options.ajax);
      } else if (self.options.multiple && self.$el.is('select')) {
        // Multiselects need to be converted to input[type=hidden]
        // for Select2
        var vals = self.$el.val() || [];
        var options = $.map(self.$el.find('option'), function (o) { return {text: $(o).html(), id: o.value}; });
        var $hidden = $('<input type="hidden" />');
        $hidden.val(vals.join(self.options.separator));
        $hidden.attr('class', self.$el.attr('class'));
        $hidden.attr('name', self.$el.attr('name'));
        $hidden.attr('id', self.$el.attr('id'));
        self.$orig = self.$el;
        self.$el.replaceWith($hidden);
        self.$el = $hidden;
        self.options.data = options;
      }

      self.initializeValues();
      self.initializeTags();
      self.initializeOrdering();
      self.initializeSelect2();
    }
  });

  return Select2;

});
