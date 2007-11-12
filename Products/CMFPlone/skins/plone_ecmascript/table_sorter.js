
/********* Table sorter script *************/
// Table sorter script, thanks to Geir Bækholt for this.
// DOM table sorter originally made by Paul Sowden 

function tablecompare(a,b)
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
    
        a.sort(tablecompare);

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
        a[j][3].className = ((j % 2) == 0) ? 'odd' : 'even';
        tbody.appendChild(a[j][3]);
    }
}
    
function initalizeTableSort(e) {
    // terminate if we hit a non-compliant DOM implementation
    if (!W3CDOM){return false};

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
               var thead = tbls[t].getElementsByTagName("thead").item(0);
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
                        node.style.cursor = 'pointer';
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

