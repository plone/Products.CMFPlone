

// Heads up! August 2003  - Geir Bækholt
// This file now requires the javascript variable portal_url to be set 
// in the plone_javascript_variables.js file. Any other variables from Plone
// that you want to pass into these scripts should be placed there.

/* <dtml-var "enableHTTPCompression(request=REQUEST, debug=1, js=1)"> (this is for http compression) */

function registerPloneFunction(func){
    // registers a function to fire onload. 
	// Turned out we kept doing this all the time
	// Use this for initilaizing any javascript that should fire once the page has been loaded. 
	// 
    if (window.addEventListener) window.addEventListener("load",func,false);
    else if (window.attachEvent) window.attachEvent("onload",func);   
  }

function getContentArea(){
	// to end all doubt on where the content sits. It also felt a bit silly doing this over and over in every
	// function, even if it is a tiny operation. Just guarding against someone changing the names again, in the name
	// of semantics or something.... ;)
	node =  document.getElementById('region-content')
	if (! node){
		node = document.getElementById('content')
		}
	return node
	}

function wrapNode(node, wrappertype, wrapperclass){
    // utility function to wrap a node "node" in an arbitrary element of type "wrappertype" , with a class of "wrapperclass"
    wrapper = document.createElement(wrappertype)
    wrapper.className = wrapperclass;
    innerNode = node.parentNode.replaceChild(wrapper,node);
    wrapper.appendChild(innerNode)
}
  










// The calendar popup show/hide:

    function showDay(date) {
        document.getElementById('day' + date).style.visibility = 'visible';
        return true;
    }    
    function hideDay(date) {
        document.getElementById('day' + date).style.visibility = 'hidden';
        return true;
    }



	
// Focus on error or tabindex=1 
function setFocus() {
    var xre = new RegExp(/\berror\b/);
    // Search only forms to avoid spending time on regular text
    for (var f = 0; (formnode = document.getElementsByTagName('form').item(f)); f++) {
        // Search for errors first, focus on first error if found
        for (var i = 0; (node = formnode.getElementsByTagName('div').item(i)); i++) {
            if (xre.exec(node.className)) {
                for (var j = 0; (inputnode = node.getElementsByTagName('input').item(j)); j++) {
                    inputnode.focus();
                    return;   
                }
            }
        }
        // If no error, focus on input element with tabindex 1
        
        
        // uncomment to reactivate
        // this part works as intended, but there are too many places where this function causes pain, moving 
        // focus away from a field in whuch the user is already typing
        
        //for (var i = 0; (node = formnode.getElementsByTagName('input').item(i)); i++) {
         //   if (node.getAttribute('tabindex') == 1) {
         //       node.focus();
         //        return;   
         //   }
        //}
    }
}
registerPloneFunction(setFocus)





/********* Table sorter script *************/
// Table sorter script, thanks to Geir Bækholt for this.
// DOM table sorter originally made by Paul Sowden 

function compare(a,b)
{
    au = new String(a);
    bu = new String(b);

    if (au.charAt(4) != '-' && au.charAt(7) != '-')
    {
    var an = parseFloat(au)
    var bn = parseFloat(bu)
    }
    if (isNaN(an) || isNaN(bn))
        {as = au.toLowerCase()
         bs = bu.toLowerCase()
        if (as > bs)
            {return 1;}
        else
            {return -1;}
        }
    else {
    return an - bn;
    }
}



