function walkHeaders(node, func, data) {
    /* this is a copy of walkTextNodes in the Plone source, if
    someone was smart they could refactor this into one function
    don't be tempted to use getElementsByTagNames, it won't work
    on Safari (as of Feb 2007), boo! */
    if (!node){return false}
    var valid = Array("h1", "h2", "h3", "h4");
    if (node.hasChildNodes) {
        var child = node.firstChild;
        while (child) {
            walkHeaders(child, func, data);
            child = child.nextSibling;
        }
        var type = node.tagName;
        if (type) {
            type = type.toLowerCase();
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
    var toc = cssQuery('dl.toc');
    if (toc.length == 0) {
       return;
    }
    toc = toc[0];
    var dest = cssQuery('dl.toc dd.portletItem');
    if (dest.length == 0) {
       return;
    }
    dest = dest[0];
    if ( dest.hasChildNodes() ) {
        while ( dest.childNodes.length >= 1 ) {
            dest.removeChild( dest.firstChild );       
        } 
    }

    var content = getContentArea();
    if (!content) {
        return;
    }

    var location = locationWithoutHash();
    var ols = [];
    var i = 0;
    var func = function(node, data) {
        if (hasClassName(node, "documentFirstHeading"))
            return;
        var li = document.createElement('li');
        var link = document.createElement('a');

        link.appendChild(document.createTextNode(getInnerTextFast(node)));
        link.href = location + '#section-' + i;

        li.appendChild(link);

        var anchor = document.createElement('a');
        anchor.name = 'section-' + i;
        node.parentNode.insertBefore(anchor, node);

        var level = node.nodeName.substring(1) - 1;
        // if the current level is deeper, add ol tags
        while (ols.length < level) {
            var ol = document.createElement('ol');
            if (ols.length > 0) {
                if (!ols[ols.length - 1].lastChild) {
                    // create a blank li for cases where, e.g., we have a subheading before any headings
                    ols[ols.length - 1].appendChild(document.createElement('li'));
                }
                ols[ols.length - 1].lastChild.appendChild(ol);            }
            ols.push(ol);
        }
        // if the current level is higher, remove ol tags
        while (ols.length > level) {
            ols.pop();
        }
        ols[ols.length - 1].appendChild(li);
        i++;
    }

    walkHeaders(content, func);
    if (ols.length > 0) {
        toc.style.display = "block";
        dest.appendChild(ols[0]);
    }
}

registerPloneFunction(createTableOfContents);
