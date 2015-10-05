/* Eventedit pattern.
 *
 * Options:
 *    errorClass(string): class to set on the end datetime field wrapper, if end date validation fails. ('error')
 *
 * Documentation:
 *   # General
 *
 *   The pattern works with plone.app.event Archetypes and Dexterity forms.
 *
 *   * Start / end validation: The pattern adds a error class, if end is before
 *     start.
 *   * Start / end delta: After changing the start date, the end date is
 *     automatically updated by a delta timespan. The delta is calculated from
 *     the difference of the start and end time, if they are already set.
 *   * Whole day handling: After clicking the whole day checkbox, the start and
 *     end time fields are hidden.
 *   * Open end handling: After clicking the open end checkbox, the end
 *     date/time field is hidden.
 *
 *   # Dexterity form example
 *
 *   {{ example-1 }}
 *
 *   # Archetypes form example
 *
 *   {{ example-2 }}
 *
 * Example: example-1
 *    <div class="pat-eventedit">
 *      <div id="formfield-form-widgets-IEventBasic-start">
 *        Start
 *        <input class="pat-pickadate" type="text" name="form.widgets.IEventBasic.start" value="2014-08-14 14:00" />
 *      </div>
 *      <div id="formfield-form-widgets-IEventBasic-end">
 *        End
 *        <input class="pat-pickadate" type="text" name="form.widgets.IEventBasic.end" value="2014-08-14 15:30" />
 *      </div>
 *      <div id="formfield-form-widgets-IEventBasic-whole_day">
 *        Whole Day
 *        <input type="checkbox" />
 *      </div>
 *      <div id="formfield-form-widgets-IEventBasic-open_end">
 *        Open End
 *        <input type="checkbox" />
 *      </div>
 *    </div>
 *
 * Example: example-2
 *    <div class="pat-eventedit">
 *      <div id="archetypes-fieldname-startDate">
 *        Start
 *        <input class="pat-pickadate" type="text" name="startDate" value="2014-08-14 14:00" />
 *      </div>
 *      <div id="archetypes-fieldname-endDate">
 *        End
 *        <input class="pat-pickadate" type="text" name="endDate" value="2014-08-14 14:30" />
 *      </div>
 *      <div id="archetypes-fieldname-wholeDay">
 *        Whole Day
 *        <input type="checkbox" id="wholeDay" />
 *      </div>
 *      <div id="archetypes-fieldname-openEnd">
 *        Open End
 *        <input type="checkbox" id="openEnd" />
 *      </div>
 *    </div>
 *
 */


