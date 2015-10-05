/* Querystring pattern.
 *
 * Options:
 *    criteria(object): options to pass into criteria ({})
 *    indexOptionsUrl(string): URL to grab index option data from. Must contain "sortable_indexes" and "indexes" data in JSON object. (null)
 *    previewURL(string): URL used to pass in a plone.app.querystring-formatted HTTP querystring and get an HTML list of results ('portal_factory/@@querybuilder_html_results')
 *    previewCountURL(string): URL used to pass in a plone.app.querystring-formatted HTTP querystring and get an HTML string of the total number of records found with the query ('portal_factory/@@querybuildernumberofresults')
 *    classWrapperName(string): CSS class to apply to the wrapper element ('querystring-wrapper')
 *    classSortLabelName(string): CSS class to apply to the sort on label ('querystring-sort-label')
 *    classSortReverseName(string): CSS class to apply to the sort order label and checkbox container ('querystring-sortreverse')
 *    classSortReverseLabelName(string): CSS class to apply to the sort order label ('querystring-sortreverse-label')
 *    classPreviewCountWrapperName(string): TODO ('querystring-previewcount-wrapper')
 *    classPreviewResultsWrapperName(string): CSS class to apply to the results wrapper ('querystring-previewresults-wrapper')
 *    classPreviewWrapperName(string): CSS class to apply to the preview wrapper ('querystring-preview-wrapper')
 *    classPreviewName(string): CSS class to apply to the preview pane ('querystring-preview')
 *    classPreviewTitleName(string): CSS class to apply to the preview title ('querystring-preview-title')
 *    classPreviewDescriptionName(string): CSS class to apply to the preview description ('querystring-preview-description')
 *    classSortWrapperName(string): CSS class to apply to the sort order and sort on wrapper ('querystring-sort-wrapper')
 *    showPreviews(boolean): Should previews be shown? (true)
 *
 * Documentation:
 *    # Default
 *
 *    {{ example-1 }}
 *
 *    # Without Previews
 *
 *    {{ example-2 }}
 *
 * Example: example-1
 *    <input class="pat-querystring"
 *           data-pat-querystring="indexOptionsUrl: /tests/json/queryStringCriteria.json" />
 *
 * Example: example-2
 *    <input class="pat-querystring"
 *           data-pat-querystring="indexOptionsUrl: /tests/json/queryStringCriteria.json;
 *                                 showPreviews: false;" />
 *
 */