function getConcatenedTextContent(node) {
    var _result = "";
	  if (node == null) {
		    return _result;
	  }
    var childrens = node.childNodes;
    var i = 0;
    while (i < childrens.length) {
        var child = childrens.item(i);
        switch (child.nodeType) {
            case 1: // ELEMENT_NODE
            case 5: // ENTITY_REFERENCE_NODE
                _result += getConcatenedTextContent(child);
                break;
            case 3: // TEXT_NODE
            case 2: // ATTRIBUTE_NODE
            case 4: // CDATA_SECTION_NODE
                _result += child.nodeValue;
                break;
            case 6: // ENTITY_NODE
            case 7: // PROCESSING_INSTRUCTION_NODE
            case 8: // COMMENT_NODE
            case 9: // DOCUMENT_NODE
            case 10: // DOCUMENT_TYPE_NODE
            case 11: // DOCUMENT_FRAGMENT_NODE
            case 12: // NOTATION_NODE
                // skip
                break;
        }
        i ++;
    }
  	return _result;
}

function sort(e) {
    var el = window.event ? window.event.srcElement : e.currentTarget;

    // a pretty ugly sort function, but it works nonetheless
    var a = new Array();
    // check if the image or the th is clicked. Proceed to parent id it is the image
    // NOTE THAT nodeName IS UPPERCASE
    if (el.nodeName == 'IMG') el = el.parentNode;
    //var name = el.firstChild.nodeValue;
    // This is not very robust, it assumes there is an image as first node then text
    var name = el.childNodes.item(1).nodeValue;
    var dad = el.parentNode;
    var node;
    
    // kill all arrows
    for (var im = 0; (node = dad.getElementsByTagName("th").item(im)); im++) {
        // NOTE THAT nodeName IS IN UPPERCASE
        if (node.lastChild.nodeName == 'IMG')
        {
            lastindex = node.getElementsByTagName('img').length - 1;
            node.getElementsByTagName('img').item(lastindex).setAttribute('src',portal_url + '/arrowBlank.gif');
        }
    }
    
    for (var i = 0; (node = dad.getElementsByTagName("th").item(i)); i++) {
        var xre = new RegExp(/\bnosort\b/);
        // Make sure we are not messing with nosortable columns, then check second node.
        if (!xre.exec(node.className) && node.childNodes.item(1).nodeValue == name) 
        {
            //window.alert(node.childNodes.item(1).nodeValue;
            lastindex = node.getElementsByTagName('img').length -1;
            node.getElementsByTagName('img').item(lastindex).setAttribute('src',portal_url + '/arrowUp.gif');
            break;
        }
    }

    var tbody = dad.parentNode.parentNode.getElementsByTagName("tbody").item(0);
    for (var j = 0; (node = tbody.getElementsByTagName("tr").item(j)); j++) {

        // crude way to sort by surname and name after first choice
        a[j] = new Array();
        a[j][0] = getConcatenedTextContent(node.getElementsByTagName("td").item(i));
        a[j][1] = getConcatenedTextContent(node.getElementsByTagName("td").item(1));
        a[j][2] = getConcatenedTextContent(node.getElementsByTagName("td").item(0));		
        a[j][3] = node;
    }

    if (a.length > 1) {
	
        a.sort(compare);

        // not a perfect way to check, but hell, it suits me fine
        if (a[0][0] == getConcatenedTextContent(tbody.getElementsByTagName("tr").item(0).getElementsByTagName("td").item(i))
	       && a[1][0] == getConcatenedTextContent(tbody.getElementsByTagName("tr").item(1).getElementsByTagName("td").item(i))) 
        {
            a.reverse();
            lastindex = el.getElementsByTagName('img').length - 1;
            el.getElementsByTagName('img').item(lastindex).setAttribute('src', portal_url + '/arrowDown.gif');
        }

    }
	
    for (var j = 0; j < a.length; j++) {
        tbody.appendChild(a[j][3]);
    }
}
    
