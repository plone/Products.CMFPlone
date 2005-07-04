function highlightTermInNode(node, word) {
    var contents = node.nodeValue;
    var index = contents.toLowerCase().indexOf(word.toLowerCase());
    if (index < 0){return false};

    var parent = node.parentNode;
    if (parent.className != "highlightedSearchTerm") {
        // make 3 shiny new nodes
        var hiword = document.createElement("span");
        hiword.className = "highlightedSearchTerm";
        hiword.appendChild(document.createTextNode(contents.substr(index, word.length)));
        parent.insertBefore(document.createTextNode(contents.substr(0, index)), node);
        parent.insertBefore(hiword, node);
        parent.insertBefore(document.createTextNode(contents.substr(index+word.length)), node);
        parent.removeChild(node);
    }
}

function highlightSearchTerms(terms, startnode) {
    // terminate if we hit a non-compliant DOM implementation
    if (!W3CDOM){return false};
    if (!terms){return false};
    if (!startnode){return false};

    for (var term_index=0; term_index < terms.length; term_index++) {
        // don't highlight reserved catalog search terms
        var term = terms[term_index];
        var term_lower = term.toLowerCase();
        if (term_lower != 'not'
            && term_lower != 'and'
            && term_lower != 'or') {
            walkTextNodes(startnode, highlightTermInNode, term);
        }
    }
}

function getSearchTermsFromURI(uri) {
    var query;
    if (typeof decodeURI != 'undefined') {
        query = decodeURI(uri);
    } else if (typeof unescape != 'undefined') {
        // _robert_ ie 5 does not have decodeURI 
        query = unescape(uri);
    } else {
        // we just try to be lucky, for single words this will still work
    }
    var qfinder = new RegExp("searchterm=([^&]*)", "gi");
    var qq = qfinder.exec(query);
    if (qq && qq[1]) {
        return qq[1].replace(/\+/g,' ').split(/\s+/);
    }
    return false;
}

function highlightSearchTermsFromURI() {
    // terminate if we hit a non-compliant DOM implementation
    if (!W3CDOM){return false};

    // search-term-highlighter function --  Geir Bækholt
    var terms = getSearchTermsFromURI(window.location.search);
    // make sure we start the right place so we don't higlight menuitems or breadcrumb
    var contentarea = getContentArea();
    highlightSearchTerms(terms, contentarea);
}

registerPloneFunction(highlightSearchTermsFromURI);