define([
  'jquery',
  'mockup-patterns-base',
  'mockup-patterns-select2',
  'mockup-patterns-pickadate',
  'select2',
  'translate',
  'underscore'
], function($, Base, Select2, PickADate, undefined, _t, _) {
  'use strict';

  var Criteria = function() { this.init.apply(this, arguments); };
  Criteria.prototype = {
    defaults: {
      indexWidth: '20em',
      remove: '',
      classBetweenDtName: 'querystring-criteria-betweendt',
      classWrapperName: 'querystring-criteria-wrapper',
      classIndexName: 'querystring-criteria-index',
      classOperatorName: 'querystring-criteria-operator',
      classValueName: 'querystring-criteria-value',
      classRemoveName: 'querystring-criteria-remove',
      classResultsName: 'querystring-criteria-results',
      classClearName: 'querystring-criteria-clear'
    },
    init: function($el, options, indexes, index, operator, value) {
      var self = this;

      self.options = $.extend(true, {}, self.defaults, options);
      self.indexes = indexes;
      self.indexGroups = {};

      // create wrapper criteria and append it to DOM
      self.$wrapper = $('<div/>')
              .addClass(self.options.classWrapperName)
              .appendTo($el);

      // Remove button
      self.$remove = $('<div>' + self.options.remove + '</div>')
        .addClass(self.options.classRemoveName)
        .appendTo(self.$wrapper)
        .on('click', function(e) {
          self.remove();
        });

      // Index selection
      self.$index = $('<select><option></option></select>')
          .attr('placeholder', _t('Select criteria'));

      // list of indexes
      $.each(self.indexes, function(value, options) {
        if (options.enabled) {
          if (!self.indexGroups[options.group]) {
            self.indexGroups[options.group] = $('<optgroup/>')
                .attr('label', options.group)
                .appendTo(self.$index);
          }
          self.indexGroups[options.group].append(
            $('<option/>')
              .attr('value', value)
              .html(options.title)
          );
        }
      });

      // attach index select to DOM
      self.$wrapper.append(
        $('<div/>')
          .addClass(self.options.classIndexName)
          .append(self.$index)
      );

      // add blink (select2)
      self.$index
        .patternSelect2({
          width: self.options.indexWidth,
          placeholder: _t('Select criteria')
        })
        .on('change', function(e) {
          self.removeValue();
          self.createOperator(e.val);
          self.createClear();
          self.trigger('index-changed');
        });

      if (index !== undefined) {
        self.$index.select2('val', index);
        self.createOperator(index, operator, value);
        self.createClear();
      }

      self.trigger('create-criteria');
    },
    createOperator: function(index, operator, value) {
      var self = this;

      self.removeOperator();
      self.$operator = $('<select/>');

      if (self.indexes[index]) {
        _.each(self.indexes[index].operations, function(value) {
          var options = self.indexes[index].operators[value];
          $('<option/>')
              .attr('value', value)
              .html(options.title)
              .appendTo(self.$operator);
        });
      }

      // attach operators select to DOM
      self.$wrapper.append(
        $('<div/>')
          .addClass(self.options.classOperatorName)
          .append(self.$operator)
      );

      // add blink (select2)
      self.$operator
        .patternSelect2({ width: '10em' })
        .on('change', function(e) {
          self.createValue(index);
          self.createClear();
          self.trigger('operator-changed');
        });

      if (operator === undefined) {
        operator = self.$operator.select2('val');
      }

      self.$operator.select2('val', operator);
      self.createValue(index, value);

      self.trigger('create-operator');
    },
    createValue: function(index, value) {
      var self = this,
          widget = self.indexes[index].operators[self.$operator.val()].widget,
          $wrapper = $('<div/>')
            .addClass(self.options.classValueName)
            .appendTo(self.$wrapper);

      self.removeValue();

      if (widget === 'StringWidget') {
        self.$value = $('<input type="text"/>')
                .addClass(self.options.classValueName + '-' + widget)
                .val(value)
                .appendTo($wrapper)
                .change(function() {
                  self.trigger('value-changed');
                });

      } else if (widget === 'DateWidget') {
        self.$value = $('<input type="text"/>')
                .addClass(self.options.classValueName + '-' + widget)
                .attr('data-pat-pickadate', '{"time": false, "date": {"format": "dd/mm/yyyy" }}')
                .val(value)
                .appendTo($wrapper)
                .patternPickadate()
                .on('updated.pickadate.patterns', function() {
                  self.trigger('value-changed');
                });


      } else if (widget === 'DateRangeWidget') {
        var startwrap = $('<span/>').appendTo($wrapper);
        var val1 = "";
        var val2 = "";

        if (value) {
          val1 = value[0]?value[0]:"";
          val2 = value[1]?value[1]:"";
        }

        var startdt = $('<input type="text"/>')
          .addClass(self.options.classValueName + '-' + widget)
          .addClass(self.options.classValueName + '-' + widget + '-start')
          .attr('data-pat-pickadate', '{"time": false, "date": {"format": "dd/mm/yyyy" }}')
          .val(val1)
          .appendTo(startwrap)
          .patternPickadate()
          .on('updated.pickadate.patterns', function() {
            self.trigger('value-changed');
          });
        $wrapper.append(
          $('<span/>')
            .html(_t('to'))
            .addClass(self.options.classBetweenDtName)
        );
        var endwrap = $('<span/>').appendTo($wrapper);
        var enddt = $('<input type="text"/>')
                        .addClass(self.options.classValueName + '-' + widget)
                        .addClass(self.options.classValueName + '-' + widget + '-end')
                        .attr('data-pat-pickadate', '{"time": false, "date": {"format": "dd/mm/yyyy" }}')
                        .val(val2)
                        .appendTo(endwrap)
                        .patternPickadate()
                        .on('updated.pickadate.patterns', function() {
                          self.trigger('value-changed');
                        });
        self.$value = [startdt, enddt];

      } else if (widget === 'RelativeDateWidget') {
        self.$value = $('<input type="text"/>')
                .after($('<span/>').html(_t('days')))
                .addClass(self.options.classValueName + '-' + widget)
                .appendTo($wrapper)
                .change(function() {
                  self.trigger('value-changed');
                });

      } else if (widget === 'ReferenceWidget') {
        self.$value = $('<input type="text"/>')
                .addClass(self.options.classValueName + '-' + widget)
                .appendTo($wrapper)
                .change(function() {
                  self.trigger('value-changed');
                });

      } else if (widget === 'RelativePathWidget') {
        self.$value = $('<input type="text"/>')
                .addClass(self.options.classValueName + '-' + widget)
                .appendTo($wrapper)
                .val(value)
                .change(function() {
                  self.trigger('value-changed');
                });

      } else if (widget === 'MultipleSelectionWidget') {
        self.$value = $('<select/>').prop('multiple', true)
                .addClass(self.options.classValueName + '-' + widget)
                .appendTo($wrapper)
                .change(function() {
                  self.trigger('value-changed');
                });
        if (self.indexes[index]) {
          $.each(self.indexes[index].values, function(value, options) {
            $('<option/>')
                .attr('value', value)
                .html(options.title)
                .appendTo(self.$value);
          });
        }
        self.$value.patternSelect2({ width: '250px' });
      }

      if (value !== undefined && typeof self.$value !== 'undefined') {
        if ($.isArray(self.$value)) {
          $.each(value, function( i, v ) {
            self.$value[i].select2('val', v);
          });
        }
        else {
          self.$value.select2('val', value);
        }
      }

      self.trigger('create-value');

    },
    createClear: function() {
      var self = this;
      self.removeClear();
      self.$clear = $('<div/>')
        .addClass(self.options.classClearName)
        .appendTo(self.$wrapper);
    },
    remove: function() {
      var self = this;
      self.trigger('remove');
      self.$remove.remove();
      self.$index.parent().remove();
      self.removeOperator();
      self.removeValue();
      self.removeClear();
      self.$wrapper.remove();
    },
    removeClear: function() {
      var self = this;
      self.trigger('remove-clear');
      if (self.$clear) {
        self.$clear.remove();
      }
    },
    removeOperator: function() {
      var self = this;
      self.trigger('remove-operator');
      if (self.$operator) {
        self.$operator.parent().remove();
      }
    },
    removeValue: function() {
      var self = this;
      self.trigger('remove-value');
      if (self.$value) {
        if ($.isArray(self.$value)) { // date ranges have 2 values
          self.$value[0].parents('.querystring-criteria-value').remove();
        }
        else {
          self.$value.parents('.querystring-criteria-value').remove();
        }
      }
    },
    // builds the parameters to go into the http querystring for requesting
    // results from the query builder
    buildQueryPart: function() {
      var self = this;

      // index
      var ival = self.$index.select2('val');
      if (ival === '') { // no index selected, no query
        return '';
      }
      var istr = 'query.i:records=' + ival;

      // operator
      if (typeof self.$operator === 'undefined') { // no operator, no query
        return '';
      }
      var oval = self.$operator.val(),
          ostr = 'query.o:records=' + oval;

      // value(s)
      var vstrbase = 'query.v:records=',
          vstrlistbase = 'query.v:records:list=',
          vstr = [];
      if (typeof self.$value === 'undefined') {
        vstr.push(vstrbase);
      }
      else if ($.isArray(self.$value)) { // handles only datepickers from the 'between' operator right now
        $.each(self.$value, function(i, v) {
          vstr.push(vstrlistbase + $(this).parent().find('.picker__input').val());
        });
      }
      else if ($.isArray(self.$value.val())) { // handles multible values
        $.each(self.$value.val(), function(i, v) {
          vstr.push(vstrlistbase + v);
        });
      }
      else {
        vstr.push(vstrbase + self.$value.val());
      }

      return istr + '&' + ostr + '&' + vstr.join('&');
    },
    getJSONListStr: function() {
      var self = this;

      // index
      var ival = self.$index.select2('val');
      if (ival === '') { // no index selected, no query
        return '';
      }

      // operator
      if (typeof self.$operator === 'undefined') { // no operator, no query
        return '';
      }
      var oval = self.$operator.val();

      // value(s)
      var varr = [];
      if ($.isArray(self.$value)) { // handles only datepickers from the 'between' operator right now
        $.each(self.$value, function(i, v) {
          varr.push($(this).val());
        });
      }
      else if (typeof self.$value !== 'undefined') {
        varr.push(self.$value.val());
      }
      var vval;
      if (varr.length > 1) {
        vval = '["' + varr.join('","') + '"]';
      }
      else if (varr.length === 1) {
        vval = JSON.stringify(varr[0]);
      }
      else {
        vval = '""';
      }

      return '{"i":"' + ival + '", "o":"' + oval + '", "v":' + vval + '}';
    },
    trigger: function(name) {
      this.$wrapper.trigger(name + '-criteria.querystring.patterns', [ this ]);
    },
    on: function(name, callback) {
      this.$wrapper.on(name + '-criteria.querystring.patterns', callback);
    }
  };

  var QueryString = Base.extend({
    name: 'querystring',
    trigger: '.pat-querystring',
    defaults: {
      indexes: [],
      classWrapperName: 'querystring-wrapper',
      criteria: {},
      indexOptionsUrl: null,
      previewURL: 'portal_factory/@@querybuilder_html_results', // base url to use to request preview information from
      previewCountURL: 'portal_factory/@@querybuildernumberofresults',
      classSortLabelName: 'querystring-sort-label',
      classSortReverseName: 'querystring-sortreverse',
      classSortReverseLabelName: 'querystring-sortreverse-label',
      classPreviewCountWrapperName: 'querystring-previewcount-wrapper',
      classPreviewResultsWrapperName: 'querystring-previewresults-wrapper',
      classPreviewWrapperName: 'querystring-preview-wrapper',
      classPreviewName: 'querystring-preview',
      classPreviewTitleName: 'querystring-preview-title',
      classPreviewDescriptionName: 'querystring-preview-description',
      classSortWrapperName: 'querystring-sort-wrapper',
      showPreviews: true
    },
    init: function() {
      var self = this;

      // hide input element
      self.$el.hide();

      // create wrapper for out criteria
      self.$wrapper = $('<div/>');
      self.$el.after(self.$wrapper);

      // initialization can be detailed if by ajax
      self.initialized = false;

      if (self.options.indexOptionsUrl) {
        $.ajax({
          url: self.options.indexOptionsUrl,
          success: function(data) {
            self.options.indexes = data.indexes;
            self.options['sortable_indexes'] = data['sortable_indexes']; // jshint ignore:line
            self._init();
          },
          error: function(xhr) {
            // XXX handle this...
          }
        });
      } else {
        self._init();
      }
    },
    _init: function() {
      var self = this;
      self.$criteriaWrapper = $('<div/>')
        .addClass(self.options.classWrapperName)
        .appendTo(self.$wrapper);

      self.$sortWrapper = $('<div/>')
        .addClass(self.options.classSortWrapperName)
        .appendTo(self.$wrapper);

      if (self.options.showPreviews === 'false') {
        self.options.showPreviews = false;
      }
      if (self.options.showPreviews) {
        self.$previewWrapper = $('<div/>')
          .addClass(self.options.classPreviewWrapperName)
          .appendTo(self.$wrapper);

        // preview title and description
        $('<div/>')
          .addClass(self.options.classPreviewTitleName)
          .html(_t('Preview'))
          .appendTo(self.$previewWrapper);
        $('<div/>')
          .addClass(self.options.classPreviewDescriptionName)
          .html(_t('Preview of at most 10 items'))
          .appendTo(self.$previewWrapper);
      }

      self.criterias = [];

      // create populated criterias
      if (self.$el.val()) {
        $.each(JSON.parse(self.$el.val()), function(i, item) {
          self.createCriteria(item.i, item.o, item.v);
        });
      }

      // add empty criteria which enables users to create new cr
      self.createCriteria();

      // add sort/order fields
      self.createSort();

      // add criteria preview pane to see results from criteria query
      if (self.options.showPreviews) {
        self.refreshPreviewEvent();
      }
      self.$el.trigger('initialized');
      self.initialized = true;
    },
    createCriteria: function(index, operator, value) {
      var self = this,
          criteria = new Criteria(self.$criteriaWrapper, self.options.criteria,
            self.options.indexes, index, operator, value);

      criteria.on('remove', function(e) {
        if (self.criterias[self.criterias.length - 1] === criteria) {
          self.createCriteria();
        }
      });

      criteria.on('index-changed', function(e) {
        if (self.criterias[self.criterias.length - 1] === criteria) {
          self.createCriteria();
        }
      });

      var doupdates = function() {
        self.refreshPreviewEvent();
        self.updateValue();
      };

      criteria.on('remove', function(e, criteria) {
        if (self.criterias.indexOf(criteria) !== -1) {
          self.criterias.splice(self.criterias.indexOf(criteria), 1);
        }
        doupdates(e, criteria);
      });
      criteria.on('remove-clear', doupdates);
      criteria.on('remove-operator', doupdates);
      criteria.on('remove-value', doupdates);
      criteria.on('index-changed', doupdates);
      criteria.on('operator-changed', doupdates);
      criteria.on('create-criteria', doupdates);
      criteria.on('create-operator', doupdates);
      criteria.on('create-value', doupdates);
      criteria.on('value-changed', doupdates);

      self.criterias.push(criteria);
    },
    createSort: function() {
      var self = this;

      // elements that may exist already on the page
      // XXX do this in a way so it'll work with other forms will work
      // as long as they provide sort_on and sort_reversed fields in z3c form
      var existingSortOn = $('[id$="-sort_on"]').filter('[id^="formfield-"]');
      var existingSortOrder = $('[id$="-sort_reversed"]').filter('[id^="formfield-"]');

      $('<span/>')
        .addClass(self.options.classSortLabelName)
        .html(_t('Sort on'))
        .appendTo(self.$sortWrapper);
      self.$sortOn = $('<select/>')
        .attr('name', 'sort_on')
        .appendTo(self.$sortWrapper)
        .change(function() {
          self.refreshPreviewEvent.call(self);
          $('[id$="sort_on"]', existingSortOn).val($(this).val());
        });

      self.$sortOn.append($('<option value="">No sorting</option>')); // default no sorting
      for (var key in self.options['sortable_indexes']) { // jshint ignore:line
        self.$sortOn.append(
          $('<option/>')
            .attr('value', key)
            .html(self.options.indexes[key].title)
        );
      }
      self.$sortOn.patternSelect2({width: 150});

      self.$sortOrder = $('<input type="checkbox" />')
        .attr('name', 'sort_reversed:boolean')
        .change(function() {
          self.refreshPreviewEvent.call(self);
          if ($(this).prop('checked')) {
            $('.option input[type="checkbox"]', existingSortOrder).prop('checked', true);
          } else {
            $('.option input[type="checkbox"]', existingSortOrder).prop('checked', false);
          }
        });

      $('<span/>')
        .addClass(self.options.classSortReverseName)
        .appendTo(self.$sortWrapper)
        .append(self.$sortOrder)
        .append(
          $('<span/>')
            .html(_t('Reversed Order'))
            .addClass(self.options.classSortReverseLabelName)
        );

      // if the form already contains the sort fields, hide them! Their values
      // will be synced back and forth between the querystring's form elements
      if (existingSortOn.length >= 1 && existingSortOrder.length >= 1) {
        var reversed = $('.option input[type="checkbox"]', existingSortOrder).prop('checked');
        var sortOn = $('[id$="-sort_on"]', existingSortOn).val();
        if (reversed) {
          self.$sortOrder.prop('checked', true);
        }
        self.$sortOn.select2('val', sortOn);
        $(existingSortOn).hide();
        $(existingSortOrder).hide();
      }
    },
    refreshPreviewEvent: function() {
      var self = this;

      if (!self.options.showPreviews) {
        return; // cut out of this if there are no previews available
      }

      /* TEMPORARY */
      //if (typeof self._tmpcnt === 'undefined') { self._tmpcnt = 0; }
      //self._tmpcnt++;
      /* /TEMPORARY */

      if (typeof self._previewXhr !== 'undefined') {
        self._previewXhr.abort();
      }
      /*
      if (typeof self._count_xhr !== 'undefined') {
        self._count_xhr.abort();
      }
      */
      if (typeof self.$previewPane !== 'undefined') {
        self.$previewPane.remove();
      }

      var query = [], querypart;
      $.each(self.criterias, function(i, criteria) {
        querypart = criteria.buildQueryPart();
        if (querypart !== '') {
          query.push(criteria.buildQueryPart());
        }
      });

      self.$previewPane = $('<div/>')
        .addClass(self.options.classPreviewName)
        .appendTo(self.$previewWrapper);

      if (query.length <= 0) {
        $('<div/>')
          .addClass(self.options.classPreviewCountWrapperName)
          .html('No results to preview')
          .prependTo(self.$previewPane);
        return; // no query means nothing to send out requests for
      }

      query.push('sort_on=' + self.$sortOn.val());
      if (self.$sortOrder.prop('checked')) {
        query.push('sort_order=reverse');
      }

      /* TEMPORARY */
      //self.$previewPane.html(
      //    'refreshed ' + self._tmpcnt + ' times<br />'
      //    + (query.length > 1 ? query.join('<br />&') : query));
      /* /TEMPORARY */

      /*
      self._count_xhr = $.get(self.options.previewCountURL + '?' + query.join('&'))
          .done(function(data, stat) {
            $('<div/>')
              .addClass(self.options.classPreviewCountWrapperName)
              .html(data)
              .prependTo(self.$previewPane);
          });
      */
      self._previewXhr = $.get(self.options.previewURL + '?' + query.join('&'))
          .done(function(data, stat) {
            $('<div/>')
              .addClass(self.options.classPreviewResultsWrapperName)
              .html(data)
              .appendTo(self.$previewPane);
          });
    },
    updateValue: function() {
      // updating the original input with json data in the form:
      // [
      //    {i:'index', o:'operator', v:'value'}
      // ]

      var self = this;

      var criteriastrs = [];
      $.each(self.criterias, function(i, criteria) {
        var jsonstr = criteria.getJSONListStr();
        if (jsonstr !== '') {
          criteriastrs.push(jsonstr);
        }
      });
      var existing = self.$el.val();
      var val = '[' + criteriastrs.join(',') + ']';
      self.$el.val(val);
      self.$el.trigger('change');
    }
  });

  return QueryString;

});