function initalizeTableSort(e) {
    var tbls = document.getElementsByTagName('table');
    for (var t = 0; t < tbls.length; t++)
        {
        // elements of class="listing" can be sorted
        var re = new RegExp(/\blisting\b/)
        // elements of class="nosort" should not be sorted
        var xre = new RegExp(/\bnosort\b/)
        if (re.exec(tbls[t].className) && !xre.exec(tbls[t].className))
        {
            try {
                var tablename = tbls[t].getAttribute('id');
                var thead = document.getElementById(tablename).getElementsByTagName("thead").item(0);
                var node;
                // set up blank spaceholder gifs
                blankarrow = document.createElement('img');
                blankarrow.setAttribute('src', portal_url + '/arrowBlank.gif');
                blankarrow.setAttribute('height',6);
                blankarrow.setAttribute('width',9);
                // the first sortable column should get an arrow initially.
                initialsort = false;
                for (var i = 0; (node = thead.getElementsByTagName("th").item(i)); i++) {
                    // check that the columns does not have class="nosort"
                    if (!xre.exec(node.className)) {
                        node.insertBefore(blankarrow.cloneNode(1), node.firstChild);
                        if (!initialsort) {
                            initialsort = true;
                            uparrow = document.createElement('img');
                            uparrow.setAttribute('src', portal_url + '/arrowUp.gif');
                            uparrow.setAttribute('height',6);
                            uparrow.setAttribute('width',9);
                            node.appendChild(uparrow);
                        } else {
                            node.appendChild(blankarrow.cloneNode(1));
                        }
    
                        if (node.addEventListener) node.addEventListener("click",sort,false);
                        else if (node.attachEvent) node.attachEvent("onclick",sort);
                    }
                }
            } catch(er) {}
        }
    }
}   
// **** End table sort script ***
registerPloneFunction(initalizeTableSort)   


// Actions used in the folder_contents view
function submitFolderAction(folderAction) {
    document.folderContentsForm.action = document.folderContentsForm.action+'/'+folderAction;
    document.folderContentsForm.submit();
}

function submitFilterAction() {
    document.folderContentsForm.action = document.folderContentsForm.action+'/folder_contents';
    filter_selection=document.getElementById('filter_selection');
    for (var i =0; i < filter_selection.length; i++){
        if (filter_selection.options[i].selected) {
            if (filter_selection.options[i].value=='#') {
                document.folderContentsForm.filter_state.value='clear_view_filter';
            }
            else {
                document.folderContentsForm.filter_state.value='set_view_filter';
            }
        }						
    }
    document.folderContentsForm.submit();
}
    

// Functions for selecting all checkboxes in folder_contents/search_form view

function selectAll(id, formName) {
  // get the elements. if formName is p rovided, get the elements inside the form
  if (formName==null) {
     checkboxes = document.getElementsByName(id)
     for (i = 0; i < checkboxes.length; i++)
         checkboxes[i].checked = true ;
  } else {
     for (i=0; i<document.forms[formName].elements.length;i++)
	 {
	   if (document.forms[formName].elements[i].name==id) 
            document.forms[formName].elements[i].checked=true;
	  }
  }
}

function deselectAll(id, formName) {
  if (formName==null) {
     checkboxes = document.getElementsByName(id)
     for (i = 0; i < checkboxes.length; i++)
         checkboxes[i].checked = false ;
  } else {
     for (i=0; i<document.forms[formName].elements.length;i++)
	 {
	   if (document.forms[formName].elements[i].name==id) 
            document.forms[formName].elements[i].checked=false;
	  }
  }
}

function toggleSelect(selectbutton, id, initialState, formName) {
  // required selectbutton: you can pass any object that will function as a toggle
  // optional id: id of the the group of checkboxes that needs to be toggled (default=ids:list
  // optional initialState: initial state of the group. (default=false)
  //   e.g. folder_contents is false, search_form=true because the item boxes
  //   are checked initially.
  // optional formName: name of the form in which the boxes reside, use this if there are more
  //   forms on the page with boxes with the same name

  id=id || 'ids:list'  // defaults to ids:list, this is the most common usage

  if (selectbutton.isSelected==null)
  {
      initialState=initialState || false;
	  selectbutton.isSelected=initialState;
  }
  
  // create and use a property on the button itself so you don't have to 
  // use a global variable and we can have as much groups on a page as we like.
  if (selectbutton.isSelected == false) {
    selectbutton.setAttribute('src', portal_url + '/select_none_icon.gif');
    selectbutton.isSelected=true;
    return selectAll(id, formName);
  }
  else {
    selectbutton.setAttribute('src',portal_url + '/select_all_icon.gif');
    selectbutton.isSelected=false;
    return deselectAll(id, formName);
  }
}

 

