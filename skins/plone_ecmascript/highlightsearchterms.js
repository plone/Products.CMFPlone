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
function highlightSearchTerm() {
    // search-term-highlighter function --  Geir Bækholt
    query = window.location.search
    // _robert_ ie 5 does not have decodeURI 
    if (typeof decodeURI != 'undefined'){
        query = unescape(decodeURI(query)) // thanks, Casper 
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
            if (!query){return false}
            queries = query.replace(/\+/g,' ').split(/\s+/)            
            // make sure we start the right place so we don't higlight menuitems or breadcrumb
            contentarea = getContentArea();
            for (q=0;q<queries.length;q++) {
                // don't highlight reserved catalog search terms
                if (queries[q].toLowerCase() != 'not'
                    && queries[q].toLowerCase() != 'and'
                    && queries[q].toLowerCase() != 'or') {
                    climb(contentarea,queries[q]);
                }
            }
        }
    }
}
registerPloneFunction(highlightSearchTerm);