define([
  'jquery',
  'mockup-patterns-base',
  'mockup-patterns-pickadate',
], function ($, Base, pickadate) {
  'use strict';

  var EventEdit = Base.extend({
    name: 'eventedit',
    trigger: '.pat-eventedit',
    defaults: {
      errorClass: 'error'
    },
    init: function () {
      var self = this, $el = self.$el, jq_open_end, jq_end, jq_start;
      var jq_whole_day, jq_time;
      jq_whole_day = self.aOrB(
        $('#formfield-form-widgets-IEventBasic-whole_day input', $el),
        $('#archetypes-fieldname-wholeDay input#wholeDay', $el)
      );

      jq_time = self.aOrB(
        $('#formfield-form-widgets-IEventBasic-start .pattern-pickadate-time-wrapper, #formfield-form-widgets-IEventBasic-end .pattern-pickadate-time-wrapper', $el),
        $('#archetypes-fieldname-startDate .pattern-pickadate-time-wrapper, #archetypes-fieldname-endDate .pattern-pickadate-time-wrapper', $el)
      );

      if (jq_whole_day.length > 0 && jq_time.length > 0) {
        jq_whole_day.bind('change', function (e) {
          self.showHideWidget(jq_time, e.target.checked, true);
        });
        self.showHideWidget(jq_time, jq_whole_day.get(0).checked, false);
      }

      // OPEN END INIT
      jq_open_end = self.aOrB(
        $('#formfield-form-widgets-IEventBasic-open_end input', $el),
        $('#archetypes-fieldname-openEnd input#openEnd', $el)
      );
      jq_end = self.aOrB(
        $('#formfield-form-widgets-IEventBasic-end', $el),
        $('#archetypes-fieldname-endDate', $el)
      );
      if (jq_open_end.length > 0) {
        jq_open_end.bind('change', function (e) {
          self.showHideWidget(jq_end, e.target.checked, true);
        });
        self.showHideWidget(jq_end, jq_open_end.get(0).checked, false);
      }

      // START/END SETTING/VALIDATION
      jq_start = self.aOrB(
        $('#formfield-form-widgets-IEventBasic-start', $el),
        $('#archetypes-fieldname-startDate', $el)
      );
      jq_start.each(function () {
        $(this).on('change', '.picker__input', function () { self.updateEndDate(); });
      });
      jq_end.each(function () {
        $(this).on('change', '.picker__input', function () { self.validateEndDate(); });
      });
    },

    aOrB: function (a, b) {
      /* Return element a or element b, depending on which is available.
       * Parameter a and b: CSS selectors.
       * Returns: a jQuery object.
       */
      var ret;
      if ($(a).length > 0) {
        ret = a;
      } else {
        ret = b;
      }
      return $(ret);
    },

    getDateTime: function (datetimewidget) {
      var date, time, datetime;
      date = $('.pattern-pickadate-date-wrapper input[name="_submit"]', datetimewidget).prop('value');
      date = date.split("-");
      time = $('.pattern-pickadate-time-wrapper input[name="_submit"]', datetimewidget).prop('value') || '00:00';
      time = time.split(":");

      // We can't just parse the ``date + 'T' + time`` string, because of
      // Chromium bug: https://code.google.com/p/chromium/issues/detail?id=145198
      // When passing date and time components, the passed date/time is
      // interpreted as local time and not UTC.
      datetime = new Date(
        parseInt(date[0], 10),
        parseInt(date[1], 10) - 1, // you know, javascript's month index starts with 0
        parseInt(date[2], 10),
        parseInt(time[0], 10),
        parseInt(time[1], 10)
      );
      return datetime;
    },

    getTimeDelta: function () {
        // Return time delta between the start and end dates in days
        var self = this, $el = self.$el, start_datetime, end_datetime;
        start_datetime = self.getDateTime(
          self.aOrB(
            $('#formfield-form-widgets-IEventBasic-start', $el),
            $('#archetypes-fieldname-startDate', $el)
          )
        );
        end_datetime = self.getDateTime(
          self.aOrB(
            $('#formfield-form-widgets-IEventBasic-end', $el),
            $('#archetypes-fieldname-endDate', $el)
          )
        );
        return (end_datetime - start_datetime) / 1000 / 60;
    },

    updateEndDate: function () {
        var self = this, $el = self.$el, jq_start, jq_end, start_date, new_end_date;
        jq_start = self.aOrB(
          $('#formfield-form-widgets-IEventBasic-start', $el),
          $('#archetypes-fieldname-startDate', $el)
        );
        jq_end = self.aOrB(
          $('#formfield-form-widgets-IEventBasic-end', $el),
          $('#archetypes-fieldname-endDate', $el)
        );

        start_date = self.getDateTime(jq_start);
        new_end_date = new Date(start_date.getTime());
        new_end_date.setMinutes(start_date.getMinutes() + self.getTimeDelta());

        if (new_end_date && !isNaN(new_end_date.getTime())) {
          $('.pattern-pickadate-date', jq_end).pickadate('picker').set('select', new_end_date);
          $('.pattern-pickadate-time', jq_end).pickatime('picker').set('select', new_end_date);
        }
    },

    validateEndDate: function () {
        var self = this, $el = self.$el, jq_start, jq_end, start_datetime, end_datetime;
        jq_start = self.aOrB(
          $('#formfield-form-widgets-IEventBasic-start', $el),
          $('#archetypes-fieldname-startDate', $el)
        );
        jq_end = self.aOrB(
          $('#formfield-form-widgets-IEventBasic-end', $el),
          $('#archetypes-fieldname-endDate', $el)
        );
        start_datetime = self.getDateTime(jq_start);
        end_datetime = self.getDateTime(jq_end);
        if (end_datetime < start_datetime) {
            jq_end.addClass(self.options.errorClass);
        } else {
            jq_end.removeClass(self.options.errorClass);
        }
    },

    showHideWidget: function (widget, hide, fade) {
        var $widget = $(widget);
        if (hide === true) {
            if (fade === true) { $widget.fadeOut(); }
            else { $widget.hide(); }
        } else {
            if (fade === true) { $widget.fadeIn(); }
            else { $widget.show(); }
        }
    }
  });
  return EventEdit;
});