// script for detecting external links.
// sets their target-attribute to _blank , and adds a class external

function scanforlinks(){
    // securing against really old DOMs 
    
    if (! document.getElementsByTagName){return false};
    if (! document.getElementById){return false};
    // Quick utility function by Geir Bækholt
    // Scan all links in the document and set classes on them dependant on 
    // whether they point to the current site or are external links
    
    contentarea = getContentArea()
    if (! contentarea){return false}
    
    links = contentarea.getElementsByTagName('a');
    for (i=0; i < links.length; i++){      
        if ((links[i].getAttribute('href'))&&(links[i].className.indexOf('link-plain')==-1 )){
            var linkval = links[i].getAttribute('href')
            // check if the link href is a relative link, or an absolute link to the current host.
			if (linkval.toLowerCase().indexOf(window.location.protocol+'//'+window.location.host)==0) {
                // we are here because the link is an absolute pointer internal to our host
                // do nothing
            } else if (linkval.indexOf('http:') != 0){
                // not a http-link. Possibly an internal relative link, but also possibly a mailto ot other snacks
                // add tests for all relevant protocols as you like.
                
                protocols = ['mailto', 'ftp', 'news', 'irc', 'h323', 'sip', 'callto', 'https']
                // h323, sip and callto are internet telephony VoIP protocols
                
                for (p=0; p < protocols.length; p++){  
                     if (linkval.indexOf(protocols[p]+':') == 0){
                    // this link matches the protocol . add a classname protocol+link
                    //links[i].className = 'link-'+protocols[p]
                        wrapNode(links[i], 'span', 'link-'+protocols[p])
                        break;
                    }
                }
            }else{
                // we are in here if the link points to somewhere else than our site.
                if ( links[i].getElementsByTagName('img').length == 0 ){
					// we do not want to mess with those links that already have images in them
                    //links[i].className = 'link-external'
                    wrapNode(links[i], 'span', 'link-external')
                    //links[i].setAttribute('target','_blank')
                    }
                
                
                
                
            }
        }
    }
}
registerPloneFunction(scanforlinks)   


function climb(node, word){
	 // traverse childnodes
    if (! node){return false}
    if (node.hasChildNodes) {
		var i;
		for (i=0;i<node.childNodes.length;i++) {
            climb(node.childNodes[i],word);
		}
        if (node.nodeType == 3){
            checkforhighlight(node, word);
           // check all textnodes. Feels inefficient, but works
        }
}
function checkforhighlight(node,word) {
        ind = node.nodeValue.toLowerCase().indexOf(word.toLowerCase())
		if (ind != -1) {
            if (node.parentNode.className != "highlightedSearchTerm"){
                par = node.parentNode;
                contents = node.nodeValue;
			
                // make 3 shiny new nodes
                hiword = document.createElement("span");
				hiword.className = "highlightedSearchTerm";
				hiword.appendChild(document.createTextNode(contents.substr(ind,word.length)));
				
                par.insertBefore(document.createTextNode(contents.substr(0,ind)),node);
				par.insertBefore(hiword,node);
				par.insertBefore(document.createTextNode(contents.substr(ind+word.length)),node);

                par.removeChild(node);
		        }
        	} 
		}
  
}


