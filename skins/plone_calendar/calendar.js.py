return r"""//<%@language = "JScript" %><%
// JavaScript Calendar Component
// Author: Robert W. Husted  (robert.husted@iname.com)
// Date:   8/22/1999
// Modified Date: 11/30/1999
// Modified By:   Bryan Davis
// Notes:  stripped nationalization and some other config info for space reasons
calDateFormat    = "yyyy-mm-dd";
// CALENDAR COLORS
topBackground    = "black"; 
bottomBackground = "white"; 
tableBGColor     = "#8cacbb"; 
cellColor        = "#dee7ec"; 
headingCellColor = "white";     
headingTextColor = "black";     
dateColor        = "blue";      
focusColor       = "#ff0000";   
hoverColor       = "darkred";   
fontStyle        = "10px Verdana, Helvetica, Arial, sans-serif";  
headingFontStyle = "bold 10px Verdana, Helvetica, Arial, sans-serif"; 

bottomBorder  = false;        
tableBorder   = 0;            
var isNav = false;
var isIE  = false;
if (navigator.appName == "Netscape") {
    isNav = true;
}
else {
    isIE = true;
}
buildCalParts();
function setDateField(dateField) {
    calDateField = dateField;
    inDate = dateField.value;
    setInitialDate();
    calDocTop    = buildTopCalFrame();
    calDocBottom = buildBottomCalFrame();
}
function setInitialDate() {
   calDate = new Date(inDate);
    if (isNaN(calDate)) {
        calDate = new Date();
    }
    calDay  = calDate.getDate();
    calDate.setDate(1);
}
function showCalendar(dateField) {
    setDateField(dateField);
    calDocFrameset = 
        "<HTML><HEAD><TITLE>JavaScript Calendar</TITLE></HEAD>\n" +
        "<FRAMESET ROWS='70,*' FRAMEBORDER='0'>\n" +
        "  <FRAME NAME='topCalFrame' SRC='javascript:parent.opener.calDocTop' SCROLLING='no'>\n" +
        "  <FRAME NAME='bottomCalFrame' SRC='javascript:parent.opener.calDocBottom' SCROLLING='no'>\n" +
        "</FRAMESET>\n";
    top.newWin = window.open("javascript:parent.opener.calDocFrameset", "calWin", winPrefs);
    top.newWin.focus();
}
function buildTopCalFrame() {
    var calDoc =
        "<HTML>" +
        "<HEAD>" +

        "<style type=\"text/css\" media=\"all\">" + 
        "@import \"ploneBasic.css\";" +
        "</style>" +

        "</HEAD>" +
        "<BODY BGCOLOR='" + topBackground + "'>" +
        "<FORM NAME='calControl' onSubmit='return false;'>" +
        "<CENTER>" +
        "<TABLE CELLPADDING=0 CELLSPACING=1 BORDER=0>" +
        "<TR><TD>" +
        "<INPUT " +
        "TYPE=BUTTON NAME='previousMonth' VALUE=' &laquo; '   onClick='parent.opener.setPreviousMonth()'>" +
        "</td><td>" +
        getMonthSelect() +
        "</td><td>" +
        "<INPUT " +
        "TYPE=BUTTON NAME='nextMonth' VALUE=' &raquo; '   onClick='parent.opener.setNextMonth()'>" +
        "</td></tr>" +
        "<tr><td>" +
        "<INPUT " +
        "TYPE=BUTTON NAME='previousYear' VALUE=' &laquo; '    onClick='parent.opener.setPreviousYear()'>" +        
        "</td><td align=\"center\">" +
        "<INPUT NAME='year' VALUE='" + calDate.getFullYear() + "'TYPE=TEXT SIZE=5 MAXLENGTH=4 onChange='parent.opener.setYear()'>" +
        "</td><td>" +
        "<INPUT " +
        "TYPE=BUTTON NAME='nextYear' VALUE=' &raquo; '    onClick='parent.opener.setNextYear()'>" +
        "</TD>" +
        "</TR>" +
        "</TABLE>" +
        "</CENTER>" +
        "</FORM>" +
        "</BODY>" +
        "</HTML>";

    return calDoc;
}

function buildBottomCalFrame() {       
    var calDoc = calendarBegin;
    month   = calDate.getMonth();
    year    = calDate.getFullYear();
    day     = calDay;
    var i   = 0;
    var days = getDaysInMonth();
    if (day > days) {
        day = days;
    }
    var firstOfMonth = new Date (year, month, 1);
    var startingPos  = firstOfMonth.getDay();
    days += startingPos;
    var columnCount = 0;
    for (i = 0; i < startingPos; i++) {
        calDoc += blankCell;
		columnCount++;
    }
    var currentDay = 0;
    var dayType    = "weekday";
    for (i = startingPos; i < days; i++) {
		var paddingChar = "&nbsp;";
        if (i-startingPos+1 < 10) {
            padding = "&nbsp;";
        }
        else {
            padding = "&nbsp;";
        }
        currentDay = i-startingPos+1;
        if (currentDay == day) {
            dayType = "focusDay";
        }
        else {
            dayType = "weekDay";
        }
        calDoc += "<TD align=center bgcolor='" + cellColor + "'>" +
                  "<a class='" + dayType + "' href='javascript:parent.opener.returnDate(" + 
                  currentDay + ")'>" +  currentDay + "</a></TD>";
        columnCount++;
		if (columnCount % 7 == 0) {
            calDoc += "</TR><TR>";
        }
    }
    for (i=days; i<42; i++)  {

        calDoc += blankCell;
		columnCount++;
        if (columnCount % 7 == 0) {
            calDoc += "</TR>";
            if (i<41) {
                calDoc += "<TR>";
            }
        }
    }
    calDoc += calendarEnd;
    return calDoc;
}

function writeCalendar() {
	calDocBottom = buildBottomCalFrame();
    top.newWin.frames['bottomCalFrame'].document.open();
    top.newWin.frames['bottomCalFrame'].document.write(calDocBottom);
    top.newWin.frames['bottomCalFrame'].document.close();
}

function setToday() {
    returnDate(-1)
}

function setYear() {
     var year  = top.newWin.frames['topCalFrame'].document.calControl.year.value;
    if (isFourDigitYear(year)) {
        calDate.setFullYear(year);
        writeCalendar();
    }
    else {
        top.newWin.frames['topCalFrame'].document.calControl.year.focus();
        top.newWin.frames['topCalFrame'].document.calControl.year.select();
    }
}

function setCurrentMonth() {

    var month = top.newWin.frames['topCalFrame'].document.calControl.month.selectedIndex;

    calDate.setMonth(month);
    writeCalendar();
}

function setPreviousYear() {
    var year  = top.newWin.frames['topCalFrame'].document.calControl.year.value;
    if (isFourDigitYear(year) && year > 1000) {
        year--;
        calDate.setFullYear(year);
        top.newWin.frames['topCalFrame'].document.calControl.year.value = year;
        writeCalendar();
    }
}

function setPreviousMonth() {
    var year  = top.newWin.frames['topCalFrame'].document.calControl.year.value;
    if (isFourDigitYear(year)) {
        var month = top.newWin.frames['topCalFrame'].document.calControl.month.selectedIndex;
        if (month == 0) {
            month = 11;
            if (year > 1000) {
                year--;
                calDate.setFullYear(year);
                top.newWin.frames['topCalFrame'].document.calControl.year.value = year;
            }
        }
        else {
            month--;
        }
        calDate.setMonth(month);
        top.newWin.frames['topCalFrame'].document.calControl.month.selectedIndex = month;
        writeCalendar();
    }
}

function setNextMonth() {
    var year = top.newWin.frames['topCalFrame'].document.calControl.year.value;
    if (isFourDigitYear(year)) {
        var month = top.newWin.frames['topCalFrame'].document.calControl.month.selectedIndex;
        if (month == 11) {
            month = 0;
            year++;
            calDate.setFullYear(year);
            top.newWin.frames['topCalFrame'].document.calControl.year.value = year;
        }
        else {
            month++;
        }
        calDate.setMonth(month);
        top.newWin.frames['topCalFrame'].document.calControl.month.selectedIndex = month;
        writeCalendar();
    }
}

function setNextYear() {
    var year  = top.newWin.frames['topCalFrame'].document.calControl.year.value;
    if (isFourDigitYear(year)) {
        year++;
        calDate.setFullYear(year);
        top.newWin.frames['topCalFrame'].document.calControl.year.value = year;
        writeCalendar();
    }
}

function getDaysInMonth()  {
    var days;
    var month = calDate.getMonth()+1;
    var year  = calDate.getFullYear();
    if (month==1 || month==3 || month==5 || month==7 || month==8 ||
        month==10 || month==12)  {
        days=31;
    }
    else if (month==4 || month==6 || month==9 || month==11) {
        days=30;
    }
    else if (month==2)  {
        if (isLeapYear(year)) {
            days=29;
        }
        else {
            days=28;
        }
    }
    return (days);
}
function isLeapYear (Year) {

    if (((Year % 4)==0) && ((Year % 100)!=0) || ((Year % 400)==0)) {
        return (true);
    }
    else {
        return (false);
    }
}
function isFourDigitYear(year) {
    if (year.length != 4) {
        top.newWin.frames['topCalFrame'].document.calControl.year.value = calDate.getFullYear();
        top.newWin.frames['topCalFrame'].document.calControl.year.select();
        top.newWin.frames['topCalFrame'].document.calControl.year.focus();
    }
    else {
        return true;
    }
}
function getMonthSelect() {
    monthArray = new Array('January', 'February', 'March', 'April', 'May', 'June',
                               'July', 'August', 'September', 'October', 'November', 'December');
    var activeMonth = calDate.getMonth();
    monthSelect = "<SELECT NAME='month' onChange='parent.opener.setCurrentMonth()'>";
    for (i in monthArray) {
        if (i == activeMonth) {
            monthSelect += "<OPTION SELECTED>" + monthArray[i] + "\n";
        }
        else {
            monthSelect += "<OPTION>" + monthArray[i] + "\n";
        }
    }
    monthSelect += "</SELECT>";
    return monthSelect;
}
function createWeekdayList() {
        weekdayList  = new Array('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday');
        weekdayArray = new Array('Su','Mo','Tu','We','Th','Fr','Sa');
	    var weekdays = "<TR>";
    for (i in weekdayArray) {

        weekdays += "<th>" + weekdayArray[i] + "</th>";
    }
    weekdays += "</TR>";
    return weekdays;
}

function buildCalParts() {
    weekdays = createWeekdayList();
    blankCell = "<TD align=center bgcolor='" + cellColor + "'>&nbsp;&nbsp;&nbsp;</TD>";
    calendarBegin =
        "<HTML>" +
        "<HEAD>" +

// Old code:
//        "<STYLE type='text/css'>" +
//        "<!--" +
//        "TD.heading { text-decoration: none; color:" + headingTextColor + "; font: " + headingFontStyle + "; }" +
//        "A.focusDay:link { color: " + focusColor + "; text-decoration: none; font: " + fontStyle + "; }" +
//        "A.focusDay:hover { color: " + focusColor + "; text-decoration: none; font: " + fontStyle + "; }" +
//        "A.weekday:link { color: " + dateColor + "; text-decoration: none; font: " + fontStyle + "; }" +
//        "A.weekday:hover { color: " + hoverColor + "; font: " + fontStyle + "; }" +
//        "-->" +
//        "</STYLE>" +

        "<style type=\"text/css\" media=\"all\">" + 
        "@import \"ploneBasic.css\";" +
        "@import \"ploneWidgets.css\";" +
        "</style>" +

        "</HEAD>" +
        "<BODY BGCOLOR='" + bottomBackground + "'" +
        "<CENTER>";
        if (isNav) {
            calendarBegin += 
                "<TABLE class=\"listing\" CELLPADDING=0 CELLSPACING=0 BORDER=0 ALIGN=CENTER><TR><TD>";
        }
        calendarBegin +=
            "<TABLE class=\"listing\" CELLPADDING=0 CELLSPACING=0 BORDER=0 ALIGN=CENTER>" +
            weekdays +
            "<TR>";
      calendarEnd = "";
        if (bottomBorder) {
            calendarEnd += "<TR></TR>";
        }
        if (isNav) {
            calendarEnd += "</TD></TR></TABLE>";
        }
        calendarEnd +=
            "</TABLE>" +
            "</CENTER>" +
            "<p align=\"center\">" +
            "<INPUT class=standalone " +
            "TYPE=BUTTON NAME='today' VALUE='Today' onClick='parent.opener.setToday()'>" + 
            "</p>" +
            "</BODY>" +
            "</HTML>";
}
function jsReplace(inString, find, replace) {
    var outString = "";
    if (!inString) {
        return "";
    }
    if (inString.indexOf(find) != -1) {
        t = inString.split(find);
        return (t.join(replace));
    }
    else {
        return inString;
    }
}
function doNothing() {
}
function makeTwoDigit(inValue) {
    var numVal = parseInt(inValue, 10);
    if (numVal < 10) {
        return("0" + numVal);
    }
    else {
        return numVal;
    }
}
function returnDate(inDay)
{
    if ( inDay == -1 )
    {
		calDate  = new Date()
    }
    else
    {
		calDate.setDate(inDay);
	}
	var day           = calDate.getDate();
	var month         = calDate.getMonth() +1 ;
	var year          = calDate.getFullYear();
    outDate = calDateFormat;
    day = makeTwoDigit(day);
    outDate = jsReplace(outDate, "dd", day);
    month = makeTwoDigit(month);
    outDate = jsReplace(outDate, "mm", month);
    outDate = jsReplace(outDate, "yyyy", year);
    calDateField.value = outDate;
    calDateField.focus();
    top.newWin.close()
}
"""
