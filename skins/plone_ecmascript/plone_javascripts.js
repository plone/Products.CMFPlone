

// Heads up! August 2003  - Geir Bækholt
// This file now requires the javascript variable portal_url to be set 
// in the plone_javascript_variables.js file. Any other variables from Plone
// that you want to pass into these scripts should be placed there.


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
if (window.addEventListener) window.addEventListener("load",setFocus,false);
else if (window.attachEvent) window.attachEvent("onload",setFocus);
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
        for (var i = 0; (node = formnode.getElementsByTagName('input').item(i)); i++) {
            if (node.getAttribute('tabindex') == 1) {
                 node.focus();
                 return;   
            }
        }
    }
}

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
    
function init(e) {
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

// initialize the sorter functions 
// add stuff to secure it from broken DOM-implanetations or missing objects.
   
    
    	
//    p.appendChild(document.createTextNode("Change sorting by clicking on each individual heading."));
//    document.getElementById(tablename).parentNode.insertBefore(p,document.getElementById(tablename));
    

if (window.addEventListener) window.addEventListener("load",init,false);
else if (window.attachEvent) window.attachEvent("onload",init);

       
// **** End table sort script ***



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


function wrapNode(node, wrappertype, wrapperclass){
    // utility function to wrap a node "node" in an arbitrary element of type "wrappertype" , with a class of "wrapperclass"
    wrapper = document.createElement(wrappertype)
    wrapper.className = wrapperclass;
    innerNode = node.parentNode.replaceChild(wrapper,node);
    wrapper.appendChild(innerNode)
}
    

// script for detecting external links.
// sets their target-attribute to _blank , and adds a class external

function scanforlinks(){
    // securing against really old DOMs 
    
    if (! document.getElementsByTagName){return false};
    if (! document.getElementById){return false};
    // Quick utility function by Geir Bækholt
    // Scan all links in the document and set classes on them dependant on whether they point to the current site or are external links
    
    contentarea = document.getElementById('content')
    if (! contentarea){return false}
    
    links = contentarea.getElementsByTagName('a');
    for (i=0; i < links.length; i++){      
        if (links[i].getAttribute('href')){
            var linkval = links[i].getAttribute('href')
            // check if the link href is a relative link, or an absolute link to the current host.
            if (linkval.indexOf(window.location.protocol+'//'+window.location.host)==0){
                // we are here because the link is an absolute pointer internal to our host
                // do nothing
            } else if (linkval.indexOf('http:') == -1){
                // not a http-link. Possibly an internal relative link, but also possibly a mailto ot other snacks
                // add tests for all relevant protocols as you like.
                
                protocols = ['mailto', 'ftp' , 'irc', 'callto', 'https']
                // callto is a proprietary protocol to the Skype application, but we happen to like it ;)
                
                for (p=0; p < protocols.length; p++){  
                     if (linkval.indexOf(protocols[p]+':') != -1){
                    // this link matches the protocol . add a classname protocol+link
                    //links[i].className = 'link-'+protocols[p]
                    wrapNode(links[i], 'span', 'link-'+protocols[p])
                    }
                }
            }else{
                // we are in here if the link points to somewhere else than our site.
                if ( links[i].getElementsByTagName('img').length == 0 ){
                    //links[i].className = 'link-external'
                    wrapNode(links[i], 'span', 'link-external')
                    //links[i].setAttribute('target','_blank')
                    }
                
                
                
                
            }
        }
    }
}

if (window.addEventListener) window.addEventListener("load",scanforlinks,false);
else if (window.attachEvent) window.attachEvent("onload",scanforlinks);


function climb(node, word){
	 // traverse childnodes
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
        contentarea = document.getElementById('content')
        if (! contentarea){return false}
        
        pres = contentarea.getElementsByTagName('pre');
        for (i=0;i<pres.length;i++){
           wrapNode(pres[i],'div','visualOverflow')
		}
               
        tables = contentarea.getElementsByTagName('table');
        for (i=0;i<tables.length;i++){
           if (tables[i].className=="listing"){
           wrapNode(tables[i],'div','visualOverflow')
		   }
        }
        
}
// if (window.addEventListener) window.addEventListener("load",correctPREformatting,false);
// else if (window.attachEvent) window.attachEvent("onload",correctPREformatting);



function highlightSearchTerm() {
        // search-term-highlighter function --  Geir Bækholt
        query = window.location.search
        // _robert_ ie 5 does not have decodeURI 
        if (typeof decodeURI != 'undefined'){
            query = decodeURI(query)
        }
        else {
            return false
        }
        if (query){
            var qfinder = new RegExp()
            qfinder.compile("searchterm=(.*)","gi")
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
                theContents = document.getElementById('bodyContent');
                for (q=0;q<queries.length;q++) {
                    climb(theContents,queries[q]);
                }
            }
        }
}
if (window.addEventListener) window.addEventListener("load",highlightSearchTerm,false);
else if (window.attachEvent) window.attachEvent("onload",highlightSearchTerm);

<!--

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
  document.cookie = name+"="+value+expires+"; path=/;";
}

function readCookie(name) {
  var nameEQ = name + "=";
  var ca = document.cookie.split(';');
  for(var i=0;i < ca.length;i++) {
    var c = ca[i];
    while (c.charAt(0)==' ') c = c.substring(1,c.length);
    if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
  }
  return null;
}

if (window.addEventListener) window.addEventListener("load",setStyle,false);
else if (window.attachEvent) window.attachEvent("onload",setStyle);