function correctPREformatting(){
        // small utility thing to correct formatting for PRE-elements and some others
        // thanks to Michael Zeltner for CSS-guruness and research ;) 
		// currently not activated
        contentarea = getContentArea();
        if (! contentarea){return false}
        
        pres = contentarea.getElementsByTagName('pre');
        for (i=0;i<pres.length;i++){
           wrapNode(pres[i],'div','visualOverflow')
			}
               
        //tables = contentarea.getElementsByTagName('table');
        // for (i=0;i<tables.length;i++){
        //   if (tables[i].className=="listing"){
        //   wrapNode(tables[i],'div','visualOverflow')
		//  }
        //}      
}
//registerPloneFunction(correctPREformatting);

function highlightSearchTerm() {
        // search-term-highlighter function --  Geir Bækholt
        query = window.location.search
        // _robert_ ie 5 does not have decodeURI 
        if (typeof decodeURI != 'undefined'){
            query = decodeURI(unescape(query)) // thanks, Casper 
        }
        else {
            return false
        }
        if (query){
            var qfinder = new RegExp()
            qfinder.compile("searchterm=([^&]*)","gi")
            qq = qfinder.exec(query)
            if (qq && qq[1]){
                query = qq[1]
                
                // the cleaner bit is not needed anymore, now that we travese textnodes. 
                //cleaner = new RegExp
                //cleaner.compile("[\\?\\+\\\\\.\\*]",'gi')
                //query = query.replace(cleaner,'')
                
                if (!query){return false}
                queries = query.replace(/\+/g,' ').split(/\s+/)
                
                // make sure we start the right place and not higlight menuitems or breadcrumb
                contentarea = getContentArea();
				for (q=0;q<queries.length;q++) {
                    climb(contentarea,queries[q]);
                }
            }
        }
}
registerPloneFunction(highlightSearchTerm);


// ----------------------------------------------
// StyleSwitcher functions written by Paul Sowden
// http://www.idontsmoke.co.uk/ss/
// - - - - - - - - - - - - - - - - - - - - - - -
// For the details, visit ALA:
// http://www.alistapart.com/stories/alternate/
// ----------------------------------------------

function setActiveStyleSheet(title, reset) {
  var i, a, main;
  for(i=0; (a = document.getElementsByTagName("link")[i]); i++) {
    if(a.getAttribute("rel").indexOf("style") != -1 && a.getAttribute("title")) {
      a.disabled = true;
      if(a.getAttribute("title") == title) a.disabled = false;
    }
  }
  if (reset == 1) {
  createCookie("wstyle", title, 365);
  }
}

function setStyle() {
var style = readCookie("wstyle");
if (style != null) {
setActiveStyleSheet(style, 0);
}
}

function createCookie(name,value,days) {
  if (days) {
    var date = new Date();
    date.setTime(date.getTime()+(days*24*60*60*1000));
    var expires = "; expires="+date.toGMTString();
  }
  else expires = "";
  document.cookie = name+"="+escape(value)+expires+"; path=/;";
}

function readCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(';');
  for(var i=0;i < ca.length;i++) {
    var c = ca[i];
    while (c.charAt(0)==' ') c = c.substring(1,c.length);
    if (c.indexOf(nameEQ) == 0) return unescape(c.substring(nameEQ.length,c.length));
  }
  return null;
}
registerPloneFunction(setStyle);





// jscalendar glue -- Leonard Norrgård <vinsci@*>
// This function gets called when the user clicks on some date.
function onJsCalendarDateUpdate(cal) {
    var year   = cal.params.input_id_year;
    var month  = cal.params.input_id_month;
    var day    = cal.params.input_id_day;
    // var hour   = cal.params.input_id_hour;
    // var minute = cal.params.input_id_minute;

    // cal.params.inputField.value = cal.date.print('%Y/%m/%d %H:%M'); // doesn't work in Opera, don't use time now
    //cal.params.inputField.value = cal.date.print('%Y/%m/%d'); // doesn't work in Opera
    var daystr = '' + cal.date.getDate();
    if (daystr.length == 1)
    	daystr = '0' + daystr;
    var monthstr = '' + (cal.date.getMonth()+1);
    if (monthstr.length == 1)
	monthstr = '0' + monthstr;
    cal.params.inputField.value = '' + cal.date.getFullYear() + '/' + monthstr + '/' + daystr

    year.value  = cal.params.inputField.value.substring(0,4);
    month.value = cal.params.inputField.value.substring(5,7);
    day.value   = cal.params.inputField.value.substring(8,10);
    // hour.value  = cal.params.inputField.value.substring(11,13);
    // minute.value= cal.params.inputField.value.substring(14,16);
}

