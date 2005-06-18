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
function highlightSearchTerm() {
    // terminate if we hit a non-compliant DOM implementation
    if (!W3CDOM){return false};

    // search-term-highlighter function --  Geir Bækholt
    query = window.location.search
    if (typeof decodeURI != 'undefined') {
        query = decodeURI(query);
    } else if (typeof unescape != 'undefined') {
        // _robert_ ie 5 does not have decodeURI 
        query = unescape(query);
    } else {
        // we just try to be lucky, for single words this will still work
    }
    if (query){
        var qfinder = new RegExp()
        qfinder.compile("searchterm=([^&]*)","gi")
        qq = qfinder.exec(query)
        if (qq && qq[1]){
            query = qq[1]
            if (!query){return false}
            queries = query.replace(/\+/g,' ').split(/\s+/)            
            // make sure we start the right place so we don't higlight menuitems or breadcrumb
            contentarea = getContentArea();
            for (q=0;q<queries.length;q++) {
                // don't highlight reserved catalog search terms
                if (queries[q].toLowerCase() != 'not'
                    && queries[q].toLowerCase() != 'and'
                    && queries[q].toLowerCase() != 'or') {
                    walkTextNodes(contentarea, checkforhighlight, queries[q]);
                }
            }
        }
    }
}
registerPloneFunction(highlightSearchTerm);
