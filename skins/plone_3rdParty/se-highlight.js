/* List of search engine matchers and the referrer search
 * code where carefully borrowed from the
 * "Search Engine Keyword Highlight" by Scott Yang,
 * see http://fucoder.com/code/se-hilite/ for further
 * details.
 */
var searchEngines = [
    ['^http://([^.]+\\.)?google.*', 'q='],              // Google
    ['^http://search\\.yahoo.*', 'p='],                // Yahoo
    ['^http://search\\.msn.*', 'q='],                  // MSN
    ['^http://search\\.aol.*', 'userQuery='],          // AOL
    ['^http://(www\\.)?altavista.*', 'q='],            // AltaVista
    ['^http://(www\\.)?feedster.*', 'q='],             // Feedster
    ['^http://search\\.lycos.*', 'query='],            // Lycos
    ['^http://(www\\.)?alltheweb.*', 'q='],             // AllTheWeb
    ['^http://(www\\.)?ask\\.com.*', 'q=']                   // Ask.com
]

function decodeReferrer(ref) {
    // checks if we are beeing searched by a search engine
    if (null == ref && document.referrer) {
        ref = document.referrer;
    }
    if (!ref) return null;

    var match = new RegExp('');
    var seQuery = '';
    for (var i = 0; i < searchEngines.length; i ++) {
        if (!match.compile) {
            // Safari doesn't support the non-standard compile method
            match = new RegExp(searchEngines[i][0], 'i');
        } else {
            match.compile(searchEngines[i][0], 'i');
        }
        if (ref.match(match)) {
            
            if (!match.compile) {
                match = new RegExp('^.*[?&]'+searchEngines[i][1]+'([^&]+)&?.*$', 'i');
            } else {
                match.compile('^.*[?&]'+searchEngines[i][1]+'([^&]+)&?.*$');
            }
            seQuery = ref.replace(match, '$1');
            if (seQuery) {
                seQuery = decodeURIComponent(seQuery);
                seQuery = seQuery.replace(/\'|"/, '');
                return seQuery.split(/[\s,\+\.]+/);
            }

        }
    }
    return null;
}