// this funtion updates a hidden date filed with the current values of the widgets
function update_date_field(field,year,month,day,hour,minute) {
    var field  = document.getElementById(field);
    var date   = document.getElementById(date);
    var year   = document.getElementById(year);
    var month  = document.getElementById(month);
    var day    = document.getElementById(day);
    var hour   = document.getElementById(hour);
    var minute = document.getElementById(minute);
    if (year.value > 0) {
	field.value = year.value + "-" + month.value + "-" + day.value + " " + hour.options[hour.selectedIndex].value + ":" + minute.options[minute.selectedIndex].value;
    } else {
	field.value = '';
    }
}

function showJsCalendar(input_id_anchor, input_id, input_id_year, input_id_month, input_id_day, input_id_hour, input_id_minute, yearStart, yearEnd) {
    // do what jscalendar-x.y.z/calendar-setup.js:Calendar.setup would do
    var input_id_anchor = document.getElementById(input_id_anchor);
    var input_id = document.getElementById(input_id);
    var input_id_year = document.getElementById(input_id_year);
    var input_id_month = document.getElementById(input_id_month);
    var input_id_day = document.getElementById(input_id_day);
    // var input_id_hour = document.getElementById(input_id_hour);
    // var input_id_minute = document.getElementById(input_id_minute);
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
	// input_id_hour : input_id_hour,
	// input_id_minute: input_id_minute
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
    param_default("mondayFirst",    true);
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

    if (!window.calendar) {
	window.calendar = cal = new Calendar(true, //params.mondayFirst,
	     null,
	     onJsCalendarDateUpdate,
	     function(cal) { cal.hide(); });
	cal.time24 = true;
	cal.weekNumbers = true;
	mustCreate = true;
    } else {
	cal.hide();
    }
    cal.setRange(yearStart,yearEnd);
    cal.params = params;
    cal.setDateStatusHandler(null);
    cal.setDateFormat(format);
    if (mustCreate)
	cal.create();
    cal.parseDate(dateEl.value || dateEl.innerHTML);
    cal.refresh();
    cal.showAtElement(input_id_anchor, null);
    return false;
}



function fullscreenMode() {
    if (document.getElementById('portal-top').style.display == 'none') {
        document.getElementById('portal-top').style.display = 'block';
        document.getElementById('portal-column-one').style.display = 'block';
        document.getElementById('portal-column-two').style.display = 'block';
        }
    else {
        document.getElementById('portal-top').style.display = 'none';
        document.getElementById('portal-column-one').style.display = 'none';
        document.getElementById('portal-column-two').style.display = 'none';
    }
}


// and finally : Mike Malloch's fixes for Internet Explorer 5 - 
// These should be considered temporary, as they actually add functionality to IE5, while we just want it to not blurt errormessages... 
//

function hackPush(el){
        this[this.length] = el;
}

function hackPop(){
        var N = this.length - 1, el = this[N];
        this.length = N
        return el;
}

function hackShift(){
        var one = this[0], N = this.length;
        for (var i = 1; i < N; i++){
                this[i-1] = this[i];
        }
        this.length = N-1
        return one;
}

var testPushPop = new Array();
if (testPushPop.push){
}else{
        Array.prototype.push = hackPush
        Array.prototype.pop = hackPop
        Array.prototype.shift =hackShift;
}

