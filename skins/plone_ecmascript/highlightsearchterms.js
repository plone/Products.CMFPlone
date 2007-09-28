function highlightTermInNode(node, word) {
    var contents = node.nodeValue;
    var index = contents.toLowerCase().indexOf(word.toLowerCase());
    if (index < 0) return;
    if ($(node).parent().hasClass("highlightedSearchTerm")) return;
    
    // replace the node with [before]<span>word</span>[after]
    $(node)
        .before(document.createTextNode(contents.substr(0, index)))
        .before(
            $('<span>')
                .addClass("highlightedSearchTerm")
                .text(contents.substr(index, word.length))
        )
        .before(document.createTextNode(contents.substr(index+word.length)))
        .remove();
}

function highlightSearchTerms(terms, startnode) {
    if (!terms || !startnode) return;

    $.each(terms, function(i, term) {
        // don't highlight reserved catalog search terms
        if (!term || /(not|and|or)/.test(term.toLowerCase())) return;
        walkTextNodes(startnode, highlightTermInNode, term);
    });
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
    var result = new Array();
    if (window.decodeReferrer) {
        var referrerSearch = decodeReferrer();
        if (null != referrerSearch && referrerSearch.length > 0) {
            result = referrerSearch;
        }
    }
    var qfinder = new RegExp("(searchterm|SearchableText)=([^&]*)", "gi");
    var qq = qfinder.exec(query);
    if (qq && qq[2]) {
        var terms = qq[2].replace(/\+/g,' ').split(' ');
        result.push.apply(result, $.grep(terms, 'a != ""'));
        return result;
    }
    return result.length == 0 ? false : result;
}

$(function() {
    // search-term-highlighter function --  Geir Baekholt
    var terms = getSearchTermsFromURI(window.location.search);
    // make sure we start the right place so we don't higlight menuitems or breadcrumb
    highlightSearchTerms(terms, getContentArea());
});

