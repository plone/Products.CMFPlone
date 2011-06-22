/* jscalendar glue
 *
 * Expects one hidden calendar field, and up to 6 extra calendar fields with
 * the same id as the hidden field, with _year, _month, _day, _hour, _minute
 * and _ampm added. These fields are expected to be single selects, although
 * _year can be a hidden field as well. The _hour and _minute fields are
 * optional, is is the _ampm field. See calendar_macros.pt for a complete
 * example
 */

/*
  Provides plone.jscalendar

  Calendar comes from plone_3rdParty/jscalendar/calendar_stripped.js
*/

/*global plone:true, Calendar:false */
/*jslint nomen:false */


if (typeof(plone)==='undefined') {
    var plone = {};
}

(function($) {

plone.jscalendar = {
    _calendar: null,
    _current_input: null,
    _field_names: ['year', 'month', 'day', 'hour', 'minute', 'ampm'],

    // All calendar fields
    _fields: function(selector) {
        if (selector === undefined) {
            selector = plone.jscalendar._current_input;
        }
        var fields = {field: $(selector)};
        $.each(plone.jscalendar._field_names, function() {
            fields[this] = $(selector + '_' + this);
        });
        return fields;
    },

    // Attach event handlers on load
    init: function() {
    	// $('.plone_jscalendar > input:hidden') was very low under ie8-
        $('.plone_jscalendar').find('input:hidden').each(function() {
            var selector = '#' + this.id;
            $.each(plone.jscalendar._fields(selector), function() {
                this.filter('select').bind(
                    'change.plone.jscalendar', {selector: selector},
                    plone.jscalendar.update_hidden);
            });
        });
    },

    // show calendar popup
    show: function(input_id, yearStart, yearEnd) {
        var cal = plone.jscalendar._cal,
        fields,
        anchor;

        if (!cal) {
            cal = plone.jscalendar._cal = new Calendar(
                    // firstdDay, datestr, onSelect, onClose
                    1, null, plone.jscalendar.handle_select,
                    plone.jscalendar.handle_close
            );
            cal.create();
        } else {
            cal.hide();
        }

        plone.jscalendar._current_input = input_id;
        fields = plone.jscalendar._fields();
        anchor = fields.month;
        cal.setRange(yearStart, yearEnd);

        // Set calendar popup date to currently selected values
        if (fields.year.val() > 0)  {cal.date.setFullYear(fields.year.val());}
        if (fields.month.val() > 0) {cal.date.setMonth(fields.month.val() - 1);}
        if (fields.day.val() > 0)   {cal.date.setDate(fields.day.val());}
        cal.refresh();
        cal.showAtElement(anchor.get(0), null);
        return false;
    },

    // handle calendar popup date select
    handle_select: function(cal, date) {
        var fields = plone.jscalendar._fields(),
            yearValue = date.substring(0,4),
            options,
            i;

        if ($.nodeName(fields.year.get(0), 'select') &&
            !fields.year.children('option[value=' + yearValue + ']').length) {
            // insert missing year into the options list
            options = fields.year.get(0).options;
            for (i=options.length; i > 0; i=i-1) {
                if (options[i].value > yearValue) {
                    options[i + 1] = new Option(options[i].value,
                                                options[i].text);
                } else {
                    options[i + 1] = new Option(yearValue, yearValue);
                    break;
                }
            }
        }

        fields.year.val(yearValue);
        fields.month.val(date.substring(5, 7));
        fields.day.val(date.substring(8, 10));
        plone.jscalendar.update_hidden();
    },

    // handle calendar popup close
    handle_close: function(cal) { cal.hide(); },

    // updates a hidden date field with the current values of the widgets
    update_hidden: function(e) {
        var val = '',
            f = plone.jscalendar._fields(e && e.data.selector),
            type,
            filter,
            date;

        if (e && e.target.selectedIndex === 0) {
            // Reset widgets; only the time widgets if this is a time select box.
            type = e.target.id.substr(e.data.selector.length);
            filter = $.inArray(type, ['hour', 'minute', 'ampm']) > -1 ?
                'select[id$=hour],select[id$=minute],select[id$=ampm]': 'select';
            $.each(f, function() { this.filter(filter).attr('selectedIndex', 0); });
        } else if (f.year.val() > 0 && f.month.val() > 0 && f.day.val() > 0) {
            // ISO date string
            val = [f.year.val(), f.month.val(), f.day.val()].join('-');

            date = new Date(val.replace(/-/g, '/'));
            if (date.print('%Y-%m-%d') !== val) {
                // Date turnes illegal dates into legal ones, update widgets
                val = date.print('%Y-%m-%d');
                f.year.val(val.substring(0, 4));
                f.month.val(val.substring(5, 7));
                f.day.val(val.substring(8, 10));
            }

            // optional time
            if (f.hour.length && f.minute.length) {
                val += " " + [f.hour.val(), f.minute.val()].join(':');
                if (f.ampm.length) {
                    val += " " + f.ampm.val();
                }
            }
        }

        f.field.val(val);
    }
};

}(jQuery));

// initialize fields
jQuery(function($) {
    $(plone.jscalendar.init);
    // find and enable datepicker popups with data from
    // hidden fields
    $('.plone-jscalendar-popup').each(function() {
        var jqt = $(this),
            widget_id = this.id.replace('_popup', ''),
            year_start = $('#' + widget_id + '_yearStart').val(),
            year_end = $('#' + widget_id + '_yearEnd').val();
        if (year_start && year_end) {
            jqt.css('cursor', 'pointer')
               .show()
               .click(function(e) {
                return plone.jscalendar.show('#' + widget_id, year_start, year_end);
               });
        }
    });
});
