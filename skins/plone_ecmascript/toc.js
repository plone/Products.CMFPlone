function walkHeaders(node, func, data) {
    /* this is a copy of walkTextNodes in the Plone source, if
    someone was smart they could refactor this into one function
    don't be tempted to use getElementsByTagNames, it won't work
    on Safari (as of Feb 2007), boo! */
    if (!node){return false}
    if (node.hasChildNodes) {
        // we can't use for (i in childNodes) here, because the number of
        // childNodes might change (higlightsearchterms)
        for (var i = 0; i < node.childNodes.length; i++) {
            walkHeaders(node.childNodes[i], func, data);
        }
        var type = node.tagName;
        if (type) {
            type = type.toLowerCase();
            var valid = Array("h1", "h2", "h3", "h4");
            for (var k = 0; k < valid.length; k++) {
                if (valid[k] == type) {
                    func(node, data);
                    break;
                }
            }
        }
    }
}

function locationWithoutHash() {
    /* you can just put # on the end of url's because
    there is a base tag that does not match the actual
    url, its the base tag to the object, so we have 
    to reconstruct from the window.location */
    var loc = window.location.href;
    var hash = window.location.hash;
    if (!hash) {
        return loc;
    } else {
        return loc.substring(0, loc.lastIndexOf(hash));
    }
}

function createTableOfContents() {
    var dest = document.getElementById('toc');
    if (!dest) {
       return;
    }
    var elems = new Array;
    var content = document.getElementById('content');
    if (!content) {
        return;
    }
    walkHeaders(content, function(n, d){d.push(n)}, elems); 
    if (elems.length < 2) {
        /* if there's only two elements, this is all rather pointless */
        return;
    }
    
    var location = locationWithoutHash();
    
    // hidden unless this is actually run
    dest.style.display = "block";
    for (var i=1; i < elems.length; i++) {
        var li = document.createElement('li');
        var tmp = document.createElement('a');
        var elem = elems[i];
        
        tmp.innerHTML = elem.innerHTML;
        // by making it 
        tmp.href = location + '#link' + i;        
        tmp.className = 'tocLink';
        
        // put the level in the class so css can do indentation
        var level = elem.nodeName.substring(1);
        li.className = 'toc-' + level;
        
        li.appendChild(tmp);
        dest.appendChild(li);
        
        // add on return to top links
        // the return to top link, dont need for the top
        if (i < 1) {
            continue;
        }
        var tmp2 = document.createElement('a');
        var span = document.createElement('span');
        
        // insert return link
        tmp2.id = 'link' + i;
        tmp2.href = location + '#documentContent';
        tmp2.className = "tocTop";
        span.innerHTML = "Return to top";
        
        tmp2.appendChild(span);
        elem.parentNode.insertBefore(tmp2, elem);
    }
}

registerPloneFunction(createTableOfContents);