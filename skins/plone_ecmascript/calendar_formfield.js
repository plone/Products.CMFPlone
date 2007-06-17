// jscalendar glue -- Leonard Norrgård <vinsci@*>
// This function gets called when the user clicks on some date.
function onJsCalendarDateUpdate(cal) {
    var year   = cal.params.input_id_year;
    var month  = cal.params.input_id_month;
    var day    = cal.params.input_id_day;

    var daystr = '' + cal.date.getDate();
    if (daystr.length == 1)
        daystr = '0' + daystr;
    var monthstr = '' + (cal.date.getMonth()+1);
    if (monthstr.length == 1)
        monthstr = '0' + monthstr;
    cal.params.inputField.value = '' + cal.date.getFullYear() + '/' + monthstr + '/' + daystr

    var yearValue  = cal.params.inputField.value.substring(0,4);

    // Check if year already exists in the options list.
    var yearExists = false;
    for (var i = 0; i < year.options.length; i++) {
        if (year.options[i].value == yearValue) {
            yearExists = true;
        }
    }

    if (!yearExists) {
        // Append missing year to the options list
        year.options[year.length] = new Option('' + yearValue, yearValue, false, true);

        // Sort options list inplace considering the list is already sorted
        // and only the last option is not at the right place.
        // Stop at i > 1 as the first option is not a year but the "----" string.
        for (var i = year.options.length - 1; i > 1; i--) {
            if (year.options[i].value < year.options[i-1].value) {
                // Swap options
                var option1 = year.options[i];
                var option2 = year.options[i-1];
                year.options[i] = new Option(option2.text, option2.value, option2.defaultSelected, option2.selected);
                year.options[i-1] = new Option(option1.text, option1.value, option1.defaultSelected, option1.selected);
            }
        }
    }

    year.value  = yearValue;
    month.value = cal.params.inputField.value.substring(5,7);
    day.value   = cal.params.inputField.value.substring(8,10);
    // hour.value  = cal.params.inputField.value.substring(11,13);
    // minute.value= cal.params.inputField.value.substring(14,16);
}


function showJsCalendar(input_id_anchor, input_id, input_id_year, input_id_month, input_id_day, input_id_hour, input_id_minute, yearStart, yearEnd) {
    // do what jscalendar-x.y.z/calendar-setup.js:Calendar.setup would do
    var input_id_anchor = document.getElementById(input_id_anchor);
    var input_id = document.getElementById(input_id);
    var input_id_year = document.getElementById(input_id_year);
    var input_id_month = document.getElementById(input_id_month);
    var input_id_day = document.getElementById(input_id_day);
    var format = 'y/mm/dd';

    var dateEl = input_id;
    var mustCreate = false;
    var cal = window.calendar;

    var params = {
        'range' : [yearStart, yearEnd],
        inputField : input_id,
        input_id_year : input_id_year,
        input_id_month: input_id_month,
        input_id_day  : input_id_day
    };

    function param_default(pname, def) { if (typeof params[pname] == "undefined") { params[pname] = def; } };

    param_default("inputField",     null);
    param_default("displayArea",    null);
    param_default("button",         null);
    param_default("eventName",      "click");
    param_default("ifFormat",       "%Y/%m/%d");
    param_default("daFormat",       "%Y/%m/%d");
    param_default("singleClick",    true);
    param_default("disableFunc",    null);
    param_default("dateStatusFunc", params["disableFunc"]); // takes precedence if both are defined
    param_default("dateText",       null);
    param_default("firstDay",       1);
    param_default("align",          "Bl");
    param_default("range",          [1900, 2999]);
    param_default("weekNumbers",    true);
    param_default("flat",           null);
    param_default("flatCallback",   null);
    param_default("onSelect",       null);
    param_default("onClose",        null);
    param_default("onUpdate",       null);
    param_default("date",           null);
    param_default("showsTime",      false);
    param_default("timeFormat",     "24");
    param_default("electric",       true);
    param_default("step",           2);
    param_default("position",       null);
    param_default("cache",          false);
    param_default("showOthers",     false);
    param_default("multiple",       null);

    if (!(cal && params.cache)) {
	window.calendar = cal = new Calendar(params.firstDay,
	     null,
	     onJsCalendarDateUpdate,
	     function(cal) { cal.hide(); });
	cal.time24 = true;
	cal.weekNumbers = true;
	mustCreate = true;
    } else {
        cal.hide();
    }
    cal.showsOtherMonths = false;
    cal.yearStep = 2;
    cal.setRange(yearStart,yearEnd);
    cal.params = params;
    cal.setDateStatusHandler(null);
    cal.getDateText = null;
    cal.setDateFormat(format);
    if (mustCreate)
	cal.create();
    cal.refresh();
    if (!params.position)
        cal.showAtElement(input_id_anchor, null);
    else
        cal.showAt(params.position[0], params.position[1]);
    return false;
}


// This function updates a hidden date field with the current values of the widgets
function update_date_field(field, year, month, day, hour, minute, ampm)
{
    var field  = document.getElementById(field)
    var date   = document.getElementById(date)
    var year   = document.getElementById(year)
    var month  = document.getElementById(month)
    var day    = document.getElementById(day)
    var hour   = document.getElementById(hour)
    var minute = document.getElementById(minute)
    var ampm   = document.getElementById(ampm)

    if (0 < year.value)
    {
        // Return ISO date string
        // Note: This relies heavily on what date_components_support.py puts into the form.
        field.value = year.value + "-" + month.value + "-" + day.value + " " + hour.value + ":" + minute.value
        // Handle optional AM/PM
        if (ampm && ampm.value)
            field.value = field.value + " " + ampm.value
    } 
    else 
    {
        // Return empty string
        field.value = ''
        // Reset widgets
        month.options[0].selected = 1
        day.options[0].selected = 1
        hour.options[0].selected = 1
        minute.options[0].selected = 1
        if (ampm && ampm.options)
            ampm.options[0].selected = 1
    }
}
