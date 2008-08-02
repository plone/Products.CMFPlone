/* jscalendar glue
 *
 * Expects one hidden calendar field, and up to 6 extra calendar fields with
 * the same id as the hidden field, with _year, _month, _day, _hour, _minute
 * and _ampm added. These fields are expected to be single selects, although
 * _year can be a hidden field as well. The _hour and _minute fields are
 * optional, is is the _ampm field. See calendar_macros.pt for a complete
 * example
 *
 * Included are backwards-compatibility function names to support the pre-3.1.4
 * calling conventions, so 3rd-party usage will still work. A future version of
 * Plone may remove this support.
 */
if (typeof(plone)=='undefined')
    var plone = {};

plone.jscalendar = {
    _calendar: null,
    _current_input: null,
    _field_names: ['year', 'month', 'day', 'hour', 'minute', 'ampm'],
    
    // All calendar fields
    _fields: function(selector) {
        if (selector === undefined) selector = plone.jscalendar._current_input;
        var fields = {field: jq(selector)};
        jq.each(plone.jscalendar._field_names, function() {
            fields[this] = jq(selector + '_' + this);
        });
        return fields;
    },
    
    // Attach event handlers on load
    init: function() {
        jq('.plone_jscalendar > input:hidden').each(function() {
            var selector = '#' + this.id;
            jq.each(plone.jscalendar._fields(selector), function() {
                this.filter('select').bind(
                    'change.plone.jscalendar', {selector: selector}, 
                    plone.jscalendar.update_hidden);
            });
        });
    },
    
    // show calendar popup
    show: function(input_id, yearStart, yearEnd) {
        var cal = plone.jscalendar._cal;
        if (!cal) {
            cal = plone.jscalendar._cal = new Calendar(
                    // firstdDay, datestr, onSelect, onClose
                    1, null, plone.jscalendar.handle_select, 
                    plone.jscalendar.handle_close
            );
            cal.create();
        } else
            cal.hide();
        
        if (arguments.length > 3) {
            // Backwards compatibility, fields passed in manually
            cal.params = {
                range: [arguments[7], arguments[8]], // yearStart, yearEnd
                inputField    : jq('#' + arguments[1]).get(0), // input_id
                input_id_year : jq('#' + arguments[2]).get(0), // "_year
                input_id_month: jq('#' + arguments[3]).get(0), // "_month,
                input_id_day  : jq('#' + arguments[4]).get(0)  // "_day
            };
            var anchor = jq('#' + arguments[0]);               // "_anchor
            cal.setRange(cal.params.range[0], cal.params.range[1]);
            window.calendar = cal;
            var fields = {
                year: jq(cal.params.input_id_year),
                month: jq(cal.params.input_id_month),
                day: jq(cal.params.input_id_day)
            };
        } else {
            plone.jscalendar._current_input = input_id;
            var fields = plone.jscalendar._fields();
            var anchor = fields.month;
            cal.setRange(yearStart, yearEnd);
        }
        
        // Set calendar popup date to currently selected values
        if (fields.year.val() > 0)  cal.date.setFullYear(fields.year.val());
        if (fields.month.val() > 0) cal.date.setMonth(fields.month.val() - 1);
        if (fields.day.val() > 0)   cal.date.setDate(fields.day.val());
        cal.refresh();
        cal.showAtElement(anchor.get(0), null);
        return false;
    },
    
    // handle calendar popup date select
    handle_select: function(cal, date) {
        if (cal.params !== undefined) {
            // backwards compat; field references stored in cal.params
            var fields = {
                year : jq(cal.params.input_id_year),
                month: jq(cal.params.input_id_month),
                day  : jq(cal.params.input_id_day)
            };
        } else
            var fields = plone.jscalendar._fields();
        
        var yearValue = date.substring(0,4);
        
        if (jq.nodeName(fields.year.get(0), 'select') && 
            !fields.year.children('option[value=' + yearValue + ']').length) {
            // insert missing year into the options list
            var options = fields.year.get(0).options;
            for (var i=options.length; i--; i > 0) {
                if (options[i].value > yearValue)
                    options[i + 1] = new Option(options[i].value, 
                                                options[i].text);
                else {
                    options[i + 1] = new Option(yearValue, yearValue);
                    break;
                }
            }
        }
        
        fields.year.val(yearValue);
        fields.month.val(date.substring(5, 7));
        fields.day.val(date.substring(8, 10));
        
        if (cal.params !== undefined) {
            // backwards compat, direct ref to field stored in cal.params
            var inputField = jq(cal.params.inputField);
            inputField.val(date + inputField.val().substr(10)); // keep time
        } else
            plone.jscalendar.update_hidden();
    },
    
    // handle calendar popup close
    handle_close: function(cal) {
        // clean up backwards compat structure
        if (cal.params !== undefined) cal.params = window.calendar = undefined;
        cal.hide();
    },
    
    // updates a hidden date field with the current values of the widgets
    update_hidden: function(e) {
        var val = '';
        
        if (arguments.length > 1)
            // backwards compat, direct ids for fields passed in
            var f = {
                field : jq('#' + arguments[0]),
                year  : jq('#' + arguments[1]),
                month : jq('#' + arguments[2]),
                day   : jq('#' + arguments[3]),
                hour  : jq('#' + arguments[4]),
                minute: jq('#' + arguments[5]),
                ampm  : jq('#' + arguments[6])
            };
        else
            var f = plone.jscalendar._fields(e && e.data.selector);
        
        // backwards-compatibility check; only the year widget can reset then
        if ((arguments.length > 1 && f.year.val() == 0) || 
            (e && e.target.selectedIndex === 0)) {
            // Reset widgets; only the time widgets if this is a time select box.
            var type = arguments.length == 1 && e.target.id.substr(e.data.selector.length);
            var filter = jq.inArray(type, ['hour', 'minute', 'ampm']) > -1 ?
                'select[id$=hour],select[id$=minute],select[id$=ampm]': 'select';
            jq.each(f, function() { this.filter(filter).attr('selectedIndex', 0); });
        } else if (f.year.val() > 0 && f.month.val() > 0 && f.day.val() > 0) {
            // ISO date string
            val = [f.year.val(), f.month.val(), f.day.val()].join('-');
            
            var date = new Date(val.replace(/-/g, '/'));
            if (date.print('%Y-%m-%d') != val) {
                // Date turnes illegal dates into legal ones, update widgets
                val = date.print('%Y-%m-%d');
                f.year.val(val.substring(0, 4));
                f.month.val(val.substring(5, 7));
                f.day.val(val.substring(8, 10));
            }
            
            // optional time
            if (f.hour.length && f.minute.length) {
                val += " " + [f.hour.val(), f.minute.val()].join(':');
                if (f.ampm.length) val += " " + f.ampm.val();
            }
        }
        
        f.field.val(val);
    }
};

// initialize fields
jq(plone.jscalendar.init);

// Backwards compatibility function names
var showJsCalendar = plone.jscalendar.show;
var onJsCalendarDateUpdate = plone.jscalendar.handle_select;
var update_date_field = plone.jscalendar.update_hidden;
